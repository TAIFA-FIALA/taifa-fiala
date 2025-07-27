#!/usr/bin/env python3
"""
Run a one-time collection and monitor the results
This script is for testing the data collection process after fixes
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the DataCollector
from main import DataCollector

async def run_test_collection():
    """Run a one-time collection and monitor the results"""
    logger.info("🧪 Starting test collection with monitoring")
    
    # Create a collector
    collector = DataCollector()
    
    try:
        # Initialize the collector
        logger.info("Initializing data collector...")
        await collector.initialize()
        
        # Run the collection
        logger.info("Running one-time collection...")
        results = await collector.run_one_time_collection()
        
        # Save results to a file for analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"logs/collection_results_{timestamp}.json"
        
        # Convert results to a serializable format
        serializable_results = {
            "timestamp": datetime.now().isoformat(),
            "rss_results_count": len(results.get("rss_results", [])),
            "serper_results_count": len(results.get("serper_results", [])),
            "web_scraping_results_count": len(results.get("web_scraping_results", [])),
            "total_results": (
                len(results.get("rss_results", [])) + 
                len(results.get("serper_results", [])) + 
                len(results.get("web_scraping_results", []))
            ),
            "serper_sample": results.get("serper_results", [])[:5] if results.get("serper_results") else [],
            "web_scraping_sample": results.get("web_scraping_results", [])[:5] if results.get("web_scraping_results") else []
        }
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Save results
        with open(results_file, "w") as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {results_file}")
        
        # Print summary
        logger.info("📊 Collection Summary:")
        logger.info(f"  RSS Results: {serializable_results['rss_results_count']}")
        logger.info(f"  Serper Results: {serializable_results['serper_results_count']}")
        logger.info(f"  Web Scraping Results: {serializable_results['web_scraping_results_count']}")
        logger.info(f"  Total Results: {serializable_results['total_results']}")
        
        # Monitor data quality
        logger.info("Monitoring data quality...")
        await collector.monitor_data_quality()
        
        logger.info("✅ Test collection completed")
        
    except Exception as e:
        logger.error(f"❌ Error during test collection: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Stop the collector
        if collector:
            await collector.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(run_test_collection())