#!/usr/bin/env python3
"""
Apply multilingual database schema to TAIFA database
Uses existing database connector infrastructure
"""

import asyncio
import logging
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_multilingual_schema():
    """Apply the multilingual database schema"""
    try:
        from database.connector import DatabaseConnector
        
        logger.info("🔧 Applying TAIFA-FIALA multilingual database schema...")
        
        # Initialize database connector
        db = DatabaseConnector()
        await db.initialize()
        
        # Read the schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'database_multilingual_schema.sql')
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute the schema
        async with db.pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Multilingual schema applied successfully!")
        
        # Test the new tables
        logger.info("🧪 Testing new multilingual tables...")
        
        async with db.pool.acquire() as conn:
            # Check supported languages
            languages = await conn.fetch("SELECT code, name, native_name FROM supported_languages ORDER BY translation_priority")
            logger.info(f"📊 Supported languages: {len(languages)}")
            for lang in languages:
                logger.info(f"   {lang['code']}: {lang['name']} ({lang['native_name']})")
            
            # Check translation services
            services = await conn.fetch("SELECT service_name, is_active, quality_score FROM translation_services WHERE is_active = TRUE")
            logger.info(f"🔧 Active translation services: {len(services)}")
            for service in services:
                logger.info(f"   {service['service_name']}: Quality {service['quality_score']:.2f}")
        
        await db.close()
        
        logger.info("🎉 TAIFA-FIALA multilingual database is ready!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema application failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(apply_multilingual_schema())
    if not success:
        sys.exit(1)