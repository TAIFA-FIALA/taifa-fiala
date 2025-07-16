"""
AI Africa Funding Tracker - Scalable ETL Pipeline Architecture
==============================================================

This module defines the architecture for a production-ready ETL pipeline
that can handle rapid scaling from day 1.

Architecture Overview:
- Queue-based processing with Redis/Celery
- Parallel processing with worker pools
- Multi-tier caching strategy
- Database optimization with connection pooling
- Real-time monitoring and alerting
- Auto-scaling capabilities
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

# =============================================================================
# PIPELINE STAGES AND PRIORITY LEVELS
# =============================================================================

class PipelineStage(Enum):
    """ETL Pipeline stages for processing funding opportunities"""
    INGESTION = "ingestion"           # Data collection from sources
    VALIDATION = "validation"         # Data quality and validation
    ENRICHMENT = "enrichment"         # AI-powered content enhancement
    TRANSFORMATION = "transformation" # Data format and structure conversion
    LOADING = "loading"              # Database persistence
    INDEXING = "indexing"            # Search index updates
    NOTIFICATION = "notification"     # Alert and notification dispatch

class Priority(Enum):
    """Task priority levels for queue processing"""
    CRITICAL = 1    # Real-time user submissions
    HIGH = 2        # RSS feeds and API updates
    MEDIUM = 3      # Scheduled crawling tasks
    LOW = 4         # Background maintenance tasks

# =============================================================================
# DATA MODELS FOR ETL PIPELINE
# =============================================================================

@dataclass
class ETLTask:
    """Base task for ETL pipeline processing"""
    id: str
    stage: PipelineStage
    priority: Priority
    source_type: str  # "rss", "api", "manual", "web_scrape"
    source_id: str
    payload: Dict[str, Any]
    created_at: datetime
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            'id': self.id,
            'stage': self.stage.value,
            'priority': self.priority.value,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'payload': self.payload,
            'created_at': self.created_at.isoformat(),
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }

@dataclass
class ProcessingResult:
    """Result of ETL processing stage"""
    task_id: str
    stage: PipelineStage
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    next_stage: Optional[PipelineStage] = None

# =============================================================================
# SCALING CONFIGURATION
# =============================================================================

class ETLConfig:
    """Configuration for scalable ETL pipeline"""
    
    # Queue Configuration
    REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    
    # Worker Configuration
    WORKER_CONCURRENCY = {
        PipelineStage.INGESTION: 20,      # High concurrency for data collection
        PipelineStage.VALIDATION: 10,     # Moderate for validation tasks
        PipelineStage.ENRICHMENT: 5,      # Limited for AI processing
        PipelineStage.TRANSFORMATION: 15, # High for data transformation
        PipelineStage.LOADING: 8,         # Limited by database connections
        PipelineStage.INDEXING: 5,        # Limited for search indexing
        PipelineStage.NOTIFICATION: 12,   # High for notifications
    }
    
    # Database Configuration
    DB_POOL_SIZE = 50
    DB_MAX_OVERFLOW = 100
    DB_POOL_TIMEOUT = 30
    DB_POOL_RECYCLE = 3600
    
    # Cache Configuration
    CACHE_TTL = {
        'funding_opportunities': 300,     # 5 minutes
        'organizations': 600,             # 10 minutes
        'search_results': 180,            # 3 minutes
        'analytics': 900,                 # 15 minutes
    }
    
    # Rate Limiting Configuration
    RATE_LIMITS = {
        'serper_api': 100,        # requests per minute
        'openai_api': 50,         # requests per minute
        'web_scraping': 30,       # requests per minute
        'rss_feeds': 200,         # requests per minute
    }
    
    # Monitoring Configuration
    METRICS_RETENTION_DAYS = 30
    ALERT_THRESHOLDS = {
        'queue_size': 1000,
        'processing_time': 300,   # seconds
        'error_rate': 0.05,       # 5%
        'memory_usage': 0.85,     # 85%
    }

# =============================================================================
# PIPELINE ARCHITECTURE COMPONENTS
# =============================================================================

class ETLPipelineArchitecture:
    """
    Main architecture coordinator for the ETL pipeline
    
    Components:
    1. Queue Manager - Redis-based task queuing
    2. Worker Pool - Celery workers for parallel processing
    3. Cache Layer - Multi-tier caching with Redis
    4. Database Layer - Optimized PostgreSQL with connection pooling
    5. Monitoring Layer - Metrics, logging, and alerting
    """
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize all pipeline components"""
        await self._setup_queue_manager()
        await self._setup_database_pool()
        await self._setup_cache_layer()
        await self._setup_monitoring()
        
    async def _setup_queue_manager(self):
        """Setup Redis-based queue manager"""
        # Queue setup will be implemented in queue_manager.py
        pass
        
    async def _setup_database_pool(self):
        """Setup optimized database connection pool"""
        # Database pool setup will be implemented in db_manager.py
        pass
        
    async def _setup_cache_layer(self):
        """Setup multi-tier caching system"""
        # Cache layer setup will be implemented in cache_manager.py
        pass
        
    async def _setup_monitoring(self):
        """Setup monitoring and alerting system"""
        # Monitoring setup will be implemented in monitoring.py
        pass

# =============================================================================
# PROCESSING STRATEGIES
# =============================================================================

class ParallelProcessingStrategy:
    """
    Strategies for parallel processing based on data type and volume
    """
    
    @staticmethod
    def get_batch_size(stage: PipelineStage, data_type: str) -> int:
        """Get optimal batch size for processing"""
        batch_sizes = {
            PipelineStage.INGESTION: {
                'rss': 50,
                'api': 20,
                'web_scrape': 10,
                'manual': 1
            },
            PipelineStage.VALIDATION: {
                'default': 25
            },
            PipelineStage.ENRICHMENT: {
                'default': 5  # Limited by AI API rate limits
            },
            PipelineStage.TRANSFORMATION: {
                'default': 30
            },
            PipelineStage.LOADING: {
                'default': 20
            }
        }
        
        stage_config = batch_sizes.get(stage, {'default': 10})
        return stage_config.get(data_type, stage_config.get('default', 10))
    
    @staticmethod
    def get_retry_strategy(stage: PipelineStage) -> Dict[str, Any]:
        """Get retry strategy for different pipeline stages"""
        return {
            PipelineStage.INGESTION: {
                'max_retries': 3,
                'retry_delay': 5,
                'backoff_factor': 2
            },
            PipelineStage.VALIDATION: {
                'max_retries': 2,
                'retry_delay': 3,
                'backoff_factor': 1.5
            },
            PipelineStage.ENRICHMENT: {
                'max_retries': 2,
                'retry_delay': 10,
                'backoff_factor': 2
            },
            PipelineStage.TRANSFORMATION: {
                'max_retries': 3,
                'retry_delay': 2,
                'backoff_factor': 1.5
            },
            PipelineStage.LOADING: {
                'max_retries': 3,
                'retry_delay': 5,
                'backoff_factor': 2
            }
        }.get(stage, {'max_retries': 2, 'retry_delay': 5, 'backoff_factor': 2})

# =============================================================================
# SCALING UTILITIES
# =============================================================================

class ScalingUtilities:
    """Utilities for handling scaling scenarios"""
    
    @staticmethod
    def estimate_processing_time(data_volume: int, stage: PipelineStage) -> int:
        """Estimate processing time based on data volume and stage"""
        # Processing time estimates per item (in seconds)
        time_estimates = {
            PipelineStage.INGESTION: 0.5,
            PipelineStage.VALIDATION: 1.0,
            PipelineStage.ENRICHMENT: 5.0,
            PipelineStage.TRANSFORMATION: 0.8,
            PipelineStage.LOADING: 0.3,
            PipelineStage.INDEXING: 0.2,
            PipelineStage.NOTIFICATION: 0.1
        }
        
        base_time = time_estimates.get(stage, 1.0)
        return int(data_volume * base_time)
    
    @staticmethod
    def calculate_required_workers(queue_size: int, stage: PipelineStage) -> int:
        """Calculate number of workers needed for optimal processing"""
        base_workers = ETLConfig.WORKER_CONCURRENCY.get(stage, 5)
        
        # Scale workers based on queue size
        if queue_size > 1000:
            return min(base_workers * 3, 50)
        elif queue_size > 500:
            return min(base_workers * 2, 30)
        elif queue_size > 100:
            return min(base_workers * 1.5, 20)
        else:
            return base_workers

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

class PerformanceMetrics:
    """Performance metrics for ETL pipeline monitoring"""
    
    def __init__(self):
        self.metrics = {
            'tasks_processed': 0,
            'tasks_failed': 0,
            'processing_times': [],
            'queue_sizes': {},
            'worker_utilization': {},
            'error_rates': {},
            'throughput': 0
        }
    
    def update_metrics(self, stage: PipelineStage, result: ProcessingResult):
        """Update performance metrics"""
        self.metrics['tasks_processed'] += 1
        
        if not result.success:
            self.metrics['tasks_failed'] += 1
            
        if result.metrics:
            processing_time = result.metrics.get('processing_time', 0)
            self.metrics['processing_times'].append(processing_time)
            
        # Calculate error rate
        total_tasks = self.metrics['tasks_processed']
        if total_tasks > 0:
            error_rate = self.metrics['tasks_failed'] / total_tasks
            self.metrics['error_rates'][stage.value] = error_rate
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        processing_times = self.metrics['processing_times']
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            'total_processed': self.metrics['tasks_processed'],
            'total_failed': self.metrics['tasks_failed'],
            'avg_processing_time': avg_processing_time,
            'overall_error_rate': self.metrics['tasks_failed'] / max(self.metrics['tasks_processed'], 1),
            'current_throughput': self.metrics['throughput'],
            'queue_health': self._assess_queue_health()
        }
    
    def _assess_queue_health(self) -> str:
        """Assess overall queue health"""
        error_rate = self.metrics['tasks_failed'] / max(self.metrics['tasks_processed'], 1)
        
        if error_rate > 0.1:
            return "CRITICAL"
        elif error_rate > 0.05:
            return "WARNING"
        else:
            return "HEALTHY"

# =============================================================================
# AUTO-SCALING LOGIC
# =============================================================================

class AutoScaler:
    """Auto-scaling logic for ETL pipeline"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        
    async def evaluate_scaling_needs(self) -> Dict[str, Any]:
        """Evaluate if scaling is needed based on current metrics"""
        recommendations = {}
        
        for stage in PipelineStage:
            queue_size = await self._get_queue_size(stage)
            current_workers = await self._get_active_workers(stage)
            recommended_workers = ScalingUtilities.calculate_required_workers(queue_size, stage)
            
            if recommended_workers > current_workers:
                recommendations[stage.value] = {
                    'action': 'scale_up',
                    'current_workers': current_workers,
                    'recommended_workers': recommended_workers,
                    'queue_size': queue_size
                }
            elif recommended_workers < current_workers and queue_size < 50:
                recommendations[stage.value] = {
                    'action': 'scale_down',
                    'current_workers': current_workers,
                    'recommended_workers': recommended_workers,
                    'queue_size': queue_size
                }
        
        return recommendations
    
    async def _get_queue_size(self, stage: PipelineStage) -> int:
        """Get current queue size for a stage"""
        # Implementation will connect to Redis to get queue size
        return 0
    
    async def _get_active_workers(self, stage: PipelineStage) -> int:
        """Get number of active workers for a stage"""
        # Implementation will connect to Celery to get worker count
        return 0

if __name__ == "__main__":
    # Example usage
    config = ETLConfig()
    pipeline = ETLPipelineArchitecture(config)
    
    print("ETL Pipeline Architecture Configuration:")
    print(f"Worker Concurrency: {config.WORKER_CONCURRENCY}")
    print(f"Database Pool Size: {config.DB_POOL_SIZE}")
    print(f"Cache TTL Settings: {config.CACHE_TTL}")
    print(f"Rate Limits: {config.RATE_LIMITS}")