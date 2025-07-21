"""
Database Configuration Module

This module provides database connectivity using Supabase client for all database operations.
Direct database connections are not used - all operations go through the Supabase API.
"""
import os
import logging
from typing import Optional, Dict, Any, List, Union, TypeVar, Type
from datetime import datetime

# Import Base from base.py to avoid circular imports
from .base import Base, metadata

# Import Supabase client for API-based operations
from app.core.supabase_client import get_supabase_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = get_supabase_client()

# Type variable for generic model types
ModelType = TypeVar('ModelType', bound='BaseModel')

class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when there's an error connecting to the database"""
    pass

class DatabaseOperationError(DatabaseError):
    """Raised when a database operation fails"""
    pass

def get_table(table_name: str):
    """Get a Supabase table reference with error handling"""
    try:
        return supabase.table(table_name)
    except Exception as e:
        logger.error(f"Error getting table {table_name}: {str(e)}")
        raise DatabaseConnectionError(f"Could not connect to table {table_name}") from e

async def fetch_all(
    table_name: str,
    columns: str = "*",
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    offset: int = 0,
    order_by: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Fetch multiple records from a table with optional filtering and pagination
    
    Args:
        table_name: Name of the table to query
        columns: Comma-separated string of columns to select (default: "*")
        filters: Dictionary of column: value pairs to filter by
        limit: Maximum number of records to return
        offset: Number of records to skip
        order_by: Dictionary of column: 'asc'|'desc' for ordering results
    
    Returns:
        List of records as dictionaries
    """
    try:
        query = get_table(table_name).select(columns).limit(limit).range(offset, offset + limit - 1)
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.eq(key, value)
        
        if order_by:
            for column, direction in order_by.items():
                query = query.order(column, desc=(direction.lower() == 'desc'))
        
        result = query.execute()
        return result.data if hasattr(result, 'data') else []
    except Exception as e:
        logger.error(f"Error fetching from {table_name}: {str(e)}")
        raise DatabaseOperationError(f"Failed to fetch from {table_name}") from e

async def fetch_one(
    table_name: str,
    columns: str = "*",
    filters: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single record from a table
    
    Args:
        table_name: Name of the table to query
        columns: Comma-separated string of columns to select (default: "*")
        filters: Dictionary of column: value pairs to filter by
    
    Returns:
        A single record as a dictionary, or None if not found
    """
    try:
        result = await fetch_all(table_name, columns, filters, limit=1)
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error fetching single record from {table_name}: {str(e)}")
        raise DatabaseOperationError(f"Failed to fetch from {table_name}") from e

async def insert(
    table_name: str,
    data: Dict[str, Any],
    returning: str = "*"
) -> Dict[str, Any]:
    """
    Insert a new record into a table
    
    Args:
        table_name: Name of the table to insert into
        data: Dictionary of column: value pairs to insert
        returning: Columns to return in the response (default: "*")
    
    Returns:
        The inserted record as a dictionary
    """
    try:
        result = get_table(table_name).insert(data).select(returning).execute()
        if hasattr(result, 'data') and result.data:
            return result.data[0]
        raise DatabaseOperationError("No data returned after insert")
    except Exception as e:
        logger.error(f"Error inserting into {table_name}: {str(e)}")
        raise DatabaseOperationError(f"Failed to insert into {table_name}") from e

async def update(
    table_name: str,
    data: Dict[str, Any],
    filters: Dict[str, Any],
    returning: str = "*"
) -> Optional[Dict[str, Any]]:
    """
    Update records in a table
    
    Args:
        table_name: Name of the table to update
        data: Dictionary of column: value pairs to update
        filters: Dictionary of column: value pairs to identify records to update
        returning: Columns to return in the response (default: "*")
    
    Returns:
        The updated record as a dictionary, or None if no records were updated
    """
    try:
        query = get_table(table_name).update(data).select(returning)
        
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data[0] if hasattr(result, 'data') and result.data else None
    except Exception as e:
        logger.error(f"Error updating {table_name}: {str(e)}")
        raise DatabaseOperationError(f"Failed to update {table_name}") from e

async def delete(
    table_name: str,
    filters: Dict[str, Any]
) -> int:
    """
    Delete records from a table
    
    Args:
        table_name: Name of the table to delete from
        filters: Dictionary of column: value pairs to identify records to delete
    
    Returns:
        Number of records deleted
    """
    try:
        query = get_table(table_name).delete()
        
        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)
        
        result = query.execute()
        return len(result.data) if hasattr(result, 'data') else 0
    except Exception as e:
        logger.error(f"Error deleting from {table_name}: {str(e)}")
        raise DatabaseOperationError(f"Failed to delete from {table_name}") from e


# This module only uses Supabase client for database operations

# Configure for Supabase client usage
logger.info("Using Supabase client for all database operations")

# No SQLAlchemy engine or sessions needed - using Supabase client only
engine = None
SessionLocal = None
Base = None

async def get_db():
    """Dependency to get database client"""
    try:
        # Return the Supabase client for all database operations
        yield supabase
    except Exception as e:
        logger.error(f"Error getting database client: {str(e)}")
        raise DatabaseConnectionError("Could not connect to database") from e

# Alias for backward compatibility
get_database = get_db

async def create_tables():
    """No-op function - tables are managed through Supabase directly"""
    logger.info("✅ Using Supabase API - table creation is managed through Supabase")
    return

async def test_connection():
    """Test Supabase API connection"""
    try:
        logger.info("🔄 Testing Supabase API connection...")
        # Test the connection by making a simple query
        result = supabase.table('africa_intelligence_feed').select("id").limit(1).execute()
        if hasattr(result, 'data') and isinstance(result.data, list):
            logger.info("✅ Supabase API connection successful")
            return True
        else:
            logger.error("❌ Supabase API connection failed - invalid response")
            return False
    except Exception as e:
        logger.error(f"❌ Supabase API connection failed: {e}")
        return False
