#!/usr/bin/env python3
"""
Test database connection to TAIFA_db on mac-mini
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def test_connection():
    """Test connection to TAIFA_db"""
    print("🔍 Testing connection to TAIFA_db...")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Host: {settings.DATABASE_HOST}")
    print(f"Database: {settings.DATABASE_NAME}")
    print(f"User: {settings.DATABASE_USER}")
    print("-" * 50)
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Check if we can access the database
            result = conn.execute(text("SELECT current_database()"))
            current_db = result.fetchone()[0]
            print(f"Connected to database: {current_db}")
            
            # Check if we have necessary permissions
            result = conn.execute(text("SELECT current_user"))
            current_user = result.fetchone()[0]
            print(f"Connected as user: {current_user}")
            
            # Test table creation permissions
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS test_connection (id SERIAL PRIMARY KEY, test_field TEXT)"))
                conn.execute(text("DROP TABLE IF EXISTS test_connection"))
                print("✅ Table creation permissions verified")
            except Exception as e:
                print(f"⚠️  Table creation test failed: {e}")
            
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure PostgreSQL is running on mac-mini")
        print("2. Verify Tailscale connection to 100.75.201.24")
        print("3. Check that TAIFA_db database exists")
        print("4. Verify postgres user has access to TAIFA_db")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Database connection test passed!")
        print("Ready to initialize tables and start the application.")
    else:
        print("\n💥 Database connection test failed!")
        print("Please fix connection issues before proceeding.")
    
    sys.exit(0 if success else 1)
