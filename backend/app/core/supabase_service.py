"""
Supabase RLS-Compatible Database Service
Provides database access that works with Row Level Security (RLS) enabled
"""

import os
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Supabase client service that respects Row Level Security (RLS)
    Use this instead of direct PostgreSQL connections when RLS is enabled
    """
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')  # Use service role key for admin operations
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized successfully")
    
    async def get_intelligence_items(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get intelligence items with optional filters
        Compatible with RLS policies
        """
        try:
            query = self.client.table('africa_intelligence_feed').select('*')
            
            # Apply filters if provided
            if filters:
                if 'min_relevance_score' in filters:
                    query = query.gte('relevance_score', filters['min_relevance_score'])
                
                if 'validation_status' in filters:
                    query = query.eq('validation_status', filters['validation_status'])
                
                if 'deadline_after' in filters:
                    query = query.gte('deadline', filters['deadline_after'].isoformat())
                
                if 'deadline_before' in filters:
                    query = query.lte('deadline', filters['deadline_before'].isoformat())
                
                if 'min_amount' in filters:
                    query = query.gte('amount_min', filters['min_amount'])
                
                if 'max_amount' in filters:
                    query = query.lte('amount_max', filters['max_amount'])
                
                if 'geographic_focus' in filters:
                    query = query.ilike('country', f"%{filters['geographic_focus']}%")
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            if response.data:
                logger.info(f"Retrieved {len(response.data)} intelligence items")
                return response.data
            else:
                logger.warning("No intelligence items found")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving intelligence items: {e}")
            return []
    
    async def get_intelligence_items_by_ids(self, ids: List[int]) -> List[Dict[str, Any]]:
        """
        Get intelligence items by specific IDs
        Used for vector search result enrichment
        """
        try:
            if not ids:
                return []
            
            response = self.client.table('africa_intelligence_feed').select('*').in_('id', ids).execute()
            
            if response.data:
                logger.info(f"Retrieved {len(response.data)} intelligence items by IDs")
                return response.data
            else:
                logger.warning(f"No intelligence items found for IDs: {ids}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving intelligence items by IDs: {e}")
            return []
    
    async def search_intelligence_items_text(
        self, 
        query: str, 
        allowed_ids: Optional[List[int]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Perform traditional text search on intelligence items
        Compatible with RLS policies
        """
        try:
            # Build text search query
            supabase_query = self.client.table('africa_intelligence_feed').select('*')
            
            # Apply text search on title and description
            search_condition = f"title.ilike.%{query}%,description.ilike.%{query}%,eligibility_criteria.ilike.%{query}%"
            supabase_query = supabase_query.or_(search_condition)
            
            # Filter by allowed IDs if provided (for quality filtering)
            if allowed_ids:
                supabase_query = supabase_query.in_('id', allowed_ids)
            
            # Apply limit
            supabase_query = supabase_query.limit(limit)
            
            response = supabase_query.execute()
            
            if response.data:
                logger.info(f"Text search found {len(response.data)} results for query: '{query}'")
                return response.data
            else:
                logger.info(f"No text search results found for query: '{query}'")
                return []
                
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    async def update_intelligence_item(self, item_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update an intelligence item
        Compatible with RLS policies
        """
        try:
            response = self.client.table('africa_intelligence_feed').update(updates).eq('id', item_id).execute()
            
            if response.data:
                logger.info(f"Successfully updated intelligence item {item_id}")
                return True
            else:
                logger.warning(f"No intelligence item found with ID {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating intelligence item {item_id}: {e}")
            return False
    
    async def insert_intelligence_items(self, items: List[Dict[str, Any]]) -> bool:
        """
        Insert new intelligence items
        Compatible with RLS policies
        """
        try:
            if not items:
                return True
            
            response = self.client.table('africa_intelligence_feed').insert(items).execute()
            
            if response.data:
                logger.info(f"Successfully inserted {len(response.data)} intelligence items")
                return True
            else:
                logger.warning("Failed to insert intelligence items")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting intelligence items: {e}")
            return False
    
    async def get_organizations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get organizations for vector indexing
        Compatible with RLS policies
        """
        try:
            response = self.client.table('organizations').select('*').limit(limit).execute()
            
            if response.data:
                logger.info(f"Retrieved {len(response.data)} organizations")
                return response.data
            else:
                logger.info("No organizations found")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving organizations: {e}")
            return []
    
    def get_sync_client(self) -> Client:
        """
        Get the synchronous Supabase client for non-async operations
        """
        return self.client


# Global instance
_supabase_service = None

def get_supabase_service() -> SupabaseService:
    """
    Get the global Supabase service instance
    Use this instead of direct database connections when RLS is enabled
    """
    global _supabase_service
    
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    
    return _supabase_service


def async_to_sync(async_func):
    """
    Decorator to convert async functions to sync for compatibility
    """
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(async_func(*args, **kwargs))
    
    return wrapper
