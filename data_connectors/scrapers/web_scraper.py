import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json
import hashlib
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class WebScraper:
    """Advanced web scraper for funding sources without RSS feeds"""
    
    def __init__(self):
        self.session = None
        self.scraped_urls = set()
        
        # Target sources for web scraping
        self.scraping_targets = [
            {
                "name": "IDRC Funding Opportunities",
                "url": "https://idrc-crdi.ca/en/funding",
                "type": "funding_page",
                "selectors": {
                    "opportunities": ".view-content .views-row",
                    "title": ".views-field-title a, .views-field-title",
                    "description": ".views-field-body, .views-field-field-summary",
                    "deadline": ".views-field-field-deadline, .deadline",
                    "call_type": ".views-field-field-call-for",
                    "amount": ".amount, .funding-amount, .grant-amount"
                },
                "keywords": ["AI", "artificial intelligence", "digital", "technology", "Africa"],
                "check_interval": 240,  # 4 hours
                "priority": "high"
            },
            {
                "name": "Science for Africa Foundation Programs",
                "url": "https://scienceforafrica.foundation/apply/",
                "type": "funding_page", 
                "selectors": {
                    "opportunities": ".program-item, .funding-item, .call-item",
                    "title": "h2, h3, .program-title",
                    "description": ".description, .program-desc, p",
                    "deadline": ".deadline, .closing-date"
                },
                "keywords": ["AI", "artificial intelligence", "technology", "innovation"],
                "check_interval": 360,  # 6 hours
                "priority": "high"
            },
            {
                "name": "Gates Foundation Grand Challenges",
                "url": "https://grandchallenges.org/challenges",
                "type": "challenges_page",
                "selectors": {
                    "opportunities": ".challenge-card, .opportunity-card",
                    "title": "h2, h3, .challenge-title",
                    "description": ".challenge-description, .summary"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "health", "agriculture"],
                "check_interval": 480,  # 8 hours
                "priority": "high"
            },
            {
                "name": "African Development Bank Opportunities",
                "url": "https://www.afdb.org/en/about/careers-procurement/procurement-opportunities",
                "type": "procurement_page",
                "selectors": {
                    "opportunities": ".procurement-item, .opportunity-row",
                    "title": "h3, .title, .procurement-title",
                    "description": ".description, .summary"
                },
                "keywords": ["digital", "technology", "AI", "innovation"],
                "check_interval": 360,
                "priority": "medium"
            },
            {
                "name": "USAID Innovation Challenges",
                "url": "https://www.usaid.gov/div/portfolio",
                "type": "innovation_page",
                "selectors": {
                    "opportunities": ".portfolio-item, .challenge-item",
                    "title": "h2, h3, .challenge-title",
                    "description": ".description, .challenge-desc"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "digital", "technology"],
                "check_interval": 480,
                "priority": "medium"
            },
            {
                "name": "World Bank Digital Development",
                "url": "https://www.worldbank.org/en/topic/digitaldevelopment",
                "type": "topic_page",
                "selectors": {
                    "opportunities": ".project-item, .initiative-item, .news-item",
                    "title": "h2, h3, .project-title",
                    "description": ".description, .summary, p"
                },
                "keywords": ["Africa", "funding", "digital", "AI", "technology"],
                "check_interval": 720,  # 12 hours
                "priority": "low"
            },
            {
                "name": "European Commission Generative AI",
                "url": "https://digital-strategy.ec.europa.eu/en/funding/commission-funds-projects-unlock-potential-generative-ai-africa",
                "type": "funding_page",
                "selectors": {
                    "opportunities": ".ecl-col-lg-8",
                    "title": "h1",
                    "description": "p"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "funding", "generative ai"],
                "check_interval": 240,
                "priority": "high"
            },
            {
                "name": "Llama Impact Accelerator",
                "url": "https://www.ictworks.org/african-artificial-intelligence-applications/",
                "type": "funding_page",
                "selectors": {
                    "opportunities": ".entry-content",
                    "title": "h1",
                    "description": "p"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "funding", "generative ai", "llama"],
                "check_interval": 240,
                "priority": "high"
            },
            {
                "name": "Milken-Motsepe Innovation Prize",
                "url": "https://www.ictworks.org/african-ai-4th-industrial-revolution/",
                "type": "funding_page",
                "selectors": {
                    "opportunities": ".entry-content",
                    "title": "h1",
                    "description": "p"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "funding", "manufacturing"],
                "check_interval": 240,
                "priority": "high"
            },
            {
                "name": "AI4PEP",
                "url": "https://ai4pep.org/funding/",
                "type": "funding_page",
                "selectors": {
                    "opportunities": ".elementor-widget-container",
                    "title": "h1",
                    "description": "p"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "funding", "health"],
                "check_interval": 240,
                "priority": "high"
            },
            {
                "name": "iAfrica",
                "url": "https://iafrica.com/unlocking-capital-funding-and-investment-opportunities-for-african-ai-startups/",
                "type": "funding_page",
                "selectors": {
                    "opportunities": ".td-post-content",
                    "title": "h1",
                    "description": "p"
                },
                "keywords": ["AI", "artificial intelligence", "Africa", "funding", "investment"],
                "check_interval": 240,
                "priority": "high"
            }
        ]
    
    async def initialize(self):
        """Initialize the web scraper"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'TAIFA-FundingTracker/1.0 (Educational Research)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        )
        logger.info("✅ Web scraper initialized")
    
    async def close(self):
        """Close the scraper session"""
        if self.session:
            await self.session.close()
    
    async def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all configured sources"""
        logger.info(f"🕷️ Starting web scraping of {len(self.scraping_targets)} sources...")
        
        all_opportunities = []
        
        for target in self.scraping_targets:
            try:
                logger.info(f"Scraping: {target['name']}")
                opportunities = await self._scrape_source(target)
                all_opportunities.extend(opportunities)
                
                # Respectful delay between requests
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping {target['name']}: {e}")
        
        logger.info(f"✅ Web scraping completed: {len(all_opportunities)} opportunities found")
        return all_opportunities
    
    async def _scrape_source(self, target: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape a single source"""
        try:
            # Fetch the page
            async with self.session.get(target["url"]) as response:
                if response.status != 200:
                    logger.warning(f"{target['name']}: HTTP {response.status}")
                    return []
                
                html = await response.text()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract opportunities using selectors
            opportunities = []
            selectors = target["selectors"]
            
            # Find opportunity containers
            opportunity_elements = soup.select(selectors["opportunities"])
            
            for element in opportunity_elements:
                try:
                    opportunity = await self._extract_opportunity(element, target, soup)
                    if opportunity and self._is_relevant_opportunity(opportunity, target["keywords"]):
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.debug(f"Error extracting opportunity: {e}")
            
            logger.info(f"{target['name']}: Found {len(opportunities)} opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping {target['name']}: {e}")
            return []
    
    async def _extract_opportunity(self, element, target: Dict[str, Any], soup) -> Optional[Dict[str, Any]]:
        """Extract opportunity details from HTML element"""
        selectors = target["selectors"]
        
        # Extract title
        title_elem = element.select_one(selectors.get("title", "h2, h3"))
        title = title_elem.get_text(strip=True) if title_elem else "Untitled"
        
        # Extract description
        desc_elem = element.select_one(selectors.get("description", ".description, p"))
        description = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # Extract deadline if available
        deadline = None
        if "deadline" in selectors:
            deadline_elem = element.select_one(selectors["deadline"])
            if deadline_elem:
                deadline = deadline_elem.get_text(strip=True)
        
        # Extract funding amount if available
        amount = None
        if "amount" in selectors:
            amount_elem = element.select_one(selectors["amount"])
            if amount_elem:
                amount = amount_elem.get_text(strip=True)
        
        # Try to find a link
        link_elem = element.select_one("a[href]")
        source_url = target["url"]  # Default to source page
        if link_elem and link_elem.get("href"):
            href = link_elem.get("href")
            source_url = urljoin(target["url"], href)
        
        # Create opportunity object
        opportunity = {
            "title": title,
            "description": description[:500] + "..." if len(description) > 500 else description,
            "source_url": source_url,
            "source_name": target["name"],
            "source_type": "web_scraping",
            "discovery_date": datetime.utcnow().isoformat(),
            "deadline": deadline,
            "amount": amount,
            "content_hash": hashlib.md5((title + source_url).encode()).hexdigest(),
            "raw_data": json.dumps({
                "html_snippet": str(element)[:1000],
                "target_config": target["name"]
            })
        }
        
        return opportunity
    
    def _is_relevant_opportunity(self, opportunity: Dict[str, Any], keywords: List[str]) -> bool:
        """Check if opportunity is relevant based on keywords"""
        text_to_check = (
            opportunity.get("title", "") + " " + 
            opportunity.get("description", "")
        ).lower()
        
        # Check for AI/tech keywords
        has_keyword = any(keyword.lower() in text_to_check for keyword in keywords)
        
        # Check for Africa-related terms (for international sources)
        africa_terms = ['africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana', 'uganda', 'rwanda', 'morocco', 'egypt']
        has_africa_term = any(term in text_to_check for term in africa_terms)
        
        # For Africa-specific sources, don't require Africa terms
        is_africa_source = any(region in opportunity.get("source_name", "").lower() 
                              for region in ['africa', 'african'])
        
        return has_keyword and (has_africa_term or is_africa_source)
    
    async def save_opportunities(self, opportunities: List[Dict[str, Any]]):
        """Save scraped opportunities to database"""
        if not opportunities:
            return
            
        try:
            from data_collectors.database.connector import DatabaseConnector
            db_connector = DatabaseConnector()
            await db_connector.initialize()
            
            try:
                results = await db_connector.save_opportunities(opportunities, "web_scraping")
                logger.info(f"💾 Scraping save results: {results['saved']} saved, {results['duplicates']} duplicates")
            finally:
                await db_connector.close()
                
        except Exception as e:
            logger.error(f"Error saving scraped opportunities: {e}")

# Usage example for testing
async def test_scraper():
    """Test the web scraper"""
    scraper = WebScraper()
    await scraper.initialize()
    
    try:
        opportunities = await scraper.scrape_all_sources()
        print(f"Found {len(opportunities)} opportunities")
        
        for opp in opportunities[:3]:  # Show first 3
            print(f"- {opp['title'][:60]}... from {opp['source_name']}")
            
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_scraper())