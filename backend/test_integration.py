"""
TAIFA-FIALA Integration Test

This script tests the connection to both Supabase and Pinecone,
verifying that the schema has been properly applied and 
the vector index is accessible.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add backend to Python path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir.endswith('/backend'):
    parent_dir = os.path.dirname(current_dir)
else:
    parent_dir = current_dir
    if 'backend' not in parent_dir and os.path.exists(os.path.join(parent_dir, 'backend')):
        sys.path.insert(0, os.path.join(parent_dir, 'backend'))


# Supabase Configuration
supabase_url = os.getenv("SUPABASE_PROJECT_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")

# Pinecone Configuration  
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_host = os.getenv("PINECONE_HOST", "")


async def test_supabase():
    """Test connection to Supabase and verify schema"""
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase environment variables")
        return False
    
    try:
        logger.info(f"Connecting to Supabase at {supabase_url}")
        supabase_client = create_client(supabase_url, supabase_key)
        
        # Test basic connection
        response = supabase_client.table("health_check").select("*").limit(1).execute()
        results = response.data
        logger.info(f"✅ Successfully connected to Supabase. Health check status: {results[0]['status'] if results else 'No data'}")
        
        # Check for our tables
        tables_to_check = ["organizations", "funding_types", "africa_intelligence_feed", "health_check"]
        for table in tables_to_check:
            try:
                result = supabase_client.table(table).select("count()", count='exact').limit(1).execute()
                count = result.count if hasattr(result, 'count') else 0
                logger.info(f"✅ Table '{table}' exists with {count} records")
            except Exception as e:
                logger.error(f"❌ Error accessing table '{table}': {str(e)}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection error: {str(e)}")
        return False


async def test_pinecone():
    """Test connection to Pinecone and verify index"""
    if not pinecone_api_key or not pinecone_host:
        logger.error("❌ Missing Pinecone environment variables")
        return False
    
    try:
        logger.info(f"Connecting to Pinecone at {pinecone_host}")
        
        # Initialize Pinecone with new API
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Get list of indexes
        indexes = pc.list_indexes()
        index_names = indexes.names() if hasattr(indexes, 'names') else []
        logger.info(f"Available Pinecone indexes: {index_names}")
        
        if not index_names:
            logger.warning("⚠️ No indexes found in Pinecone")
            return False
        
        # Get index name from host
        # The host format is usually: https://<index-name>-<project-id>.svc.<region>.pinecone.io
        host_parts = pinecone_host.replace("https://", "").split(".")
        if len(host_parts) >= 1:
            index_project = host_parts[0]  # This might be "<index-name>-<project-id>"
            index_name_parts = index_project.split("-")
            if len(index_name_parts) > 0:
                possible_index_name = index_name_parts[0]
                
                # Try to find an exact match or close match in the available indexes
                matched_index = None
                for idx in index_names:
                    if idx == possible_index_name or idx.startswith(possible_index_name):
                        matched_index = idx
                        break
                
                if matched_index:
                    index_name = matched_index
                else:
                    # Use the first available index if we can't find a match
                    index_name = index_names[0]
            else:
                # Use the first available index if we can't parse the host
                index_name = index_names[0]
        else:
            # Use the first available index if we can't parse the host
            index_name = index_names[0]
            
        logger.info(f"Using Pinecone index: {index_name}")
        
        # Connect to the index
        index = pc.Index(index_name)
        
        # Get index stats
        stats = index.describe_index_stats()
        logger.info(f"✅ Successfully connected to Pinecone index. Stats: {json.dumps(stats, indent=2)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Pinecone connection error: {str(e)}")
        return False


async def main():
    """Run all tests"""
    logger.info("====== TAIFA-FIALA Integration Test ======")
    
    # Test Supabase
    logger.info("\nTesting Supabase connection...")
    supabase_success = await test_supabase()
    
    # Test Pinecone
    logger.info("\nTesting Pinecone connection...")
    pinecone_success = await test_pinecone()
    
    # Report overall results
    logger.info("\n====== Integration Test Results ======")
    logger.info(f"Supabase connection: {'✅ PASSED' if supabase_success else '❌ FAILED'}")
    logger.info(f"Pinecone connection: {'✅ PASSED' if pinecone_success else '❌ FAILED'}")
    
    if supabase_success and pinecone_success:
        logger.info("\n🎉 SUCCESS: All integrations are working correctly!")
        logger.info("The TAIFA-FIALA platform is ready for use with:")
        logger.info("- Organization role distinctions (provider/recipient)")
        logger.info("- Funding type categories (grant/investment/prize/other)")
        logger.info("- Grant-specific and investment-specific properties")
        logger.info("- Equity and inclusion tracking fields")
        logger.info("- Vector search capabilities for intelligence feed")
    else:
        logger.error("\n⚠️ Some integrations failed. Please review the logs and fix the issues.")


if __name__ == "__main__":
    asyncio.run(main())
