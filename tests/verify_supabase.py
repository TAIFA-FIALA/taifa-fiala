#!/usr/bin/env python3
"""
Verify Supabase database schema after SQL execution
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def verify_supabase_schema():
    """Verify the schema was applied correctly"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_PROJECT_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    
    if not url or not key:
        print("❌ Missing SUPABASE_PROJECT_URL or SUPABASE_PUBLISHABLE_KEY environment variables")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Test tables to verify
        test_tables = [
            "health_check",
            "geographic_scopes", 
            "ai_domains",
            "community_users",
            "organizations",
            "africa_intelligence_feed",
            "applications",
            "funding_rounds",
            "investments",
            "performance_metrics",
            "impact_metrics",
            "partnerships",
            "research_projects",
            "publications",
            "events",
            "announcements",
            "discussions",
            "resources",
            "user_profiles",
            "notifications"
        ]
        
        verified_tables = []
        missing_tables = []
        
        for table in test_tables:
            try:
                # Try to query the table (limit 0 to just check if it exists)
                result = supabase.table(table).select("*").limit(0).execute()
                verified_tables.append(table)
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                missing_tables.append(table)
                print(f"❌ Table '{table}' missing or inaccessible: {str(e)}")
        
        # Check health_check table has data
        try:
            health_result = supabase.table("health_check").select("*").execute()
            if health_result.data:
                print(f"✅ Health check table has {len(health_result.data)} record(s)")
            else:
                print("⚠️  Health check table exists but has no data")
        except Exception as e:
            print(f"❌ Could not verify health check data: {str(e)}")
        
        # Summary
        print(f"\n📊 Verification Summary:")
        print(f"✅ Verified tables: {len(verified_tables)}")
        print(f"❌ Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print(f"Missing tables: {', '.join(missing_tables)}")
        
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_supabase_schema()
    sys.exit(0 if success else 1)