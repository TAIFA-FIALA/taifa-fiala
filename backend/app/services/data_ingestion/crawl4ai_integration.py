"""
Crawl4AI Integration for High-Volume Data Ingestion Pipeline
Integrates the existing sophisticated Crawl4AI web scraper with the new high-volume approach

This module provides:
- Integration with existing UnifiedScraperModule
- High-volume batch processing capabilities
- Advanced LLM-based content extraction
- Intelligent content classification and validation
- Seamless integration with the master pipeline

Strategy:
1. Leverage existing sophisticated LLM extraction
2. Add high-volume batch processing capabilities
3. Integrate with new monitoring and quality systems
4. Maintain backward compatibility with existing admin portal
5. Scale for 10K-100M records processing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from contextlib import asynccontextmanager

# Import existing components
from app.core.integrated_ingestion_pipeline import IntegratedIngestionPipeline, IngestionMethod, IngestionContext

# Import new pipeline components
from .monitoring_system import ComprehensiveMonitoringSystem, MetricType
from .batch_processor import BatchTask, DataSource, BatchStatus

# Crawl4AI imports
from crawl4ai import AsyncWebCrawler, LLMExtractionStrategy, CrawlerRunConfig, CacheMode

logger = logging.getLogger(__name__)


class Crawl4AIMode(Enum):
    """Different modes for Crawl4AI operation"""
    ADMIN_PORTAL = "admin_portal"          # Existing admin portal integration
    HIGH_VOLUME_BATCH = "high_volume_batch"  # New high-volume batch processing
    SCHEDULED_MONITORING = "scheduled_monitoring"  # Automated monitoring of sources
    TARGETED_EXTRACTION = "targeted_extraction"    # Targeted extraction for specific sources


@dataclass
class Crawl4AIConfig:
    """Configuration for Crawl4AI integration"""
    # Crawl4AI settings
    browser_type: str = "chromium"
    headless: bool = True
    max_concurrent_crawlers: int = 5
    request_timeout: int = 30
    page_timeout: int = 60
    
    # LLM settings
    llm_provider: str = "openai/gpt-4o-mini"
    llm_api_key: str = ""
    extraction_temperature: float = 0.1
    
    # Batch processing settings
    batch_size: int = 50
    max_workers: int = 10
    retry_attempts: int = 3
    rate_limit_delay: float = 2.0
    
    # Content filtering
    min_content_length: int = 100
    max_content_length: int = 50000
    relevance_threshold: float = 0.7
    
    # Quality control
    enable_content_validation: bool = True
    enable_duplicate_detection: bool = True
    enable_bias_monitoring: bool = True


@dataclass
class CrawlTarget:
    """Target for Crawl4AI processing"""
    url: str
    target_type: str  # 'funding_database', 'news_site', 'org_website', 'search_result'
    priority: int = 1
    extraction_strategy: str = "intelligence_item"
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_crawled: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    enabled: bool = True


class EnhancedCrawl4AIProcessor:
    """
    Enhanced Crawl4AI processor that integrates with high-volume pipeline
    Combines existing sophisticated extraction with new scalability features
    """
    
    def __init__(self, config: Crawl4AIConfig, monitoring_system: ComprehensiveMonitoringSystem, settings):
        self.config = config
        self.monitoring_system = monitoring_system
        self.settings = settings
        
        # Initialize existing components
        self.unified_scraper = None
        self.integrated_pipeline = None  # Will be initialized later
        
        # Crawler pool management
        self.crawler_pool: List[AsyncWebCrawler] = []
        self.crawler_semaphore = asyncio.Semaphore(config.max_concurrent_crawlers)
        
        # Target management
        self.crawl_targets: List[CrawlTarget] = []
        self.target_queue = asyncio.Queue()
        
        # Processing statistics
        self.stats = {
            'total_targets_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'content_items_extracted': 0,
            'duplicates_filtered': 0,
            'high_quality_items': 0,
            'processing_time_total': 0.0,
            'average_processing_time': 0.0
        }
        
        # Control
        self.is_running = False
        self.stop_event = asyncio.Event()
        
        # Initialize extraction strategies
        self._initialize_extraction_strategies()
    
    def _initialize_extraction_strategies(self):
        """Initialize different extraction strategies for different content types"""
        self.extraction_strategies = {
            'intelligence_item': LLMExtractionStrategy(
                llm_config=LLMConfig(
                    provider=self.config.llm_provider,
                    api_token=self.config.llm_api_key
                ),
                instruction="""
                Extract comprehensive intelligence item information from this webpage.
                
                Look for and extract:
                1. FUNDING DETAILS:
                   - Program/grant title and names
                   - Funding amounts and currencies
                   - Application deadlines (convert to ISO format)
                   - Funding stages (seed, early, growth, etc.)
                   - Geographic scope and focus areas
                
                2. ORGANIZATION INFORMATION:
                   - Funding organization name
                   - Organization type (foundation, government, private, etc.)
                   - Contact information (email, phone, address)
                   - Website URLs (separate from current page)
                
                3. OPPORTUNITY DETAILS:
                   - Detailed description of the opportunity
                   - Eligibility criteria and requirements
                   - Application process and requirements
                   - Target sectors (AI, healthcare, education, etc.)
                   - Target regions (Africa focus preferred)
                
                4. AI/TECH RELEVANCE:
                   - AI/technology focus indicators
                   - Innovation requirements
                   - Digital transformation aspects
                   - Technical requirements
                
                5. EQUITY AND INCLUSION:
                   - Diversity and inclusion requirements
                   - Women/minority-focused programs
                   - Accessibility requirements
                   - Local community impact requirements
                
                Return as JSON array with fields:
                {
                    "title": "string",
                    "organization_name": "string",
                    "organization_type": "string",
                    "description": "string",
                    "funding_amount": "string",
                    "currency": "string",
                    "deadline": "ISO date string",
                    "funding_stage": "string",
                    "geographic_scope": "string",
                    "eligibility_criteria": "string",
                    "application_process": "string",
                    "target_sectors": ["array of strings"],
                    "ai_tech_relevance": "string",
                    "equity_inclusion_focus": "string",
                    "contact_email": "string",
                    "contact_phone": "string",
                    "organization_website": "string",
                    "application_url": "string",
                    "source_quality_indicators": ["array of strings"]
                }
                
                IMPORTANT: Only extract real intelligence feed, not general information.
                """,
                schema=None,
                extraction_type="json"
            ),
            
            'news_article': LLMExtractionStrategy(
                llm_config=LLMConfig(
                    provider=self.config.llm_provider,
                    api_token=self.config.llm_api_key
                ),
                instruction="""
                Extract news article information related to AI funding in Africa.
                
                Look for:
                - Article headline and summary
                - Funding announcements and amounts
                - AI/technology companies mentioned
                - Investment details and investors
                - Geographic focus (Africa preferred)
                - Publication date and source
                
                Return as JSON with fields:
                {
                    "headline": "string",
                    "summary": "string",
                    "funding_announcements": ["array of objects"],
                    "companies_mentioned": ["array of strings"],
                    "investors_mentioned": ["array of strings"],
                    "funding_amounts": ["array of strings"],
                    "geographic_focus": ["array of strings"],
                    "ai_tech_focus": "string",
                    "publication_date": "ISO date string",
                    "source_credibility": "string"
                }
                """,
                schema=None,
                extraction_type="json"
            ),
            
            'organization_profile': LLMExtractionStrategy(
                llm_config=LLMConfig(
                    provider=self.config.llm_provider,
                    api_token=self.config.llm_api_key
                ),
                instruction="""
                Extract organization profile information for potential funding sources.
                
                Look for:
                - Organization name and type
                - Mission and focus areas
                - Funding programs and initiatives
                - Geographic focus
                - Contact information
                - Historical funding patterns
                
                Return as JSON with comprehensive organization data.
                """,
                schema=None,
                extraction_type="json"
            )
        }
    
    async def initialize(self):
        """Initialize the Crawl4AI processor"""
        logger.info("Initializing Enhanced Crawl4AI Processor")
        
        try:
            # Initialize unified scraper
            
            # Initialize crawler pool
            await self._initialize_crawler_pool()
            
            # Initialize integrated pipeline if available
            try:
                from app.core.vector_database import VectorDatabaseManager
                from app.core.multilingual_search import MultilingualSearchEngine
                
                # These would need to be configured based on your environment
                # For now, we'll skip integrated pipeline initialization
                logger.info("Integrated pipeline initialization skipped - configure as needed")
            except ImportError:
                logger.warning("Integrated pipeline components not available")
            
            # Initialize default targets
            await self._initialize_default_targets()
            
            logger.info("Enhanced Crawl4AI Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Crawl4AI Processor: {e}")
            raise
    
    async def _initialize_crawler_pool(self):
        """Initialize pool of AsyncWebCrawler instances"""
        for i in range(self.config.max_concurrent_crawlers):
            crawler = AsyncWebCrawler(
                headless=self.config.headless,
                browser_type=self.config.browser_type,
                verbose=False
            )
            await crawler.start()
            self.crawler_pool.append(crawler)
        
        logger.info(f"Initialized {len(self.crawler_pool)} crawler instances")
    
    async def _initialize_default_targets(self):
        """Initialize default high-priority targets for AI funding"""
        default_targets = [
            # Major funding databases
            CrawlTarget(
                url="https://grantsdatabase.org/category/africa/",
                target_type="funding_database",
                priority=1,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Grants Database - Africa'}
            ),
            CrawlTarget(
                url="https://www.grants.gov/search-grants.html",
                target_type="funding_database",
                priority=2,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Grants.gov'}
            ),
            
            # Major foundation websites
            CrawlTarget(
                url="https://www.gatesfoundation.org/how-we-work/quick-links/grants-database",
                target_type="org_website",
                priority=1,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Gates Foundation'}
            ),
            CrawlTarget(
                url="https://www.mozillafoundation.org/en/what-we-fund/",
                target_type="org_website",
                priority=2,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Mozilla Foundation'}
            ),
            
            # African funding sources
            CrawlTarget(
                url="https://www.afdb.org/en/topics-and-sectors/initiatives-partnerships/",
                target_type="org_website",
                priority=1,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'African Development Bank'}
            ),
            CrawlTarget(
                url="https://www.mastercardfdn.org/what-we-do/",
                target_type="org_website",
                priority=1,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Mastercard Foundation'}
            ),
            
            # Technology/AI focused sources
            CrawlTarget(
                url="https://ai.google/commitments/",
                target_type="org_website",
                priority=2,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Google AI'}
            ),
            CrawlTarget(
                url="https://www.microsoft.com/en-us/corporate-responsibility/",
                target_type="org_website",
                priority=2,
                extraction_strategy="intelligence_item",
                metadata={'source_name': 'Microsoft'}
            )
        ]
        
        self.crawl_targets.extend(default_targets)
        logger.info(f"Added {len(default_targets)} default crawl targets")
    
    @asynccontextmanager
    async def get_crawler(self):
        """Get a crawler from the pool"""
        async with self.crawler_semaphore:
            if self.crawler_pool:
                crawler = self.crawler_pool.pop(0)
                try:
                    yield crawler
                finally:
                    self.crawler_pool.append(crawler)
            else:
                # Create temporary crawler if pool is empty
                temp_crawler = AsyncWebCrawler(
                    headless=self.config.headless,
                    browser_type=self.config.browser_type,
                    verbose=False
                )
                await temp_crawler.start()
                try:
                    yield temp_crawler
                finally:
                    await temp_crawler.close()
    
    async def process_admin_portal_request(self, url: str, source_type: str = "unknown") -> Dict[str, Any]:
        """
        Process admin portal request using existing unified scraper
        Maintains backward compatibility with existing admin portal
        """
        try:
            # Record metrics
            self.monitoring_system.record_metric(
                'crawl4ai_admin_requests',
                1,
                MetricType.COUNTER,
                {'source_type': source_type}
            )
            
            # Use existing unified scraper
            input_data = {
                "source": InputSource.ADMIN_PORTAL.value,
                "data": {
                    "url": url,
                    "source_type": source_type
                },
                "priority": ProcessingPriority.HIGH.value
            }
            
            result = await self.unified_scraper.process_input(input_data)
            
            # Record success/failure metrics
            if result.get("status") == "success":
                self.monitoring_system.record_metric(
                    'crawl4ai_admin_success_rate',
                    1,
                    MetricType.GAUGE,
                    {'source_type': source_type}
                )
                self.stats['successful_extractions'] += 1
                self.stats['content_items_extracted'] += result.get('opportunities_found', 0)
            else:
                self.monitoring_system.record_metric(
                    'crawl4ai_admin_error_rate',
                    1,
                    MetricType.GAUGE,
                    {'source_type': source_type}
                )
                self.stats['failed_extractions'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Admin portal processing failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            return {
                "status": "error",
                "error": str(e),
                "source": "admin_portal"
            }
    
    async def process_high_volume_batch(self, targets: List[CrawlTarget]) -> List[Dict[str, Any]]:
        """
        Process high-volume batch of targets
        New capability for scaling to 10K-100M records
        """
        logger.info(f"Processing high-volume batch of {len(targets)} targets")
        
        all_results = []
        batch_start_time = time.time()
        
        try:
            # Process in chunks to manage memory and resources
            chunk_size = self.config.batch_size
            
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i + chunk_size]
                
                # Process chunk concurrently
                chunk_tasks = [
                    self._process_single_target(target) 
                    for target in chunk
                ]
                
                chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
                
                # Filter successful results
                for result in chunk_results:
                    if isinstance(result, Exception):
                        logger.error(f"Chunk processing error: {result}")
                        self.stats['failed_extractions'] += 1
                        continue
                    
                    if result and result.get('status') == 'success':
                        all_results.extend(result.get('opportunities', []))
                        self.stats['successful_extractions'] += 1
                        self.stats['content_items_extracted'] += len(result.get('opportunities', []))
                
                # Rate limiting between chunks
                await asyncio.sleep(self.config.rate_limit_delay)
                
                # Record progress
                self.monitoring_system.record_metric(
                    'crawl4ai_batch_progress',
                    (i + len(chunk)) / len(targets) * 100,
                    MetricType.GAUGE,
                    {'batch_id': f"batch_{int(time.time())}"}
                )
            
            # Calculate batch statistics
            batch_time = time.time() - batch_start_time
            self.stats['processing_time_total'] += batch_time
            self.stats['total_targets_processed'] += len(targets)
            
            if self.stats['total_targets_processed'] > 0:
                self.stats['average_processing_time'] = (
                    self.stats['processing_time_total'] / self.stats['total_targets_processed']
                )
            
            # Record batch metrics
            self.monitoring_system.record_metric(
                'crawl4ai_batch_size',
                len(targets),
                MetricType.GAUGE,
                {'batch_type': 'high_volume'}
            )
            
            self.monitoring_system.record_metric(
                'crawl4ai_batch_time',
                batch_time,
                MetricType.GAUGE,
                {'batch_type': 'high_volume'}
            )
            
            self.monitoring_system.record_metric(
                'crawl4ai_items_per_second',
                len(all_results) / batch_time if batch_time > 0 else 0,
                MetricType.GAUGE,
                {'batch_type': 'high_volume'}
            )
            
            logger.info(f"Batch processing completed: {len(all_results)} items extracted in {batch_time:.2f}s")
            
            return all_results
            
        except Exception as e:
            logger.error(f"High-volume batch processing failed: {e}")
            return []
    
    async def _process_single_target(self, target: CrawlTarget) -> Dict[str, Any]:
        """Process a single crawl target"""
        try:
            start_time = time.time()
            
            # Get extraction strategy
            extraction_strategy = self.extraction_strategies.get(
                target.extraction_strategy, 
                self.extraction_strategies['intelligence_item']
            )
            
            # Create crawler config
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=extraction_strategy,
                word_count_threshold=self.config.min_content_length,
                only_text=False,
                bypass_cache=True
            )
            
            # Get crawler from pool and process
            async with self.get_crawler() as crawler:
                result = await crawler.arun(url=target.url, config=crawler_config)
                
                if not result or not result.extracted_content:
                    target.error_count += 1
                    return {
                        'status': 'no_content',
                        'target': target.url,
                        'error': 'No content extracted'
                    }
                
                # Parse extracted content
                opportunities = await self._parse_extracted_content(
                    result.extracted_content, 
                    target
                )
                
                # Filter for quality and relevance
                filtered_opportunities = await self._filter_opportunities(
                    opportunities, 
                    target
                )
                
                # Update target statistics
                target.success_count += len(filtered_opportunities)
                target.last_crawled = datetime.now()
                
                processing_time = time.time() - start_time
                
                return {
                    'status': 'success',
                    'target': target.url,
                    'opportunities': filtered_opportunities,
                    'processing_time': processing_time,
                    'raw_count': len(opportunities),
                    'filtered_count': len(filtered_opportunities)
                }
                
        except Exception as e:
            logger.error(f"Target processing failed for {target.url}: {e}")
            target.error_count += 1
            return {
                'status': 'error',
                'target': target.url,
                'error': str(e)
            }
    
    async def _parse_extracted_content(self, content: str, target: CrawlTarget) -> List[Dict[str, Any]]:
        """Parse extracted content into structured opportunities"""
        try:
            # Try to parse as JSON
            if content.strip().startswith('{') or content.strip().startswith('['):
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    opportunities = parsed
                else:
                    opportunities = [parsed]
            else:
                # Fallback: create single opportunity from text
                opportunities = [{
                    'title': f"Content from {target.url}",
                    'description': content[:2000],  # Truncate long content
                    'source_url': target.url,
                    'extracted_content': content
                }]
            
            # Standardize and enrich
            standardized = []
            for opp in opportunities:
                if not opp.get('title'):
                    continue
                
                standardized_opp = {
                    'title': opp.get('title', ''),
                    'organization_name': opp.get('organization_name', target.metadata.get('source_name', 'Unknown')),
                    'description': opp.get('description', ''),
                    'funding_amount': opp.get('funding_amount'),
                    'currency': opp.get('currency', 'USD'),
                    'deadline': opp.get('deadline'),
                    'geographic_scope': opp.get('geographic_scope'),
                    'eligibility_criteria': opp.get('eligibility_criteria'),
                    'target_sectors': opp.get('target_sectors', []),
                    'ai_tech_relevance': opp.get('ai_tech_relevance'),
                    'equity_inclusion_focus': opp.get('equity_inclusion_focus'),
                    'source_url': target.url,
                    'application_url': opp.get('application_url'),
                    'contact_email': opp.get('contact_email'),
                    'source_type': 'crawl4ai_extraction',
                    'extraction_strategy': target.extraction_strategy,
                    'crawl_metadata': {
                        'target_type': target.target_type,
                        'extraction_timestamp': datetime.now().isoformat(),
                        'source_priority': target.priority,
                        'target_metadata': target.metadata
                    }
                }
                standardized.append(standardized_opp)
            
            return standardized
            
        except Exception as e:
            logger.error(f"Content parsing failed for {target.url}: {e}")
            return []
    
    async def _filter_opportunities(self, opportunities: List[Dict[str, Any]], 
                                  target: CrawlTarget) -> List[Dict[str, Any]]:
        """Filter opportunities for quality and relevance"""
        filtered = []
        
        for opp in opportunities:
            # Basic quality checks
            if not opp.get('title') or len(opp.get('title', '')) < 10:
                continue
            
            if not opp.get('description') or len(opp.get('description', '')) < 50:
                continue
            
            # Relevance scoring
            relevance_score = self._calculate_relevance_score(opp)
            
            if relevance_score >= self.config.relevance_threshold:
                opp['relevance_score'] = relevance_score
                filtered.append(opp)
                self.stats['high_quality_items'] += 1
        
        return filtered
    
    def _calculate_relevance_score(self, opportunity: Dict[str, Any]) -> float:
        """Calculate objective relevance score based on measurable criteria"""
        score = 0.0
        
        title = opportunity.get('title', '').lower()
        description = opportunity.get('description', '').lower()
        full_text = f"{title} {description}"
        
        # 1. Geographic Relevance (0.0 - 0.25)
        score += self._score_geographic_relevance(full_text)
        
        # 2. Technology Relevance (0.0 - 0.30)
        score += self._score_technology_relevance(full_text)
        
        # 3. Funding Specificity & Disbursement Clarity (0.0 - 0.35)
        score += self._score_funding_specificity(opportunity, full_text)
        
        # 4. Urgency & Actionability (0.0 - 0.10)
        score += self._score_urgency_actionability(opportunity)
        
        return min(score, 1.0)
    
    def _score_geographic_relevance(self, full_text: str) -> float:
        """Score geographic relevance to Africa"""
        african_countries = [
            'africa', 'african', 'ghana', 'nigeria', 'south africa', 'kenya', 'uganda',
            'ethiopia', 'tanzania', 'morocco', 'egypt', 'senegal', 'rwanda', 'botswana',
            'zambia', 'zimbabwe', 'mali', 'burkina faso', 'ivory coast', 'cameroon'
        ]
        
        developing_terms = ['developing countries', 'global south', 'emerging markets']
        international_terms = ['international', 'worldwide', 'global']
        exclusion_terms = ['us only', 'usa only', 'american residents', 'eu only', 'europe only']
        
        # Check for exclusions first
        for term in exclusion_terms:
            if term in full_text:
                return 0.0
        
        # Check for African countries/regions
        for country in african_countries:
            if country in full_text:
                return 0.25
        
        # Check for developing country terms
        for term in developing_terms:
            if term in full_text:
                return 0.15
        
        # Check for international terms
        for term in international_terms:
            if term in full_text:
                return 0.10
        
        # Default: no geographic restrictions mentioned
        return 0.05
    
    def _score_technology_relevance(self, full_text: str) -> float:
        """Score technology relevance to AI/tech"""
        ai_title_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml']
        ai_desc_keywords = ['neural network', 'deep learning', 'algorithm', 'data science']
        tech_keywords = ['digital', 'innovation', 'technology', 'tech']
        adjacent_tech = ['automation', 'robotics', 'data analytics', 'software']
        research_terms = ['research', 'innovation', 'development']
        
        # AI/ML in title gets highest score
        title_part = full_text.split(' ')[:10]  # First 10 words approximate title
        title_text = ' '.join(title_part)
        
        for keyword in ai_title_keywords:
            if keyword in title_text:
                return 0.30
        
        # AI/ML in description with tech keywords
        ai_in_desc = any(keyword in full_text for keyword in ai_title_keywords + ai_desc_keywords)
        tech_in_desc = any(keyword in full_text for keyword in tech_keywords)
        
        if ai_in_desc and tech_in_desc:
            return 0.25
        
        # General tech keywords
        if any(keyword in full_text for keyword in tech_keywords):
            return 0.20
        
        # Adjacent tech fields
        if any(keyword in full_text for keyword in adjacent_tech):
            return 0.15
        
        # Broad research/innovation focus
        if any(keyword in full_text for keyword in research_terms):
            return 0.10
        
        return 0.0
    
    def _score_funding_specificity(self, opportunity: Dict[str, Any], full_text: str) -> float:
        """Score funding specificity and disbursement clarity"""
        score = 0.0
        
        # Disbursement Language (0.0 - 0.15)
        active_disbursement = [
            'accepting applications', 'now open', 'apply by', 'grants awarded',
            'applications due', 'submit proposal', 'deadline', 'apply now'
        ]
        present_funding = [
            'offers grants', 'provides funding', 'supports', 'funds',
            'available', 'open for', 'invites applications'
        ]
        future_conditional = [
            'will fund', 'plans to support', 'intends to', 'aims to provide',
            'expects to', 'looking to fund'
        ]
        vague_allocation = [
            'allocated', 'committed', 'announced', 'pledged', 'set aside'
        ]
        
        if any(term in full_text for term in active_disbursement):
            score += 0.15
        elif any(term in full_text for term in present_funding):
            score += 0.10
        elif any(term in full_text for term in future_conditional):
            score += 0.05
        elif any(term in full_text for term in vague_allocation):
            score += 0.00
        
        # Amount Specificity (0.0 - 0.10)
        funding_amount = opportunity.get('funding_amount', '')
        if funding_amount:
            amount_text = str(funding_amount).lower()
            if 'per project' in amount_text or 'per grant' in amount_text or 'individual' in amount_text:
                score += 0.10
            elif '-' in amount_text and ('grant' in amount_text or 'award' in amount_text):
                score += 0.08
            elif any(word in full_text for word in ['total', 'grants', 'recipients']):
                score += 0.05
            elif any(char.isdigit() for char in amount_text):
                score += 0.02
        
        # Application Process Clarity (0.0 - 0.10)
        clarity_score = 0.0
        if opportunity.get('application_url'):
            clarity_score += 0.025
        if opportunity.get('application_deadline') or opportunity.get('deadline'):
            clarity_score += 0.025
        if opportunity.get('eligibility_criteria'):
            clarity_score += 0.025
        if opportunity.get('contact_email') or opportunity.get('contact_info'):
            clarity_score += 0.025
        
        score += clarity_score
        
        return score
    
    def _score_urgency_actionability(self, opportunity: Dict[str, Any]) -> float:
        """Score urgency and actionability based on deadlines"""
        from datetime import datetime, timedelta
        
        deadline_field = opportunity.get('application_deadline') or opportunity.get('deadline')
        if not deadline_field:
            # Check for rolling/ongoing applications
            description = opportunity.get('description', '').lower()
            if any(term in description for term in ['rolling', 'ongoing', 'continuous']):
                return 0.02
            return 0.0
        
        try:
            # Try to parse deadline (this would need more robust date parsing in production)
            deadline_str = str(deadline_field).lower()
            current_date = datetime.now()
            
            # Simple heuristic - look for month names and years
            # In production, you'd want more sophisticated date parsing
            if any(month in deadline_str for month in ['january', 'february', 'march']):
                # Rough estimate - within 3 months
                return 0.10
            elif any(month in deadline_str for month in ['april', 'may', 'june']):
                # Rough estimate - within 6 months  
                return 0.08
            elif '2024' in deadline_str or '2025' in deadline_str:
                # Within a year
                return 0.05
            
        except Exception:
            pass
        
        return 0.02  # Default for having a deadline but unable to parse
    
    async def start_scheduled_monitoring(self, interval_hours: int = 12):
        """Start scheduled monitoring of crawl targets"""
        logger.info(f"Starting scheduled monitoring every {interval_hours} hours")
        
        self.is_running = True
        
        async def monitoring_loop():
            while not self.stop_event.is_set():
                try:
                    # Process all enabled targets
                    enabled_targets = [t for t in self.crawl_targets if t.enabled]
                    
                    if enabled_targets:
                        results = await self.process_high_volume_batch(enabled_targets)
                        
                        logger.info(f"Scheduled monitoring completed: {len(results)} opportunities extracted")
                        
                        # Record monitoring metrics
                        self.monitoring_system.record_metric(
                            'crawl4ai_scheduled_run',
                            1,
                            MetricType.COUNTER,
                            {'interval_hours': str(interval_hours)}
                        )
                        
                        self.monitoring_system.record_metric(
                            'crawl4ai_scheduled_opportunities',
                            len(results),
                            MetricType.GAUGE,
                            {'interval_hours': str(interval_hours)}
                        )
                    
                    # Wait for next interval
                    await asyncio.sleep(interval_hours * 3600)
                    
                except Exception as e:
                    logger.error(f"Scheduled monitoring error: {e}")
                    await asyncio.sleep(1800)  # Wait 30 minutes before retry
        
        # Start monitoring task
        asyncio.create_task(monitoring_loop())
    
    def stop_scheduled_monitoring(self):
        """Stop scheduled monitoring"""
        logger.info("Stopping scheduled monitoring")
        self.is_running = False
        self.stop_event.set()
    
    def add_crawl_target(self, target: CrawlTarget):
        """Add a new crawl target"""
        self.crawl_targets.append(target)
        logger.info(f"Added crawl target: {target.url}")
    
    def remove_crawl_target(self, url: str):
        """Remove a crawl target"""
        self.crawl_targets = [t for t in self.crawl_targets if t.url != url]
        logger.info(f"Removed crawl target: {url}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            'total_targets': len(self.crawl_targets),
            'enabled_targets': len([t for t in self.crawl_targets if t.enabled]),
            'crawler_pool_size': len(self.crawler_pool),
            'is_running': self.is_running,
            'timestamp': datetime.now().isoformat()
        }
    
    async def close(self):
        """Clean up resources"""
        logger.info("Closing Enhanced Crawl4AI Processor")
        
        # Stop monitoring
        self.stop_scheduled_monitoring()
        
        # Close unified scraper
        if self.unified_scraper:
            await self.unified_scraper.close()
        
        # Close crawler pool
        for crawler in self.crawler_pool:
            try:
                await crawler.close()
            except Exception as e:
                logger.warning(f"Error closing crawler: {e}")
        
        self.crawler_pool.clear()
        
        logger.info("Enhanced Crawl4AI Processor closed")


# Integration with master pipeline
class Crawl4AIMasterPipelineIntegration:
    """Integration class for connecting Crawl4AI with master pipeline"""
    
    def __init__(self, master_pipeline, crawl4ai_processor: EnhancedCrawl4AIProcessor):
        self.master_pipeline = master_pipeline
        self.crawl4ai_processor = crawl4ai_processor
    
    async def create_crawl4ai_batch_task(self, targets: List[CrawlTarget]) -> BatchTask:
        """Create a batch task for Crawl4AI processing"""
        return BatchTask(
            task_id=f"crawl4ai_batch_{int(time.time())}",
            data_source=DataSource.API,
            source_config={
                'processor': 'crawl4ai',
                'targets': [t.__dict__ for t in targets]
            },
            processor_func=self._process_crawl4ai_batch,
            batch_size=len(targets),
            priority=1
        )
    
    async def _process_crawl4ai_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process Crawl4AI batch for master pipeline"""
        try:
            # Extract targets from batch data
            targets = [
                CrawlTarget(**target_data) 
                for target_data in batch_data[0].get('targets', [])
            ]
            
            # Process with Crawl4AI
            results = await self.crawl4ai_processor.process_high_volume_batch(targets)
            
            return [{'success': True, 'opportunities': results}]
            
        except Exception as e:
            logger.error(f"Crawl4AI batch processing failed: {e}")
            return [{'success': False, 'error': str(e)}]


# Usage example
async def main():
    """Example usage of Enhanced Crawl4AI Processor"""
    
    # Create configuration
    config = Crawl4AIConfig(
        max_concurrent_crawlers=5,
        batch_size=50,
        max_workers=10,
        llm_api_key="your-openai-api-key",
        relevance_threshold=0.7
    )
    
    # Create monitoring system (would be shared with master pipeline)
    from .monitoring_system import MonitoringConfig
    monitoring_config = MonitoringConfig()
    monitoring_system = ComprehensiveMonitoringSystem(monitoring_config)
    
    # Create enhanced processor
    processor = EnhancedCrawl4AIProcessor(config, monitoring_system)
    
    try:
        # Initialize
        await processor.initialize()
        
        # Process admin portal request (existing functionality)
        
        # Process high-volume batch (new functionality)
        batch_results = await processor.process_high_volume_batch(
            processor.crawl_targets[:10]  # Process first 10 targets
        )
        print(f"Batch processing: {len(batch_results)} opportunities extracted")
        
        # Start scheduled monitoring
        await processor.start_scheduled_monitoring(interval_hours=12)
        
        # Get statistics
        stats = processor.get_stats()
        print(f"Processing stats: {stats}")
        
    finally:
        await processor.close()


if __name__ == "__main__":
    asyncio.run(main())