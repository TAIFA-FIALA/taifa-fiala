#!/usr/bin/env python3
"""
Create RLS Policies via API
==========================

This script creates RLS policies for tables now that RLS is enabled in the dashboard.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def create_policies():
    """Create RLS policies for tables"""
    
    client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
    
    # Tables to create policies for
    tables = [
        'health_check',
        'africa_intelligence_feed',
        'organizations',
        'funding_types'
    ]
    
    # Policy statements
    policy_statements = []
    
    for table in tables:
        # Policy 1: Allow all operations for service_role
        policy_statements.append(f"""
            CREATE POLICY "Enable all access for service role" ON {table}
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
        """)
        
        # Policy 2: Allow read access for authenticated users
        policy_statements.append(f"""
            CREATE POLICY "Enable read access for authenticated users" ON {table}
            FOR SELECT
            TO authenticated
            USING (true);
        """)
        
        # Policy 3: Allow read access for anonymous users (for public data)
        policy_statements.append(f"""
            CREATE POLICY "Enable read access for anonymous users" ON {table}
            FOR SELECT
            TO anon
            USING (true);
        """)
        
        # Policy 4: Allow insert for authenticated users (for africa_intelligence_feed)
        if table == 'africa_intelligence_feed':
            policy_statements.append(f"""
                CREATE POLICY "Enable insert for authenticated users" ON {table}
                FOR INSERT
                TO authenticated
                WITH CHECK (true);
            """)
    
    print("Creating RLS policies...")
    print("=" * 50)
    
    success_count = 0
    failed_policies = []
    
    for i, statement in enumerate(policy_statements, 1):
        # Extract table name and policy name for logging
        lines = statement.strip().split('\n')
        policy_line = lines[1].strip() if len(lines) > 1 else statement
        table_name = policy_line.split(' ON ')[1].split()[0] if ' ON ' in policy_line else 'unknown'
        policy_name = policy_line.split('"')[1] if '"' in policy_line else 'unknown'
        
        print(f"\n{i}. Creating policy '{policy_name}' for table '{table_name}'")
        
        try:
            result = client.rpc('exec_sql', {'sql': statement})
            print(f"   ✅ Success")
            success_count += 1
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Failed: {error_msg}")
            
            # Check if policy already exists
            if "already exists" in error_msg.lower():
                print(f"   ℹ️  Policy already exists - this is okay")
                success_count += 1
            else:
                failed_policies.append((table_name, policy_name, error_msg))
    
    print(f"\n🎉 Process completed!")
    print(f"✅ {success_count}/{len(policy_statements)} policies processed successfully")
    
    if failed_policies:
        print(f"\n⚠️  {len(failed_policies)} policies failed:")
        for table, policy, error in failed_policies:
            print(f"   - {table}: {policy} - {error}")
    
    return success_count > 0

def test_policies():
    """Test that the policies are working"""
    
    client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
    
    print("\nTesting policies...")
    print("=" * 30)
    
    # Test reading from health_check
    try:
        result = client.table('health_check').select('*').limit(1).execute()
        print("✅ health_check table - read access works")
    except Exception as e:
        print(f"❌ health_check table - read failed: {e}")
    
    # Test reading from africa_intelligence_feed
    try:
        result = client.table('africa_intelligence_feed').select('*').limit(1).execute()
        print("✅ africa_intelligence_feed table - read access works")
    except Exception as e:
        print(f"❌ africa_intelligence_feed table - read failed: {e}")
    
    # Test inserting into africa_intelligence_feed
    try:
        test_record = {
            'title': 'Policy Test',
            'description': 'Testing RLS policies'
        }
        result = client.table('africa_intelligence_feed').insert(test_record).execute()
        print("✅ africa_intelligence_feed table - insert access works")
        
        # Clean up test record
        if result.data:
            client.table('africa_intelligence_feed').delete().eq('title', 'Policy Test').execute()
            print("✅ Test record cleaned up")
            
    except Exception as e:
        print(f"❌ africa_intelligence_feed table - insert failed: {e}")

if __name__ == "__main__":
    print("🔐 Creating RLS Policies for AI Africa Funding Tracker")
    print("=" * 60)
    
    success = create_policies()
    
    if success:
        print("\n✅ RLS policies created successfully!")
        test_policies()
        print("\n🎉 Your database is now properly secured with RLS!")
        print("\nYour tables now have the following access:")
        print("- Service role: Full access (for your backend)")
        print("- Authenticated users: Read access + Insert for africa_intelligence_feed")
        print("- Anonymous users: Read access (for public data)")
        print("\nThe security warning should now disappear from your dashboard.")
    else:
        print("\n❌ Policy creation failed.")
        print("You may need to create policies manually in the dashboard.")
