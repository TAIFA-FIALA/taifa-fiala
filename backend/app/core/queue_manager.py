"""
Queue Manager for Scalable ETL Pipeline
=====================================

High-throughput queue management using Redis and Celery for handling
rapid data ingestion and processing at scale.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import asdict
import redis.asyncio as redis
from celery import Celery
from celery.result import AsyncResult
from celery.exceptions import Retry
import uuid

from .etl_architecture import ETLTask, PipelineStage, Priority, ETLConfig, ProcessingResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CELERY APP CONFIGURATION
# =============================================================================

def create_celery_app(config: ETLConfig) -> Celery:
    """Create and configure Celery application for scalable processing"""
    
    app = Celery(
        'taifa_etl_pipeline',
        broker=config.CELERY_BROKER_URL,
        backend=config.CELERY_RESULT_BACKEND,
        include=[
            'app.core.etl_tasks',
            'app.core.data_processors',
            'app.core.ai_processors'
        ]
    )
    
    # Celery Configuration for High Performance
    app.conf.update(
        # Task Routing
        task_routes={
            'app.core.etl_tasks.ingest_data': {'queue': 'ingestion'},
            'app.core.etl_tasks.validate_data': {'queue': 'validation'},
            'app.core.etl_tasks.enrich_data': {'queue': 'enrichment'},
            'app.core.etl_tasks.transform_data': {'queue': 'transformation'},
            'app.core.etl_tasks.load_data': {'queue': 'loading'},
            'app.core.etl_tasks.index_data': {'queue': 'indexing'},
            'app.core.etl_tasks.send_notifications': {'queue': 'notifications'},
        },
        
        # Task Serialization
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        
        # Task Execution
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_reject_on_worker_lost=True,
        
        # Task Results
        result_expires=3600,  # 1 hour
        result_persistent=True,
        
        # Task Routing
        task_default_queue='default',
        task_default_exchange='default',
        task_default_exchange_type='direct',
        task_default_routing_key='default',
        
        # Worker Configuration
        worker_pool_restarts=True,
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=False,
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Queue Configuration
        task_create_missing_queues=True,
        
        # Rate Limiting
        task_annotations={
            'app.core.etl_tasks.enrich_data': {'rate_limit': '50/m'},
            'app.core.etl_tasks.external_api_call': {'rate_limit': '100/m'},
        },
        
        # Retry Configuration
        task_retry_jitter=True,
        task_retry_jitter_max=5.0,
        
        # Security
        worker_hijack_root_logger=False,
        worker_log_color=False,
    )
    
    return app

# =============================================================================
# REDIS QUEUE MANAGER
# =============================================================================

class RedisQueueManager:
    """High-performance Redis-based queue manager for ETL pipeline"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.config.REDIS_URL,
                encoding='utf-8',
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            self.logger.info("Redis connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def enqueue_task(self, task: ETLTask) -> str:
        """Enqueue a task for processing"""
        try:
            # Serialize task
            task_data = json.dumps(task.to_dict(), default=str)
            
            # Determine queue name based on stage and priority
            queue_name = self._get_queue_name(task.stage, task.priority)
            
            # Add task to queue with priority scoring
            priority_score = self._calculate_priority_score(task.priority)
            
            await self.redis_client.zadd(
                queue_name,
                {task_data: priority_score}
            )
            
            # Track task in processing registry
            await self._track_task(task)
            
            # Update queue metrics
            await self._update_queue_metrics(queue_name, 'enqueued')
            
            self.logger.info(f"Task {task.id} enqueued to {queue_name}")
            return task.id
            
        except Exception as e:
            self.logger.error(f"Failed to enqueue task {task.id}: {e}")
            raise
    
    async def dequeue_task(self, stage: PipelineStage, timeout: int = 10) -> Optional[ETLTask]:
        """Dequeue highest priority task from stage queue"""
        try:
            queue_name = self._get_queue_name(stage, Priority.HIGH)
            
            # Get highest priority task (lowest score)
            result = await self.redis_client.bzpopmin(queue_name, timeout=timeout)
            
            if not result:
                return None
            
            # Parse task data
            _, task_data, _ = result
            task_dict = json.loads(task_data)
            
            # Convert back to ETLTask
            task = ETLTask(
                id=task_dict['id'],
                stage=PipelineStage(task_dict['stage']),
                priority=Priority(task_dict['priority']),
                source_type=task_dict['source_type'],
                source_id=task_dict['source_id'],
                payload=task_dict['payload'],
                created_at=datetime.fromisoformat(task_dict['created_at']),
                retry_count=task_dict.get('retry_count', 0),
                max_retries=task_dict.get('max_retries', 3)
            )
            
            # Update processing status
            await self._update_task_status(task.id, 'processing')
            
            # Update queue metrics
            await self._update_queue_metrics(queue_name, 'dequeued')
            
            self.logger.info(f"Task {task.id} dequeued from {queue_name}")
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to dequeue task from {stage.value}: {e}")
            raise
    
    async def requeue_task(self, task: ETLTask, delay_seconds: int = 0) -> bool:
        """Requeue a failed task with retry logic"""
        try:
            if task.retry_count >= task.max_retries:
                await self._move_to_dead_letter_queue(task)
                return False
            
            # Increment retry count
            task.retry_count += 1
            
            # Calculate delay based on exponential backoff
            if delay_seconds == 0:
                delay_seconds = min(300, 2 ** task.retry_count)  # Max 5 minutes
            
            # Schedule for reprocessing
            if delay_seconds > 0:
                await self._schedule_delayed_task(task, delay_seconds)
            else:
                await self.enqueue_task(task)
            
            self.logger.info(f"Task {task.id} requeued with {delay_seconds}s delay (retry {task.retry_count}/{task.max_retries})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to requeue task {task.id}: {e}")
            raise
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics"""
        try:
            stats = {}
            
            for stage in PipelineStage:
                for priority in Priority:
                    queue_name = self._get_queue_name(stage, priority)
                    queue_size = await self.redis_client.zcard(queue_name)
                    
                    if queue_size > 0:
                        stats[queue_name] = {
                            'size': queue_size,
                            'stage': stage.value,
                            'priority': priority.value
                        }
            
            # Get processing stats
            processing_count = await self.redis_client.hlen('processing_tasks')
            completed_count = await self.redis_client.hlen('completed_tasks')
            failed_count = await self.redis_client.hlen('failed_tasks')
            
            stats['summary'] = {
                'total_queued': sum(q['size'] for q in stats.values() if 'size' in q),
                'processing': processing_count,
                'completed': completed_count,
                'failed': failed_count,
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
            raise
    
    async def clear_queue(self, stage: PipelineStage, priority: Optional[Priority] = None) -> int:
        """Clear specific queue or all queues for a stage"""
        try:
            cleared_count = 0
            
            if priority:
                queue_name = self._get_queue_name(stage, priority)
                cleared_count = await self.redis_client.delete(queue_name)
            else:
                # Clear all priority queues for the stage
                for p in Priority:
                    queue_name = self._get_queue_name(stage, p)
                    cleared_count += await self.redis_client.delete(queue_name)
            
            self.logger.info(f"Cleared {cleared_count} items from {stage.value} queues")
            return cleared_count
            
        except Exception as e:
            self.logger.error(f"Failed to clear queue {stage.value}: {e}")
            raise
    
    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================
    
    def _get_queue_name(self, stage: PipelineStage, priority: Priority) -> str:
        """Generate queue name based on stage and priority"""
        return f"taifa_etl:{stage.value}:{priority.name.lower()}"
    
    def _calculate_priority_score(self, priority: Priority) -> float:
        """Calculate priority score for sorted set (lower = higher priority)"""
        base_score = priority.value * 1000
        timestamp_score = datetime.now().timestamp()
        return base_score + timestamp_score
    
    async def _track_task(self, task: ETLTask):
        """Track task in processing registry"""
        task_key = f"task:{task.id}"
        task_data = {
            'id': task.id,
            'stage': task.stage.value,
            'status': 'queued',
            'created_at': task.created_at.isoformat(),
            'retry_count': task.retry_count
        }
        
        await self.redis_client.hset(task_key, mapping=task_data)
        await self.redis_client.expire(task_key, 86400)  # 24 hours
    
    async def _update_task_status(self, task_id: str, status: str):
        """Update task status in registry"""
        task_key = f"task:{task_id}"
        await self.redis_client.hset(task_key, 'status', status)
        await self.redis_client.hset(task_key, 'updated_at', datetime.now().isoformat())
    
    async def _update_queue_metrics(self, queue_name: str, operation: str):
        """Update queue metrics for monitoring"""
        metrics_key = f"metrics:{queue_name}"
        await self.redis_client.hincrby(metrics_key, operation, 1)
        await self.redis_client.expire(metrics_key, 86400)  # 24 hours
    
    async def _schedule_delayed_task(self, task: ETLTask, delay_seconds: int):
        """Schedule task for delayed processing"""
        execute_at = datetime.now() + timedelta(seconds=delay_seconds)
        delayed_queue = "taifa_etl:delayed"
        
        task_data = json.dumps(task.to_dict(), default=str)
        score = execute_at.timestamp()
        
        await self.redis_client.zadd(delayed_queue, {task_data: score})
    
    async def _move_to_dead_letter_queue(self, task: ETLTask):
        """Move failed task to dead letter queue"""
        dead_letter_queue = "taifa_etl:dead_letter"
        task_data = json.dumps(task.to_dict(), default=str)
        
        await self.redis_client.lpush(dead_letter_queue, task_data)
        await self._update_task_status(task.id, 'failed')
        
        self.logger.warning(f"Task {task.id} moved to dead letter queue after {task.retry_count} retries")

# =============================================================================
# BATCH PROCESSING MANAGER
# =============================================================================

class BatchProcessingManager:
    """Manager for batch processing operations"""
    
    def __init__(self, queue_manager: RedisQueueManager, config: ETLConfig):
        self.queue_manager = queue_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def enqueue_batch(self, tasks: List[ETLTask]) -> List[str]:
        """Enqueue multiple tasks efficiently"""
        task_ids = []
        
        try:
            # Group tasks by stage and priority for batch processing
            grouped_tasks = self._group_tasks_by_queue(tasks)
            
            for (stage, priority), task_group in grouped_tasks.items():
                queue_name = self.queue_manager._get_queue_name(stage, priority)
                
                # Prepare batch data
                batch_data = {}
                for task in task_group:
                    task_data = json.dumps(task.to_dict(), default=str)
                    priority_score = self.queue_manager._calculate_priority_score(priority)
                    batch_data[task_data] = priority_score
                    task_ids.append(task.id)
                
                # Batch enqueue
                if batch_data:
                    await self.queue_manager.redis_client.zadd(queue_name, batch_data)
                    
                    # Update metrics
                    await self.queue_manager._update_queue_metrics(queue_name, 'batch_enqueued')
                    
                    self.logger.info(f"Batch enqueued {len(task_group)} tasks to {queue_name}")
            
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Failed to enqueue batch: {e}")
            raise
    
    def _group_tasks_by_queue(self, tasks: List[ETLTask]) -> Dict[tuple, List[ETLTask]]:
        """Group tasks by their target queue"""
        grouped = {}
        
        for task in tasks:
            key = (task.stage, task.priority)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(task)
        
        return grouped

# =============================================================================
# RATE LIMITING MANAGER
# =============================================================================

class RateLimitManager:
    """Distributed rate limiting using Redis"""
    
    def __init__(self, redis_client: redis.Redis, config: ETLConfig):
        self.redis = redis_client
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def check_rate_limit(self, resource: str, limit: int, window: int = 60) -> bool:
        """Check if resource is within rate limit"""
        try:
            key = f"rate_limit:{resource}"
            current_time = int(datetime.now().timestamp())
            window_start = current_time - window
            
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = await self.redis.zcard(key)
            
            if current_count >= limit:
                return False
            
            # Add current request
            await self.redis.zadd(key, {str(uuid.uuid4()): current_time})
            await self.redis.expire(key, window)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed for {resource}: {e}")
            return False
    
    async def get_rate_limit_status(self, resource: str) -> Dict[str, Any]:
        """Get current rate limit status"""
        try:
            key = f"rate_limit:{resource}"
            current_count = await self.redis.zcard(key)
            limit = self.config.RATE_LIMITS.get(resource, 100)
            
            return {
                'resource': resource,
                'current_count': current_count,
                'limit': limit,
                'remaining': max(0, limit - current_count),
                'reset_time': datetime.now() + timedelta(seconds=60)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get rate limit status for {resource}: {e}")
            return {'resource': resource, 'error': str(e)}

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of the queue manager"""
    config = ETLConfig()
    queue_manager = RedisQueueManager(config)
    
    await queue_manager.initialize()
    
    # Create a sample task
    task = ETLTask(
        id=str(uuid.uuid4()),
        stage=PipelineStage.INGESTION,
        priority=Priority.HIGH,
        source_type="rss",
        source_id="example_feed",
        payload={"url": "https://example.com/feed"},
        created_at=datetime.now()
    )
    
    # Enqueue task
    task_id = await queue_manager.enqueue_task(task)
    print(f"Enqueued task: {task_id}")
    
    # Get queue stats
    stats = await queue_manager.get_queue_stats()
    print(f"Queue stats: {stats}")
    
    # Dequeue task
    dequeued_task = await queue_manager.dequeue_task(PipelineStage.INGESTION)
    if dequeued_task:
        print(f"Dequeued task: {dequeued_task.id}")

if __name__ == "__main__":
    asyncio.run(example_usage())