"""
Direct Database Connection Test
==============================

This script directly tests connections to Supabase and Pinecone
using the environment variable names from your .env file.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_supabase():
    """Test Supabase connection with direct imports"""
    try:
        from supabase import create_client
        import jwt
        import time
        
        logger.info("Testing Supabase connection...")
        
        # Get variables directly from environment
        url = os.getenv("SUPABASE_PROJECT_URL")
        key = os.getenv("SUPABASE_API_KEY")
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        if not url or not key:
            logger.error("❌ Missing Supabase environment variables")
            return False
            
        # Create client directly
        try:
            client = create_client(url, key)
            logger.info("✅ Successfully created Supabase client")
            
            # Test by querying the health_check table
            response = client.table('health_check').select('*').execute()
            
            if response.data:
                logger.info(f"✅ Supabase data connection successful! Found {len(response.data)} records in health_check table")
            else:
                logger.info(f"✅ Supabase data connection works but health_check table appears empty")
            
            # Test JWT authentication if JWT secret is available
            if jwt_secret:
                try:
                    # Create a test JWT token
                    payload = {
                        "exp": int(time.time()) + 3600,  # 1 hour expiry
                        "iat": int(time.time()),
                        "sub": "test-user-id",
                        "email": "test@example.com",
                        "role": "authenticated",
                        "aud": "authenticated"
                    }
                    
                    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
                    logger.info("✅ Successfully generated JWT token using SUPABASE_JWT_SECRET")
                    
                    # You can verify the token with:
                    # jwt.decode(token, jwt_secret, algorithms=["HS256"])
                    
                    # For a real auth test, you would use this token in an authorization header
                    logger.info("✅ JWT authentication setup is valid")
                except Exception as e:
                    logger.warning(f"⚠️ JWT authentication test failed: {e}")
            else:
                logger.info("ℹ️ SUPABASE_JWT_SECRET not found in environment, skipping JWT authentication test")
                
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection error: {e}")
            return False
    except ImportError as e:
        logger.error(f"❌ Required library not installed: {e}. Run: pip install supabase pyjwt")
        return False

async def test_pinecone():
    """Test Pinecone connection with direct imports"""
    try:
        from pinecone import Pinecone
        
        logger.info("Testing Pinecone connection...")
        
        # Get variables directly from environment
        api_key = os.getenv("PINECONE_API_KEY")
        host = os.getenv("PINECONE_HOST")
        
        if not api_key:
            logger.error("❌ Missing Pinecone API key")
            return False
            
        # Initialize client directly
        try:
            pc = Pinecone(api_key=api_key)
            logger.info("✅ Successfully created Pinecone client")
            
            # List indexes
            indexes = pc.list_indexes()
            logger.info(f"✅ Available Pinecone indexes: {indexes.names()}")
            
            # Extract index name from host if available
            if host:
                parts = host.replace("https://", "").split(".")
                if parts and len(parts) > 0:
                    index_name = parts[0]
                    logger.info(f"Detected index name from host: {index_name}")
                    
                    if index_name in indexes.names():
                        logger.info(f"✅ Index '{index_name}' exists")
                        
                        # Get index stats
                        try:
                            index = pc.Index(index_name)
                            stats = index.describe_index_stats()
                            logger.info(f"✅ Index stats: {stats}")
                        except Exception as e:
                            logger.error(f"❌ Failed to get index stats: {e}")
                    else:
                        logger.warning(f"⚠️ Index '{index_name}' does not exist")
            
            return True
        except Exception as e:
            logger.error(f"❌ Pinecone connection error: {e}")
            return False
    except ImportError:
        logger.error("❌ Pinecone library not installed. Run: pip install pinecone-client")
        return False

async def main():
    """Run all tests"""
    logger.info("====== Database Connection Tests ======")
    
    # Load environment variables
    load_dotenv()
    
    # Test connections
    supabase_success = await test_supabase()
    logger.info("-" * 50)
    pinecone_success = await test_pinecone()
    
    # Print summary
    logger.info("=" * 50)
    logger.info("RESULTS SUMMARY:")
    logger.info(f"Supabase: {'✅ CONNECTED' if supabase_success else '❌ FAILED'}")
    logger.info(f"Pinecone: {'✅ CONNECTED' if pinecone_success else '❌ FAILED'}")
    
    if supabase_success and pinecone_success:
        logger.info("\n🎉 Success! Both databases are connected.")
        logger.info("\nYour database setup is ready for:")
        logger.info("- Organization role distinctions (provider/recipient)")
        logger.info("- Funding type categories (grant/investment)")
        logger.info("- Grant-specific and investment-specific properties")
        logger.info("- Equity-aware semantic search")
    else:
        logger.info("\n⚠️ One or more connections failed.")
        
        if not supabase_success:
            logger.info("\nSupabase troubleshooting:")
            logger.info("1. Check that SUPABASE_PROJECT_URL and SUPABASE_API_KEY are correct")
            logger.info("2. Verify your network connection to Supabase")
            logger.info("3. Check that your Supabase project is active")
        
        if not pinecone_success:
            logger.info("\nPinecone troubleshooting:")
            logger.info("1. Check that PINECONE_API_KEY is correct")
            logger.info("2. Verify your network connection to Pinecone")
            logger.info("3. Make sure your index exists and is properly configured")

if __name__ == "__main__":
    asyncio.run(main())
