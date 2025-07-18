"""
Vector Database Integration Implementation
=======================================

Implements the connection and operations between the TAIFA-FIALA platform
and the Pinecone vector database with Microsoft's multilingual embedding model.
This integration preserves and enhances the equity-aware aspects of the platform.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from pinecone.spec import ServerlessSpec
from pinecone.core.client.models import QueryResponse

from app.core.pinecone_client import get_pinecone_client
from app.core.vector_db_config import PineconeConfig, VectorIndexType, EmbeddingProvider, default_config
from app.models.funding import AfricaIntelligenceItem
from app.models.validation import ValidationResult
from app.models.organization import Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBIntegration:
    """Integration class for Pinecone vector database operations"""
    
    def __init__(self, config: PineconeConfig = default_config):
        self.config = config
        self.pinecone_client = None
        self.index = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize connection to Pinecone"""
        try:
            # Initialize Pinecone client
            self.pinecone_client = get_pinecone_client()
            if not self.pinecone_client:
                raise ConnectionError("Failed to initialize Pinecone client.")
            
            # Check if index exists, create if not
            index_list = self.pinecone_client.list_indexes()
            if self.config.index_name not in index_list.names():
                self.logger.info(f"Creating new index: {self.config.index_name}")
                
                # Create index with serverless spec
                self.pinecone_client.create_index(
                    name=self.config.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric,
                    spec=ServerlessSpec(
                        cloud=self.config.cloud,
                        region=self.config.region
                    ),
                    metadata_config={
                        "indexed": list(self.config.equity_metadata_fields)[:5]  # Pinecone limits indexed fields
                    }
                )
                self.logger.info(f"Created index {self.config.index_name} successfully")
                
            # Connect to the index
            self.index = self.pinecone_client.Index(self.config.index_name)
            self.initialized = True
            self.logger.info(f"Connected to index: {self.config.index_name}")
            
            # Check index stats
            stats = self.index.describe_index_stats()
            self.logger.info(f"Index stats: {stats}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            return False
    
    async def index_intelligence_item(self, opportunity: AfricaIntelligenceItem) -> bool:
        """Index a intelligence item with equity-aware metadata"""
        if not self.initialized:
            await self.initialize()
            
        try:
            # Generate a unique ID for the opportunity
            vector_id = f"opportunity_{opportunity.id}"
            
            # Extract content for vector embedding
            # This step will be handled by the Microsoft model in Pinecone
            content = self._prepare_opportunity_content(opportunity)
            
            # Prepare metadata with equity-aware fields
            metadata = self._prepare_opportunity_metadata(opportunity)
            
            # Use Pinecone's hosted embedding with the index client
            # For Microsoft's multilingual-e5-large model
            self.index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "metadata": metadata,
                        "values": None  # No need to provide values when using a hosted embedding model
                    }
                ],
                namespace=VectorIndexType.OPPORTUNITIES.value,
                async_req=False,
                use_hosted_model=True
            )
            
            self.logger.info(f"Indexed opportunity {opportunity.id} successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to index opportunity {opportunity.id}: {e}")
            return False
    
    async def index_organization(self, organization: Organization) -> bool:
        """Index an organization with role/type metadata"""
        if not self.initialized:
            await self.initialize()
            
        try:
            # Generate a unique ID for the organization
            vector_id = f"organization_{organization.id}"
            
            # Extract content for vector embedding
            content = self._prepare_organization_content(organization)
            
            # Prepare metadata with organization role and type information
            metadata = {
                "organization_id": organization.id,
                "name": organization.name,
                "role": organization.role,  # provider, recipient, both
                "provider_type": getattr(organization, "provider_type", None),  # granting_agency, venture_capital, etc.
                "recipient_type": getattr(organization, "recipient_type", None),  # grantee, startup, etc.
                "startup_stage": getattr(organization, "startup_stage", None),
                "country_code": organization.country_code,
                "region": organization.region
            }
            
            # Use Pinecone's hosted embedding
            self.index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "metadata": metadata,
                        "values": None  # No need to provide values when using a hosted embedding model
                    }
                ],
                namespace=VectorIndexType.ORGANIZATIONS.value,
                async_req=False,
                use_hosted_model=True
            )
            
            self.logger.info(f"Indexed organization {organization.id} successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to index organization {organization.id}: {e}")
            return False
    
    async def search_opportunities(self, 
                                 query: str, 
                                 filters: Optional[Dict[str, Any]] = None,
                                 top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for intelligence feed with equity-aware filtering
        
        Parameters:
        - query: Search text (will be embedded by Microsoft's multilingual model)
        - filters: Dict of filters to apply (geographic, inclusion, funding_type, etc.)
        - top_k: Number of results to return
        
        Returns:
        - List of matching opportunities with metadata
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Prepare filter condition if provided
            filter_dict = {}
            
            if filters:
                # Handle special filters for funding types
                if "funding_category" in filters:
                    filter_dict["funding_category"] = {"$eq": filters["funding_category"]}  # grant, investment, prize, etc
                
                # Handle organization role filters
                if "organization_role" in filters:
                    filter_dict["organization_role"] = {"$eq": filters["organization_role"]}
                    
                # Handle geographic filters
                if "geographic_scopes" in filters:
                    # Check for underserved regions to implement equity-aware search
                    filter_dict["geographic_scopes"] = {"$in": filters["geographic_scopes"]}
                
                # Handle inclusion indicators
                for indicator in ["underserved_focus", "women_focus", "youth_focus"]:
                    if indicator in filters and filters[indicator]:
                        filter_dict[indicator] = {"$eq": True}
            
            # Execute search with Microsoft's multilingual model
            results = self.index.query(
                namespace=VectorIndexType.OPPORTUNITIES.value,
                top_k=top_k,
                filter=filter_dict if filter_dict else None,
                vector=None,  # No need to provide vector when using a hosted model
                text=query,  # Provide the raw text for the hosted model to embed
                include_metadata=True
            )
            
            # Process and return results
            processed_results = []
            for match in results.matches:
                result = {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata,
                    "opportunity_id": int(match.id.split("_")[1]) if match.id.startswith("opportunity_") else None
                }
                processed_results.append(result)
                
            self.logger.info(f"Search returned {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def _prepare_opportunity_content(self, opportunity: AfricaIntelligenceItem) -> str:
        """Prepare opportunity content for embedding with multilingual support"""
        content_parts = [
            f"Title: {opportunity.title}",
            f"Description: {opportunity.description or 'No description'}",
            f"Organization: {opportunity.organization_name or 'Unknown'}",
            f"Amount: {opportunity.funding_amount or 'Not specified'}",
            f"Type: {opportunity.funding_category or 'General'}",  # grant, investment, prize, other
            f"Deadline: {opportunity.deadline or 'No deadline'}",
            f"Status: {opportunity.status or 'Unknown'}"
        ]
        
        # Add grant-specific information
        if hasattr(opportunity, 'is_grant') and opportunity.is_grant:
            grant_props = getattr(opportunity, 'grant_properties', {}) or {}
            if grant_props:
                content_parts.append(f"Grant Duration: {grant_props.get('duration_months', 'Not specified')} months")
                content_parts.append(f"Renewable: {'Yes' if grant_props.get('renewable') else 'No'}")
                content_parts.append(f"Reporting Required: {grant_props.get('reporting_requirements', 'Not specified')}")
        
        # Add investment-specific information
        if hasattr(opportunity, 'is_investment') and opportunity.is_investment:
            investment_props = getattr(opportunity, 'investment_properties', {}) or {}
            if investment_props:
                content_parts.append(f"Equity Required: {investment_props.get('equity_percentage', 'Not specified')}%")
                content_parts.append(f"Expected ROI: {investment_props.get('expected_roi', 'Not specified')}%")
                content_parts.append(f"Valuation Cap: {investment_props.get('valuation_cap', 'Not specified')}")
                content_parts.append(f"Interest Rate: {investment_props.get('interest_rate', 'Not specified')}%")
        
        # Add geographic and domain information
        if hasattr(opportunity, 'geographic_scope_names') and opportunity.geographic_scope_names:
            content_parts.append(f"Geographic Scope: {', '.join(opportunity.geographic_scope_names)}")
        
        if hasattr(opportunity, 'ai_domain_names') and opportunity.ai_domain_names:
            content_parts.append(f"AI Domains: {', '.join(opportunity.ai_domain_names)}")
        
        # Add equity-awareness indicators
        for indicator in ["underserved_focus", "women_focus", "youth_focus"]:
            if hasattr(opportunity, indicator) and getattr(opportunity, indicator):
                content_parts.append(f"{indicator.replace('_', ' ').title()}: Yes")
        
        return "\n".join(content_parts)
    
    def _prepare_opportunity_metadata(self, opportunity: AfricaIntelligenceItem) -> Dict[str, Any]:
        """Prepare metadata for opportunity with enhanced equity-aware fields"""
        metadata = {
            'opportunity_id': opportunity.id,
            'title': opportunity.title[:100] if opportunity.title else "",  # Truncate long titles
            'organization_name': opportunity.organization_name[:100] if opportunity.organization_name else "",
            'funding_amount': str(opportunity.funding_amount or '') if hasattr(opportunity, 'funding_amount') else '',
            'currency': opportunity.currency or 'USD' if hasattr(opportunity, 'currency') else 'USD',
            'status': opportunity.status or 'unknown' if hasattr(opportunity, 'status') else 'unknown',
            'content_type': 'intelligence_item',
        }
        
        # Add deadline if available
        if hasattr(opportunity, 'deadline') and opportunity.deadline:
            try:
                metadata['deadline'] = opportunity.deadline.isoformat()
            except (AttributeError, TypeError):
                metadata['deadline'] = str(opportunity.deadline)
        
        # Add funding type information
        if hasattr(opportunity, 'funding_category'):
            metadata['funding_category'] = opportunity.funding_category  # grant, investment, prize, other
            
        if hasattr(opportunity, 'is_grant'):
            metadata['is_grant'] = opportunity.is_grant
            
        if hasattr(opportunity, 'is_investment'):
            metadata['is_investment'] = opportunity.is_investment
            
        # Add geographic and domain information as strings (Pinecone requirement)
        if hasattr(opportunity, 'geographic_scope_names') and opportunity.geographic_scope_names:
            metadata['geographic_scopes'] = ','.join(opportunity.geographic_scope_names)
            
        if hasattr(opportunity, 'ai_domain_names') and opportunity.ai_domain_names:
            metadata['ai_domains'] = ','.join(opportunity.ai_domain_names)
            
        # Add equity-awareness indicators
        for indicator in ["underserved_focus", "women_focus", "youth_focus"]:
            if hasattr(opportunity, indicator):
                metadata[indicator] = bool(getattr(opportunity, indicator))
                
        # Add organization relationships if available
        if hasattr(opportunity, 'provider_organization_id'):
            metadata['provider_organization_id'] = opportunity.provider_organization_id
            
        if hasattr(opportunity, 'recipient_organization_id'):
            metadata['recipient_organization_id'] = opportunity.recipient_organization_id
            
        # Add funding stage if available
        if hasattr(opportunity, 'funding_stage'):
            metadata['funding_stage'] = opportunity.funding_stage
            
        return metadata
        
    def _prepare_organization_content(self, organization: Organization) -> str:
        """Prepare organization content for embedding"""
        content_parts = [
            f"Name: {organization.name}",
            f"Description: {organization.description or 'No description'}",
            f"Role: {organization.role or 'Unknown'}"  # provider, recipient, both
        ]
        
        # Add provider-specific information
        if hasattr(organization, 'provider_type') and organization.provider_type:
            content_parts.append(f"Provider Type: {organization.provider_type}")  # granting_agency, venture_capital, etc.
            
        # Add recipient-specific information
        if hasattr(organization, 'recipient_type') and organization.recipient_type:
            content_parts.append(f"Recipient Type: {organization.recipient_type}")  # grantee, startup, etc.
            
        # Add startup stage if available
        if hasattr(organization, 'startup_stage') and organization.startup_stage:
            content_parts.append(f"Startup Stage: {organization.startup_stage}")
            
        # Add geographic information
        if hasattr(organization, 'country_name') and organization.country_name:
            content_parts.append(f"Country: {organization.country_name}")
            
        if hasattr(organization, 'region') and organization.region:
            content_parts.append(f"Region: {organization.region}")
            
        return "\n".join(content_parts)


# Example usage in an async context
async def example_usage():
    """Example of how to use the VectorDBIntegration class"""
    # Initialize with config
    vector_db = VectorDBIntegration()
    await vector_db.initialize()
    
    # Search for opportunities with equity-aware filtering
    results = await vector_db.search_opportunities(
        query="healthcare AI funding for women entrepreneurs in West Africa",
        filters={
            "funding_category": "grant",
            "women_focus": True,
            "geographic_scopes": ["west_africa", "nigeria", "ghana"]
        },
        top_k=5
    )
    
    print(f"Found {len(results)} relevant opportunities")
    for result in results:
        print(f"Score: {result['score']:.2f} - {result['metadata']['title']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
