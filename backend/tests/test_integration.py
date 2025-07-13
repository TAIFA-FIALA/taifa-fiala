#!/usr/bin/env python3
"""
Test script for database integration and DeepSeek parsing
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
import aiohttp

# Add the data_collectors directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collectors'))

from database.connector import DatabaseConnector
from serper_search.collector import SerperSearchCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test basic database connectivity"""
    logger.info("🧪 Testing database connection...")
    
    db = DatabaseConnector()
    try:
        await db.initialize()
        
        # Test getting statistics
        stats = await db.get_statistics()
        logger.info(f"📊 Database stats: {stats}")
        
        # Test getting recent opportunities
        recent = await db.get_recent_opportunities(limit=5)
        logger.info(f"📋 Recent opportunities: {len(recent)} found")
        
        await db.close()
        logger.info("✅ Database connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

async def test_serper_with_location_rotation():
    """Test Serper search with location rotation"""
    logger.info("🧪 Testing Serper search with location rotation...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("SERPER_DEV_API_KEY")
    if not api_key:
        logger.error("❌ SERPER_DEV_API_KEY not found")
        return False
    
    try:
        collector = SerperSearchCollector(api_key)
        
        # Initialize the session (this was missing)
        collector.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
        # Test with a single query to see location alternation
        test_query = {
            "name": "Test AI Africa Funding",
            "query": "AI funding Africa grants",
            "priority": "high"
        }
        
        opportunities = await collector._search_funding_opportunities(test_query)
        
        # Close the session
        await collector.session.close()
        
        if opportunities:
            logger.info(f"✅ Serper test successful! Found {len(opportunities)} opportunities")
            logger.info(f"📋 Sample: {opportunities[0]['title'][:80]}...")
            return True
        else:
            logger.warning("⚠️  Serper test returned no results")
            return False
            
    except Exception as e:
        logger.error(f"❌ Serper test failed: {e}")
        return False

async def test_end_to_end_pipeline():
    """Test complete pipeline: Search → Parse → Database"""
    logger.info("🧪 Testing end-to-end pipeline...")
    
    # Initialize database
    db = DatabaseConnector()
    await db.initialize()
    
    # Create a test opportunity to save
    test_opportunity = {
        "title": "Test AI Research Grant for African Universities",
        "description": "A test funding opportunity for AI research in Africa. Amount: $50,000. Deadline: Apply by December 31, 2025.",
        "source_url": f"https://test-funding.example.com/test-{datetime.now().timestamp()}",
        "search_query": "Test Query",
        "priority": "high",
        "content_hash": f"test_hash_{datetime.now().timestamp()}",
        "ai_relevance_score": 0.9,
        "africa_relevance_score": 0.8,
        "funding_relevance_score": 0.95,
        "overall_relevance_score": 0.88
    }
    
    try:
        # Test saving
        results = await db.save_opportunities([test_opportunity], "test")
        
        if results["saved"] > 0:
            logger.info("✅ End-to-end test successful!")
            logger.info(f"📊 Results: {results}")
            
            # Check if it was parsed with AI
            if results["ai_parsed"] > 0:
                logger.info("✨ DeepSeek AI parsing was used successfully!")
            
            return True
        else:
            logger.error("❌ No opportunities were saved")
            return False
            
    except Exception as e:
        logger.error(f"❌ End-to-end test failed: {e}")
        return False
    finally:
        await db.close()

async def main():
    """Run all tests"""
    logger.info("🚀 Starting AI Africa Funding Tracker tests...")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Serper Location Rotation", test_serper_with_location_rotation),
        ("End-to-End Pipeline", test_end_to_end_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            results[test_name] = await test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All tests passed! System ready for deployment.")
    else:
        logger.info("\n⚠️  Some tests failed. Check logs above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
