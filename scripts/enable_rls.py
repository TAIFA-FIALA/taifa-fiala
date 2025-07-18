#!/usr/bin/env python3
"""
Enable Row Level Security (RLS) on Supabase Tables
=================================================

This script enables RLS and creates basic policies for your tables.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def enable_rls():
    """Enable RLS on tables and create basic policies"""
    
    client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
    
    # Tables to enable RLS on
    tables = [
        'health_check',
        'africa_intelligence_feed',
        'organizations',
        'funding_types'
    ]
    
    # SQL statements to enable RLS and create policies
    rls_statements = []
    
    for table in tables:
        # Enable RLS on table
        rls_statements.append(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        
        # Create a policy that allows all operations for service_role
        # This allows your backend to work while still having RLS enabled
        rls_statements.append(f"""
            CREATE POLICY "Enable all access for service role" ON {table}
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
        """)
        
        # Create a policy for authenticated users (you can customize this)
        rls_statements.append(f"""
            CREATE POLICY "Enable read access for authenticated users" ON {table}
            FOR SELECT
            TO authenticated
            USING (true);
        """)
        
        # For development, you might want to allow anonymous access to read data
        # Comment out the next block if you want to restrict anonymous access
        rls_statements.append(f"""
            CREATE POLICY "Enable read access for anonymous users" ON {table}
            FOR SELECT
            TO anon
            USING (true);
        """)
    
    print("Enabling Row Level Security (RLS) on tables...")
    print("=" * 50)
    
    success_count = 0
    
    for i, statement in enumerate(rls_statements, 1):
        print(f"\n{i}. Executing: {statement.strip()[:50]}...")
        
        try:
            result = client.rpc('exec_sql', {'sql': statement})
            print(f"   ✅ Success")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            # Continue with other statements
    
    print(f"\n🎉 Process completed! {success_count}/{len(rls_statements)} statements executed")
    
    return success_count > 0

def show_manual_instructions():
    """Show manual instructions for enabling RLS"""
    
    print("\n" + "="*60)
    print("MANUAL INSTRUCTIONS FOR SUPABASE DASHBOARD")
    print("="*60)
    print("\nTo enable RLS manually in Supabase Dashboard:")
    print("\n1. Go to your Supabase Dashboard")
    print("2. Navigate to Authentication > Policies")
    print("3. For each table (health_check, africa_intelligence_feed, etc.):")
    print("   a. Click 'Enable RLS' if not already enabled")
    print("   b. Click 'New Policy'")
    print("   c. Choose 'Full customization' or use a template")
    print("   d. Create policies like:")
    print("\n   Policy Name: 'Enable all access for service role'")
    print("   Target Roles: service_role")
    print("   Command: ALL")
    print("   USING expression: true")
    print("   WITH CHECK expression: true")
    print("\n   Policy Name: 'Enable read access for authenticated users'")
    print("   Target Roles: authenticated")
    print("   Command: SELECT")
    print("   USING expression: true")
    print("\n4. Save the policies")
    print("\nThis will secure your tables while allowing your app to function.")

if __name__ == "__main__":
    print("🚀 AI Africa Funding Tracker - Enable Row Level Security")
    print("="*60)
    
    success = enable_rls()
    
    if not success:
        show_manual_instructions()
    else:
        print("\n✅ RLS has been enabled on your tables!")
        print("\nYour tables are now secure with the following access:")
        print("- Service role: Full access (for your backend)")
        print("- Authenticated users: Read access")
        print("- Anonymous users: Read access (for public data)")
        print("\nYou can customize these policies in the Supabase Dashboard.")
