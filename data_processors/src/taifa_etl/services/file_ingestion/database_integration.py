"""
Database Integration for AI Africa Funding Tracker
===============================================

This module integrates the file ingestion pipeline with the database,
extending the existing database insertion functionality.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIntegration:
    """
    Integration with the database for the file ingestion pipeline.
    """
    
    def __init__(self):
        """Initialize the database integration."""
        self.logger = logging.getLogger(__name__)
        
    async def insert_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert records into the database.
        
        Args:
            records: List of records to insert
            
        Returns:
            Dict with insertion results
        """
        self.logger.info(f"Inserting {len(records)} records into the database")
        
        try:
            # Import the enhanced database inserter
            from data_processors.db_inserter_enhanced import insert_enhanced_africa_intelligence_feed
            
            # Prepare records for insertion
            prepared_records = await self._prepare_records_for_insertion(records)
            
            # Insert records
            await insert_enhanced_africa_intelligence_feed(prepared_records)
            
            self.logger.info(f"Successfully inserted {len(records)} records into the database")
            
            return {
                'success': True,
                'inserted_count': len(records),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error inserting records into database: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_records_for_insertion(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare records for insertion into the database.
        
        Args:
            records: List of records to prepare
            
        Returns:
            List of prepared records
        """
        prepared_records = []
        
        for record in records:
            # Create a new record with the required fields
            prepared = {
                # Core fields
                'title': self._get_title(record),
                'description': record.get('project_description', ''),
                'funding_amount': self._format_amount(record),
                'application_deadline': self._parse_date(record.get('deadline')),
                'application_url': record.get('application_url', record.get('source_url', '')),
                
                # Source information
                'source_url': record.get('source_url', ''),
                'source_type': record.get('source_type', 'file_ingestion'),
                'source_name': record.get('source_file', 'manual_import'),
                
                # Organization information
                'organization_name': record.get('organization_name', ''),
                'lead_investor_name': record.get('lead_investor_name', ''),
                
                # Metadata
                'content_hash': record.get('dedup_hash', ''),
                'raw_data': self._prepare_raw_data(record),
                'discovered_date': datetime.now(),
                'last_updated': datetime.now(),
                
                # Classification
                'funding_type': record.get('funding_stage', ''),
                'currency': record.get('currency', 'USD'),
                
                # Status
                'parsed_with_ai': True,
                'verified': False,
                'active': True,
                
                # Localization
                'detected_language': 'en',
                'is_multilingual': False,
                'translation_status': {"en": "original"},
                
                # Additional fields
                'ai_extracted': True,
                'relevance_score': record.get('confidence_score', 0.7) * 100,
                'geographic_focus': record.get('geographic_focus', []),
                'sector_tags': record.get('ai_sectors', []),
                
                # Amount fields
                'amount_exact': record.get('amount_usd'),
                'amount_min': record.get('amount_min'),
                'amount_max': record.get('amount_max'),
            }
            
            # Add transaction date if available
            if record.get('transaction_date'):
                prepared['announcement_date'] = self._parse_date(record.get('transaction_date'))
            
            prepared_records.append(prepared)
        
        return prepared_records
    
    def _get_title(self, record: Dict[str, Any]) -> str:
        """
        Generate a title for the record if not available.
        
        Args:
            record: Record to generate title for
            
        Returns:
            Title string
        """
        if record.get('title'):
            return record['title']
        
        # Generate title from available fields
        org_name = record.get('organization_name', '')
        amount = self._format_amount(record)
        stage = record.get('funding_stage', '')
        
        if org_name and amount:
            return f"{org_name} receives {amount} {stage} funding"
        elif org_name:
            return f"{org_name} funding opportunity"
        else:
            return "AI Funding Opportunity"
    
    def _format_amount(self, record: Dict[str, Any]) -> str:
        """
        Format the amount for display.
        
        Args:
            record: Record containing amount information
            
        Returns:
            Formatted amount string
        """
        amount = record.get('amount_usd')
        currency = record.get('currency', 'USD')
        
        if not amount:
            return "Undisclosed amount"
        
        # Format based on magnitude
        try:
            amount_float = float(amount)
            
            if amount_float >= 1_000_000_000:
                return f"{currency} {amount_float / 1_000_000_000:.1f} billion"
            elif amount_float >= 1_000_000:
                return f"{currency} {amount_float / 1_000_000:.1f} million"
            elif amount_float >= 1_000:
                return f"{currency} {amount_float / 1_000:.1f}k"
            else:
                return f"{currency} {amount_float:,.0f}"
        except (ValueError, TypeError):
            return str(amount)
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """
        Parse a date value to a datetime object.
        
        Args:
            date_value: Date value to parse
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_value:
            return None
        
        try:
            if isinstance(date_value, datetime):
                return date_value
            elif isinstance(date_value, str):
                # Try ISO format first
                try:
                    return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except ValueError:
                    # Try other formats
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%B %d, %Y', '%d %B %Y'):
                        try:
                            return datetime.strptime(date_value, fmt)
                        except ValueError:
                            continue
            return None
        except Exception:
            return None
    
    def _prepare_raw_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the raw_data field for the database.
        
        Args:
            record: Record to prepare raw_data for
            
        Returns:
            Dict with raw_data
        """
        # Include all original fields in raw_data
        raw_data = {
            'source_type': record.get('source_type', 'file_ingestion'),
            'source_file': record.get('source_file', ''),
            'extraction_method': record.get('extraction_method', 'auto'),
            'confidence_score': record.get('confidence_score', 0.7),
            'processed_at': datetime.now().isoformat(),
            'ingestion_branch': 'file_ingestion',
            'original_currency': record.get('currency', 'USD'),
            'original_amount': record.get('amount_original', record.get('amount_usd')),
        }
        
        # Add any additional fields that might be useful
        for key, value in record.items():
            if key not in raw_data and key not in ('dedup_hash', 'duplicate_info'):
                raw_data[key] = value
        
        return raw_data


# Create a singleton instance
database_integration = DatabaseIntegration()