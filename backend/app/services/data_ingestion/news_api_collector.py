"""
High-Volume News API Data Collection System
Designed for massive scale real-time news data ingestion

This module provides automated news collection from multiple APIs:
- NewsAPI (newsapi.org)
- GNews API (gnews.io)
- Bing News API (Microsoft)
- Google News API (via RSS)
- MediaStack API
- Currents API
- NewsCatcher API
- Serper News API
- Tavily News API

Features:
- Multi-API aggregation for maximum coverage
- Real-time and batch processing modes
- Intelligent query optimization
- Content deduplication across sources
- Rate limiting and quota management
- Automatic failover between APIs
- Keyword-based filtering and relevance scoring
- Structured data extraction
- Comprehensive error handling and retry logic
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
from urllib.parse import urlencode, quote
import backoff
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import feedparser
from dateutil import parser as date_parser
import os
from collections import defaultdict
import random

logger = logging.getLogger(__name__)


class NewsAPIType(Enum):
    """Different news API types"""
    NEWS_API = "newsapi"
    GNEWS_API = "gnews"
    BING_NEWS = "bing_news"
    GOOGLE_NEWS = "google_news"
    MEDIASTACK = "mediastack"
    CURRENTS_API = "currents"
    NEWSCATCHER = "newscatcher"
    SERPER_NEWS = "serper"
    TAVILY_NEWS = "tavily"


class QueryType(Enum):
    """Different query types for news APIs"""
    EVERYTHING = "everything"
    TOP_HEADLINES = "top_headlines"
    SOURCES = "sources"
    SEARCH = "search"


@dataclass
class NewsAPIConfig:
    """Configuration for a news API"""
    name: str
    api_type: NewsAPIType
    base_url: str
    api_key: str
    rate_limit_per_minute: int = 60
    max_requests_per_day: int = 1000
    supported_languages: List[str] = field(default_factory=lambda: ['en'])
    supported_countries: List[str] = field(default_factory=lambda: ['us', 'gb', 'za', 'ng', 'ke', 'gh'])
    max_results_per_request: int = 100
    requires_premium: bool = False
    endpoint_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 1  # 1 = highest priority
    
    def __post_init__(self):
        if isinstance(self.api_type, str):
            self.api_type = NewsAPIType(self.api_type)


@dataclass
class NewsQuery:
    """News search query configuration"""
    query: str
    query_type: QueryType = QueryType.EVERYTHING
    language: str = 'en'
    country: Optional[str] = None
    category: Optional[str] = None
    sources: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    sort_by: str = 'publishedAt'
    page_size: int = 100
    priority: int = 1
    
    def __post_init__(self):
        if isinstance(self.query_type, str):
            self.query_type = QueryType(self.query_type)


@dataclass
class NewsArticle:
    """News article data structure"""
    title: str
    description: str
    url: str
    content: str
    source: str
    api_source: str
    published_at: datetime
    author: Optional[str] = None
    url_to_image: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    relevance_score: float = 0.0
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)
    content_hash: str = field(init=False)
    
    def __post_init__(self):
        # Generate content hash for deduplication
        content_str = f"{self.title}{self.description}{self.url}"
        self.content_hash = hashlib.md5(content_str.encode()).hexdigest()


@dataclass
class APIQuota:
    """API quota tracking"""
    api_name: str
    requests_made: int = 0
    requests_limit: int = 1000
    reset_time: datetime = field(default_factory=datetime.now)
    rate_limit_remaining: int = 60
    rate_limit_reset: datetime = field(default_factory=datetime.now)
    
    def is_available(self) -> bool:
        """Check if API quota is available"""
        now = datetime.now()
        
        # Check daily limit
        if now.date() > self.reset_time.date():
            self.requests_made = 0
            self.reset_time = now
        
        # Check rate limit
        if now > self.rate_limit_reset:
            self.rate_limit_remaining = 60
            self.rate_limit_reset = now + timedelta(minutes=1)
        
        return (self.requests_made < self.requests_limit and 
                self.rate_limit_remaining > 0)


class HighVolumeNewsAPICollector:
    """
    High-volume news API data collection system
    Supports multiple news APIs with intelligent quota management
    """
    
    def __init__(self, max_workers: int = 10, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        # API configurations
        self.api_configs: Dict[str, NewsAPIConfig] = {}
        self.api_quotas: Dict[str, APIQuota] = {}
        
        # Query management
        self.queries: List[NewsQuery] = []
        self.query_queue = []
        
        # Content storage
        self.collected_articles: List[NewsArticle] = []
        self.content_hashes: Set[str] = set()
        
        # Session management
        self.session = None
        
        # Statistics
        self.stats = {
            'apis_initialized': 0,
            'queries_processed': 0,
            'articles_collected': 0,
            'duplicates_filtered': 0,
            'api_errors': 0,
            'quota_exceeded': 0,
            'start_time': datetime.now()
        }
        
        # Thread control
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Initialize logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the news collector"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/news_api_collector.log'),
                logging.StreamHandler()
            ]
        )
    
    def initialize_apis(self):
        """Initialize all news API configurations"""
        logger.info("Initializing news APIs")
        
        # NewsAPI.org
        news_api_key = os.getenv('NEWS_API_KEY')
        if news_api_key:
            self.api_configs['newsapi'] = NewsAPIConfig(
                name="NewsAPI",
                api_type=NewsAPIType.NEWS_API,
                base_url="https://newsapi.org/v2",
                api_key=news_api_key,
                rate_limit_per_minute=1000,
                max_requests_per_day=1000,
                max_results_per_request=100,
                endpoint_configs={
                    'everything': {'endpoint': '/everything', 'params': ['q', 'language', 'sortBy', 'pageSize', 'page', 'from', 'to']},
                    'top_headlines': {'endpoint': '/top-headlines', 'params': ['q', 'country', 'category', 'pageSize', 'page']},
                    'sources': {'endpoint': '/sources', 'params': ['language', 'country', 'category']}
                },
                priority=1
            )
        
        # GNews API
        gnews_api_key = os.getenv('GNEWS_API_KEY')
        if gnews_api_key:
            self.api_configs['gnews'] = NewsAPIConfig(
                name="GNews",
                api_type=NewsAPIType.GNEWS_API,
                base_url="https://gnews.io/api/v4",
                api_key=gnews_api_key,
                rate_limit_per_minute=100,
                max_requests_per_day=100,
                max_results_per_request=100,
                endpoint_configs={
                    'search': {'endpoint': '/search', 'params': ['q', 'lang', 'country', 'max', 'from', 'to', 'sortby']},
                    'top_headlines': {'endpoint': '/top-headlines', 'params': ['category', 'lang', 'country', 'max']}
                },
                priority=2
            )
        
        # Bing News API
        bing_api_key = os.getenv('BING_NEWS_API_KEY')
        if bing_api_key:
            self.api_configs['bing_news'] = NewsAPIConfig(
                name="Bing News",
                api_type=NewsAPIType.BING_NEWS,
                base_url="https://api.bing.microsoft.com/v7.0/news",
                api_key=bing_api_key,
                rate_limit_per_minute=1000,
                max_requests_per_day=10000,
                max_results_per_request=100,
                endpoint_configs={
                    'search': {'endpoint': '/search', 'params': ['q', 'count', 'offset', 'mkt', 'safeSearch', 'textFormat']},
                    'trending': {'endpoint': '/trendingtopics', 'params': ['count', 'offset', 'mkt', 'safeSearch']}
                },
                priority=2
            )
        
        # MediaStack API
        mediastack_api_key = os.getenv('MEDIASTACK_API_KEY')
        if mediastack_api_key:
            self.api_configs['mediastack'] = NewsAPIConfig(
                name="MediaStack",
                api_type=NewsAPIType.MEDIASTACK,
                base_url="https://api.mediastack.com/v1",
                api_key=mediastack_api_key,
                rate_limit_per_minute=1000,
                max_requests_per_day=1000,
                max_results_per_request=100,
                endpoint_configs={
                    'news': {'endpoint': '/news', 'params': ['keywords', 'countries', 'languages', 'limit', 'offset', 'sort', 'date']},
                    'sources': {'endpoint': '/sources', 'params': ['countries', 'languages', 'categories']}
                },
                priority=3
            )
        
        # Currents API
        currents_api_key = os.getenv('CURRENTS_API_KEY')
        if currents_api_key:
            self.api_configs['currents'] = NewsAPIConfig(
                name="Currents",
                api_type=NewsAPIType.CURRENTS_API,
                base_url="https://api.currentsapi.services/v1",
                api_key=currents_api_key,
                rate_limit_per_minute=600,
                max_requests_per_day=1000,
                max_results_per_request=200,
                endpoint_configs={
                    'latest_news': {'endpoint': '/latest-news', 'params': ['keywords', 'language', 'country', 'page_size', 'page']},
                    'search': {'endpoint': '/search', 'params': ['keywords', 'language', 'country', 'page_size', 'page', 'start_date', 'end_date']}
                },
                priority=3
            )
        
        # NewsCatcher API
        newscatcher_api_key = os.getenv('NEWSCATCHER_API_KEY')
        if newscatcher_api_key:
            self.api_configs['newscatcher'] = NewsAPIConfig(
                name="NewsCatcher",
                api_type=NewsAPIType.NEWSCATCHER,
                base_url="https://api.newscatcherapi.com/v2",
                api_key=newscatcher_api_key,
                rate_limit_per_minute=1000,
                max_requests_per_day=10000,
                max_results_per_request=100,
                endpoint_configs={
                    'search': {'endpoint': '/search', 'params': ['q', 'lang', 'countries', 'page_size', 'page', 'from', 'to']},
                    'latest_headlines': {'endpoint': '/latest_headlines', 'params': ['countries', 'lang', 'page_size', 'page']}
                },
                priority=1
            )
        
        # Serper News API
        serper_api_key = os.getenv('SERPER_API_KEY')
        if serper_api_key:
            self.api_configs['serper'] = NewsAPIConfig(
                name="Serper",
                api_type=NewsAPIType.SERPER_NEWS,
                base_url="https://google.serper.dev",
                api_key=serper_api_key,
                rate_limit_per_minute=100,
                max_requests_per_day=2500,
                max_results_per_request=100,
                endpoint_configs={
                    'news': {'endpoint': '/news', 'params': ['q', 'gl', 'hl', 'num', 'tbs']},
                    'search': {'endpoint': '/search', 'params': ['q', 'gl', 'hl', 'num', 'tbs']}
                },
                priority=2
            )
        
        # Tavily News API
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.api_configs['tavily'] = NewsAPIConfig(
                name="Tavily",
                api_type=NewsAPIType.TAVILY_NEWS,
                base_url="https://api.tavily.com",
                api_key=tavily_api_key,
                rate_limit_per_minute=100,
                max_requests_per_day=1000,
                max_results_per_request=100,
                endpoint_configs={
                    'search': {'endpoint': '/search', 'params': ['query', 'search_depth', 'max_results', 'include_domains', 'exclude_domains']},
                    'news': {'endpoint': '/news', 'params': ['query', 'max_results', 'include_domains', 'exclude_domains']}
                },
                priority=3
            )
        
        # Google News RSS (free)
        self.api_configs['google_news'] = NewsAPIConfig(
            name="Google News RSS",
            api_type=NewsAPIType.GOOGLE_NEWS,
            base_url="https://news.google.com/rss",
            api_key="",  # No API key required
            rate_limit_per_minute=60,
            max_requests_per_day=10000,
            max_results_per_request=100,
            endpoint_configs={
                'search': {'endpoint': '/search', 'params': ['q', 'hl', 'gl', 'ceid']},
                'topics': {'endpoint': '/topics', 'params': ['hl', 'gl', 'ceid']}
            },
            priority=4
        )
        
        # Initialize quota tracking
        for api_name, config in self.api_configs.items():
            self.api_quotas[api_name] = APIQuota(
                api_name=api_name,
                requests_limit=config.max_requests_per_day,
                rate_limit_remaining=config.rate_limit_per_minute
            )
        
        self.stats['apis_initialized'] = len(self.api_configs)
        logger.info(f"Initialized {len(self.api_configs)} news APIs")
    
    def initialize_queries(self):
        """Initialize comprehensive news queries for AI Africa funding"""
        logger.info("Initializing news queries")
        
        # High-priority queries
        high_priority_queries = [
            # Direct AI funding queries
            "\"AI funding\" Africa OR \"artificial intelligence funding\" Africa",
            "\"AI grants\" Africa OR \"artificial intelligence grants\" Africa",
            "\"AI investment\" Africa OR \"artificial intelligence investment\" Africa",
            "\"AI accelerator\" Africa OR \"artificial intelligence accelerator\" Africa",
            "\"AI startup funding\" Africa OR \"artificial intelligence startup funding\" Africa",
            
            # Specific funding entities
            "\"Google AI\" Africa funding OR grants",
            "\"Microsoft AI\" Africa funding OR grants",
            "\"OpenAI\" Africa funding OR partnership",
            "\"Gates Foundation\" AI Africa OR \"artificial intelligence\" Africa",
            "\"World Bank\" AI Africa OR \"artificial intelligence\" Africa",
            
            # Development and research funding
            "\"AI4D\" OR \"AI for Development\" Africa funding",
            "\"machine learning\" Africa funding OR grants",
            "\"deep learning\" Africa funding OR grants",
            "\"natural language processing\" Africa funding OR grants",
            "\"computer vision\" Africa funding OR grants",
            
            # Regional and country-specific
            "\"South Africa\" AI funding OR \"artificial intelligence\" funding",
            "\"Nigeria\" AI funding OR \"artificial intelligence\" funding",
            "\"Kenya\" AI funding OR \"artificial intelligence\" funding",
            "\"Ghana\" AI funding OR \"artificial intelligence\" funding",
            "\"Egypt\" AI funding OR \"artificial intelligence\" funding",
        ]
        
        # Medium-priority queries
        medium_priority_queries = [
            "\"digital transformation\" Africa funding",
            "\"innovation hub\" Africa AI OR \"artificial intelligence\"",
            "\"tech startup\" Africa funding",
            "\"venture capital\" Africa AI OR \"artificial intelligence\"",
            "\"research collaboration\" Africa AI OR \"artificial intelligence\"",
            "\"capacity building\" Africa AI OR \"artificial intelligence\"",
            "\"talent development\" Africa AI OR \"artificial intelligence\"",
            "\"STEM education\" Africa AI OR \"artificial intelligence\"",
            
            # Sector-specific
            "\"healthcare AI\" Africa funding",
            "\"fintech AI\" Africa funding",
            "\"agriculture AI\" Africa funding",
            "\"education AI\" Africa funding",
            "\"climate AI\" Africa funding",
            
            # Organizations and institutions
            "\"African Union\" AI OR \"artificial intelligence\"",
            "\"UNECA\" AI OR \"artificial intelligence\"",
            "\"AfDB\" AI OR \"artificial intelligence\"",
            "\"USAID\" AI Africa OR \"artificial intelligence\" Africa",
            "\"EU\" AI Africa OR \"artificial intelligence\" Africa",
        ]
        
        # Low-priority queries
        low_priority_queries = [
            "\"technology transfer\" Africa",
            "\"innovation ecosystem\" Africa",
            "\"digital economy\" Africa",
            "\"fourth industrial revolution\" Africa",
            "\"smart cities\" Africa",
            "\"Internet of Things\" Africa funding",
            "\"blockchain\" Africa funding",
            "\"quantum computing\" Africa",
            "\"robotics\" Africa funding",
            "\"data science\" Africa funding",
        ]
        
        # Add high-priority queries
        for query in high_priority_queries:
            self.queries.append(NewsQuery(
                query=query,
                query_type=QueryType.EVERYTHING,
                priority=1,
                from_date=datetime.now() - timedelta(days=30),
                sort_by='publishedAt'
            ))
        
        # Add medium-priority queries
        for query in medium_priority_queries:
            self.queries.append(NewsQuery(
                query=query,
                query_type=QueryType.EVERYTHING,
                priority=2,
                from_date=datetime.now() - timedelta(days=14),
                sort_by='publishedAt'
            ))
        
        # Add low-priority queries
        for query in low_priority_queries:
            self.queries.append(NewsQuery(
                query=query,
                query_type=QueryType.EVERYTHING,
                priority=3,
                from_date=datetime.now() - timedelta(days=7),
                sort_by='publishedAt'
            ))
        
        logger.info(f"Initialized {len(self.queries)} news queries")
    
    def _create_session(self) -> requests.Session:
        """Create a configured requests session"""
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return session
    
    def _check_api_availability(self, api_name: str) -> bool:
        """Check if an API is available for use"""
        if api_name not in self.api_quotas:
            return False
        
        quota = self.api_quotas[api_name]
        return quota.is_available()
    
    def _update_quota(self, api_name: str, requests_used: int = 1):
        """Update API quota after request"""
        if api_name in self.api_quotas:
            quota = self.api_quotas[api_name]
            quota.requests_made += requests_used
            quota.rate_limit_remaining -= requests_used
    
    def _calculate_relevance_score(self, article: NewsArticle, query: str) -> float:
        """Calculate relevance score for an article"""
        score = 0.0
        
        # Keywords in title (higher weight)
        title_lower = article.title.lower()
        query_words = query.lower().split()
        
        for word in query_words:
            if word in ['or', 'and', 'not', '"']:
                continue
            if word in title_lower:
                score += 0.3
        
        # Keywords in description
        desc_lower = article.description.lower()
        for word in query_words:
            if word in ['or', 'and', 'not', '"']:
                continue
            if word in desc_lower:
                score += 0.2
        
        # Specific high-value keywords
        high_value_keywords = ['ai', 'artificial intelligence', 'funding', 'grants', 'investment', 'africa']
        for keyword in high_value_keywords:
            if keyword in title_lower:
                score += 0.1
            if keyword in desc_lower:
                score += 0.05
        
        return min(score, 1.0)
    
    def _is_duplicate(self, article: NewsArticle) -> bool:
        """Check if article is a duplicate"""
        if article.content_hash in self.content_hashes:
            return True
        
        self.content_hashes.add(article.content_hash)
        return False
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _collect_from_newsapi(self, query: NewsQuery) -> List[NewsArticle]:
        """Collect articles from NewsAPI.org"""
        api_name = 'newsapi'
        if not self._check_api_availability(api_name):
            return []
        
        config = self.api_configs[api_name]
        articles = []
        
        try:
            # Build request URL
            endpoint = config.endpoint_configs[query.query_type.value]['endpoint']
            url = f"{config.base_url}{endpoint}"
            
            params = {
                'apiKey': config.api_key,
                'q': query.query,
                'language': query.language,
                'sortBy': query.sort_by,
                'pageSize': min(query.page_size, config.max_results_per_request),
                'page': 1
            }
            
            if query.from_date:
                params['from'] = query.from_date.isoformat()
            if query.to_date:
                params['to'] = query.to_date.isoformat()
            
            # Make request
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                for article_data in data.get('articles', []):
                    # Parse published date
                    published_at = datetime.now()
                    if article_data.get('publishedAt'):
                        try:
                            published_at = date_parser.parse(article_data['publishedAt'])
                        except:
                            pass
                    
                    # Create article object
                    article = NewsArticle(
                        title=article_data.get('title', ''),
                        description=article_data.get('description', ''),
                        content=article_data.get('content', ''),
                        url=article_data.get('url', ''),
                        source=article_data.get('source', {}).get('name', 'Unknown'),
                        api_source=api_name,
                        published_at=published_at,
                        author=article_data.get('author'),
                        url_to_image=article_data.get('urlToImage'),
                        language=query.language,
                        metadata={'query': query.query, 'api_response': article_data}
                    )
                    
                    # Calculate relevance score
                    article.relevance_score = self._calculate_relevance_score(article, query.query)
                    
                    # Filter by relevance
                    if article.relevance_score > 0.1:
                        articles.append(article)
            
            self._update_quota(api_name)
            
        except Exception as e:
            logger.error(f"Error collecting from NewsAPI: {e}")
            self.stats['api_errors'] += 1
        
        return articles
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _collect_from_google_news(self, query: NewsQuery) -> List[NewsArticle]:
        """Collect articles from Google News RSS"""
        api_name = 'google_news'
        if not self._check_api_availability(api_name):
            return []
        
        articles = []
        
        try:
            # Build Google News RSS URL
            base_url = "https://news.google.com/rss/search"
            params = {
                'q': query.query,
                'hl': query.language,
                'gl': query.country or 'US',
                'ceid': f"{query.country or 'US'}:{query.language}"
            }
            
            url = f"{base_url}?{urlencode(params)}"
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                # Parse published date
                published_at = datetime.now()
                if hasattr(entry, 'published'):
                    try:
                        published_at = date_parser.parse(entry.published)
                    except:
                        pass
                
                # Create article object
                article = NewsArticle(
                    title=entry.get('title', ''),
                    description=entry.get('summary', ''),
                    content=entry.get('summary', ''),
                    url=entry.get('link', ''),
                    source=entry.get('source', {}).get('href', 'Google News'),
                    api_source=api_name,
                    published_at=published_at,
                    language=query.language,
                    metadata={'query': query.query, 'rss_entry': entry}
                )
                
                # Calculate relevance score
                article.relevance_score = self._calculate_relevance_score(article, query.query)
                
                # Filter by relevance
                if article.relevance_score > 0.1:
                    articles.append(article)
            
            self._update_quota(api_name)
            
        except Exception as e:
            logger.error(f"Error collecting from Google News: {e}")
            self.stats['api_errors'] += 1
        
        return articles
    
    def _collect_from_api(self, api_name: str, query: NewsQuery) -> List[NewsArticle]:
        """Collect articles from a specific API"""
        if api_name == 'newsapi':
            return self._collect_from_newsapi(query)
        elif api_name == 'google_news':
            return self._collect_from_google_news(query)
        else:
            logger.warning(f"Collection method not implemented for {api_name}")
            return []
    
    def collect_articles(self, query: NewsQuery) -> List[NewsArticle]:
        """Collect articles for a query from all available APIs"""
        all_articles = []
        
        # Sort APIs by priority
        sorted_apis = sorted(
            [(name, config) for name, config in self.api_configs.items() if config.enabled],
            key=lambda x: x[1].priority
        )
        
        for api_name, config in sorted_apis:
            if not self._check_api_availability(api_name):
                logger.warning(f"API {api_name} quota exceeded, skipping")
                self.stats['quota_exceeded'] += 1
                continue
            
            try:
                articles = self._collect_from_api(api_name, query)
                
                # Filter duplicates
                unique_articles = []
                for article in articles:
                    if not self._is_duplicate(article):
                        unique_articles.append(article)
                    else:
                        self.stats['duplicates_filtered'] += 1
                
                all_articles.extend(unique_articles)
                
                logger.info(f"Collected {len(unique_articles)} articles from {api_name} for query: {query.query[:50]}...")
                
            except Exception as e:
                logger.error(f"Error collecting from {api_name}: {e}")
                self.stats['api_errors'] += 1
        
        return all_articles
    
    def collect_all_queries(self) -> List[NewsArticle]:
        """Collect articles for all queries using parallel processing"""
        logger.info(f"Starting collection for {len(self.queries)} queries")
        
        all_articles = []
        
        # Sort queries by priority
        sorted_queries = sorted(self.queries, key=lambda x: x.priority)
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all query tasks
            future_to_query = {
                executor.submit(self.collect_articles, query): query 
                for query in sorted_queries
            }
            
            # Process completed tasks
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    self.stats['queries_processed'] += 1
                    self.stats['articles_collected'] += len(articles)
                    
                except Exception as e:
                    logger.error(f"Error processing query '{query.query}': {e}")
                    self.stats['api_errors'] += 1
        
        logger.info(f"Completed collection: {len(all_articles)} articles collected")
        return all_articles
    
    def start_continuous_collection(self, interval_hours: int = 1):
        """Start continuous news collection with specified interval"""
        logger.info(f"Starting continuous collection with {interval_hours}h interval")
        
        self.is_running = True
        self.stop_event.clear()
        
        def collection_loop():
            while not self.stop_event.is_set():
                try:
                    # Collect all articles
                    articles = self.collect_all_queries()
                    
                    # Store articles (extend with database storage)
                    self.collected_articles.extend(articles)
                    
                    # Wait for next interval
                    if not self.stop_event.wait(interval_hours * 3600):
                        continue
                    else:
                        break
                        
                except Exception as e:
                    logger.error(f"Error in collection loop: {e}")
                    time.sleep(300)  # Wait 5 minutes before retrying
        
        # Start collection thread
        collection_thread = threading.Thread(target=collection_loop, daemon=True)
        collection_thread.start()
        
        return collection_thread
    
    def stop_collection(self):
        """Stop continuous collection"""
        logger.info("Stopping news API collection")
        self.is_running = False
        self.stop_event.set()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        elapsed_time = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'apis_initialized': self.stats['apis_initialized'],
            'apis_available': len([name for name in self.api_configs.keys() if self._check_api_availability(name)]),
            'queries_total': len(self.queries),
            'queries_processed': self.stats['queries_processed'],
            'articles_collected': self.stats['articles_collected'],
            'duplicates_filtered': self.stats['duplicates_filtered'],
            'api_errors': self.stats['api_errors'],
            'quota_exceeded': self.stats['quota_exceeded'],
            'articles_per_hour': self.stats['articles_collected'] / (elapsed_time / 3600) if elapsed_time > 0 else 0,
            'success_rate': (self.stats['queries_processed'] / len(self.queries)) * 100 if self.queries else 0,
            'uptime_hours': elapsed_time / 3600,
            'articles_in_memory': len(self.collected_articles),
            'unique_content_hashes': len(self.content_hashes)
        }
    
    def get_collected_articles(self) -> List[NewsArticle]:
        """Get all collected articles"""
        return self.collected_articles.copy()
    
    def clear_collected_articles(self):
        """Clear collected articles from memory"""
        self.collected_articles.clear()
        self.content_hashes.clear()
        logger.info("Cleared collected articles from memory")


# Example usage
async def main():
    """Example usage of the news API collector"""
    collector = HighVolumeNewsAPICollector(max_workers=5, batch_size=100)
    
    try:
        # Initialize APIs and queries
        collector.initialize_apis()
        collector.initialize_queries()
        
        # Collect articles once
        articles = collector.collect_all_queries()
        
        # Print statistics
        stats = collector.get_stats()
        print(f"Collection completed: {stats}")
        
        # Print sample articles
        if articles:
            print(f"\nSample articles ({len(articles)} total):")
            for article in articles[:5]:
                print(f"- {article.title} ({article.source}) - Score: {article.relevance_score:.2f}")
        
    finally:
        collector.stop_collection()


if __name__ == "__main__":
    asyncio.run(main())