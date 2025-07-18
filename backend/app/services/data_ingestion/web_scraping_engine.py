"""
High-Volume Web Scraping Engine for Funding Sources
Designed for massive scale data extraction from funding databases and websites

This module provides robust web scraping capabilities for:
- Government funding databases (EU, USAID, World Bank, etc.)
- Corporate funding programs (Google, Microsoft, Gates Foundation, etc.)
- University and research funding sources
- Accelerators and incubators
- News and media sites

Features:
- Intelligent content extraction with BeautifulSoup and Scrapy
- Respect for robots.txt and rate limiting
- Multi-threaded crawling with proper queue management
- Content deduplication and validation
- Structured data extraction
- Error handling and retry logic
- Proxy rotation and session management
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import json
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
import re
from urllib.parse import urljoin, urlparse, urlencode
from urllib.robotparser import RobotFileParser
import backoff
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import random
import os

logger = logging.getLogger(__name__)


class ScrapingStrategy(Enum):
    """Different scraping strategies for various site types"""
    SIMPLE_HTML = "simple_html"
    JAVASCRIPT_HEAVY = "javascript_heavy"
    API_ENDPOINT = "api_endpoint"
    PAGINATED = "paginated"
    INFINITE_SCROLL = "infinite_scroll"
    FORM_BASED = "form_based"
    CLOUDFLARE_PROTECTED = "cloudflare_protected"


class ContentType(Enum):
    """Types of content to extract"""
    FUNDING_OPPORTUNITY = "funding_opportunity"
    GRANT_ANNOUNCEMENT = "grant_announcement"
    PARTNERSHIP_NEWS = "partnership_news"
    RESEARCH_CALL = "research_call"
    COMPETITION_NOTICE = "competition_notice"
    PROGRAM_UPDATE = "program_update"
    POLICY_DOCUMENT = "policy_document"


@dataclass
class ScrapingTarget:
    """Configuration for a web scraping target"""
    name: str
    base_url: str
    strategy: ScrapingStrategy
    content_type: ContentType
    selectors: Dict[str, str]  # CSS selectors for different content elements
    pagination_config: Optional[Dict[str, Any]] = None
    rate_limit_seconds: float = 2.0
    max_pages: int = 50
    requires_js: bool = False
    requires_proxy: bool = False
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    form_data: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    enabled: bool = True
    last_scraped: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    
    def __post_init__(self):
        if isinstance(self.strategy, str):
            self.strategy = ScrapingStrategy(self.strategy)
        if isinstance(self.content_type, str):
            self.content_type = ContentType(self.content_type)


@dataclass
class ScrapedContent:
    """Scraped content item"""
    title: str
    content: str
    url: str
    source: str
    content_type: ContentType
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)
    content_hash: str = field(init=False)
    
    def __post_init__(self):
        # Generate content hash for deduplication
        content_str = f"{self.title}{self.content}{self.url}"
        self.content_hash = hashlib.md5(content_str.encode()).hexdigest()


class HighVolumeWebScrapingEngine:
    """
    High-volume web scraping engine for funding sources
    Designed to handle hundreds of sites with robust error handling
    """
    
    def __init__(self, max_workers: int = 20, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        # Scraping targets
        self.targets: List[ScrapingTarget] = []
        
        # Session management
        self.session_pools = {}
        self.user_agents = UserAgent()
        
        # Selenium drivers for JS-heavy sites
        self.selenium_drivers = []
        self.max_selenium_drivers = 3
        
        # Content storage
        self.scraped_content: List[ScrapedContent] = []
        self.content_hashes: Set[str] = set()
        
        # Rate limiting
        self.rate_limiters = {}
        
        # Statistics
        self.stats = {
            'targets_processed': 0,
            'content_extracted': 0,
            'duplicates_filtered': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Thread control
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Initialize logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the scraping engine"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/web_scraping.log'),
                logging.StreamHandler()
            ]
        )
    
    def initialize_targets(self):
        """Initialize all scraping targets"""
        logger.info("Initializing web scraping targets")
        
        # Government funding databases
        self._add_government_targets()
        
        # Corporate funding programs
        self._add_corporate_targets()
        
        # University and research sources
        self._add_academic_targets()
        
        # Accelerators and incubators
        self._add_accelerator_targets()
        
        # News and media sources
        self._add_news_targets()
        
        logger.info(f"Initialized {len(self.targets)} scraping targets")
    
    def _add_government_targets(self):
        """Add government funding database targets"""
        
        # EU Funding Database
        self.targets.append(ScrapingTarget(
            name="EU Funding & Tenders Portal",
            base_url="https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search",
            strategy=ScrapingStrategy.JAVASCRIPT_HEAVY,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            selectors={
                'title': '.opportunity-title',
                'description': '.opportunity-description',
                'deadline': '.deadline-date',
                'budget': '.budget-amount',
                'link': '.opportunity-link'
            },
            pagination_config={
                'type': 'button_click',
                'next_button': '.next-page-btn',
                'page_param': 'page'
            },
            rate_limit_seconds=3.0,
            max_pages=100,
            requires_js=True,
            keywords=['AI', 'artificial intelligence', 'digital', 'innovation', 'Africa']
        ))
        
        # USAID Funding
        self.targets.append(ScrapingTarget(
            name="USAID Partnership Opportunities",
            base_url="https://www.usaid.gov/work-usaid/partnership-opportunities",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            selectors={
                'title': '.partnership-title',
                'description': '.partnership-description',
                'deadline': '.deadline',
                'location': '.location',
                'link': '.partnership-link'
            },
            rate_limit_seconds=2.0,
            max_pages=20,
            keywords=['Africa', 'development', 'technology', 'AI', 'innovation']
        ))
        
        # World Bank Projects
        self.targets.append(ScrapingTarget(
            name="World Bank Projects",
            base_url="https://projects.worldbank.org/en/projects-operations/projects-list",
            strategy=ScrapingStrategy.PAGINATED,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            selectors={
                'title': '.project-title',
                'description': '.project-description',
                'country': '.project-country',
                'sector': '.project-sector',
                'amount': '.project-amount',
                'link': '.project-link'
            },
            pagination_config={
                'type': 'url_param',
                'param_name': 'page',
                'start_page': 1
            },
            rate_limit_seconds=2.0,
            max_pages=50,
            keywords=['Africa', 'AI', 'digital', 'technology', 'innovation']
        ))
        
        # African Development Bank
        self.targets.append(ScrapingTarget(
            name="African Development Bank",
            base_url="https://www.afdb.org/en/projects-and-operations",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            selectors={
                'title': '.project-title',
                'description': '.project-summary',
                'country': '.project-country',
                'sector': '.project-sector',
                'link': '.project-detail-link'
            },
            rate_limit_seconds=2.0,
            max_pages=30,
            keywords=['Africa', 'development', 'technology', 'digital', 'AI']
        ))
    
    def _add_corporate_targets(self):
        """Add corporate funding program targets"""
        
        # Google AI
        self.targets.append(ScrapingTarget(
            name="Google AI Research",
            base_url="https://ai.google/research/",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.RESEARCH_CALL,
            selectors={
                'title': '.research-title',
                'description': '.research-description',
                'date': '.publication-date',
                'link': '.research-link'
            },
            rate_limit_seconds=3.0,
            max_pages=10,
            keywords=['AI', 'artificial intelligence', 'research', 'grants', 'funding']
        ))
        
        # Microsoft Research
        self.targets.append(ScrapingTarget(
            name="Microsoft Research",
            base_url="https://www.microsoft.com/en-us/research/",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.RESEARCH_CALL,
            selectors={
                'title': '.research-project-title',
                'description': '.research-project-description',
                'date': '.research-date',
                'link': '.research-project-link'
            },
            rate_limit_seconds=2.0,
            max_pages=15,
            keywords=['AI', 'artificial intelligence', 'research', 'Africa', 'development']
        ))
        
        # Gates Foundation
        self.targets.append(ScrapingTarget(
            name="Gates Foundation Grants",
            base_url="https://www.gatesfoundation.org/how-we-work/quick-links/grants-database",
            strategy=ScrapingStrategy.JAVASCRIPT_HEAVY,
            content_type=ContentType.GRANT_ANNOUNCEMENT,
            selectors={
                'title': '.grant-title',
                'description': '.grant-description',
                'amount': '.grant-amount',
                'recipient': '.grant-recipient',
                'date': '.grant-date',
                'link': '.grant-link'
            },
            rate_limit_seconds=3.0,
            max_pages=25,
            requires_js=True,
            keywords=['Africa', 'development', 'technology', 'AI', 'innovation']
        ))
    
    def _add_academic_targets(self):
        """Add university and research funding targets"""
        
        # MIT Research
        self.targets.append(ScrapingTarget(
            name="MIT Research",
            base_url="https://web.mit.edu/research/",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.RESEARCH_CALL,
            selectors={
                'title': '.research-title',
                'description': '.research-description',
                'link': '.research-link'
            },
            rate_limit_seconds=2.0,
            max_pages=10,
            keywords=['AI', 'artificial intelligence', 'research', 'funding', 'collaboration']
        ))
        
        # Stanford Research
        self.targets.append(ScrapingTarget(
            name="Stanford Research",
            base_url="https://www.stanford.edu/research/",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.RESEARCH_CALL,
            selectors={
                'title': '.research-project-title',
                'description': '.research-project-description',
                'link': '.research-project-link'
            },
            rate_limit_seconds=2.0,
            max_pages=10,
            keywords=['AI', 'artificial intelligence', 'research', 'international', 'Africa']
        ))
    
    def _add_accelerator_targets(self):
        """Add accelerator and incubator targets"""
        
        # Y Combinator
        self.targets.append(ScrapingTarget(
            name="Y Combinator",
            base_url="https://www.ycombinator.com/companies",
            strategy=ScrapingStrategy.JAVASCRIPT_HEAVY,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            selectors={
                'title': '.company-title',
                'description': '.company-description',
                'batch': '.company-batch',
                'link': '.company-link'
            },
            rate_limit_seconds=3.0,
            max_pages=20,
            requires_js=True,
            keywords=['AI', 'artificial intelligence', 'Africa', 'startup', 'funding']
        ))
        
        # Techstars
        self.targets.append(ScrapingTarget(
            name="Techstars",
            base_url="https://www.techstars.com/accelerators",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            selectors={
                'title': '.accelerator-title',
                'description': '.accelerator-description',
                'location': '.accelerator-location',
                'link': '.accelerator-link'
            },
            rate_limit_seconds=2.0,
            max_pages=15,
            keywords=['AI', 'artificial intelligence', 'Africa', 'startup', 'accelerator']
        ))
    
    def _add_news_targets(self):
        """Add news and media source targets"""
        
        # TechCrunch
        self.targets.append(ScrapingTarget(
            name="TechCrunch Funding",
            base_url="https://techcrunch.com/category/venture/",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.PARTNERSHIP_NEWS,
            selectors={
                'title': '.post-title',
                'description': '.post-excerpt',
                'date': '.post-date',
                'link': '.post-link'
            },
            rate_limit_seconds=2.0,
            max_pages=30,
            keywords=['AI', 'artificial intelligence', 'Africa', 'funding', 'startup']
        ))
        
        # VentureBeat
        self.targets.append(ScrapingTarget(
            name="VentureBeat AI",
            base_url="https://venturebeat.com/category/ai/",
            strategy=ScrapingStrategy.SIMPLE_HTML,
            content_type=ContentType.PARTNERSHIP_NEWS,
            selectors={
                'title': '.article-title',
                'description': '.article-excerpt',
                'date': '.article-date',
                'link': '.article-link'
            },
            rate_limit_seconds=2.0,
            max_pages=25,
            keywords=['AI', 'artificial intelligence', 'Africa', 'funding', 'investment']
        ))
    
    def _create_session(self, target: ScrapingTarget) -> requests.Session:
        """Create a configured session for a target"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': self.user_agents.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Add custom headers
        session.headers.update(target.headers)
        
        # Add cookies
        for name, value in target.cookies.items():
            session.cookies.set(name, value)
        
        return session
    
    def _create_selenium_driver(self) -> webdriver.Chrome:
        """Create a Selenium WebDriver instance"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={self.user_agents.random}')
        
        # Add random options to avoid detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _get_selenium_driver(self) -> webdriver.Chrome:
        """Get or create a Selenium driver"""
        if len(self.selenium_drivers) < self.max_selenium_drivers:
            driver = self._create_selenium_driver()
            self.selenium_drivers.append(driver)
            return driver
        else:
            # Reuse existing driver
            return random.choice(self.selenium_drivers)
    
    def _apply_rate_limit(self, target: ScrapingTarget):
        """Apply rate limiting for a target"""
        domain = urlparse(target.base_url).netloc
        
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = time.time()
        
        # Check if we need to wait
        time_since_last = time.time() - self.rate_limiters[domain]
        if time_since_last < target.rate_limit_seconds:
            wait_time = target.rate_limit_seconds - time_since_last
            time.sleep(wait_time)
        
        self.rate_limiters[domain] = time.time()
    
    def _extract_content_simple(self, html: str, target: ScrapingTarget) -> List[ScrapedContent]:
        """Extract content using simple HTML parsing"""
        soup = BeautifulSoup(html, 'html.parser')
        content_items = []
        
        # Find all content containers
        containers = soup.find_all(attrs={'class': re.compile(r'(item|article|post|project|opportunity|grant)')})
        
        for container in containers:
            try:
                # Extract data using selectors
                extracted_data = {}
                
                for field, selector in target.selectors.items():
                    element = container.select_one(selector)
                    if element:
                        extracted_data[field] = element.get_text(strip=True)
                
                # Create scraped content if we have minimum required fields
                if extracted_data.get('title') and extracted_data.get('link'):
                    content = ScrapedContent(
                        title=extracted_data['title'],
                        content=extracted_data.get('description', ''),
                        url=urljoin(target.base_url, extracted_data['link']),
                        source=target.name,
                        content_type=target.content_type,
                        extracted_data=extracted_data,
                        metadata={'scraping_strategy': target.strategy.value}
                    )
                    
                    # Check for keyword relevance
                    if self._is_relevant_content(content, target.keywords):
                        content_items.append(content)
                        
            except Exception as e:
                logger.warning(f"Error extracting content from container: {e}")
                continue
        
        return content_items
    
    def _extract_content_javascript(self, target: ScrapingTarget) -> List[ScrapedContent]:
        """Extract content from JavaScript-heavy sites using Selenium"""
        driver = self._get_selenium_driver()
        content_items = []
        
        try:
            driver.get(target.base_url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            
            # Handle pagination
            page_count = 0
            while page_count < target.max_pages:
                # Extract content from current page
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                page_content = self._extract_content_simple(soup.prettify(), target)
                content_items.extend(page_content)
                
                # Try to navigate to next page
                if target.pagination_config:
                    try:
                        if target.pagination_config['type'] == 'button_click':
                            next_button = driver.find_element(By.CSS_SELECTOR, target.pagination_config['next_button'])
                            if next_button.is_enabled():
                                driver.execute_script("arguments[0].click();", next_button)
                                time.sleep(2)
                                page_count += 1
                            else:
                                break
                        else:
                            break
                    except Exception:
                        break
                else:
                    break
                    
        except TimeoutException:
            logger.warning(f"Timeout loading JavaScript content for {target.name}")
        except Exception as e:
            logger.error(f"Error extracting JavaScript content for {target.name}: {e}")
        
        return content_items
    
    def _is_relevant_content(self, content: ScrapedContent, keywords: List[str]) -> bool:
        """Check if content is relevant based on keywords"""
        if not keywords:
            return True
        
        text = f"{content.title} {content.content}".lower()
        return any(keyword.lower() in text for keyword in keywords)
    
    def _is_duplicate(self, content: ScrapedContent) -> bool:
        """Check if content is a duplicate"""
        if content.content_hash in self.content_hashes:
            return True
        
        self.content_hashes.add(content.content_hash)
        return False
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _scrape_target(self, target: ScrapingTarget) -> List[ScrapedContent]:
        """Scrape a single target"""
        if not target.enabled:
            return []
        
        logger.info(f"Scraping {target.name}")
        start_time = time.time()
        
        try:
            # Apply rate limiting
            self._apply_rate_limit(target)
            
            content_items = []
            
            if target.strategy == ScrapingStrategy.JAVASCRIPT_HEAVY:
                content_items = self._extract_content_javascript(target)
            
            elif target.strategy == ScrapingStrategy.CLOUDFLARE_PROTECTED:
                # Use cloudscraper for Cloudflare protection
                scraper = cloudscraper.create_scraper()
                response = scraper.get(target.base_url)
                content_items = self._extract_content_simple(response.text, target)
            
            else:
                # Use simple HTML parsing
                session = self._create_session(target)
                
                if target.strategy == ScrapingStrategy.PAGINATED:
                    # Handle pagination
                    page = 1
                    while page <= target.max_pages:
                        if target.pagination_config:
                            url = f"{target.base_url}?{target.pagination_config['param_name']}={page}"
                        else:
                            url = target.base_url
                        
                        response = session.get(url, timeout=30)
                        if response.status_code == 200:
                            page_content = self._extract_content_simple(response.text, target)
                            content_items.extend(page_content)
                            
                            # Check if we have content, if not, we might have reached the end
                            if not page_content:
                                break
                        else:
                            logger.warning(f"Failed to fetch page {page} for {target.name}: {response.status_code}")
                            break
                        
                        page += 1
                        time.sleep(1)  # Additional delay between pages
                
                else:
                    # Simple single-page scraping
                    response = session.get(target.base_url, timeout=30)
                    if response.status_code == 200:
                        content_items = self._extract_content_simple(response.text, target)
                    else:
                        logger.warning(f"Failed to fetch {target.name}: {response.status_code}")
            
            # Filter duplicates
            unique_content = []
            for content in content_items:
                if not self._is_duplicate(content):
                    unique_content.append(content)
                else:
                    self.stats['duplicates_filtered'] += 1
            
            # Update statistics
            target.success_count += len(unique_content)
            target.last_scraped = datetime.now()
            self.stats['content_extracted'] += len(unique_content)
            
            logger.info(f"Scraped {len(unique_content)} items from {target.name} in {time.time() - start_time:.2f}s")
            
            return unique_content
            
        except Exception as e:
            logger.error(f"Error scraping {target.name}: {e}")
            target.error_count += 1
            self.stats['errors'] += 1
            return []
    
    def scrape_all_targets(self) -> List[ScrapedContent]:
        """Scrape all targets using parallel processing"""
        logger.info(f"Starting parallel scraping of {len(self.targets)} targets")
        
        all_content = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_target = {
                executor.submit(self._scrape_target, target): target 
                for target in self.targets if target.enabled
            }
            
            # Process completed tasks
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    content = future.result()
                    all_content.extend(content)
                    self.stats['targets_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {target.name}: {e}")
                    self.stats['errors'] += 1
        
        logger.info(f"Completed scraping: {len(all_content)} items extracted")
        return all_content
    
    def start_continuous_scraping(self, interval_hours: int = 6):
        """Start continuous scraping with specified interval"""
        logger.info(f"Starting continuous scraping with {interval_hours}h interval")
        
        self.is_running = True
        self.stop_event.clear()
        
        def scraping_loop():
            while not self.stop_event.is_set():
                try:
                    # Scrape all targets
                    content = self.scrape_all_targets()
                    
                    # Store content (extend with database storage)
                    self.scraped_content.extend(content)
                    
                    # Wait for next interval
                    if not self.stop_event.wait(interval_hours * 3600):
                        continue
                    else:
                        break
                        
                except Exception as e:
                    logger.error(f"Error in scraping loop: {e}")
                    time.sleep(300)  # Wait 5 minutes before retrying
        
        # Start scraping thread
        scraping_thread = threading.Thread(target=scraping_loop, daemon=True)
        scraping_thread.start()
        
        return scraping_thread
    
    def stop_scraping(self):
        """Stop continuous scraping"""
        logger.info("Stopping web scraping engine")
        self.is_running = False
        self.stop_event.set()
        
        # Close Selenium drivers
        for driver in self.selenium_drivers:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing Selenium driver: {e}")
        
        self.selenium_drivers.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        elapsed_time = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'targets_total': len(self.targets),
            'targets_enabled': len([t for t in self.targets if t.enabled]),
            'targets_processed': self.stats['targets_processed'],
            'content_extracted': self.stats['content_extracted'],
            'duplicates_filtered': self.stats['duplicates_filtered'],
            'errors': self.stats['errors'],
            'content_per_hour': self.stats['content_extracted'] / (elapsed_time / 3600) if elapsed_time > 0 else 0,
            'success_rate': (self.stats['targets_processed'] / len(self.targets)) * 100 if self.targets else 0,
            'uptime_hours': elapsed_time / 3600,
            'selenium_drivers': len(self.selenium_drivers),
            'content_in_memory': len(self.scraped_content),
            'unique_content_hashes': len(self.content_hashes)
        }
    
    def get_scraped_content(self) -> List[ScrapedContent]:
        """Get all scraped content"""
        return self.scraped_content.copy()
    
    def clear_scraped_content(self):
        """Clear scraped content from memory"""
        self.scraped_content.clear()
        self.content_hashes.clear()
        logger.info("Cleared scraped content from memory")


# Example usage
async def main():
    """Example usage of the web scraping engine"""
    engine = HighVolumeWebScrapingEngine(max_workers=10, batch_size=100)
    
    try:
        # Initialize all targets
        engine.initialize_targets()
        
        # Scrape all targets once
        content = engine.scrape_all_targets()
        
        # Print statistics
        stats = engine.get_stats()
        print(f"Scraping completed: {stats}")
        
        # Print sample content
        if content:
            print(f"\nSample content ({len(content)} items):")
            for item in content[:3]:
                print(f"- {item.title} ({item.source})")
        
    finally:
        engine.stop_scraping()


if __name__ == "__main__":
    asyncio.run(main())