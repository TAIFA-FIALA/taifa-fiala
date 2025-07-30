import os
import asyncio
import psycopg
from dotenv import load_dotenv

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment variable
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Extract connection parameters from the URL
        # Format: postgresql+asyncpg://user:password@host:port/dbname
        url_parts = db_url.split('://', 1)[1].split('@')
        user_pass = url_parts[0].split(':')
        host_port_db = url_parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1]
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        dbname = host_port_db[1]
        
        print(f"Connecting to: host={host}, port={port}, dbname={dbname}, user={user}, password=***")
        
        # Connect directly with psycopg with explicit GSSAPI disable
        conn_string = f"host={host} port={port} dbname={dbname} user={user} password={password} sslmode=prefer gssencmode=disable"
        print(f"Connection string (sanitized): host={host} port={port} dbname={dbname} user={user} password=*** sslmode=prefer gssencmode=disable")
        
        # Try connecting
        async with await psycopg.AsyncConnection.connect(conn_string) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                print(f"Connection successful, query result: {result}")
                return True
                
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
