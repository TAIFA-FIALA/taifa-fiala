"""
High-Volume Data Ingestion Pipeline for AI Africa Funding Tracker
Target: 10K-100M records with automated, scalable data collection

This pipeline is designed to handle massive scale data ingestion from multiple sources:
- RSS feeds (hundreds of sources)
- News APIs (real-time feeds)
- Web scraping (targeted sites)
- Document parsing (PDFs, reports)
- Social media monitoring
- API integrations (funding databases)
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import json
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
import feedparser
from urllib.parse import urljoin, urlparse
import re
import backoff
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

# Database and vector imports
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import asyncpg

logger = logging.getLogger(__name__)


class SourceType(Enum):
    RSS = "rss"
    NEWS_API = "news_api"
    WEB_SCRAPE = "web_scrape"
    API_INTEGRATION = "api_integration"
    DOCUMENT_FEED = "document_feed"
    SOCIAL_MEDIA = "social_media"


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class DataSource:
    """Configuration for a data source"""
    name: str
    url: str
    source_type: SourceType
    priority: Priority = Priority.MEDIUM
    check_interval_minutes: int = 60
    keywords: List[str] = field(default_factory=list)
    rate_limit_delay: float = 1.0
    retry_count: int = 3
    timeout: int = 30
    enabled: bool = True
    last_check: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    auth: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if isinstance(self.source_type, str):
            self.source_type = SourceType(self.source_type)
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)


@dataclass
class IngestionStats:
    """Statistics for data ingestion"""
    total_sources: int = 0
    active_sources: int = 0
    total_items_processed: int = 0
    total_items_stored: int = 0
    total_errors: int = 0
    processing_rate_per_minute: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class HighVolumeDataPipeline:
    """
    Massively scalable data ingestion pipeline
    Designed to handle 10K-100M records
    """
    
    def __init__(self, max_workers: int = 50, batch_size: int = 1000):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.stats = IngestionStats()
        
        # Data sources configuration
        self.sources: List[DataSource] = []
        self.source_queue = queue.PriorityQueue()
        self.processing_queue = queue.Queue(maxsize=10000)
        
        # Database connections
        self.db_pool = None
        self.supabase_client = None
        
        # Processing control
        self.is_running = False
        self.stop_event = threading.Event()
        self.workers = []
        
        # Session management
        self.session_connector = None
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        
        # Rate limiting
        self.rate_limiters = {}
        
        # Initialize logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_ingestion.log'),
                logging.StreamHandler()
            ]
        )
    
    async def initialize(self):
        """Initialize the pipeline"""
        logger.info("Initializing high-volume data pipeline")
        
        # Initialize database connections
        await self._initialize_db_connections()
        
        # Initialize HTTP session
        self.session_connector = aiohttp.TCPConnector(
            limit=200,
            limit_per_host=20,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        # Load data sources
        await self._load_data_sources()
        
        logger.info(f"Pipeline initialized with {len(self.sources)} data sources")
    
    async def _initialize_db_connections(self):
        """Initialize database connection pools"""
        try:
            # Initialize PostgreSQL/Supabase connection pool
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                # Convert SQLAlchemy URL format to asyncpg format
                if db_url.startswith('postgresql+asyncpg://'):
                    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
                elif db_url.startswith('postgresql+asyncpg://'):
                    db_url = db_url.replace('postgresql+asyncpg://', 'postgres://')
                
                self.db_pool = await asyncpg.create_pool(
                    db_url,
                    min_size=10,
                    max_size=50,
                    command_timeout=60
                )
                logger.info("Database connection pool initialized")
            
            # Initialize Supabase client
            from supabase import create_client
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
            
            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized")
        
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _load_data_sources(self):
        """Load and configure data sources"""
        # Load existing RSS feeds
        rss_sources = await self._load_rss_sources()
        
        # Add news API sources
        news_api_sources = await self._load_news_api_sources()
        
        # Add web scraping sources
        web_scrape_sources = await self._load_web_scrape_sources()
        
        # Add API integration sources
        api_integration_sources = await self._load_api_integration_sources()
        
        # Combine all sources
        self.sources = rss_sources + news_api_sources + web_scrape_sources + api_integration_sources
        
        # Update stats
        self.stats.total_sources = len(self.sources)
        self.stats.active_sources = len([s for s in self.sources if s.enabled])
        
        logger.info(f"Loaded {len(self.sources)} data sources")
    
    async def _load_rss_sources(self) -> List[DataSource]:
        """Load RSS feed sources (expanded from current 20 to 500+)"""
        sources = []
        
        # Load existing RSS feeds
        try:
            with open('data_connectors/config/rss_feeds.json', 'r') as f:
                rss_config = json.load(f)
                
            for source_config in rss_config.get('rss_sources', []):
                source = DataSource(
                    name=source_config['name'],
                    url=source_config['url'],
                    source_type=SourceType.RSS,
                    priority=Priority.HIGH if source_config.get('priority') == 'high' else Priority.MEDIUM,
                    check_interval_minutes=source_config.get('check_interval', 60),
                    keywords=source_config.get('keywords', []),
                    rate_limit_delay=1.0,
                    retry_count=3,
                    timeout=30
                )
                sources.append(source)
        except Exception as e:
            logger.warning(f"Failed to load RSS config: {e}")
        
        # Add massive list of additional RSS feeds for scaling
        additional_rss_feeds = [
            # African News Sources
            ("AllAfrica.com", "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf"),
            ("News24 Africa", "https://feeds.news24.com/articles/news24/africa/rss"),
            ("Mail & Guardian", "https://mg.co.za/feed/"),
            ("Daily Maverick", "https://www.dailymaverick.co.za/dmrss/"),
            ("The Citizen", "https://citizen.co.za/feed/"),
            ("IOL", "https://www.iol.co.za/cmlink/1.640"),
            ("Business Day", "https://www.businesslive.co.za/bd/feed/"),
            ("Financial Mail", "https://www.businesslive.co.za/fm/feed/"),
            ("Engineering News", "https://www.engineeringnews.co.za/rss-feeds/latest-news"),
            ("ITWeb", "https://www.itweb.co.za/rss/content.rss"),
            
            # Tech & Innovation Sources
            ("TechCentral", "https://techcentral.co.za/feed/"),
            ("MyBroadband", "https://mybroadband.co.za/news/feed"),
            ("Ventureburn", "https://ventureburn.com/feed/"),
            ("Gadget", "https://gadget.co.za/feed/"),
            ("ITNews Africa", "https://www.itnewsafrica.com/feed/"),
            ("CIO", "https://www.cio.com/feed/"),
            ("ComputerWorld", "https://www.computerworld.com/index.rss"),
            ("InformationWeek", "https://www.informationweek.com/rss_simple.asp"),
            ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
            ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
            
            # Global Development Sources
            ("DevEx", "https://www.devex.com/rss"),
            ("IRIN News", "https://www.thenewhumanitarian.org/rss.xml"),
            ("ReliefWeb", "https://reliefweb.int/rss.xml"),
            ("Development Gateway", "https://www.developmentgateway.org/feed/"),
            ("Bond", "https://www.bond.org.uk/news/feed"),
            ("Overseas Development Institute", "https://odi.org/en/feed/"),
            ("Brookings", "https://www.brookings.edu/feed/"),
            ("Council on Foreign Relations", "https://www.cfr.org/rss-feeds"),
            ("Center for Global Development", "https://www.cgdev.org/feed"),
            ("Gates Foundation", "https://www.gatesfoundation.org/news-and-insights/rss"),
            
            # AI & Technology Research Sources
            ("AI Research", "https://www.airesearch.com/feed/"),
            ("Machine Learning Mastery", "https://machinelearningmastery.com/feed/"),
            ("Towards Data Science", "https://towardsdatascience.com/feed"),
            ("Analytics Vidhya", "https://www.analyticsvidhya.com/feed/"),
            ("KDnuggets", "https://www.kdnuggets.com/feed"),
            ("AI News", "https://artificialintelligence-news.com/feed/"),
            ("The Gradient", "https://thegradient.pub/rss/"),
            ("Distill", "https://distill.pub/rss.xml"),
            ("Papers with Code", "https://paperswithcode.com/rss.xml"),
            ("Arxiv CS.AI", "https://export.arxiv.org/rss/cs.AI"),
            
            # Funding & Investment Sources
            ("Crunchbase News", "https://news.crunchbase.com/feed/"),
            ("PitchBook", "https://pitchbook.com/news/feed"),
            ("VC Circle", "https://www.vccircle.com/feed/"),
            ("Deal Street Asia", "https://www.dealstreetasia.com/feed/"),
            ("African Business", "https://african.business/feed/"),
            ("How We Made It In Africa", "https://www.howwemadeitinafrica.com/feed/"),
            ("Ventures Africa", "https://venturesafrica.com/feed/"),
            ("Africa.com", "https://www.africa.com/feed/"),
            ("This is Africa", "https://thisisafrica.me/feed/"),
            ("New African", "https://newafricanmagazine.com/feed/"),
        ]
        
        # Add additional feeds
        for name, url in additional_rss_feeds:
            source = DataSource(
                name=name,
                url=url,
                source_type=SourceType.RSS,
                priority=Priority.MEDIUM,
                check_interval_minutes=120,
                keywords=['AI', 'artificial intelligence', 'funding', 'Africa', 'technology', 'investment'],
                rate_limit_delay=2.0,
                retry_count=3,
                timeout=30
            )
            sources.append(source)
        
        return sources
    
    async def _load_news_api_sources(self) -> List[DataSource]:
        """Load news API sources for real-time data"""
        sources = []
        
        # News API sources
        news_api_key = os.getenv('NEWS_API_KEY')
        if news_api_key:
            # High-volume news API queries
            news_queries = [
                "AI+Africa+funding",
                "artificial+intelligence+Africa+investment",
                "machine+learning+Africa+grants",
                "AI+startups+Africa",
                "technology+funding+Africa",
                "innovation+grants+Africa",
                "digital+transformation+Africa",
                "AI+research+Africa"
            ]
            
            for query in news_queries:
                source = DataSource(
                    name=f"NewsAPI: {query}",
                    url=f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={news_api_key}",
                    source_type=SourceType.NEWS_API,
                    priority=Priority.HIGH,
                    check_interval_minutes=30,
                    keywords=['AI', 'Africa', 'funding'],
                    rate_limit_delay=1.0,
                    retry_count=3,
                    timeout=30
                )
                sources.append(source)
        
        return sources
    
    async def _load_web_scrape_sources(self) -> List[DataSource]:
        """Load web scraping sources for targeted data extraction"""
        sources = []
        
        # Major funding databases and websites
        scrape_targets = [
            # Government funding databases
            ("EU Funding", "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search"),
            ("USAID", "https://www.usaid.gov/work-usaid/partnership-opportunities"),
            ("UK Aid", "https://www.gov.uk/government/collections/dfid-research-and-evidence"),
            ("Gates Foundation", "https://www.gatesfoundation.org/how-we-work/quick-links/grants-database"),
            ("World Bank", "https://projects.worldbank.org/"),
            ("AfDB", "https://www.afdb.org/en/projects-and-operations"),
            
            # University and research funding
            ("MIT", "https://web.mit.edu/"),
            ("Stanford", "https://www.stanford.edu/"),
            ("Oxford", "https://www.ox.ac.uk/"),
            ("Cambridge", "https://www.cam.ac.uk/"),
            
            # Corporate funding programs
            ("Google AI", "https://ai.google/"),
            ("Microsoft Research", "https://www.microsoft.com/en-us/research/"),
            ("IBM Research", "https://www.research.ibm.com/"),
            ("Amazon Science", "https://www.amazon.science/"),
            ("Facebook Research", "https://research.fb.com/"),
            
            # Accelerators and incubators
            ("Y Combinator", "https://www.ycombinator.com/"),
            ("Techstars", "https://www.techstars.com/"),
            ("500 Startups", "https://500.co/"),
            ("Plug and Play", "https://www.plugandplaytechcenter.com/"),
            ("SOSV", "https://sosv.com/"),
        ]
        
        for name, url in scrape_targets:
            source = DataSource(
                name=f"Scraper: {name}",
                url=url,
                source_type=SourceType.WEB_SCRAPE,
                priority=Priority.MEDIUM,
                check_interval_minutes=240,  # 4 hours
                keywords=['AI', 'funding', 'Africa', 'grants', 'investment'],
                rate_limit_delay=5.0,  # Slower for scraping
                retry_count=2,
                timeout=60
            )
            sources.append(source)
        
        return sources
    
    async def _load_api_integration_sources(self) -> List[DataSource]:
        """Load API integration sources for structured data"""
        sources = []
        
        # API integrations
        api_integrations = [
            ("GrantsDB API", "https://api.grantsdb.org/v1/grants"),
            ("OpenAI API", "https://api.openai.com/v1/"),
            ("Anthropic API", "https://api.anthropic.com/v1/"),
            ("Serper API", "https://google.serper.dev/search"),
            ("Tavily API", "https://api.tavily.com/search"),
        ]
        
        for name, url in api_integrations:
            source = DataSource(
                name=f"API: {name}",
                url=url,
                source_type=SourceType.API_INTEGRATION,
                priority=Priority.HIGH,
                check_interval_minutes=60,
                keywords=['AI', 'funding', 'Africa'],
                rate_limit_delay=1.0,
                retry_count=3,
                timeout=30
            )
            sources.append(source)
        
        return sources
    
    async def start_pipeline(self):
        """Start the high-volume data pipeline"""
        if self.is_running:
            logger.warning("Pipeline is already running")
            return
        
        logger.info("Starting high-volume data pipeline")
        self.is_running = True
        self.stop_event.clear()
        
        # Start worker threads
        self.workers = []
        
        # Source monitoring workers
        for i in range(min(10, len(self.sources))):
            worker = threading.Thread(
                target=self._source_monitor_worker,
                name=f"SourceMonitor-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # Data processing workers
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._data_processor_worker,
                name=f"DataProcessor-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # Statistics monitoring
        stats_worker = threading.Thread(
            target=self._stats_monitor_worker,
            name="StatsMonitor",
            daemon=True
        )
        stats_worker.start()
        self.workers.append(stats_worker)
        
        # Queue management
        queue_worker = threading.Thread(
            target=self._queue_manager_worker,
            name="QueueManager",
            daemon=True
        )
        queue_worker.start()
        self.workers.append(queue_worker)
        
        logger.info(f"Pipeline started with {len(self.workers)} workers")
    
    def _source_monitor_worker(self):
        """Worker thread that monitors sources and schedules collection"""
        while not self.stop_event.is_set():
            try:
                current_time = datetime.now()
                
                for source in self.sources:
                    if not source.enabled:
                        continue
                    
                    # Check if it's time to collect from this source
                    if (source.last_check is None or 
                        current_time - source.last_check >= timedelta(minutes=source.check_interval_minutes)):
                        
                        # Add to priority queue
                        priority = source.priority.value
                        self.source_queue.put((priority, current_time, source))
                        source.last_check = current_time
                
                # Sleep for a bit before checking again
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Source monitor error: {e}")
                time.sleep(30)
    
    def _data_processor_worker(self):
        """Worker thread that processes data from sources"""
        while not self.stop_event.is_set():
            try:
                # Get source from queue
                try:
                    priority, scheduled_time, source = self.source_queue.get(timeout=5)
                except queue.Empty:
                    continue
                
                # Process the source
                asyncio.run(self._process_source(source))
                
                # Mark task as done
                self.source_queue.task_done()
                
            except Exception as e:
                logger.error(f"Data processor error: {e}")
                time.sleep(1)
    
    def _stats_monitor_worker(self):
        """Worker thread that monitors and updates statistics"""
        while not self.stop_event.is_set():
            try:
                # Update system stats
                self.stats.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self.stats.cpu_usage_percent = psutil.cpu_percent()
                self.stats.last_update = datetime.now()
                
                # Calculate processing rate
                elapsed_minutes = (datetime.now() - self.stats.start_time).total_seconds() / 60
                if elapsed_minutes > 0:
                    self.stats.processing_rate_per_minute = self.stats.total_items_processed / elapsed_minutes
                
                # Log stats periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    logger.info(f"Pipeline Stats: {self.stats.total_items_processed} items processed, "
                               f"{self.stats.processing_rate_per_minute:.1f} items/min, "
                               f"{self.stats.memory_usage_mb:.1f}MB memory, "
                               f"{self.stats.cpu_usage_percent:.1f}% CPU")
                
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Stats monitor error: {e}")
                time.sleep(60)
    
    def _queue_manager_worker(self):
        """Worker thread that manages queue health and prevents overload"""
        while not self.stop_event.is_set():
            try:
                # Monitor queue sizes
                source_queue_size = self.source_queue.qsize()
                processing_queue_size = self.processing_queue.qsize()
                
                # Log queue health
                if source_queue_size > 1000 or processing_queue_size > 5000:
                    logger.warning(f"Queue sizes: source={source_queue_size}, processing={processing_queue_size}")
                
                # Implement backpressure if needed
                if processing_queue_size > 8000:
                    logger.warning("Processing queue full, implementing backpressure")
                    time.sleep(30)
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Queue manager error: {e}")
                time.sleep(60)
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _process_source(self, source: DataSource):
        """Process a single data source"""
        try:
            start_time = time.time()
            
            # Apply rate limiting
            await self._apply_rate_limit(source)
            
            # Collect data based on source type
            if source.source_type == SourceType.RSS:
                items = await self._collect_rss_data(source)
            elif source.source_type == SourceType.NEWS_API:
                items = await self._collect_news_api_data(source)
            elif source.source_type == SourceType.WEB_SCRAPE:
                items = await self._collect_web_scrape_data(source)
            elif source.source_type == SourceType.API_INTEGRATION:
                items = await self._collect_api_data(source)
            else:
                logger.warning(f"Unknown source type: {source.source_type}")
                return
            
            # Process and store items
            if items:
                await self._store_items(items, source)
                source.success_count += len(items)
                self.stats.total_items_processed += len(items)
                
                logger.info(f"Processed {len(items)} items from {source.name} in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing source {source.name}: {e}")
            source.error_count += 1
            self.stats.total_errors += 1
            raise
    
    async def _apply_rate_limit(self, source: DataSource):
        """Apply rate limiting for a source"""
        domain = urlparse(source.url).netloc
        
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = time.time()
        
        # Check if we need to wait
        time_since_last = time.time() - self.rate_limiters[domain]
        if time_since_last < source.rate_limit_delay:
            await asyncio.sleep(source.rate_limit_delay - time_since_last)
        
        self.rate_limiters[domain] = time.time()
    
    async def _collect_rss_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Collect data from RSS feed"""
        try:
            # Use feedparser for RSS parsing
            feed = feedparser.parse(source.url)
            
            items = []
            for entry in feed.entries:
                # Extract relevant data
                item = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', '') or entry.get('description', ''),
                    'url': entry.get('link', ''),
                    'published_at': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'source_name': source.name,
                    'source_type': source.source_type.value,
                    'collected_at': datetime.now().isoformat(),
                    'keywords': source.keywords
                }
                
                # Filter by keywords if specified
                if source.keywords:
                    content_text = (item['title'] + ' ' + item['content']).lower()
                    if any(keyword.lower() in content_text for keyword in source.keywords):
                        items.append(item)
                else:
                    items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"RSS collection error for {source.name}: {e}")
            return []
    
    async def _collect_news_api_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Collect data from News API"""
        try:
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(source.url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        items = []
                        for article in data.get('articles', []):
                            item = {
                                'title': article.get('title', ''),
                                'content': article.get('description', '') or article.get('content', ''),
                                'url': article.get('url', ''),
                                'published_at': article.get('publishedAt', ''),
                                'author': article.get('author', ''),
                                'source_name': source.name,
                                'source_type': source.source_type.value,
                                'collected_at': datetime.now().isoformat(),
                                'keywords': source.keywords
                            }
                            items.append(item)
                        
                        return items
                    else:
                        logger.warning(f"News API returned status {response.status} for {source.name}")
                        return []
                        
        except Exception as e:
            logger.error(f"News API collection error for {source.name}: {e}")
            return []
    
    async def _collect_web_scrape_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Collect data from web scraping"""
        try:
            # Basic web scraping - would need to be enhanced for production
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(source.url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Simple content extraction (would need proper parsing)
                        item = {
                            'title': f"Scraped content from {source.name}",
                            'content': content[:1000],  # Truncate for now
                            'url': source.url,
                            'published_at': datetime.now().isoformat(),
                            'author': '',
                            'source_name': source.name,
                            'source_type': source.source_type.value,
                            'collected_at': datetime.now().isoformat(),
                            'keywords': source.keywords
                        }
                        
                        return [item]
                    else:
                        logger.warning(f"Web scraping returned status {response.status} for {source.name}")
                        return []
                        
        except Exception as e:
            logger.error(f"Web scraping error for {source.name}: {e}")
            return []
    
    async def _collect_api_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Collect data from API integration"""
        try:
            headers = source.headers.copy()
            if source.auth:
                headers.update(source.auth)
            
            async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                async with session.get(source.url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process API response (structure depends on API)
                        item = {
                            'title': f"API data from {source.name}",
                            'content': json.dumps(data)[:1000],
                            'url': source.url,
                            'published_at': datetime.now().isoformat(),
                            'author': '',
                            'source_name': source.name,
                            'source_type': source.source_type.value,
                            'collected_at': datetime.now().isoformat(),
                            'keywords': source.keywords
                        }
                        
                        return [item]
                    else:
                        logger.warning(f"API returned status {response.status} for {source.name}")
                        return []
                        
        except Exception as e:
            logger.error(f"API collection error for {source.name}: {e}")
            return []
    
    async def _store_items(self, items: List[Dict[str, Any]], source: DataSource):
        """Store collected items in database"""
        try:
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    # Batch insert for efficiency
                    for batch in self._batch_items(items, self.batch_size):
                        await self._batch_insert(conn, batch)
                        self.stats.total_items_stored += len(batch)
            
        except Exception as e:
            logger.error(f"Error storing items: {e}")
            raise
    
    def _batch_items(self, items: List[Dict[str, Any]], batch_size: int):
        """Yield batches of items"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    async def _batch_insert(self, conn, batch: List[Dict[str, Any]]):
        """Batch insert items into database"""
        try:
            # Insert into raw_content table for now
            insert_query = """
            INSERT INTO raw_content (title, content, url, published_at, author, source_name, source_type, collected_at, keywords)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (url) DO UPDATE SET
                collected_at = EXCLUDED.collected_at,
                content = EXCLUDED.content
            """
            
            for item in batch:
                await conn.execute(
                    insert_query,
                    item.get('title', ''),
                    item.get('content', ''),
                    item.get('url', ''),
                    item.get('published_at', ''),
                    item.get('author', ''),
                    item.get('source_name', ''),
                    item.get('source_type', ''),
                    item.get('collected_at', ''),
                    json.dumps(item.get('keywords', []))
                )
            
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            raise
    
    async def stop_pipeline(self):
        """Stop the data pipeline"""
        if not self.is_running:
            logger.warning("Pipeline is not running")
            return
        
        logger.info("Stopping data pipeline")
        self.is_running = False
        self.stop_event.set()
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=30)
        
        # Close database connections
        if self.db_pool:
            await self.db_pool.close()
        
        logger.info("Pipeline stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            'total_sources': self.stats.total_sources,
            'active_sources': self.stats.active_sources,
            'total_items_processed': self.stats.total_items_processed,
            'total_items_stored': self.stats.total_items_stored,
            'total_errors': self.stats.total_errors,
            'processing_rate_per_minute': self.stats.processing_rate_per_minute,
            'memory_usage_mb': self.stats.memory_usage_mb,
            'cpu_usage_percent': self.stats.cpu_usage_percent,
            'uptime_minutes': (datetime.now() - self.stats.start_time).total_seconds() / 60,
            'queue_sizes': {
                'source_queue': self.source_queue.qsize(),
                'processing_queue': self.processing_queue.qsize()
            }
        }


# Example usage
async def main():
    """Example usage of the high-volume pipeline"""
    pipeline = HighVolumeDataPipeline(max_workers=50, batch_size=1000)
    
    try:
        await pipeline.initialize()
        await pipeline.start_pipeline()
        
        # Run for a while
        await asyncio.sleep(3600)  # Run for 1 hour
        
    finally:
        await pipeline.stop_pipeline()


if __name__ == "__main__":
    asyncio.run(main())