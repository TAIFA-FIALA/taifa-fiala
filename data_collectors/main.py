import asyncio
import logging
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add the backend app to Python path so we can import models and config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings
from rss_monitors.base_monitor import RSSMonitor
from serper_search.collector import SerperSearchCollector
from web_scraper import WebScraper
from database.connector import DatabaseConnector

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
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
        self.db_connector = DatabaseConnector()
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
        
        # Verified RSS feeds with correct URLs and comprehensive coverage
        rss_sources = [
            # === MULTILATERAL ORGANIZATIONS ===
            {
                "name": "World Bank - Digital Development",
                "url": "https://www.worldbank.org/en/rss",
                "keywords": ["digital", "technology", "AI", "artificial intelligence", "innovation", "Africa"],
                "check_interval": 120,
                "priority": "high"
            },
            {
                "name": "African Development Bank",
                "url": "https://www.afdb.org/rss.xml", 
                "keywords": ["AI", "artificial intelligence", "digital", "technology", "innovation", "Africa"],
                "check_interval": 120,
                "priority": "high"
            },
            {
                "name": "UNDP Global",
                "url": "https://www.undp.org/rss.xml",
                "keywords": ["AI", "artificial intelligence", "digital", "technology", "innovation", "Africa"],
                "check_interval": 180,
                "priority": "high"
            },
            
            # === RESEARCH & DEVELOPMENT ===
            {
                "name": "IDRC - Research & Innovation",
                "url": "https://idrc-crdi.ca/rss.xml",
                "keywords": ["AI", "AI4D", "artificial intelligence", "machine learning", "digital", "technology", "Africa"],
                "check_interval": 120,
                "priority": "high"
            },
            {
                "name": "MIT Technology Review",
                "url": "https://www.technologyreview.com/feed/",
                "keywords": ["AI", "artificial intelligence", "Africa", "development", "funding", "grants"],
                "check_interval": 240,
                "priority": "medium"
            },
            
            # === FOUNDATIONS & NONPROFITS ===
            {
                "name": "TechCrunch - Startups",
                "url": "https://techcrunch.com/category/startups/feed/",
                "keywords": ["AI", "artificial intelligence", "Africa", "funding", "investment", "startup"],
                "check_interval": 180,
                "priority": "medium"
            },
            {
                "name": "Devex - Development News", 
                "url": "https://www.devex.com/en/rss",
                "keywords": ["AI", "artificial intelligence", "digital", "technology", "Africa", "funding"],
                "check_interval": 120,
                "priority": "high"
            },
            
            # === GOVERNMENT SOURCES ===
            {
                "name": "USAID - Opportunities",
                "url": "https://www.usaid.gov/rss/opportunities",
                "keywords": ["digital", "technology", "AI", "artificial intelligence", "Africa"],
                "check_interval": 240,
                "priority": "medium"
            },
            
            # === ACADEMIC & RESEARCH ===
            {
                "name": "Nature - Technology",
                "url": "https://www.nature.com/subjects/information-technology.rss",
                "keywords": ["AI", "artificial intelligence", "machine learning", "Africa", "research", "funding"],
                "check_interval": 360,
                "priority": "low"
            },
            {
                "name": "Science Magazine",
                "url": "https://www.science.org/rss/news_current.xml",
                "keywords": ["AI", "artificial intelligence", "Africa", "international", "funding", "research"],
                "check_interval": 360,
                "priority": "low"
            },
            
            # === CORPORATE TECH ===
            {
                "name": "Google AI Blog",
                "url": "https://ai.googleblog.com/feeds/posts/default",
                "keywords": ["Africa", "AI for good", "development", "funding", "grant", "program"],
                "check_interval": 240,
                "priority": "medium"
            },
            {
                "name": "Microsoft AI for Good",
                "url": "https://blogs.microsoft.com/ai-for-good/feed/",
                "keywords": ["Africa", "development", "funding", "grant", "program", "AI"],
                "check_interval": 240,
                "priority": "medium"
            },
            
            # === STARTUP & INNOVATION ===
            {
                "name": "VentureBeat - AI",
                "url": "https://venturebeat.com/category/ai/feed/",
                "keywords": ["Africa", "funding", "investment", "startup", "AI", "artificial intelligence"],
                "check_interval": 240,
                "priority": "medium"
            },
            {
                "name": "AngelList - Startup News",
                "url": "https://angel.co/feed",
                "keywords": ["Africa", "AI", "artificial intelligence", "funding", "startup", "accelerator"],
                "check_interval": 360,
                "priority": "low"
            },
            
            # === AFRICAN TECH SOURCES ===
            {
                "name": "TechCabal - African Tech",
                "url": "https://techcabal.com/feed/",
                "keywords": ["AI", "artificial intelligence", "funding", "investment", "startup", "innovation"],
                "check_interval": 180,
                "priority": "high"
            },
            {
                "name": "African Business",
                "url": "https://african.business/feed/",
                "keywords": ["AI", "artificial intelligence", "technology", "digital", "funding", "innovation"],
                "check_interval": 240,
                "priority": "medium"
            }
        ]
        
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
