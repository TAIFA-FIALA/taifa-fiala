#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced migration helper functionality
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from migration_helper import MigrationHelper

def test_migration_helper():
    """Test the migration helper functionality"""
    print("🧪 Testing Enhanced Migration Helper")
    print("=" * 50)
    
    helper = MigrationHelper()
    
    # Test 1: Get local schema
    print("\n1. Testing get_schema('local')...")
    local_schema = helper.get_schema('local')
    if local_schema:
        print(f"✅ Local schema loaded: {len(local_schema.tables)} tables")
        print(f"   Sample tables: {list(local_schema.tables.keys())[:5]}")
    else:
        print("❌ Failed to load local schema")
    
    # Test 2: Test schema comparison
    print("\n2. Testing schema comparison...")
    comparison = helper.compare_schemas()
    print(f"✅ Schema comparison completed")
    print(f"   Local tables: {len(comparison['local_tables'])}")
    print(f"   Supabase accessible: {'Yes' if comparison['supabase_tables'] else 'No'}")
    
    # Test 3: Test SQLite schema generation
    print("\n3. Testing SQLite schema generation...")
    try:
        sql_schema = helper.generate_sqlite_schema()
        print(f"✅ SQLite schema generated: {len(sql_schema)} characters")
        print(f"   Sample: {sql_schema[:100]}...")
    except Exception as e:
        print(f"❌ Failed to generate SQLite schema: {e}")
    
    # Test 4: Test database creation
    print("\n4. Testing SQLite database creation...")
    test_db_path = "test_migration.db"
    try:
        success = helper.create_sqlite_database(test_db_path)
        if success:
            print(f"✅ Test database created: {test_db_path}")
            # Clean up
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
                print("   Test database cleaned up")
        else:
            print("❌ Failed to create test database")
    except Exception as e:
        print(f"❌ Error creating test database: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Migration Helper Test Complete!")
    print("\nKey Features Available:")
    print("• get_schema(source) - Get schema from 'local' or 'supabase'")
    print("• update_local_migration() - Sync migration from Supabase")
    print("• generate_migration_from_supabase() - Create Alembic migration")
    print("• compare_schemas() - Compare local vs Supabase schemas")
    print("• create_sqlite_database() - Create SQLite DB from models")
    
    print("\nCLI Usage Examples:")
    print("python migration_helper.py --get-schema local")
    print("python migration_helper.py --get-schema supabase")
    print("python migration_helper.py --update-migration")
    print("python migration_helper.py --generate-migration custom_name")
    print("python migration_helper.py --compare")

if __name__ == "__main__":
    test_migration_helper()
