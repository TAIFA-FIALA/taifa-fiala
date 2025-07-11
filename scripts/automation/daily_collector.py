import asyncio
import logging
import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data_collectors.serper_search.collector import SerperSearchCollector
from data_collectors.rss_monitors.base_monitor import RSSMonitor
from data_collectors.database.connector import DatabaseConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../../logs/daily_collection.log"),
        logging.StreamHandler()
    ]
)

async def main():
    """Main function to run the daily data collection"""
    logging.info(f"🚀 Starting daily data collection run at {datetime.now()}")

    db_connector = DatabaseConnector()
    await db_connector.initialize()

    try:
        # --- Serper Search Collection ---
        serper_api_key = os.getenv("SERPER_DEV_API_KEY")
        if not serper_api_key:
            logging.error("SERPER_DEV_API_KEY not found in environment variables.")
            return

        serper_collector = SerperSearchCollector(api_key=serper_api_key)
        serper_opportunities = await serper_collector.start_collection()

        if serper_opportunities:
            logging.info(f"Found {len(serper_opportunities)} opportunities from Serper Search.")
            await db_connector.save_opportunities(serper_opportunities, "serper_search")
        else:
            logging.info("No new opportunities found from Serper Search.")

        # --- RSS Feed Collection ---
        rss_sources = [
            {
                "name": "IDRC AI4D Program",
                "url": "https://idrc-crdi.ca/rss.xml",
                "keywords": ["AI", "artificial intelligence", "AI4D", "machine learning", "digital", "technology", "Africa"],
                "check_interval": 120,  # Check every 2 hours
                "priority": "high"
            },
            {
                "name": "Science for Africa Foundation",
                "url": "https://scienceforafrica.foundation/rss.xml",
                "keywords": ["AI", "artificial intelligence", "innovation", "technology", "digital", "Africa"],
                "check_interval": 180,  # Check every 3 hours  
                "priority": "high"
            }
        ]

        for source in rss_sources:
            monitor = RSSMonitor(
                name=source["name"],
                url=source["url"],
                keywords=source["keywords"],
                check_interval=source["check_interval"]
            )
            await monitor._check_feed()

    finally:
        await db_connector.close()
        logging.info("✅ Daily data collection run finished.")

if __name__ == "__main__":
    asyncio.run(main())