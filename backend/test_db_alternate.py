"""
Alternative Database Connection Test
===================================
"""
import asyncio
import os
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

# Get database connection parameters
# Try with quoted username to avoid parsing issues with the dot
DB_USER = "postgres.turcbnsgdlyelzmcqixd"
DB_PASSWORD = "cbGzmHCTZqbEsg6afVhL"
DB_HOST = "aws-0-eu-central-2.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"

async def test_connection_with_dsn():
    """Test connection using DSN string"""
    print("\n--- Testing Connection with DSN String ---")
    try:
        # Create a connection using DSN
        dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"Connecting with DSN: {dsn[:25]}...(truncated)")
        conn = await asyncpg.connect(dsn=dsn)
        
        version = await conn.fetchval('SELECT version()')
        print(f"Connected! PostgreSQL version: {version}")
        
        await conn.close()
        print("Connection closed successfully")
        return True
    except Exception as e:
        print(f"DSN connection error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_connection_with_uri():
    """Test connection using URI with escaped username"""
    print("\n--- Testing Connection with URI and Escaped Username ---")
    try:
        # Create a connection using URI with the username quoted
        # This replaces the dot with %2E to avoid regex issues
        escaped_user = DB_USER.replace('.', '%2E')
        uri = f"postgresql://{escaped_user}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"Connecting with escaped username URI: {uri[:25]}...(truncated)")
        conn = await asyncpg.connect(uri)
        
        version = await conn.fetchval('SELECT version()')
        print(f"Connected! PostgreSQL version: {version}")
        
        await conn.close()
        print("Connection closed successfully")
        return True
    except Exception as e:
        print(f"Escaped URI connection error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("=== Alternative Database Connection Tests ===")
    loop = asyncio.get_event_loop()
    
    # Run both tests
    print("Trying multiple connection methods to bypass the authentication issue...")
    loop.run_until_complete(test_connection_with_dsn())
    print("\n" + "-"*50)
    loop.run_until_complete(test_connection_with_uri())
