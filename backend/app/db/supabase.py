"""
Supabase client utility for database operations.
"""
from typing import Generator
from supabase import create_client, Client
from fastapi import Depends, HTTPException
from ..core.config import settings

# Initialize Supabase client
supabase_client = None

def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.
    
    Returns:
        Client: Supabase client instance
    """
    global supabase_client
    
    if supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise HTTPException(
                status_code=500,
                detail="Supabase configuration is missing. Please check your environment variables."
            )
        
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    return supabase_client
