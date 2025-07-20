"""
Supabase utility functions for the enrichment pipeline.

This module provides helper functions to interact with Supabase for the enrichment pipeline,
replacing direct SQLAlchemy database access with Supabase client calls.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import Client
from app.core.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class SupabaseUtils:
    """Utility class for Supabase operations in the enrichment pipeline."""
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.supabase: Client = get_supabase_client()
        if not self.supabase:
            raise RuntimeError("Failed to initialize Supabase client")
    
    async def get_sparse_rss_items(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve RSS items that need enrichment (sparse data).
        
        Args:
            hours: Number of hours to look back for items
            limit: Maximum number of items to return
            
        Returns:
            List of RSS items that need enrichment
        """
        try:
            # Calculate the timestamp for the cutoff
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            # Query for sparse RSS items that need enrichment
            response = self.supabase.table('ai_intelligence_feed') \
                .select('*') \
                .gte('created_at', cutoff_time) \
                .ilike('source_type', '%rss%') \
                .or_('funding_amount.is.null,'
                     'application_deadline.is.null,'
                     'eligibility_criteria.is.null,'
                     'contact_email.is.null') \
                .limit(limit) \
                .execute()
            
            logger.info(f"Retrieved {len(response.data)} sparse RSS items for enrichment")
            return response.data
            
        except Exception as e:
            logger.error(f"Error retrieving sparse RSS items: {e}")
            return []
    
    async def update_enriched_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an RSS item with enriched data.
        
        Args:
            item_id: ID of the item to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update the item in Supabase
            response = self.supabase.table('ai_intelligence_feed') \
                .update(updates) \
                .eq('id', item_id) \
                .execute()
            
            if response.data:
                logger.debug(f"Successfully updated item {item_id} with enriched data")
                return True
            else:
                logger.warning(f"No records were updated for item {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating enriched item {item_id}: {e}")
            return False
    
    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single item by its ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            The item data or None if not found
        """
        try:
            response = self.supabase.table('ai_intelligence_feed') \
                .select('*') \
                .eq('id', item_id) \
                .single() \
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            logger.error(f"Error retrieving item {item_id}: {e}")
            return None
    
    async def bulk_update_items(self, updates: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Update multiple items in bulk.
        
        Args:
            updates: List of update objects, each containing 'id' and fields to update
            
        Returns:
            Dictionary with success and failure counts
        """
        if not updates:
            return {'success': 0, 'failed': 0}
        
        success = 0
        failed = 0
        
        for update in updates:
            if 'id' not in update:
                logger.warning("Skipping update with missing 'id' field")
                failed += 1
                continue
                
            item_id = update.pop('id')
            if await self.update_enriched_item(item_id, update):
                success += 1
            else:
                failed += 1
        
        return {'success': success, 'failed': failed}

# Create a singleton instance
supabase_utils = SupabaseUtils()
