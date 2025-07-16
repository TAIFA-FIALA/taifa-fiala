"""
Supabase Configuration and Client Management
===========================================

This module handles Supabase database configuration and client management.
"""

import os
import logging
from typing import Optional
from pydantic import BaseModel, Field
from supabase import create_client, Client

class SupabaseConfig(BaseModel):
    """Configuration for Supabase client"""
    url: str = Field(default_factory=lambda: os.getenv("SUPABASE_PROJECT_URL", ""))
    key: str = Field(default_factory=lambda: os.getenv("SUPABASE_API_KEY", ""))
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.url and self.key)

class DatabaseService:
    """Service for database connections and operations"""
    
    def __init__(self):
        self.supabase_config = SupabaseConfig()
        self.supabase_client: Optional[Client] = None
        
        # Initialize connection lazily - don't connect right away
        
    def get_supabase(self) -> Optional[Client]:
        """Get Supabase client, connecting lazily if needed"""
        if not self.supabase_client and self.supabase_config.is_valid:
            try:
                self.supabase_client = create_client(
                    self.supabase_config.url, 
                    self.supabase_config.key
                )
                logger.info("Successfully connected to Supabase")
            except Exception as e:
                logger.error(f"Failed to create Supabase client: {e}")
        
        return self.supabase_client
    
    def test_connection(self) -> bool:
        """Test Supabase connection and return status"""
        supabase = self.get_supabase()
        if not supabase:
            return False
            
        try:
            # Simple query to test connection
            result = supabase.table("health_check").select("*").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

# Create singleton instance
db_service = DatabaseService()

# Export Supabase client getter for direct access
def get_supabase_client() -> Optional[Client]:
    return db_service.get_supabase()
