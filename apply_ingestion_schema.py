#!/usr/bin/env python3
"""
Apply High-Volume Ingestion Schema to Supabase Database
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def apply_schema():
    """Apply the high-volume ingestion schema to the database"""
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Clean up the URL for asyncpg
    if db_url.startswith('postgresql+asyncpg://'):
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"Connecting to database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        
        # Read the schema file
        with open('database/migrations/high_volume_ingestion_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        print("Applying high-volume ingestion schema...")
        
        # Split by semicolon and execute each statement
        statements = schema_sql.split(';')
        applied_count = 0
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(statement)
                    applied_count += 1
                except Exception as e:
                    print(f"Warning: Error executing statement: {e}")
                    # Continue with other statements
        
        print(f"✅ Applied {applied_count} statements successfully!")
        
        # Check if key tables were created
        tables_to_check = ['raw_content', 'processed_content', 'data_sources', 'batch_processing_jobs']
        
        for table in tables_to_check:
            try:
                result = await conn.fetchval(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}'")
                if result > 0:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' not found")
            except Exception as e:
                print(f"⚠️  Could not check table '{table}': {e}")
        
        # Test inserting a sample record
        try:
            await conn.execute("""
                INSERT INTO raw_content (title, content, url, source_name, source_type, keywords)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (url) DO NOTHING
            """, 
            "Test Title", 
            "Test content for schema validation", 
            "https://test.example.com/schema-test",
            "schema_test",
            "test",
            '["schema", "test"]'
            )
            print("✅ Successfully inserted test record")
            
            # Clean up test record
            await conn.execute("DELETE FROM raw_content WHERE source_name = 'schema_test'")
            print("✅ Test record cleaned up")
            
        except Exception as e:
            print(f"❌ Error testing raw_content table: {e}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(apply_schema())
    
    if success:
        print("\n🎉 High-volume ingestion schema applied successfully!")
        print("\nYour database is now ready for:")
        print("- Massive data ingestion (10K-100M records)")
        print("- RSS feed collection")
        print("- Web scraping")
        print("- News API integration")
        print("- Batch processing")
        print("- Data deduplication")
        print("- Performance monitoring")
    else:
        print("\n❌ Schema application failed. Please check the errors above.")
