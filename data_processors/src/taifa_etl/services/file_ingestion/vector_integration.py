"""
Vector Database Integration for AI Africa Funding Tracker
=====================================================

This module integrates the file ingestion pipeline with the Pinecone vector database,
allowing for semantic search of funding data.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import asyncio  
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabaseIntegration:
    """
    Integration with the Pinecone vector database for the file ingestion pipeline.
    """
    
    def __init__(self):
        """Initialize the vector database integration."""
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the vector database connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
            
        try:
            # Import vector services
            from backend.app.core.vector_services.helper_functions import (
                index_intelligence_item,
                index_organization
            )
            
            self.index_intelligence_item = index_intelligence_item
            self.index_organization = index_organization
            
            self.initialized = True
            self.logger.info("Vector database integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing vector database integration: {e}")
            return False
    
    async def index_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index records in the vector database.
        
        Args:
            records: List of records to index
            
        Returns:
            Dict with indexing results
        """
        if not await self.initialize():
            return {
                'success': False,
                'error': 'Vector database integration not initialized',
                'timestamp': datetime.now().isoformat()
            }
        
        self.logger.info(f"Indexing {len(records)} records in vector database")
        
        try:
            indexed_count = 0
            failed_count = 0
            
            for record in records:
                try:
                    # Prepare record for indexing
                    intelligence_item = await self._prepare_intelligence_item(record)
                    
                    # Index the record
                    result = await self.index_intelligence_item(intelligence_item)
                    
                    if result.success:
                        indexed_count += 1
                    else:
                        failed_count += 1
                        self.logger.warning(f"Failed to index record: {result.error}")
                        
                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Error indexing record: {e}")
            
            # Index organizations if present
            organizations = self._extract_organizations(records)
            org_indexed_count = 0
            
            for org in organizations:
                try:
                    # Prepare organization for indexing
                    organization = await self._prepare_organization(org)
                    
                    # Index the organization
                    result = await self.index_organization(organization)
                    
                    if result.success:
                        org_indexed_count += 1
                    else:
                        self.logger.warning(f"Failed to index organization: {result.error}")
                        
                except Exception as e:
                    self.logger.error(f"Error indexing organization: {e}")
            
            self.logger.info(f"Successfully indexed {indexed_count} records and {org_indexed_count} organizations")
            
            return {
                'success': True,
                'indexed_count': indexed_count,
                'failed_count': failed_count,
                'org_indexed_count': org_indexed_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error indexing records in vector database: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_intelligence_item(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a record for indexing as an intelligence item.
        
        Args:
            record: Record to prepare
            
        Returns:
            Prepared intelligence item
        """
        # Create a new record with the required fields
        intelligence_item = {
            'id': record.get('id', f"file_ingestion_{datetime.now().timestamp()}"),
            'title': record.get('title', ''),
            'description': record.get('project_description', ''),
            'amount_usd': record.get('amount_usd'),
            'transaction_date': record.get('transaction_date'),
            'organization_name': record.get('organization_name', ''),
            'funding_stage': record.get('funding_stage', ''),
            'lead_investor_name': record.get('lead_investor_name', ''),
            'ai_sectors': record.get('ai_sectors', []),
            'geographic_focus': record.get('geographic_focus', []),
            'source_url': record.get('source_url', ''),
            'source_type': record.get('source_type', 'file_ingestion'),
            'confidence_score': record.get('confidence_score', 0.7),
            'extraction_method': record.get('extraction_method', 'auto'),
            'processed_at': datetime.now().isoformat()
        }
        
        return intelligence_item
    
    async def _prepare_organization(self, org: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare an organization for indexing.
        
        Args:
            org: Organization to prepare
            
        Returns:
            Prepared organization
        """
        # Create a new record with the required fields
        organization = {
            'id': org.get('id', f"file_ingestion_org_{datetime.now().timestamp()}"),
            'name': org.get('name', ''),
            'description': org.get('description', ''),
            'website': org.get('website', ''),
            'headquarters_country': org.get('headquarters_country', ''),
            'headquarters_city': org.get('headquarters_city', ''),
            'role': org.get('role', 'provider'),  # Default to provider
            'provider_type': org.get('provider_type', ''),
            'recipient_type': org.get('recipient_type', ''),
            'ai_domains': org.get('ai_domains', []),
            'geographic_focus': org.get('geographic_focus', []),
            'processed_at': datetime.now().isoformat()
        }
        
        return organization
    
    def _extract_organizations(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract unique organizations from records.
        
        Args:
            records: Records to extract organizations from
            
        Returns:
            List of unique organizations
        """
        organizations = {}
        
        for record in records:
            # Extract organization from record
            org_name = record.get('organization_name')
            if not org_name:
                continue
                
            # Create or update organization
            if org_name not in organizations:
                organizations[org_name] = {
                    'name': org_name,
                    'role': 'provider',  # Default to provider
                    'ai_domains': record.get('ai_sectors', []),
                    'geographic_focus': record.get('geographic_focus', [])
                }
            else:
                # Update existing organization
                org = organizations[org_name]
                
                # Merge AI domains
                if 'ai_sectors' in record and record['ai_sectors']:
                    org['ai_domains'] = list(set(org['ai_domains'] + record['ai_sectors']))
                
                # Merge geographic focus
                if 'geographic_focus' in record and record['geographic_focus']:
                    org['geographic_focus'] = list(set(org['geographic_focus'] + record['geographic_focus']))
        
        return list(organizations.values())


# Create a singleton instance
vector_database_integration = VectorDatabaseIntegration()