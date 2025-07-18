#!/usr/bin/env python3
"""
Discover the exact schema of the funding_opportunities table
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def discover_schema():
    """Discover the exact schema by trying different field combinations"""
    
    client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
    
    # Try different combinations of fields to find what works
    field_combinations = [
        # Most basic
        {'title': 'Test', 'description': 'Test description'},
        
        # Add common fields one by one
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org'},
        
        # Try without some fields
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'funding_amount': None},
        
        # Try different field names
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'deadline': None},
        
        # Try with different variations
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'amount': None},
        
        # Try with created_at/updated_at
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'created_at': '2025-01-01T00:00:00', 'updated_at': '2025-01-01T00:00:00'},
        
        # Try with contact info
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'contact_information': 'test@example.com'},
        
        # Try with application deadline
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'application_deadline': None},
        
        # Try with eligibility
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org', 'eligibility_criteria': None},
        
        # Try all required fields only
        {'title': 'Test', 'description': 'Test description', 'organization_name': 'Test Org'},
    ]
    
    print("Discovering schema for funding_opportunities table...")
    print("=" * 50)
    
    for i, fields in enumerate(field_combinations):
        print(f"\nAttempt {i+1}: {list(fields.keys())}")
        
        try:
            result = client.table('funding_opportunities').insert(fields).execute()
            print(f"✅ SUCCESS! Working schema: {list(fields.keys())}")
            
            # Clean up the test record
            if result.data:
                client.table('funding_opportunities').delete().eq('title', 'Test').execute()
                print("✅ Test record cleaned up")
            
            return list(fields.keys())
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    print("\n❌ Could not determine working schema")
    return None

if __name__ == "__main__":
    working_schema = discover_schema()
    
    if working_schema:
        print(f"\n🎉 Working schema found: {working_schema}")
        print("\nYou can now use this schema in your ingestion script:")
        print("opportunity_data = {")
        for field in working_schema:
            print(f"    '{field}': 'your_value_here',")
        print("}")
    else:
        print("\n❌ Could not find a working schema. Check your table structure.")
