#!/usr/bin/env python3
"""
Simple script to initialize funding opportunities table
"""

import asyncio
import asyncpg
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_funding_table():
    """Initialize the funding opportunities table"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Create the funding opportunities table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS funding_opportunities (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                source_url TEXT UNIQUE NOT NULL,
                organization_name TEXT,
                funding_amount TEXT,
                deadline DATE,
                application_url TEXT,
                
                -- Source tracking
                source_type TEXT NOT NULL, -- 'rss' or 'serper_search'
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
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON funding_opportunities(content_hash);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_source_type ON funding_opportunities(source_type);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_relevance_score ON funding_opportunities(overall_relevance_score);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_discovered_date ON funding_opportunities(discovered_date);")
        
        logger.info("✅ Funding opportunities table created successfully")
        
        # Test the table
        result = await conn.fetchval("SELECT COUNT(*) FROM funding_opportunities")
        logger.info(f"📊 Current opportunities in database: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize table: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(init_funding_table())
