#!/usr/bin/env python3
"""
Quick test of full pipeline: RSS + Serper + Database
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add the data_collectors directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collectors'))

from database.connector import DatabaseConnector
from serper_search.collector import SerperSearchCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def quick_pipeline_test():
    """Test the complete pipeline with a simple Serper search"""
    
    load_dotenv()
    
    logger.info("🚀 Testing complete AI Africa funding pipeline...")
    
    # Initialize database
    db = DatabaseConnector()
    await db.initialize()
    
    # Test Serper search with one query
    api_key = os.getenv("SERPER_DEV_API_KEY")
    if not api_key:
        logger.error("❌ SERPER_DEV_API_KEY not found")
        return False
    
    collector = SerperSearchCollector(api_key)
    
    # Run a single search
    try:
        logger.info("🔍 Running Serper search...")
        opportunities = await collector.start_collection()
        
        if opportunities:
            logger.info(f"✅ Found {len(opportunities)} opportunities via Serper")
            
            # Show top 3
            for i, opp in enumerate(opportunities[:3], 1):
                logger.info(f"  {i}. {opp['title'][:60]}... (Score: {opp['overall_relevance_score']:.2f})")
            
            # Save to database
            logger.info("💾 Saving to database...")
            results = await db.save_opportunities(opportunities, "serper_search")
            
            logger.info(f"📊 Save results: {results}")
            
            # Get final stats
            stats = await db.get_statistics()
            logger.info(f"📈 Final database stats: {stats['total_opportunities']} total, {stats['serper_opportunities']} from Serper")
            
            await db.close()
            return True
        else:
            logger.warning("⚠️  No opportunities found")
            await db.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        await db.close()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_pipeline_test())
    if success:
        logger.info("🎉 Pipeline test successful!")
    else:
        logger.info("❌ Pipeline test failed!")
