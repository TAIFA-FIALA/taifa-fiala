#!/usr/bin/env python3
"""
Add Missing Columns to africa_intelligence_feed Table
=================================================

This script adds the missing columns needed for data ingestion
to the existing africa_intelligence_feed table.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def add_missing_columns():
    """Add missing columns to africa_intelligence_feed table"""
    
    client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
    
    # SQL to add missing columns
    alter_statements = [
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS funding_type VARCHAR(100);",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS application_deadline TIMESTAMP;",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS funding_amount VARCHAR(200);",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS eligibility_criteria TEXT;",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS application_process TEXT;",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS contact_information TEXT;",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS additional_notes TEXT;",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS source_url VARCHAR(2000);",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS source_type VARCHAR(50) DEFAULT 'rss';",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS collected_at TIMESTAMP DEFAULT NOW();",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS keywords JSONB;",
        "ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';"
    ]
    
    print("Adding missing columns to africa_intelligence_feed table...")
    print("=" * 60)
    
    success_count = 0
    
    for i, statement in enumerate(alter_statements, 1):
        column_name = statement.split('ADD COLUMN IF NOT EXISTS ')[1].split()[0] if 'ADD COLUMN' in statement else 'unknown'
        print(f"\n{i}. Adding column: {column_name}")
        
        try:
            # Try to execute the ALTER statement using RPC
            result = client.rpc('exec_sql', {'sql': statement})
            print(f"   ✅ Column '{column_name}' added successfully")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed to add column '{column_name}': {e}")
            
            # If RPC fails, try alternative approach
            print(f"   ⚠️  RPC method failed, you may need to add this column manually in Supabase Dashboard:")
            print(f"   SQL: {statement}")
    
    print(f"\n🎉 Process completed! {success_count}/{len(alter_statements)} columns processed successfully")
    
    # Test the updated schema
    print("\nTesting updated schema...")
    test_record = {
        'title': 'Schema Test',
        'description': 'Testing the updated schema',
        'organization_name': 'Test Organization',
        'funding_type': 'grant',
        'application_deadline': None,
        'funding_amount': '$10,000',
        'eligibility_criteria': 'African startups',
        'application_process': 'Online application',
        'contact_information': 'test@example.com',
        'additional_notes': 'Test record for schema validation',
        'source_url': 'https://example.com/test',
        'source_type': 'manual',
        'keywords': '["test", "schema"]',
        'status': 'active'
    }
    
    try:
        result = client.table('africa_intelligence_feed').insert(test_record).execute()
        print("✅ Schema test successful! All columns are working.")
        
        # Clean up test record
        if result.data:
            client.table('africa_intelligence_feed').delete().eq('title', 'Schema Test').execute()
            print("✅ Test record cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        print("\nSome columns may still be missing. Please check the Supabase Dashboard.")
        return False

def show_manual_instructions():
    """Show manual instructions for adding columns in Supabase Dashboard"""
    
    print("\n" + "="*60)
    print("MANUAL INSTRUCTIONS FOR SUPABASE DASHBOARD")
    print("="*60)
    print("\nIf the automatic column addition failed, you can add them manually:")
    print("\n1. Go to your Supabase Dashboard")
    print("2. Navigate to Table Editor > africa_intelligence_feed")
    print("3. Click 'Add Column' and add these columns:")
    print()
    
    columns = [
        ("funding_type", "varchar", "100", "Nullable"),
        ("application_deadline", "timestamp", "", "Nullable"),
        ("funding_amount", "varchar", "200", "Nullable"),
        ("eligibility_criteria", "text", "", "Nullable"),
        ("application_process", "text", "", "Nullable"),
        ("contact_information", "text", "", "Nullable"),
        ("additional_notes", "text", "", "Nullable"),
        ("source_url", "varchar", "2000", "Nullable"),
        ("source_type", "varchar", "50", "Default: 'rss'"),
        ("collected_at", "timestamp", "", "Default: NOW()"),
        ("keywords", "jsonb", "", "Nullable"),
        ("status", "varchar", "50", "Default: 'active'")
    ]
    
    for name, type_name, length, notes in columns:
        length_str = f"({length})" if length else ""
        print(f"   • {name:<20} {type_name}{length_str:<10} {notes}")
    
    print("\n4. Save the changes")
    print("5. Run the data ingestion script again")

if __name__ == "__main__":
    print("🚀 AI Africa Funding Tracker - Database Schema Update")
    print("="*60)
    
    success = add_missing_columns()
    
    if not success:
        show_manual_instructions()
    else:
        print("\n✅ Database schema is now ready for data ingestion!")
        print("\nYou can now run: python tools/ingestion/start_data_ingestion.py")
