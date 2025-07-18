"""
Diagnostic Script for AI Africa Funding Tracker API
==================================================

This script helps diagnose issues with the API startup process
by checking components individually.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print(f"DATABASE_URL from environment: {os.getenv('DATABASE_URL')}")

async def check_database_connection():
    """Test database connection directly"""
    print("\n--- Database Connection Test ---")
    try:
        from app.core.database import engine, Base
        
        print("Trying to connect to database...")
        async with engine.begin() as conn:
            print("Database connection successful!")
            
            # Try basic query
            result = await conn.execute("SELECT 1")
            print(f"Test query result: {result.scalar()}")
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def check_api_imports():
    """Test API imports"""
    print("\n--- API Imports Test ---")
    try:
        # Test importing api_router
        from app.api import api_router
        print("Successfully imported API router")
        
        # Test modules used by api_router
        import app.api.endpoints
        print("Successfully imported API endpoints")
        
        # Check if africa_intelligence_feed is properly set up
        from app.api.endpoints.africa_intelligence_feed import router as ai_router
        print("Successfully imported africa_intelligence_feed router")
        
        return True
    except Exception as e:
        print(f"API imports error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def main():
    """Main diagnostic function"""
    print("=== AI Africa Funding Tracker API Diagnostic ===\n")
    
    # Check database connection
    db_ok = await check_database_connection()
    
    # Check API imports
    api_ok = await check_api_imports()
    
    # Print summary
    print("\n=== Diagnostic Summary ===")
    print(f"Database Connection: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"API Imports: {'✅ OK' if api_ok else '❌ FAILED'}")
    
    if not db_ok:
        print("\nRecommended action for database issues:")
        print("1. Check that DATABASE_URL is correctly set")
        print("2. Ensure PostgreSQL server is running")
        print("3. Verify credentials and connection parameters")
    
    if not api_ok:
        print("\nRecommended action for API import issues:")
        print("1. Check that all required modules are present")
        print("2. Verify import paths and module structure")
        print("3. Look for circular imports or initialization errors")

if __name__ == "__main__":
    asyncio.run(main())
