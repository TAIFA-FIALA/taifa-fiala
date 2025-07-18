"""
Database Configuration Helper
============================

This script helps diagnose and fix database connection issues by parsing
the DATABASE_URL and extracting components.
"""

import os
import re
from urllib.parse import urlparse

def parse_db_url(url):
    """Parse a database URL into components"""
    if not url:
        print("Error: DATABASE_URL is not set")
        return {}
    
    try:
        parsed = urlparse(url)
        
        # Extract user and password (might contain special chars)
        auth = parsed.netloc.split('@')[0] if '@' in parsed.netloc else ''
        user = auth.split(':')[0] if ':' in auth else auth
        password = auth.split(':')[1] if ':' in auth else ''
        
        # Extract host and port
        host_port = parsed.netloc.split('@')[1] if '@' in parsed.netloc else parsed.netloc
        host = host_port.split(':')[0] if ':' in host_port else host_port
        port = host_port.split(':')[1] if ':' in host_port else '5432'
        
        # Extract database name
        db_name = parsed.path.lstrip('/')
        
        return {
            "driver": "postgresql+asyncpg",
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "database": db_name
        }
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        return {}

def main():
    """Main function to extract DB components"""
    # Get DATABASE_URL from environment or .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.environ.get("DATABASE_URL", "")
    print(f"Original DATABASE_URL: {database_url}")
    
    # Parse the URL
    components = parse_db_url(database_url)
    
    if not components:
        print("Could not parse DATABASE_URL")
        return
    
    # Print components
    print("\nDatabase Components:")
    print(f"  Driver: {components.get('driver')}")
    print(f"  User: {components.get('user')}")
    print(f"  Password: {'*' * len(components.get('password', ''))}")
    print(f"  Host: {components.get('host')}")
    print(f"  Port: {components.get('port')}")
    print(f"  Database: {components.get('database')}")
    
    # Construct a clean URL
    clean_url = f"{components['driver']}://{components['user']}"
    if components.get('password'):
        clean_url += f":{components['password']}"
    clean_url += f"@{components['host']}:{components['port']}/{components['database']}"
    
    print(f"\nConstructed clean URL: {clean_url}")
    
    # Suggest environment variable exports
    print("\nSuggested environment variable exports:")
    print(f"export DB_USER=\"{components.get('user')}\"")
    print(f"export DB_PASSWORD=\"{components.get('password')}\"")
    print(f"export DB_HOST=\"{components.get('host')}\"")
    print(f"export DB_PORT=\"{components.get('port')}\"")
    print(f"export DB_NAME=\"{components.get('database')}\"")
    print(f"export DATABASE_URL=\"{clean_url}\"")

if __name__ == "__main__":
    main()
