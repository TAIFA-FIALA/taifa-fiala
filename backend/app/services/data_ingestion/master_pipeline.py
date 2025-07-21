"""
Master High-Volume Data Ingestion Pipeline
Orchestrates all data collection systems for 10K-100M records scale

This is the main orchestrator that brings together all data ingestion components:
- High-volume RSS feed ingestion
- Web scraping engine
- News API collection
- Batch processing system
- Monitoring and alerting
- Data quality validation
- Retry logic and error handling
- Scheduled data collection jobs

Designed for production deployment with comprehensive error handling,
monitoring, and scalability features.
"""
import os
import asyncio
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import schedule
import signal
import sys
from contextlib import asynccontextmanager

# Import Supabase utilities
from .supabase_utils import supabase_utils

# Import our pipeline components
from .high_volume_pipeline import HighVolumeDataPipeline
from .web_scraping_engine import HighVolumeWebScrapingEngine
from .news_api_collector import HighVolumeNewsAPICollector
from .batch_processor import HighVolumeBatchProcessor, BatchConfig, BatchTask, DataSource
from .monitoring_system import ComprehensiveMonitoringSystem, MonitoringConfig, MetricType, Threshold, AlertLevel

# Import enrichment layers (CRITICAL: These were missing!)
from .crawl4ai_integration import EnhancedCrawl4AIProcessor, Crawl4AIConfig, CrawlTarget, Crawl4AIMasterPipelineIntegration
from ..ETL_pipelines.serper_search import SerperSearch

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Master pipeline status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class PipelineConfig:
    """Master pipeline configuration"""
    # Component configurations
    rss_pipeline_config: Dict[str, Any]
    web_scraping_config: Dict[str, Any]
    news_api_config: Dict[str, Any]
    batch_processing_config: BatchConfig
    monitoring_config: MonitoringConfig
    
    # Enrichment layer configurations (CRITICAL: Stage 2 & 3)
    enrichment_config: Dict[str, Any] = None
    
    # Pipeline settings
    max_concurrent_jobs: int = 10
    data_retention_days: int = 90
    error_threshold: float = 10.0  # percentage
    enable_scheduled_jobs: bool = True
    
    # Database settings
    supabase_url: str = ""
    supabase_key: str = ""
    db_host: Optional[str] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_port: int = 5432
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/master_pipeline.log"


class MasterDataIngestionPipeline:
    """
    Master pipeline that orchestrates all data ingestion systems
    Designed for production-scale data collection (10K-100M records)
    """
    
    def __init__(self, config: PipelineConfig, settings):
        self.config = config
        self.settings = settings
        self.status = PipelineStatus.STOPPED
        self.start_time: Optional[datetime] = None
        
        # Initialize components
        self.rss_pipeline = HighVolumeDataPipeline(
            max_workers=config.rss_pipeline_config.get('max_workers', 50),
            batch_size=config.rss_pipeline_config.get('batch_size', 1000)
        )
        
        self.web_scraper = HighVolumeWebScrapingEngine(
            max_workers=config.web_scraping_config.get('max_workers', 20),
            batch_size=config.web_scraping_config.get('batch_size', 100)
        )
        
        self.news_collector = HighVolumeNewsAPICollector(
            max_workers=config.news_api_config.get('max_workers', 10),
            batch_size=config.news_api_config.get('batch_size', 100)
        )
        
        self.batch_processor = HighVolumeBatchProcessor(config.batch_processing_config)
        
        self.monitoring_system = ComprehensiveMonitoringSystem(config.monitoring_config)
        
        # Initialize enrichment layers (CRITICAL: Stage 2 & 3 processing)
        self.crawl4ai_config = Crawl4AIConfig(
            max_concurrent_crawlers=config.enrichment_config.get('crawl4ai_max_workers', 5),
            batch_size=config.enrichment_config.get('crawl4ai_batch_size', 50),
            llm_api_key=self.settings.OPENAI_API_KEY,
            relevance_threshold=0.6,
            enable_content_validation=True
        )
        
        self.crawl4ai_processor = EnhancedCrawl4AIProcessor(
            self.crawl4ai_config,
            self.monitoring_system,
            settings=self.settings
        )
        
        self.crawl4ai_integration = Crawl4AIMasterPipelineIntegration(
            self, 
            self.crawl4ai_processor
        )
        
        self.serper_search = SerperSearch()
        
        # Pipeline control
        self.stop_event = threading.Event()
        self.scheduler_thread = None
        self.status_monitor_thread = None
        
        # Statistics
        self.stats = {
            'total_items_processed': 0,
            'total_errors': 0,
            'uptime_seconds': 0,
            'last_successful_run': None,
            'component_stats': {}
        }
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        # Create logs directory
        log_dir = Path(self.config.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        
        logger.info("Master pipeline logging initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Initialize all pipeline components"""
        logger.info("Initializing master data ingestion pipeline")
        
        try:
            # Initialize monitoring system first
            self.monitoring_system.start()
            
            # Add pipeline-specific thresholds
            self._setup_monitoring_thresholds()
            
            # Initialize RSS pipeline
            await self.rss_pipeline.initialize()
            
            # Initialize web scraper
            self.web_scraper.initialize_targets()
            
            # Initialize news collector
            self.news_collector.initialize_apis()
            self.news_collector.initialize_queries()
            
            # Initialize batch processor
            await self.batch_processor.initialize()
            
            logger.info("Master pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing master pipeline: {e}")
            self.status = PipelineStatus.ERROR
            raise
    
    def _setup_monitoring_thresholds(self):
        """Setup monitoring thresholds for pipeline components"""
        # RSS Pipeline thresholds
        self.monitoring_system.add_threshold(Threshold(
            metric_name='rss_error_rate',
            warning_threshold=5.0,
            critical_threshold=10.0,
            comparison_operator='>'
        ))
        
        # Web scraping thresholds
        self.monitoring_system.add_threshold(Threshold(
            metric_name='web_scraping_error_rate',
            warning_threshold=10.0,
            critical_threshold=20.0,
            comparison_operator='>'
        ))
        
        # News API thresholds
        self.monitoring_system.add_threshold(Threshold(
            metric_name='news_api_quota_usage',
            warning_threshold=80.0,
            critical_threshold=95.0,
            comparison_operator='>'
        ))
        
        # Batch processing thresholds
        self.monitoring_system.add_threshold(Threshold(
            metric_name='batch_processing_failure_rate',
            warning_threshold=5.0,
            critical_threshold=15.0,
            comparison_operator='>'
        ))
        
        # System resource thresholds
        self.monitoring_system.add_threshold(Threshold(
            metric_name='system_memory_percent',
            warning_threshold=80.0,
            critical_threshold=90.0,
            comparison_operator='>'
        ))
        
        logger.info("Monitoring thresholds configured")
    
    def _record_component_metrics(self):
        """Record metrics from all components"""
        try:
            # RSS Pipeline metrics
            rss_stats = self.rss_pipeline.get_stats()
            self.monitoring_system.record_metric(
                'rss_items_processed',
                rss_stats.get('total_items_processed', 0),
                MetricType.COUNTER,
                {'component': 'rss_pipeline'}
            )
            
            self.monitoring_system.record_metric(
                'rss_error_rate',
                rss_stats.get('total_errors', 0) / max(rss_stats.get('total_items_processed', 1), 1) * 100,
                MetricType.GAUGE,
                {'component': 'rss_pipeline'}
            )
            
            # Web scraping metrics
            web_stats = self.web_scraper.get_stats()
            self.monitoring_system.record_metric(
                'web_scraping_content_extracted',
                web_stats.get('content_extracted', 0),
                MetricType.COUNTER,
                {'component': 'web_scraper'}
            )
            
            self.monitoring_system.record_metric(
                'web_scraping_error_rate',
                web_stats.get('errors', 0) / max(web_stats.get('targets_processed', 1), 1) * 100,
                MetricType.GAUGE,
                {'component': 'web_scraper'}
            )
            
            # News API metrics
            news_stats = self.news_collector.get_stats()
            self.monitoring_system.record_metric(
                'news_api_articles_collected',
                news_stats.get('articles_collected', 0),
                MetricType.COUNTER,
                {'component': 'news_collector'}
            )
            
            self.monitoring_system.record_metric(
                'news_api_quota_usage',
                news_stats.get('quota_exceeded', 0),
                MetricType.GAUGE,
                {'component': 'news_collector'}
            )
            
            # Batch processing metrics
            batch_stats = self.batch_processor.get_stats()
            self.monitoring_system.record_metric(
                'batch_processing_items_processed',
                batch_stats.total_items_processed,
                MetricType.COUNTER,
                {'component': 'batch_processor'}
            )
            
            self.monitoring_system.record_metric(
                'batch_processing_failure_rate',
                batch_stats.total_items_failed / max(batch_stats.total_items_processed, 1) * 100,
                MetricType.GAUGE,
                {'component': 'batch_processor'}
            )
            
            # Overall pipeline metrics
            total_processed = (
                rss_stats.get('total_items_processed', 0) +
                web_stats.get('content_extracted', 0) +
                news_stats.get('articles_collected', 0) +
                batch_stats.total_items_processed
            )
            
            self.monitoring_system.record_metric(
                'pipeline_total_items_processed',
                total_processed,
                MetricType.COUNTER,
                {'component': 'master_pipeline'}
            )
            
            self.stats['total_items_processed'] = total_processed
            
        except Exception as e:
            logger.error(f"Error recording component metrics: {e}")
    
    def _run_scheduled_jobs(self):
        """Run scheduled data collection jobs"""
        logger.info("Starting scheduled jobs")
        
        # Schedule RSS collection every 30 minutes
        schedule.every(30).minutes.do(self._schedule_rss_collection)
        
        # Schedule web scraping every 2 hours
        schedule.every(2).hours.do(self._schedule_web_scraping)
        
        # Schedule news API collection every 1 hour
        schedule.every(1).hours.do(self._schedule_news_collection)
        
        # Schedule metrics recording every 5 minutes
        schedule.every(5).minutes.do(self._record_component_metrics)
        
        # Run scheduler
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _schedule_rss_collection(self):
        """Schedule RSS collection job"""
        try:
            logger.info("Running scheduled RSS collection")
            
            # Create batch task for RSS collection
            task = BatchTask(
                task_id=f"rss_collection_{int(time.time())}",
                data_source=DataSource.API,
                source_config={'pipeline': 'rss'},
                processor_func=self._process_rss_data,
                batch_size=1000,
                priority=1
            )
            
            self.batch_processor.add_task(task)
            
        except Exception as e:
            logger.error(f"Error scheduling RSS collection: {e}")
    
    def _schedule_web_scraping(self):
        """Schedule web scraping job"""
        try:
            logger.info("Running scheduled web scraping")
            
            # Create batch task for web scraping
            task = BatchTask(
                task_id=f"web_scraping_{int(time.time())}",
                data_source=DataSource.API,
                source_config={'pipeline': 'web_scraping'},
                processor_func=self._process_web_scraping_data,
                batch_size=100,
                priority=2
            )
            
            self.batch_processor.add_task(task)
            
        except Exception as e:
            logger.error(f"Error scheduling web scraping: {e}")
    
    def _schedule_news_collection(self):
        """Schedule news API collection job"""
        try:
            logger.info("Running scheduled news collection")
            
            # Create batch task for news collection
            task = BatchTask(
                task_id=f"news_collection_{int(time.time())}",
                data_source=DataSource.API,
                source_config={'pipeline': 'news_api'},
                processor_func=self._process_news_data,
                batch_size=100,
                priority=1
            )
            
            self.batch_processor.add_task(task)
            
        except Exception as e:
            logger.error(f"Error scheduling news collection: {e}")
    
    async def _process_rss_data(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process RSS data batch WITH ENHANCED EXTRACTION (Stage 1 -> 2 -> 3)"""
        try:
            # Import enhanced ETL integration
            from ..etl.enhanced_etl_integration import EnhancedMasterPipelineWrapper
            
            # Create enhanced wrapper
            enhanced_wrapper = EnhancedMasterPipelineWrapper(self)
            
            # STAGE 1: Run enhanced RSS collection with extraction
            logger.info("STAGE 1: Starting enhanced RSS data collection...")
            enhanced_results = await enhanced_wrapper.enhanced_rss_collection()
            
            # STAGE 2 & 3: Additional enrichment if needed
            if enhanced_results.get('enhanced_opportunities', 0) > 0:
                logger.info("STAGE 2 & 3: Enhanced extraction completed successfully")
                enrichment_results = {
                    'enhanced_extraction_applied': True,
                    'opportunities_processed': enhanced_results.get('enhanced_opportunities', 0),
                    'enhanced_stats': enhanced_results.get('enhanced_stats', {})
                }
            else:
                # Fallback to original enrichment if enhanced extraction failed
                logger.info("STAGE 2 & 3: Falling back to original enrichment...")
                stats = await self.rss_pipeline.process_funding_intelligence(
                    search_mode="comprehensive",
                    processing_mode="batch"
                )
                enrichment_results = await self._enrich_rss_data(stats)
            
            return [{
                'success': True, 
                'enhanced_results': enhanced_results,
                'enrichment_results': enrichment_results
            }]
            
        except Exception as e:
            logger.error(f"Error processing RSS data with enhanced extraction: {e}")
            # Fallback to original processing
            try:
                logger.info("Falling back to original RSS processing...")
                stats = await self.rss_pipeline.process_funding_intelligence(
                    search_mode="comprehensive",
                    processing_mode="batch"
                )
                enrichment_results = await self._enrich_rss_data(stats)
                return [{
                    'success': True, 
                    'stats': stats,
                    'enrichment_results': enrichment_results,
                    'fallback_used': True
                }]
            except Exception as fallback_error:
                logger.error(f"Fallback RSS processing also failed: {fallback_error}")
                return [{'success': False, 'error': str(e), 'fallback_error': str(fallback_error)}]
    
    async def _process_web_scraping_data(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process web scraping data batch"""
        try:
            # Run web scraping
            content = self.web_scraper.scrape_all_targets()
            
            return [{'success': True, 'content_count': len(content)}]
            
        except Exception as e:
            logger.error(f"Error processing web scraping data: {e}")
            return [{'success': False, 'error': str(e)}]
    
    async def _process_news_data(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process news API data batch"""
        try:
            # Run news collection
            articles = self.news_collector.collect_all_queries()
            
            return [{'success': True, 'articles_count': len(articles)}]
            
        except Exception as e:
            logger.error(f"Error processing news data: {e}")
            return [{'success': False, 'error': str(e)}]
    
    async def _enrich_rss_data(self, rss_stats: Dict[str, Any]) -> Dict[str, Any]:
        """CRITICAL: Enrich sparse RSS data with Crawl4AI and serper-dev (Stage 2 & 3)"""
        try:
            logger.info("Starting RSS data enrichment pipeline...")
            
            # Get recent RSS items that need enrichment (sparse data)
            recent_items = await supabase_utils.get_sparse_rss_items(hours=24, limit=50)
            
            logger.info(f"Found {len(recent_items)} RSS items needing enrichment")
            
            enrichment_results = {
                'total_items_processed': len(recent_items),
                'crawl4ai_enriched': 0,
                'serper_enriched': 0,
                'errors': 0,
                'enrichment_details': []
            }
            
            if not recent_items:
                logger.info("No RSS items need enrichment at this time")
                return enrichment_results
            
            # STAGE 2: Crawl4AI enrichment (extract precise data from source URLs)
            logger.info("STAGE 2: Starting Crawl4AI enrichment...")
            crawl4ai_results = await self._crawl4ai_enrich_items(recent_items)
            enrichment_results['crawl4ai_enriched'] = crawl4ai_results['enriched_count']
            enrichment_results['enrichment_details'].extend(crawl4ai_results['details'])
            
            # STAGE 3: Serper-dev search enrichment (find related opportunities)
            logger.info("STAGE 3: Starting serper-dev search enrichment...")
            serper_results = await self._serper_enrich_items(recent_items)
            enrichment_results['serper_enriched'] = serper_results['enriched_count']
            enrichment_results['enrichment_details'].extend(serper_results['details'])
            
            logger.info(f"Enrichment completed: {enrichment_results['crawl4ai_enriched']} Crawl4AI + {enrichment_results['serper_enriched']} serper-dev")
            
            # Update monitoring metrics
            self.monitoring_system.record_metric(
                'enrichment_pipeline_success_rate',
                MetricType.GAUGE,
                (enrichment_results['crawl4ai_enriched'] + enrichment_results['serper_enriched']) / max(len(recent_items), 1) * 100
            )
            
            return enrichment_results
            
        except Exception as e:
            logger.error(f"Critical error in RSS enrichment pipeline: {e}")
            return {
                'total_items_processed': 0,
                'crawl4ai_enriched': 0,
                'serper_enriched': 0,
                'errors': 1,
                'error_message': str(e)
            }
    
    async def _crawl4ai_enrich_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """STAGE 2: Use Crawl4AI to extract precise data from source URLs"""
        try:
            enriched_count = 0
            details = []
            
            # Create crawl targets from RSS items with source URLs
            crawl_targets = []
            for item in items:
                source_url = item.get('source_url')
                if source_url and source_url.startswith('http'):
                    target = CrawlTarget(
                        url=source_url,
                        target_type='funding_opportunity',
                        priority=1,
                        extraction_strategy='intelligence_item',
                        metadata={
                            'rss_item_id': item['id'],
                            'title': item.get('title', ''),
                            'description': (item.get('description') or '')[:200]
                        }
                    )
                    crawl_targets.append(target)
            
            logger.info(f"Created {len(crawl_targets)} Crawl4AI targets from RSS items")
            
            if not crawl_targets:
                return {'enriched_count': 0, 'details': []}
            
            # Process targets with Crawl4AI
            enrichment_opportunities = await self.crawl4ai_processor.process_high_volume_batch(crawl_targets)
            
            # Prepare updates for Supabase
            updates = []
            for opportunity in enrichment_opportunities:
                rss_item_id = opportunity.get('metadata', {}).get('rss_item_id')
                if not rss_item_id:
                    continue
                
                # Prepare update object
                update_data = {
                    'id': rss_item_id,
                    'enrichment_status': 'crawl4ai_enriched',
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Add fields to update if they exist in the opportunity
                for field in ['funding_amount', 'application_deadline', 'eligibility_criteria', 
                            'contact_email', 'application_url']:
                    if field in opportunity and opportunity[field] is not None:
                        update_data[field] = opportunity[field]
                
                # Handle relevance score
                if 'relevance_score' in opportunity and opportunity['relevance_score'] is not None:
                    # Get current relevance score to compare
                    current_item = await supabase_utils.get_item_by_id(rss_item_id)
                    current_score = current_item.get('relevance_score', 0) if current_item else 0
                    update_data['relevance_score'] = max(
                        current_score,
                        float(opportunity['relevance_score'])
                    )
                
                updates.append(update_data)
                
                # Track enrichment details
                enriched_fields = [k for k in opportunity.keys() 
                                 if k not in ['metadata', 'relevance_score'] and opportunity[k] is not None]
                if enriched_fields:
                    details.append({
                        'item_id': rss_item_id,
                        'enrichment_type': 'crawl4ai',
                        'fields_enriched': enriched_fields
                    })
            
            # Apply updates in bulk
            if updates:
                result = await supabase_utils.bulk_update_items(updates)
                enriched_count = result.get('success', 0)
                logger.info(f"Crawl4AI updated {enriched_count} RSS items via Supabase")
            
            return {
                'enriched_count': enriched_count,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Error in Crawl4AI enrichment: {e}")
            return {'enriched_count': 0, 'details': [], 'error': str(e)}
    
    async def _serper_enrich_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """STAGE 3: Use serper-dev to find related opportunities and additional context"""
        try:
            enriched_count = 0
            details = []
            updates = []
            
            # Process each item with serper search (limit to first 10 to avoid API quota issues)
            for item in items[:10]:
                try:
                    # Create search query from item title and description
                    title = item.get('title', '')
                    description = item.get('description', '')
                    search_query = f"{title} funding opportunity application"
                    if description:
                        search_query += f" {description[:100]}"
                    
                    # Search for related opportunities
                    search_results = await self.serper_search.search(search_query, num_results=5)
                    
                    if not search_results or 'organic' not in search_results:
                        continue
                    
                    # Process search results and extract relevant information
                    for result in search_results['organic']:
                        # Prepare update data for this item
                        update_data = {
                            'id': item['id'],
                            'enrichment_status': 'serper_enriched',
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        updated_fields = []
                        
                        # Extract funding amount if not already set
                        snippet = result.get('snippet', '').lower()
                        if 'funding' in snippet and not item.get('funding_amount'):
                            # Simple regex to find dollar amounts in the snippet
                            import re
                            funding_match = re.search(r'\$([\d,]+(?:[.]\d{2})?)', snippet)
                            if funding_match:
                                update_data['funding_amount'] = funding_match.group(1)
                                updated_fields.append('funding_amount')
                        
                        # Update application URL if not already set
                        if 'link' in result and not item.get('application_url'):
                            update_data['application_url'] = result['link']
                            updated_fields.append('application_url')
                        
                        # Update eligibility criteria if we find relevant information
                        if 'eligibility' in snippet and not item.get('eligibility_criteria'):
                            # Extract a portion of the snippet as eligibility criteria
                            update_data['eligibility_criteria'] = snippet[:500]  # Truncate to avoid too much text
                            updated_fields.append('eligibility_criteria')
                        
                        # Only add to updates if we found new information
                        if len(updated_fields) > 1:  # More than just the status and timestamp
                            updates.append(update_data)
                            details.append({
                                'item_id': item['id'],
                                'enrichment_type': 'serper',
                                'fields_enriched': updated_fields,
                                'source_url': result.get('link')
                            })
                            break  # Only process first relevant result per item
                            
                except Exception as e:
                    logger.error(f"Error enriching item with serper: {e}")
                    continue
            
            # Apply all updates in bulk
            if updates:
                result = await supabase_utils.bulk_update_items(updates)
                enriched_count = result.get('success', 0)
                logger.info(f"Serper updated {enriched_count} RSS items via Supabase")
            
            return {
                'enriched_count': enriched_count,
                'details': details
            }
            
        except Exception as e:
            logger.error(f"Error in serper-dev enrichment: {e}")
            return {'enriched_count': 0, 'details': [], 'error': str(e)}
    
    def _status_monitor(self):
        """Monitor pipeline status and health"""
        while not self.stop_event.is_set():
            try:
                # Update uptime
                if self.start_time:
                    self.stats['uptime_seconds'] = (datetime.now() - self.start_time).total_seconds()
                
                # Record component metrics
                self._record_component_metrics()
                
                # Check overall health
                if self.stats['total_errors'] > 0:
                    error_rate = self.stats['total_errors'] / max(self.stats['total_items_processed'], 1) * 100
                    
                    if error_rate > self.config.error_threshold:
                        logger.warning(f"High error rate detected: {error_rate:.2f}%")
                        
                        # Send alert
                        self.monitoring_system.record_metric(
                            'pipeline_error_rate',
                            error_rate,
                            MetricType.GAUGE,
                            {'component': 'master_pipeline'}
                        )
                
                # Update last successful run
                self.stats['last_successful_run'] = datetime.now()
                
                # Sleep before next check
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in status monitor: {e}")
                time.sleep(60)
    
    async def start(self):
        """Start the master pipeline"""
        if self.status == PipelineStatus.RUNNING:
            logger.warning("Master pipeline is already running")
            return
        
        logger.info("Starting master data ingestion pipeline")
        self.status = PipelineStatus.STARTING
        
        try:
            # Initialize components
            await self.initialize()
            
            # Start all components
            await self.rss_pipeline.start_pipeline()
            
            if self.config.enable_scheduled_jobs:
                # Start web scraping (every 12 hours)
                self.web_scraper.start_continuous_scraping(interval_hours=12)
                
                # Start news collection (every 12 hours)
                self.news_collector.start_continuous_collection(interval_hours=12)
            
            # Start batch processor
            self.batch_processor.start()
            
            # CRITICAL: Initialize and start enrichment layers (Stage 2 & 3)
            logger.info("Initializing enrichment layers (Crawl4AI and serper-dev)...")
            await self.crawl4ai_processor.initialize()
            
            # Start Crawl4AI scheduled monitoring for continuous enrichment
            if self.config.enable_scheduled_jobs:
                await self.crawl4ai_processor.start_scheduled_monitoring(interval_hours=12)
                logger.info("Crawl4AI scheduled monitoring started (12-hour intervals)")
            
            # Start scheduled jobs
            if self.config.enable_scheduled_jobs:
                self.scheduler_thread = threading.Thread(
                    target=self._run_scheduled_jobs,
                    name="SchedulerThread",
                    daemon=True
                )
                self.scheduler_thread.start()
            
            # Start status monitor
            self.status_monitor_thread = threading.Thread(
                target=self._status_monitor,
                name="StatusMonitor",
                daemon=True
            )
            self.status_monitor_thread.start()
            
            # Update status
            self.status = PipelineStatus.RUNNING
            self.start_time = datetime.now()
            
            logger.info("Master pipeline started successfully")
            
        except Exception as e:
            logger.error(f"Error starting master pipeline: {e}")
            self.status = PipelineStatus.ERROR
            raise
    
    async def stop(self):
        """Stop the master pipeline"""
        if self.status == PipelineStatus.STOPPED:
            logger.warning("Master pipeline is already stopped")
            return
        
        logger.info("Stopping master data ingestion pipeline")
        self.status = PipelineStatus.STOPPING
        
        try:
            # Stop all components
            self.stop_event.set()
            
            # Stop RSS pipeline
            asyncio.run(self.rss_pipeline.stop_pipeline())
            
            # Stop web scraping
            self.web_scraper.stop_scraping()
            
            # Stop news collection
            self.news_collector.stop_collection()
            
            # Stop batch processor
            self.batch_processor.stop()
            
            # Stop monitoring
            self.monitoring_system.stop()
            
            # CRITICAL: Stop enrichment layers
            logger.info("Stopping enrichment layers...")
            self.crawl4ai_processor.stop_scheduled_monitoring()
            await self.crawl4ai_processor.close()
            
            # Wait for threads to finish
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=10)
            
            if self.status_monitor_thread:
                self.status_monitor_thread.join(timeout=10)
            
            self.status = PipelineStatus.STOPPED
            logger.info("Master pipeline stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping master pipeline: {e}")
            self.status = PipelineStatus.ERROR
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        return {
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': self.stats['uptime_seconds'],
            'total_items_processed': self.stats['total_items_processed'],
            'total_errors': self.stats['total_errors'],
            'last_successful_run': self.stats['last_successful_run'].isoformat() if self.stats['last_successful_run'] else None,
            'component_stats': {
                'rss_pipeline': self.rss_pipeline.get_stats(),
                'web_scraper': self.web_scraper.get_stats(),
                'news_collector': self.news_collector.get_stats(),
                'batch_processor': self.batch_processor.get_stats().__dict__,
                'monitoring_system': self.monitoring_system.get_dashboard_data()
            }
        }
    
    def pause(self):
        """Pause the pipeline"""
        if self.status != PipelineStatus.RUNNING:
            logger.warning("Pipeline is not running, cannot pause")
            return
        
        logger.info("Pausing master pipeline")
        self.status = PipelineStatus.PAUSED
        # Implementation for pausing components
    
    def resume(self):
        """Resume the pipeline"""
        if self.status != PipelineStatus.PAUSED:
            logger.warning("Pipeline is not paused, cannot resume")
            return
        
        logger.info("Resuming master pipeline")
        self.status = PipelineStatus.RUNNING
        # Implementation for resuming components


def create_default_config() -> PipelineConfig:
    """Create default pipeline configuration"""
    # Parse database URL if available
    db_url = os.getenv('DATABASE_URL', '')
    db_config = {}
    
    if db_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            if parsed.hostname:
                db_config['db_host'] = parsed.hostname
            if parsed.port:
                db_config['db_port'] = parsed.port
            if parsed.username:
                db_config['db_user'] = parsed.username
            if parsed.password:
                db_config['db_password'] = parsed.password
            if parsed.path and len(parsed.path) > 1:
                db_config['db_name'] = parsed.path[1:]  # Remove leading '/'
        except Exception as e:
            logging.warning(f"Failed to parse DATABASE_URL: {e}")
    
    # Default enrichment configuration
    enrichment_config = {
        'crawl4ai_max_workers': 5,
        'crawl4ai_batch_size': 50,
        'serper_enabled': True,
        'serper_api_key': os.getenv('SERPER_API_KEY', '')
    }
    
    return PipelineConfig(
        rss_pipeline_config={
            'max_workers': 10,  # Reduced workers for less frequent processing
            'batch_size': 50    # Smaller batches, processed less frequently
        },
        web_scraping_config={
            'max_workers': 5,   # Reduced workers
            'batch_size': 50    # Consistent batch size
        },
        news_api_config={
            'max_workers': 5,   # Reduced workers
            'batch_size': 50    # Consistent batch size
        },
        batch_processing_config=BatchConfig(
            max_workers=5,      # Reduced workers
            batch_size=50,      # Consistent with new strategy
            enable_checkpointing=True
        ),
        monitoring_config=MonitoringConfig(
            slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
            prometheus_enabled=True,
            enable_anomaly_detection=True,
            prometheus_port=8001  # Explicitly set port to avoid conflicts
        ),
        enrichment_config=enrichment_config,  # Add the enrichment config
        max_concurrent_jobs=10,
        enable_scheduled_jobs=True,
        supabase_url=os.getenv('SUPABASE_URL', ''),
        supabase_key=os.getenv('SUPABASE_SERVICE_API_KEY', ''),
        **db_config,  # Unpack the database configuration
        log_level='INFO',
        log_file='logs/master_pipeline.log'
    )


# CLI and main execution
async def main():
    """Main function for running the master pipeline"""
    logger.info("🚀 Starting AI Africa Funding Tracker - Master Data Ingestion Pipeline")
    
    # Create configuration
    config = create_default_config()
    
    # Create master pipeline
    pipeline = MasterDataIngestionPipeline(config)
    
    try:
        # Start pipeline
        await pipeline.start()
        
        # Keep running
        while pipeline.status == PipelineStatus.RUNNING:
            await asyncio.sleep(60)
            
            # Print status every hour
            if int(time.time()) % 3600 == 0:
                status = pipeline.get_status()
                logger.info(f"Pipeline Status: {status['status']}, "
                           f"Items Processed: {status['total_items_processed']}, "
                           f"Uptime: {status['uptime_seconds']:.0f}s")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error in main pipeline: {e}")
    finally:
        # Stop pipeline
        pipeline.stop()
        logger.info("Master pipeline shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
