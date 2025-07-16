#!/usr/bin/env python3
"""
Simple database connection test for TAIFA_db
"""

import os
from sqlalchemy import create_engine, text

# Direct database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    """Test connection to TAIFA_db"""
    print("🔍 Testing connection to TAIFA_db...")
    print(f"Database URL: {DATABASE_URL}")
    print("-" * 50)
    
    try:
        engine = create_engine(DATABASE_URL)
        
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
    
    exit(0 if success else 1)
