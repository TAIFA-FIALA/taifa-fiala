#!/usr/bin/env python3
"""
Check and reset intelligence feed table
"""

import asyncio
import asyncpg
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_funding_table():
    """Drop and recreate the intelligence feed table"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Check existing tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        logger.info("📋 Existing tables:")
        for table in tables:
            logger.info(f"  - {table['table_name']}")
        
        # Check if africa_intelligence_feed exists
        existing = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'africa_intelligence_feed'
            )
        """)
        
        if existing:
            logger.info("🗑️  Dropping existing africa_intelligence_feed table...")
            await conn.execute("DROP TABLE africa_intelligence_feed CASCADE")
        
        # Create the intelligence feed table fresh
        logger.info("🏗️  Creating africa_intelligence_feed table...")
        await conn.execute("""
            CREATE TABLE africa_intelligence_feed (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                source_url TEXT UNIQUE NOT NULL,
                organization_name TEXT,
                funding_amount TEXT,
                deadline DATE,
                application_url TEXT,
                
                -- Source tracking
                source_type TEXT NOT NULL,
                source_name TEXT NOT NULL,
                search_query TEXT,
                
                -- Relevance scoring
                ai_relevance_score REAL DEFAULT 0.0,
                africa_relevance_score REAL DEFAULT 0.0,
                funding_relevance_score REAL DEFAULT 0.0,
                overall_relevance_score REAL DEFAULT 0.0,
                
                -- Metadata
                content_hash TEXT UNIQUE NOT NULL,
                raw_data JSONB,
                discovered_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                -- Processing flags
                parsed_with_ai BOOLEAN DEFAULT FALSE,
                verified BOOLEAN DEFAULT FALSE,
                active BOOLEAN DEFAULT TRUE
            );
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX idx_content_hash ON africa_intelligence_feed(content_hash);")
        await conn.execute("CREATE INDEX idx_source_type ON africa_intelligence_feed(source_type);")
        await conn.execute("CREATE INDEX idx_relevance_score ON africa_intelligence_feed(overall_relevance_score);")
        await conn.execute("CREATE INDEX idx_discovered_date ON africa_intelligence_feed(discovered_date);")
        
        logger.info("✅ Funding opportunities table created successfully")
        
        # Verify the table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'africa_intelligence_feed'
            ORDER BY ordinal_position
        """)
        
        logger.info("📋 Table structure:")
        for col in columns:
            logger.info(f"  - {col['column_name']}: {col['data_type']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to reset table: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(reset_funding_table())
