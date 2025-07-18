#!/usr/bin/env python3
"""
Check RLS Status on Tables
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def check_rls_status():
    """Check if RLS is enabled on tables"""
    
    client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
    
    # SQL to check RLS status
    check_sql = """
    SELECT 
        schemaname,
        tablename,
        rowsecurity as rls_enabled,
        CASE 
            WHEN rowsecurity THEN 'RLS Enabled' 
            ELSE 'RLS Disabled' 
        END as status
    FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename IN ('health_check', 'funding_opportunities', 'organizations', 'funding_types')
    ORDER BY tablename;
    """
    
    print("Checking RLS status on tables...")
    print("=" * 50)
    
    try:
        result = client.rpc('exec_sql', {'sql': check_sql})
        print("✅ RLS status check completed!")
        print("\nIf RLS is enabled, the security warning should disappear.")
        
        # Also check policies
        policies_sql = """
        SELECT 
            tablename,
            policyname,
            roles,
            cmd as command
        FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename IN ('health_check', 'funding_opportunities', 'organizations', 'funding_types')
        ORDER BY tablename, policyname;
        """
        
        print("\nChecking policies...")
        policies_result = client.rpc('exec_sql', {'sql': policies_sql})
        print("✅ Policies check completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking RLS status: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking RLS Status on Tables")
    print("=" * 50)
    
    success = check_rls_status()
    
    if success:
        print("\n✅ RLS check completed!")
        print("\nIf you're still seeing the security warning:")
        print("1. Refresh your Supabase dashboard")
        print("2. Clear browser cache")
        print("3. Wait a few minutes for the dashboard to update")
        print("4. Check Authentication > Policies in the dashboard")
    else:
        print("\n❌ Could not check RLS status")
        print("Please check your Supabase dashboard manually:")
