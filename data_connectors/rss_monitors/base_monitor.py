import asyncio
import aiohttp
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import hashlib

logger = logging.getLogger(__name__)

class RSSMonitor:
    """Base RSS monitor for funding sources"""
    
    def __init__(self, name: str, url: str, keywords: List[str], check_interval: int = 60):
        self.name = name
        self.url = url
        self.keywords = [kw.lower() for kw in keywords]
        self.check_interval = check_interval  # minutes
        self.is_running = False
        self.last_checked = None
        self.session = None
        
    async def start(self):
        """Start monitoring the RSS feed"""
        if self.is_running:
            logger.warning(f"{self.name}: Monitor is already running")
            return
            
        logger.info(f"{self.name}: Starting RSS monitor")
        self.is_running = True
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'AI-Africa-Funding-Tracker/1.0'}
        )
        
        try:
            while self.is_running:
                await self._check_feed()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval * 60)
                
        except Exception as e:
            logger.error(f"{self.name}: Error in monitoring loop: {e}")
        finally:
            if self.session:
                await self.session.close()
    
    async def stop(self):
        """Stop monitoring"""
        logger.info(f"{self.name}: Stopping RSS monitor")
        self.is_running = False
        
        if self.session:
            await self.session.close()
    
    async def _check_feed(self):
        """Check the RSS feed for new opportunities"""
        try:
            logger.info(f"{self.name}: Checking RSS feed at {self.url}")
            
            # Create session if it doesn't exist
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={'User-Agent': 'AI-Africa-Funding-Tracker/1.0'}
                )
            
            # Fetch RSS feed
            feed_content = await self._fetch_feed()
            if not feed_content:
                logger.warning(f"{self.name}: Failed to fetch feed content")
                return
            
            # Parse feed
            feed = feedparser.parse(feed_content)
            if feed.bozo:
                logger.warning(f"{self.name}: Feed parsing issues: {feed.bozo_exception}")
            
            # Process entries
            new_opportunities = []
            for entry in feed.entries:
                if self._is_relevant_entry(entry):
                    opportunity = await self._process_entry(entry)
                    if opportunity:
                        new_opportunities.append(opportunity)
            
            # Report results
            if new_opportunities:
                logger.info(f"{self.name}: Found {len(new_opportunities)} new opportunities")
                await self._save_opportunities(new_opportunities)
            else:
                logger.info(f"{self.name}: No new opportunities found")
                
            self.last_checked = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"{self.name}: Error checking feed: {e}")
    
    async def _fetch_feed(self) -> Optional[str]:
        """Fetch RSS feed content"""
        try:
            async with self.session.get(self.url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    logger.warning(f"{self.name}: HTTP {response.status} when fetching feed")
                    return None
        except Exception as e:
            logger.error(f"{self.name}: Error fetching feed: {e}")
            return None
    
    def _is_relevant_entry(self, entry) -> bool:
        """Check if RSS entry is relevant to AI funding in Africa"""
        text_to_check = (
            getattr(entry, 'title', '') + ' ' + 
            getattr(entry, 'summary', '') + ' ' +
            getattr(entry, 'description', '')
        ).lower()
        
        # Check for AI keywords
        has_ai_keyword = any(keyword in text_to_check for keyword in self.keywords)
        
        # Check for Africa-related terms
        africa_terms = ['africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana', 'uganda', 'rwanda']
        has_africa_term = any(term in text_to_check for term in africa_terms)
        
        return has_ai_keyword and has_africa_term
    
    async def _process_entry(self, entry) -> Optional[Dict[str, Any]]:
        """Process a relevant RSS entry into a intelligence item"""
        try:
            opportunity = {
                'title': getattr(entry, 'title', 'Untitled'),
                'description': getattr(entry, 'summary', '') or getattr(entry, 'description', ''),
                'source_url': getattr(entry, 'link', ''),
                'announcement_date': self._parse_date(getattr(entry, 'published', '')),
                'source_name': self.name,
                'content_hash': self._generate_content_hash(getattr(entry, 'title', '') + getattr(entry, 'link', '')),
                'raw_data': json.dumps(dict(entry), default=str)
            }
            
            # Extract more details if available
            await self._enrich_opportunity(opportunity, entry)
            
            return opportunity
            
        except Exception as e:
            logger.error(f"{self.name}: Error processing entry: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
            
        try:
            # feedparser usually handles this
            import time
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime(*parsed_time[:6])
        except:
            pass
            
        return None
    
    async def _enrich_opportunity(self, opportunity: Dict[str, Any], entry) -> None:
        """Enrich opportunity with additional details"""
        # This can be extended to extract amounts, deadlines, etc.
        # For now, just basic information
        pass
    
    async def _save_opportunities(self, opportunities: List[Dict[str, Any]]):
        """Save opportunities to database with enhanced extraction"""
        try:
            # Import enhanced ETL integration
            from backend.app.services.etl.enhanced_etl_integration import EnhancedETLIntegrator, EnhancedETLConfig, ETLDataSource
            
            # Create enhanced ETL integrator
            config = EnhancedETLConfig(
                enable_enhanced_extraction=True,
                enable_field_validation=True,
                enable_data_enrichment=True,
                min_relevance_score=0.5  # Lower threshold for RSS feeds
            )
            integrator = EnhancedETLIntegrator(config)
            
            # Process opportunities with enhanced extraction
            enhanced_opportunities = await integrator.process_rss_data_enhanced(opportunities)
            
            logger.info(f"Enhanced extraction applied to {len(opportunities)} RSS items, "
                       f"resulted in {len(enhanced_opportunities)} enhanced opportunities")
            
            # Fallback to original database connector if enhanced processing fails
            if not enhanced_opportunities:
                logger.warning("Enhanced extraction failed, falling back to original database connector")
                from database.connector import DatabaseConnector
                import os
                database_url = os.getenv("DATABASE_URL")
                db_connector = DatabaseConnector(database_url)
                await db_connector.initialize()
                try:
                    await db_connector.save_opportunities(opportunities, "rss")
                finally:
                    await db_connector.close()
            
        except Exception as e:
            logger.error(f"Enhanced extraction failed: {e}, falling back to original database connector")
            # Fallback to original database connector
            from database.connector import DatabaseConnector
            import os
            database_url = os.getenv("DATABASE_URL")
            db_connector = DatabaseConnector(database_url)
            await db_connector.initialize()
            try:
                await db_connector.save_opportunities(opportunities, "rss")
            finally:
                await db_connector.close()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
