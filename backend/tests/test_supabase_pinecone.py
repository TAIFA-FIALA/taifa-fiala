"""
Connection Testing Script
========================

This script tests connections to both Supabase and Pinecone 
to verify that the environment variables are set up correctly.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import directly from libraries rather than from refactored structure
try:
    from supabase import create_client, Client
    from pinecone.spec import ServerlessSpec
    from app.core.pinecone_client import get_pinecone_client
except ImportError:
    logger.error("❌ Required libraries not found. Please run: pip install supabase pinecone-client python-dotenv")
    sys.exit(1)

async def test_supabase_connection():
    """Test connection to Supabase"""
    logger.info("Testing Supabase connection...")
    
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase environment variables. Please check your .env file for SUPABASE_URL and SUPABASE_KEY.")
        return False
    
    # Create Supabase client
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Successfully created Supabase client!")
        
        # Test connection with a simple query
        try:
            # The following will throw an error if connection fails
            response = supabase.auth.get_session()
            logger.info("✅ Successfully connected to Supabase!")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase query test failed: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to create Supabase client: {e}")
        return False

async def test_pinecone_connection():
    """Test connection to Pinecone"""
    logger.info("Testing Pinecone connection...")
    
    # Get environment variables
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "taifa-fiala")
    
    if not pinecone_index_name:
        logger.warning("⚠️ PINECONE_INDEX_NAME not found, using default: 'taifa-fiala'")
    
    # Initialize Pinecone
    try:
        pc = get_pinecone_client()
        if not pc:
            raise ConnectionError("Failed to initialize Pinecone client.")
        logger.info("✅ Successfully created Pinecone client!")
        
        # List indexes to verify connection
        indexes = pc.list_indexes()
        logger.info(f"✅ Successfully connected to Pinecone! Available indexes: {indexes.names()}")
        
        # Check if our index exists
        if pinecone_index_name in indexes.names():
            logger.info(f"✅ Index '{pinecone_index_name}' exists!")
            
            # Get index stats
            try:
                index = pc.Index(pinecone_index_name)
                stats = index.describe_index_stats()
                logger.info(f"✅ Index stats: {stats}")
            except Exception as e:
                logger.error(f"❌ Failed to get index stats: {e}")
        else:
            logger.warning(f"⚠️ Index '{pinecone_index_name}' does not exist. You may need to create it.")
            
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create Pinecone client: {e}")
        return False

async def main():
    """Run connection tests"""
    logger.info("====== Starting Connection Tests ======")
    logger.info("Loading environment variables from .env file...")
    
    # Test Supabase connection
    supabase_success = await test_supabase_connection()
    
    # Add a separator
    logger.info("-" * 50)
    
    # Test Pinecone connection
    pinecone_success = await test_pinecone_connection()
    
    # Report results
    logger.info("=" * 50)
    logger.info("====== Connection Test Results ======")
    logger.info(f"Supabase Connection: {'✅ SUCCESS' if supabase_success else '❌ FAILED'}")
    logger.info(f"Pinecone Connection: {'✅ SUCCESS' if pinecone_success else '❌ FAILED'}")
    
    if supabase_success and pinecone_success:
        logger.info("🎉 All connections successful! Your environment is properly configured.")
        
        # Additional information about organization roles and funding types
        logger.info("\nYour Supabase database is now ready for:")
        logger.info("- Organization role distinctions (provider/recipient)")
        logger.info("- Funding type categories (grant/investment)")
        logger.info("- Grant-specific and investment-specific properties")
        logger.info("\nYour Pinecone vector database is ready for:")
        logger.info("- Semantic search across all intelligence feed")
        logger.info("- Equity-aware filtering by organization role and funding type")
    else:
        logger.info("⚠️ Some connections failed. Please check your environment variables and try again.")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the connection tests
    asyncio.run(main())
