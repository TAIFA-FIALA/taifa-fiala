"""
Database Configuration for TAIFA-FIALA
======================================

This module handles configuration and connections for both:
1. Supabase (PostgreSQL) - primary database for structured data
2. Pinecone - vector database for semantic search

The configuration is loaded from environment variables.
"""

import os
import logging
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client, Client
from pinecone import ServerlessSpec

# Local imports
from app.core.pinecone_client import get_pinecone_client

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables


# Supabase Configuration
class SupabaseConfig(BaseModel):
    """Configuration for Supabase client"""
    url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    key: str = Field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_API_KEY", ""))
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.url and self.key)

# Pinecone Configuration is already defined in vector_db_config.py

class DatabaseService:
    """Service for database connections and operations"""
    
    def __init__(self):
        self.supabase_config = SupabaseConfig()
        self.supabase_client: Optional[Client] = None
        self.pinecone_client = None
        self.pinecone_index = None
        
        # Initialize connections
        self.initialize()
    
    def initialize(self) -> bool:
        """Initialize database connections"""
        success = True
        
        # Initialize Supabase
        if self.supabase_config.is_valid:
            try:
                self.supabase_client = create_client(
                    self.supabase_config.url,
                    self.supabase_config.key
                )
                logger.info("Successfully connected to Supabase")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {e}")
                success = False
        else:
            logger.warning("Supabase configuration not valid. Skipping connection.")
            success = False
            
        # Initialize Pinecone
        self.pinecone_client = get_pinecone_client()
        if not self.pinecone_client:
            success = False
            
        return success
    
    def get_supabase(self) -> Optional[Client]:
        """Get Supabase client"""
        if not self.supabase_client and self.supabase_config.is_valid:
            try:
                self.supabase_client = create_client(
                    self.supabase_config.url, 
                    self.supabase_config.key
                )
            except Exception as e:
                logger.error(f"Failed to create Supabase client: {e}")
        
        return self.supabase_client
    
    def test_connections(self) -> dict:
        """Test database connections and return status"""
        status = {
            "supabase": False,
            "pinecone": False
        }
        
        # Test Supabase
        supabase = self.get_supabase()
        if supabase:
            try:
                # Simple query to test connection
                result = supabase.table("health_check").select("*").limit(1).execute()
                status["supabase"] = True
            except Exception as e:
                logger.error(f"Supabase connection test failed: {e}")
        
        # Test Pinecone - we'll rely on VectorIndexingService for this
        # This would be integrated with your existing vector_indexing.py
        
        return status

# Create singleton instance
db_service = DatabaseService()

# Export the instance for use in other modules
def get_db_service():
    return db_service

# Export Supabase client getter for direct access
def get_supabase_client() -> Optional[Client]:
    return db_service.get_supabase()
