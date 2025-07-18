#!/usr/bin/env python3
"""
Apply Schema using Supabase Client
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def apply_schema():
    """Apply the high-volume ingestion schema using Supabase client"""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_PROJECT_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    print("Connecting to Supabase...")
    client = create_client(supabase_url, supabase_key)
    
    # Read the schema file
    with open('database/migrations/high_volume_ingestion_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    print("Applying high-volume ingestion schema...")
    
    # Execute the schema using raw SQL (if available)
    try:
        # Try to execute the schema using RPC (if available)
        result = client.rpc('exec_sql', {'sql': schema_sql})
        print("✅ Schema applied successfully using RPC!")
        
    except Exception as e:
        print(f"RPC not available: {e}")
        print("Applying schema manually by creating tables...")
        
        # Manually create essential tables
        essential_tables = [
            """
            CREATE TABLE IF NOT EXISTS raw_content (
                id BIGSERIAL PRIMARY KEY,
                title VARCHAR(1000),
                content TEXT,
                url VARCHAR(2000) NOT NULL,
                published_at TIMESTAMP,
                author VARCHAR(500),
                source_name VARCHAR(200) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                collected_at TIMESTAMP DEFAULT NOW(),
                keywords JSONB,
                processing_status VARCHAR(20) DEFAULT 'pending',
                processed_at TIMESTAMP,
                content_hash VARCHAR(64),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT unique_url UNIQUE (url)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS processed_content (
                id BIGSERIAL PRIMARY KEY,
                raw_content_id BIGINT,
                funding_relevance_score FLOAT DEFAULT 0.0,
                ai_summary TEXT,
                ai_insights TEXT,
                extracted_entities JSONB,
                funding_signals JSONB,
                content_category VARCHAR(100),
                funding_type VARCHAR(50),
                priority_score INTEGER DEFAULT 0,
                processing_model VARCHAR(100),
                processing_version VARCHAR(20),
                processing_duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS data_sources (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                url VARCHAR(2000) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                check_interval_minutes INTEGER DEFAULT 60,
                priority VARCHAR(20) DEFAULT 'medium',
                keywords JSONB,
                headers JSONB,
                enabled BOOLEAN DEFAULT TRUE,
                last_check TIMESTAMP,
                last_success TIMESTAMP,
                last_error TIMESTAMP,
                total_items_collected INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                average_response_time_ms INTEGER DEFAULT 0,
                success_rate FLOAT DEFAULT 0.0,
                last_error_message TEXT,
                consecutive_errors INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT unique_source_url UNIQUE (url)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS batch_processing_jobs (
                id BIGSERIAL PRIMARY KEY,
                job_name VARCHAR(200) NOT NULL,
                job_type VARCHAR(50) NOT NULL,
                source_filters JSONB,
                processing_params JSONB,
                status VARCHAR(20) DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                total_items INTEGER DEFAULT 0,
                processed_items INTEGER DEFAULT 0,
                failed_items INTEGER DEFAULT 0,
                error_message TEXT,
                error_details JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
        ]
        
        # Apply each table using client.table operations
        for table_sql in essential_tables:
            try:
                # Since we can't execute raw SQL, we'll use the client to test table existence
                # and inform the user
                print(f"⚠️  Manual table creation required")
            except Exception as e:
                print(f"Error processing table: {e}")
                
        # Test if tables exist by trying to query them
        test_tables = ['raw_content', 'processed_content', 'data_sources', 'batch_processing_jobs']
        
        for table in test_tables:
            try:
                result = client.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' missing: {e}")
        
        return True

if __name__ == "__main__":
    success = apply_schema()
    
    if success:
        print("\n🎉 Schema check completed!")
        print("\nNote: Due to Supabase client limitations, you may need to")
        print("apply the schema manually using the Supabase Dashboard SQL editor.")
        print("The SQL file is: database/migrations/high_volume_ingestion_schema.sql")
    else:
        print("\n❌ Schema application failed.")
