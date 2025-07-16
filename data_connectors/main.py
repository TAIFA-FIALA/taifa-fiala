import asyncio
import logging
from datetime import datetime
import sys
import os
import json

def load_env_vars(env_path=".env"):
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Loaded env var: {key}={value[:5]}...") # Print first 5 chars of value for security

# Add the backend app to Python path so we can import models and config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_env_vars()

from app.core.config import settings
from rss_monitors.base_monitor import RSSMonitor
from database.connector import DatabaseConnector
from serper_search.collector import SerperSearchCollector
from scrapers.web_scraper import WebScraper

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DataCollector:
    """Main data collection orchestrator with RSS, Serper search, and database integration"""
    
    def __init__(self):
        self.rss_monitors = []
        self.serper_collector = None
        self.web_scraper = None
        self.db_connector = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize all data collectors and database"""
        logger.info("Initializing AI Africa Funding Tracker data collectors...")
        
        # Initialize database connector
        self.db_connector = DatabaseConnector(settings.DATABASE_URL)
        await self.db_connector.initialize()
        
        # Initialize RSS monitors for known sources
        await self._setup_rss_monitors()
        
        # Initialize Serper search collector
        await self._setup_serper_collector()
        
        # Initialize web scraper
        await self._setup_web_scraper()
        
        rss_count = len(self.rss_monitors)
        serper_status = "✅" if self.serper_collector else "❌"
        scraper_status = "✅" if self.web_scraper else "❌"
        
        logger.info(f"✅ Initialized {rss_count} RSS monitors, Serper search {serper_status}, Web scraper {scraper_status}, and database")
    
    async def _setup_rss_monitors(self):
        """Setup RSS monitors for verified high-quality sources"""
        
        # Load RSS feeds from configuration file
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'rss_feeds.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                rss_sources = config['rss_sources']
        except FileNotFoundError:
            logger.error(f"RSS feeds configuration file not found at {config_path}")
            rss_sources = []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in RSS feeds configuration: {e}")
            rss_sources = []
        
        logger.info(f"Setting up {len(rss_sources)} RSS monitors...")
        
        for source in rss_sources:
            monitor = RSSMonitor(
                name=source["name"],
                url=source["url"],
                keywords=source["keywords"],
                check_interval=source["check_interval"]
            )
            self.rss_monitors.append(monitor)
            
        logger.info(f"✅ Configured {len(self.rss_monitors)} RSS monitors")
    
    async def _setup_serper_collector(self):
        """Setup Serper search collector"""
        if settings.SERPER_DEV_API_KEY:
            self.serper_collector = SerperSearchCollector(settings.SERPER_DEV_API_KEY)
            logger.info("✅ Serper search collector initialized")
        else:
            logger.warning("⚠️  SERPER_DEV_API_KEY not found - Serper search disabled")
    
    async def _setup_web_scraper(self):
        """Setup web scraper for sources without RSS feeds"""
        try:
            self.web_scraper = WebScraper()
            await self.web_scraper.initialize()
            logger.info("✅ Web scraper initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize web scraper: {e}")
            self.web_scraper = None
    
    async def start_monitoring(self):
        """Start all monitoring processes"""
        if self.is_running:
            logger.warning("Data collector is already running")
            return
            
        logger.info("🚀 Starting AI Africa Funding Tracker data collection...")
        self.is_running = True
        
        tasks = []
        
        # Start RSS monitors
        for monitor in self.rss_monitors:
            task = asyncio.create_task(monitor.start())
            tasks.append(task)
        
        # Start periodic Serper searches (every 6 hours)
        if self.serper_collector:
            task = asyncio.create_task(self._run_periodic_serper_search())
            tasks.append(task)
        
        # Start periodic web scraping (every 8 hours)
        if self.web_scraper:
            task = asyncio.create_task(self._run_periodic_web_scraping())
            tasks.append(task)
        
        try:
            # Wait for all monitors to complete (they run indefinitely)
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal...")
            await self.stop_monitoring()
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            await self.stop_monitoring()
    
    async def _run_periodic_serper_search(self):
        """Run Serper search periodically"""
        search_interval = 6 * 60 * 60  # 6 hours in seconds
        
        while self.is_running:
            try:
                logger.info("🔍 Starting periodic Serper search...")
                opportunities = await self.serper_collector.start_collection()
                
                if opportunities:
                    logger.info(f"📊 Serper search found {len(opportunities)} opportunities")
                    # TODO: Save opportunities to database
                    await self._save_serper_opportunities(opportunities)
                else:
                    logger.info("📊 Serper search completed - no new opportunities found")
                
                logger.info(f"⏰ Next Serper search in {search_interval/3600:.1f} hours")
                await asyncio.sleep(search_interval)
                
            except Exception as e:
                logger.error(f"Error in Serper search: {e}")
    async def _run_periodic_web_scraping(self):
        """Run web scraping periodically"""
        scraping_interval = 8 * 60 * 60  # 8 hours in seconds
        
        while self.is_running:
            try:
                logger.info("🕷️ Starting periodic web scraping...")
                opportunities = await self.web_scraper.scrape_all_sources()
                
                if opportunities:
                    logger.info(f"📊 Web scraping found {len(opportunities)} opportunities")
                    await self._save_web_scraping_opportunities(opportunities)
                else:
                    logger.info("📊 Web scraping completed - no new opportunities found")
                
                logger.info(f"⏰ Next web scraping in {scraping_interval/3600:.1f} hours")
                await asyncio.sleep(scraping_interval)
                
            except Exception as e:
                logger.error(f"Error in web scraping: {e}")
                # Wait 2 hours before retrying on error
                await asyncio.sleep(7200)
    
    async def _save_serper_opportunities(self, opportunities):
        """Save Serper opportunities to database"""
        logger.info("💾 Saving Serper opportunities to database...")
        
        if not self.db_connector:
            logger.error("Database connector not initialized")
            return
        
        try:
            results = await self.db_connector.save_opportunities(opportunities, "serper_search")
            
            logger.info(f"📊 Serper save results: {results['saved']} saved, {results['duplicates']} duplicates, {results['ai_parsed']} AI-parsed")
            
            if results["ai_parsed"] > 0:
                logger.info(f"✨ DeepSeek AI helped parse {results['ai_parsed']} complex opportunities")
                
        except Exception as e:
            logger.error(f"Error saving Serper opportunities: {e}")
    
    async def _save_web_scraping_opportunities(self, opportunities):
        """Save web scraping opportunities to database"""
        logger.info("💾 Saving web scraping opportunities to database...")
        
        if not self.db_connector:
            logger.error("Database connector not initialized")
            return
        
        try:
            results = await self.db_connector.save_opportunities(opportunities, "web_scraping")
            
            logger.info(f"📊 Web scraping save results: {results['saved']} saved, {results['duplicates']} duplicates, {results['ai_parsed']} AI-parsed")
            
            if results["ai_parsed"] > 0:
                logger.info(f"✨ AI helped parse {results['ai_parsed']} complex opportunities")
                
        except Exception as e:
            logger.error(f"Error saving web scraping opportunities: {e}")
    
    async def stop_monitoring(self):
        """Stop all monitoring processes"""
        logger.info("Stopping data collection monitoring...")
        self.is_running = False
        
        # Stop all RSS monitors
        for monitor in self.rss_monitors:
            await monitor.stop()
        
        # Close web scraper
        if self.web_scraper:
            await self.web_scraper.close()
        
        # Close database connection
        if self.db_connector:
            await self.db_connector.close()
        
        logger.info("✅ Data collection stopped")
    
    async def run_one_time_collection(self):
        """Run a one-time collection from all sources"""
        logger.info("🚀 Running one-time data collection from all sources...")
        
        results = {
            "rss_results": [],
            "serper_results": [],
            "web_scraping_results": []
        }
        
        # Run RSS collection
        for monitor in self.rss_monitors:
            logger.info(f"📡 Checking RSS: {monitor.name}")
            await monitor._check_feed()
        
        # Run Serper search
        if self.serper_collector:
            logger.info("🔍 Running Serper search...")
            opportunities = await self.serper_collector.start_collection()
            results["serper_results"] = opportunities
            
            if opportunities:
                logger.info(f"🎉 Found {len(opportunities)} opportunities via Serper!")
                for i, opp in enumerate(opportunities[:5], 1):
                    logger.info(f"  {i}. {opp['title'][:80]}... (Score: {opp['overall_relevance_score']:.2f})")
        
        # Run web scraping
        if self.web_scraper:
            logger.info("🕷️ Running web scraping...")
            opportunities = await self.web_scraper.scrape_all_sources()
            results["web_scraping_results"] = opportunities
            
            if opportunities:
                logger.info(f"🎉 Found {len(opportunities)} opportunities via web scraping!")
                for i, opp in enumerate(opportunities[:5], 1):
                    logger.info(f"  {i}. {opp['title'][:80]}... from {opp['source_name']}")
        
        return results

async def main():
    """Main entry point"""
    logger.info("🚀 Starting AI Africa Funding Tracker Data Collector")
    
    collector = DataCollector()
    
    try:
        await collector.initialize()
        
        # Check if we want to run once or continuously
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            logger.info("Running one-time collection...")
            results = await collector.run_one_time_collection()
            logger.info("✅ One-time collection completed")
        else:
            logger.info("Starting continuous monitoring...")
            await collector.start_monitoring()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
