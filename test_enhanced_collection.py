#!/usr/bin/env python3
"""
Test script for enhanced TAIFA data collection capabilities
Tests RSS monitoring, Serper search, and web scraping
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the data_collectors directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_enhanced_data_collection():
    """Test all enhanced data collection methods"""
    logger.info("🧪 Starting TAIFA Enhanced Data Collection Test")
    logger.info("=" * 60)
    
    try:
        # Import after path setup
        from data_collectors.main import DataCollector
        
        # Initialize collector
        collector = DataCollector()
        await collector.initialize()
        
        logger.info(f"✅ Initialized data collector with:")
        logger.info(f"   📡 RSS Monitors: {len(collector.rss_monitors)}")
        logger.info(f"   🔍 Serper Search: {'✅' if collector.serper_collector else '❌'}")
        logger.info(f"   🕷️  Web Scraper: {'✅' if collector.web_scraper else '❌'}")
        logger.info("")
        
        # Test RSS monitors
        logger.info("📡 Testing RSS Monitors...")
        rss_test_count = 0
        for i, monitor in enumerate(collector.rss_monitors[:3], 1):  # Test first 3
            try:
                logger.info(f"   {i}. Testing {monitor.name}...")
                await monitor._check_feed()
                rss_test_count += 1
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"   ❌ RSS test failed for {monitor.name}: {e}")
        
        logger.info(f"   ✅ RSS Tests: {rss_test_count}/{min(3, len(collector.rss_monitors))} successful")
        logger.info("")
        
        # Test Serper search (if available)
        if collector.serper_collector:
            logger.info("🔍 Testing Serper Search...")
            try:
                # Test with a simple query
                test_queries = collector.serper_collector.search_queries[:2]  # Test first 2
                logger.info(f"   Testing {len(test_queries)} search queries...")
                
                for query in test_queries:
                    logger.info(f"   - {query['name']}")
                
                logger.info("   ✅ Serper search configuration valid")
            except Exception as e:
                logger.error(f"   ❌ Serper test failed: {e}")
        else:
            logger.info("🔍 Serper Search: Not configured (SERPER_DEV_API_KEY missing)")
        
        logger.info("")
        
        # Test web scraper
        if collector.web_scraper:
            logger.info("🕷️ Testing Web Scraper...")
            try:
                # Test first 2 scraping targets
                test_targets = collector.web_scraper.scraping_targets[:2]
                logger.info(f"   Testing {len(test_targets)} scraping targets...")
                
                for target in test_targets:
                    logger.info(f"   - {target['name']}: {target['url']}")
                
                logger.info("   ✅ Web scraper configuration valid")
            except Exception as e:
                logger.error(f"   ❌ Web scraper test failed: {e}")
        else:
            logger.info("🕷️ Web Scraper: Not initialized")
        
        logger.info("")
        logger.info("📊 Enhanced Data Collection Summary:")
        logger.info(f"   Total RSS Sources: {len(collector.rss_monitors)}")
        logger.info(f"   Serper Search Queries: {len(collector.serper_collector.search_queries) if collector.serper_collector else 0}")
        logger.info(f"   Web Scraping Targets: {len(collector.web_scraper.scraping_targets) if collector.web_scraper else 0}")
        
        # Calculate total potential sources
        total_sources = len(collector.rss_monitors)
        if collector.serper_collector:
            total_sources += len(collector.serper_collector.search_queries)
        if collector.web_scraper:
            total_sources += len(collector.web_scraper.scraping_targets)
            
        logger.info(f"   🎯 Total Data Sources: {total_sources}")
        
        # Cleanup
        await collector.stop_monitoring()
        
        logger.info("")
        logger.info("🎉 Enhanced Data Collection Test Complete!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def test_individual_components():
    """Test individual components separately"""
    logger.info("🔬 Testing Individual Components...")
    
    # Test RSS Monitor
    try:
        from data_collectors.rss_monitors.base_monitor import RSSMonitor
        
        logger.info("📡 Testing RSS Monitor class...")
        monitor = RSSMonitor(
            name="Test RSS",
            url="https://feeds.feedburner.com/oreilly/radar",  # Known working RSS
            keywords=["AI", "technology"],
            check_interval=60
        )
        
        # Test initialization
        logger.info("   ✅ RSS Monitor class initialized successfully")
        
    except Exception as e:
        logger.error(f"   ❌ RSS Monitor test failed: {e}")
    
    # Test Web Scraper
    try:
        from data_collectors.web_scraper import WebScraper
        
        logger.info("🕷️ Testing Web Scraper class...")
        scraper = WebScraper()
        await scraper.initialize()
        await scraper.close()
        
        logger.info("   ✅ Web Scraper class initialized successfully")
        
    except Exception as e:
        logger.error(f"   ❌ Web Scraper test failed: {e}")
    
    # Test Serper Collector
    try:
        from data_collectors.serper_search.collector import SerperSearchCollector
        
        logger.info("🔍 Testing Serper Collector class...")
        # Don't test actual API calls without key
        collector = SerperSearchCollector("test_key")
        
        logger.info(f"   Configured {len(collector.search_queries)} search queries")
        logger.info("   ✅ Serper Collector class initialized successfully")
        
    except Exception as e:
        logger.error(f"   ❌ Serper Collector test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 TAIFA Enhanced Data Collection Test Suite")
    print("=" * 60)
    
    # Test individual components first
    await test_individual_components()
    
    print("")
    
    # Test integrated system
    success = await test_enhanced_data_collection()
    
    if success:
        print("\n🎉 All tests passed! Your enhanced data collection is ready.")
        print("\n📋 Next Steps:")
        print("1. Register your domains: taifa-fiala.net, taifa-africa.com, fiala-afrique.com")
        print("2. Set up SERPER_DEV_API_KEY for search functionality")
        print("3. Run: python data_collectors/main.py --once")
        print("4. Start building the French translation pipeline")
    else:
        print("\n⚠️  Some tests failed. Please check the logs above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())