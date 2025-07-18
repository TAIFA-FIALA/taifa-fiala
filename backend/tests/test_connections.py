"""
Connection Testing Script
========================

This script tests connections to both Supabase and Pinecone 
to verify that the environment variables are set up correctly.
"""

import asyncio
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import services from refactored structure
# Use relative imports for the current project structure
from .db_services import get_supabase_client, db_service
from .vector_services.indexing_service import vector_indexing_service

async def test_supabase_connection():
    """Test connection to Supabase"""
    logger.info("Testing Supabase connection...")
    
    # Get Supabase client
    supabase = get_supabase_client()
    if not supabase:
        logger.error("❌ Failed to get Supabase client. Check your SUPABASE_URL and SUPABASE_KEY.")
        return False
    
    # Test connection with a simple query
    try:
        # Attempt to run a simple query to verify connection
        response = supabase.table("health_check").select("*").limit(1).execute()
        logger.info(f"✅ Successfully connected to Supabase! Response: {response}")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection test failed: {e}")
        
        # If the error might be due to the health_check table not existing, give additional guidance
        if "does not exist" in str(e):
            logger.info("Note: If the health_check table doesn't exist, you might need to create it "
                        "or modify this test to query a table that does exist.")
        
        return False

async def test_pinecone_connection():
    """Test connection to Pinecone"""
    logger.info("Testing Pinecone connection...")
    
    # Initialize vector indexing service
    initialized = await vector_indexing_service.initialize()
    if not initialized:
        logger.error("❌ Failed to initialize Pinecone. Check your PINECONE_API_KEY and PINECONE_INDEX_NAME.")
        return False
    
    # Print index stats to verify connection
    try:
        index_stats = vector_indexing_service.index.describe_index_stats()
        logger.info(f"✅ Successfully connected to Pinecone! Index stats: {index_stats}")
        return True
    except Exception as e:
        logger.error(f"❌ Pinecone connection test failed: {e}")
        return False

async def main():
    """Run connection tests"""
    logger.info("====== Starting Connection Tests ======")
    
    # Test Supabase connection
    supabase_success = await test_supabase_connection()
    
    # Test Pinecone connection
    pinecone_success = await test_pinecone_connection()
    
    # Report results
    logger.info("====== Connection Test Results ======")
    logger.info(f"Supabase Connection: {'✅ SUCCESS' if supabase_success else '❌ FAILED'}")
    logger.info(f"Pinecone Connection: {'✅ SUCCESS' if pinecone_success else '❌ FAILED'}")
    
    if supabase_success and pinecone_success:
        logger.info("🎉 All connections successful! Your environment is properly configured.")
    else:
        logger.info("⚠️ Some connections failed. Please check your environment variables and try again.")

if __name__ == "__main__":
    # Load environment variables
    
    
    # Run the connection tests
    asyncio.run(main())
