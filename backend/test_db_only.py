"""
Simple Database Connection Test
==============================
"""
import asyncio
import os
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

# Get database connection parameters
DB_USER = "postgres.turcbnsgdlyelzmcqixd"
DB_PASSWORD = "cbGzmHCTZqbEsg6afVhL"
DB_HOST = "aws-0-eu-central-2.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"

async def test_asyncpg_connection():
    """Test direct asyncpg connection"""
    print("\n--- Testing Direct asyncpg Connection ---")
    try:
        # Create a connection
        print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        
        # Run a simple query
        version = await conn.fetchval('SELECT version()')
        print(f"Connected! PostgreSQL version: {version}")
        
        # Close the connection
        await conn.close()
        print("Connection closed successfully")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("=== Direct Database Connection Test ===")
    asyncio.run(test_asyncpg_connection())
