"""
Vector Indexing Methods
=======================

Implementation of specific indexing methods for different data types.
This module contains the core logic for processing and indexing various entities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .indexing_service import VectorIndexingService
from .pinecone_config import VectorIndexType
from ..etl_architecture import ETLTask, ProcessingResult, PipelineStage

logger = logging.getLogger(__name__)

async def _index_funding_opportunity(self, task: ETLTask) -> ProcessingResult:
    """Process and index a funding opportunity"""
    opportunity_data = task.payload.get('funding_opportunity', {})
    
    if not opportunity_data:
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error="No opportunity data provided"
        )
    
    try:
        # Generate a vector ID
        opportunity_id = opportunity_data.get('id')
        vector_id = f"opp_{opportunity_id}"
        
        # Prepare metadata with organization role distinctions
        metadata = self._prepare_opportunity_metadata(opportunity_data)
        
        # Prepare content for embedding
        content = self._prepare_opportunity_content(opportunity_data)
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[{
                "id": vector_id,
                "metadata": metadata
            }],
            namespace=VectorIndexType.OPPORTUNITIES.value,
            use_hosted_model=True,
            host_text=content
        )
        
        self.logger.info(f"Indexed funding opportunity: {opportunity_id}")
        
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=True,
            data={
                'vector_id': vector_id,
                'namespace': VectorIndexType.OPPORTUNITIES.value
            }
        )
    except Exception as e:
        self.logger.error(f"Error indexing opportunity {opportunity_data.get('id')}: {e}")
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error=str(e)
        )

async def _index_organization(self, task: ETLTask) -> ProcessingResult:
    """Process and index an organization with role distinctions"""
    org_data = task.payload.get('organization', {})
    
    if not org_data:
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error="No organization data provided"
        )
    
    try:
        # Generate a vector ID
        org_id = org_data.get('id')
        vector_id = f"org_{org_id}"
        
        # Prepare metadata with organization role distinctions
        metadata = {
            'organization_id': str(org_id),
            'name': org_data.get('name', '')[:100],
            'website': org_data.get('website', ''),
            'content_type': 'organization',
            # Add organization role information
            'role': org_data.get('role', 'unknown'),  # provider, recipient, both
        }
        
        # Add provider-specific information if applicable
        if org_data.get('role') in ['provider', 'both']:
            metadata['provider_type'] = org_data.get('provider_type', '')  # granting_agency, venture_capital, etc.
        
        # Add recipient-specific information if applicable
        if org_data.get('role') in ['recipient', 'both']:
            metadata['recipient_type'] = org_data.get('recipient_type', '')  # grantee, startup, etc.
            
            # Add startup stage if it's a startup
            if org_data.get('recipient_type') == 'startup':
                metadata['startup_stage'] = org_data.get('startup_stage', '')
        
        # Add geographic and domain focus
        if 'geographic_focus' in org_data:
            geo_focus = org_data['geographic_focus']
            if isinstance(geo_focus, list):
                metadata['geographic_scopes'] = ",".join(geo_focus)
            else:
                metadata['geographic_scopes'] = str(geo_focus)
                
        if 'domain_focus' in org_data:
            domain_focus = org_data['domain_focus']
            if isinstance(domain_focus, list):
                metadata['ai_domains'] = ",".join(domain_focus)
            else:
                metadata['ai_domains'] = str(domain_focus)
        
        # Prepare content for embedding
        content_parts = [
            f"Organization: {org_data.get('name', '')}",
            f"Website: {org_data.get('website', '')}",
            f"Description: {org_data.get('description', '')}",
            f"Role: {org_data.get('role', 'unknown')}"
        ]
        
        # Add role-specific details
        if org_data.get('role') in ['provider', 'both']:
            content_parts.append(f"Provider Type: {org_data.get('provider_type', '')}")
        
        if org_data.get('role') in ['recipient', 'both']:
            content_parts.append(f"Recipient Type: {org_data.get('recipient_type', '')}")
            
            if org_data.get('recipient_type') == 'startup':
                content_parts.append(f"Startup Stage: {org_data.get('startup_stage', '')}")
        
        # Add geographic and domain focus
        if 'geographic_focus' in org_data:
            geo_focus = org_data['geographic_focus']
            if isinstance(geo_focus, list):
                content_parts.append(f"Geographic Focus: {', '.join(geo_focus)}")
            else:
                content_parts.append(f"Geographic Focus: {geo_focus}")
                
        if 'domain_focus' in org_data:
            domain_focus = org_data['domain_focus']
            if isinstance(domain_focus, list):
                content_parts.append(f"AI Domain Focus: {', '.join(domain_focus)}")
            else:
                content_parts.append(f"AI Domain Focus: {domain_focus}")
        
        content = "\n".join(content_parts)
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[{
                "id": vector_id,
                "metadata": metadata
            }],
            namespace=VectorIndexType.ORGANIZATIONS.value,
            use_hosted_model=True,
            host_text=content
        )
        
        self.logger.info(f"Indexed organization: {org_id}")
        
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=True,
            data={
                'vector_id': vector_id,
                'namespace': VectorIndexType.ORGANIZATIONS.value
            }
        )
    except Exception as e:
        self.logger.error(f"Error indexing organization {org_data.get('id')}: {e}")
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error=str(e)
        )

# Add these methods to VectorIndexingService class
VectorIndexingService._index_funding_opportunity = _index_funding_opportunity
VectorIndexingService._index_organization = _index_organization
