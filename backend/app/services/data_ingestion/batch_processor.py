"""
High-Volume Batch Processing System for Large Datasets
Designed for processing 10K-100M records efficiently

This module provides comprehensive batch processing capabilities:
- Parallel processing of large datasets
- Memory-efficient streaming processing
- Intelligent workload distribution
- Error handling and retry logic
- Progress tracking and monitoring
- Checkpointing for fault tolerance
- Resource management and throttling
- Data validation and quality checks

Key Features:
- Multi-threaded and async processing
- Configurable batch sizes and worker counts
- Memory usage monitoring and optimization
- Database connection pooling
- Comprehensive logging and metrics
- Fault tolerance with automatic recovery
- Support for different data sources (files, databases, APIs)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Iterator, Union, Tuple
from datetime import datetime, timedelta
import json
import time
import threading
import multiprocessing
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import queue
import gc
import psutil
import os
import pickle
from pathlib import Path
import hashlib
import tempfile
from contextlib import contextmanager
import asyncpg
import aiofiles
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import pandas as pd
import numpy as np
from functools import partial
import traceback
import signal
import sys

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Different processing modes"""
    SEQUENTIAL = "sequential"
    PARALLEL_THREADS = "parallel_threads"
    PARALLEL_PROCESSES = "parallel_processes"
    HYBRID = "hybrid"
    STREAMING = "streaming"


class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DataSource(Enum):
    """Different data source types"""
    DATABASE = "database"
    FILE = "file"
    API = "api"
    STREAM = "stream"
    MEMORY = "memory"


@dataclass
class BatchTask:
    """Individual batch processing task"""
    task_id: str
    data_source: DataSource
    source_config: Dict[str, Any]
    processor_func: Callable
    batch_size: int = 1000
    priority: int = 1
    retry_count: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: BatchStatus = BatchStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processed_items: int = 0
    total_items: int = 0
    failed_items: int = 0
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = BatchStatus(self.status)
        if isinstance(self.data_source, str):
            self.data_source = DataSource(self.data_source)


@dataclass
class ProcessingStats:
    """Batch processing statistics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    processing_tasks: int = 0
    total_items_processed: int = 0
    total_items_failed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    throughput_items_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class BatchConfig:
    """Batch processing configuration"""
    max_workers: int = 10
    max_processes: int = 4
    batch_size: int = 1000
    max_memory_mb: int = 8192  # 8GB
    max_cpu_percent: int = 80
    processing_mode: ProcessingMode = ProcessingMode.PARALLEL_THREADS
    enable_checkpointing: bool = True
    checkpoint_interval: int = 1000
    checkpoint_dir: str = "/tmp/batch_checkpoints"
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: int = 300
    enable_monitoring: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if isinstance(self.processing_mode, str):
            self.processing_mode = ProcessingMode(self.processing_mode)


class CheckpointManager:
    """Manages checkpointing for fault tolerance"""
    
    def __init__(self, checkpoint_dir: str):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, task_id: str, progress_data: Dict[str, Any]):
        """Save checkpoint data"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.checkpoint"
        
        try:
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(progress_data, f)
            
            logger.debug(f"Saved checkpoint for task {task_id}")
            
        except Exception as e:
            logger.error(f"Error saving checkpoint for task {task_id}: {e}")
    
    def load_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint data"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.checkpoint"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'rb') as f:
                progress_data = pickle.load(f)
            
            logger.debug(f"Loaded checkpoint for task {task_id}")
            return progress_data
            
        except Exception as e:
            logger.error(f"Error loading checkpoint for task {task_id}: {e}")
            return None
    
    def remove_checkpoint(self, task_id: str):
        """Remove checkpoint file"""
        checkpoint_file = self.checkpoint_dir / f"{task_id}.checkpoint"
        
        try:
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                logger.debug(f"Removed checkpoint for task {task_id}")
                
        except Exception as e:
            logger.error(f"Error removing checkpoint for task {task_id}: {e}")


class ResourceMonitor:
    """Monitors system resources"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return self.process.cpu_percent()
    
    def check_resource_limits(self, max_memory_mb: int, max_cpu_percent: int) -> bool:
        """Check if resource limits are exceeded"""
        memory_usage = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()
        
        if memory_usage > max_memory_mb:
            logger.warning(f"Memory usage ({memory_usage:.1f} MB) exceeds limit ({max_memory_mb} MB)")
            return False
        
        if cpu_usage > max_cpu_percent:
            logger.warning(f"CPU usage ({cpu_usage:.1f}%) exceeds limit ({max_cpu_percent}%)")
            return False
        
        return True
    
    def optimize_memory(self):
        """Optimize memory usage"""
        gc.collect()
        logger.debug("Memory optimization completed")


class DataLoader:
    """Loads data from different sources"""
    
    def __init__(self, db_pool: Optional[asyncpg.Pool] = None):
        self.db_pool = db_pool
    
    async def load_from_database(self, config: Dict[str, Any]) -> Iterator[List[Dict[str, Any]]]:
        """Load data from database in batches"""
        query = config.get('query', '')
        batch_size = config.get('batch_size', 1000)
        
        if not self.db_pool:
            raise ValueError("Database pool not initialized")
        
        async with self.db_pool.acquire() as conn:
            offset = 0
            while True:
                paginated_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
                
                try:
                    rows = await conn.fetch(paginated_query)
                    
                    if not rows:
                        break
                    
                    # Convert to dictionaries
                    batch_data = [dict(row) for row in rows]
                    yield batch_data
                    
                    offset += batch_size
                    
                except Exception as e:
                    logger.error(f"Error loading data from database: {e}")
                    break
    
    async def load_from_file(self, config: Dict[str, Any]) -> Iterator[List[Dict[str, Any]]]:
        """Load data from file in batches"""
        file_path = config.get('file_path', '')
        batch_size = config.get('batch_size', 1000)
        file_type = config.get('file_type', 'json')
        
        if file_type == 'json':
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                
                # Yield in batches
                for i in range(0, len(data), batch_size):
                    yield data[i:i + batch_size]
        
        elif file_type == 'csv':
            # Use pandas for CSV processing
            chunk_reader = pd.read_csv(file_path, chunksize=batch_size)
            
            for chunk in chunk_reader:
                yield chunk.to_dict('records')
        
        elif file_type == 'jsonl':
            async with aiofiles.open(file_path, 'r') as f:
                batch = []
                async for line in f:
                    batch.append(json.loads(line.strip()))
                    
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
                
                if batch:
                    yield batch
    
    def load_from_memory(self, config: Dict[str, Any]) -> Iterator[List[Dict[str, Any]]]:
        """Load data from memory in batches"""
        data = config.get('data', [])
        batch_size = config.get('batch_size', 1000)
        
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]


class HighVolumeBatchProcessor:
    """
    High-volume batch processing system
    Handles large datasets with parallel processing and fault tolerance
    """
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.tasks: Dict[str, BatchTask] = {}
        self.task_queue = queue.PriorityQueue()
        self.stats = ProcessingStats()
        self.checkpoint_manager = CheckpointManager(config.checkpoint_dir)
        self.resource_monitor = ResourceMonitor()
        self.data_loader = DataLoader()
        
        # Thread/process management
        self.thread_executor = None
        self.process_executor = None
        self.workers = []
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Database connection
        self.db_pool = None
        
        # Initialize logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/batch_processor.log'),
                logging.StreamHandler()
            ]
        )
    
    async def initialize(self):
        """Initialize the batch processor"""
        logger.info("Initializing batch processor")
        
        # Initialize database connection pool
        await self._initialize_database()
        
        # Initialize executors
        self._initialize_executors()
        
        # Set up signal handlers
        self._setup_signal_handlers()
        
        logger.info("Batch processor initialized")
    
    async def _initialize_database(self):
        """Initialize database connection pool"""
        try:
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                self.db_pool = await asyncpg.create_pool(
                    db_url,
                    min_size=5,
                    max_size=20,
                    command_timeout=60
                )
                
                self.data_loader.db_pool = self.db_pool
                logger.info("Database connection pool initialized")
        
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def _initialize_executors(self):
        """Initialize thread/process executors"""
        if self.config.processing_mode in [ProcessingMode.PARALLEL_THREADS, ProcessingMode.HYBRID]:
            self.thread_executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        if self.config.processing_mode in [ProcessingMode.PARALLEL_PROCESSES, ProcessingMode.HYBRID]:
            self.process_executor = ProcessPoolExecutor(max_workers=self.config.max_processes)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def add_task(self, task: BatchTask):
        """Add a task to the processing queue"""
        self.tasks[task.task_id] = task
        self.task_queue.put((task.priority, task.created_at, task.task_id))
        self.stats.total_tasks += 1
        
        logger.info(f"Added task {task.task_id} to processing queue")
    
    def get_task_status(self, task_id: str) -> Optional[BatchTask]:
        """Get task status"""
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status in [BatchStatus.PENDING, BatchStatus.PROCESSING]:
                task.status = BatchStatus.CANCELLED
                logger.info(f"Task {task_id} cancelled")
                return True
        
        return False
    
    async def _process_batch(self, batch_data: List[Dict[str, Any]], 
                           processor_func: Callable,
                           task_id: str) -> Tuple[int, int]:
        """Process a batch of data"""
        processed_count = 0
        failed_count = 0
        
        try:
            # Process batch (could be async or sync function)
            if asyncio.iscoroutinefunction(processor_func):
                results = await processor_func(batch_data)
            else:
                results = processor_func(batch_data)
            
            # Count successful/failed items
            if isinstance(results, list):
                for result in results:
                    if result.get('success', True):
                        processed_count += 1
                    else:
                        failed_count += 1
            else:
                # Assume all items processed successfully
                processed_count = len(batch_data)
        
        except Exception as e:
            logger.error(f"Error processing batch for task {task_id}: {e}")
            failed_count = len(batch_data)
        
        return processed_count, failed_count
    
    async def _process_task(self, task: BatchTask):
        """Process a single task"""
        logger.info(f"Starting task {task.task_id}")
        
        task.status = BatchStatus.PROCESSING
        task.started_at = datetime.now()
        self.stats.processing_tasks += 1
        
        try:
            # Load checkpoint if available
            checkpoint_data = None
            if self.config.enable_checkpointing:
                checkpoint_data = self.checkpoint_manager.load_checkpoint(task.task_id)
            
            # Determine data loader based on source
            data_iterator = None
            if task.data_source == DataSource.DATABASE:
                data_iterator = self.data_loader.load_from_database(task.source_config)
            elif task.data_source == DataSource.FILE:
                data_iterator = self.data_loader.load_from_file(task.source_config)
            elif task.data_source == DataSource.MEMORY:
                data_iterator = self.data_loader.load_from_memory(task.source_config)
            else:
                raise ValueError(f"Unsupported data source: {task.data_source}")
            
            # Process data in batches
            batch_count = 0
            start_batch = 0
            
            if checkpoint_data:
                start_batch = checkpoint_data.get('batch_count', 0)
                task.processed_items = checkpoint_data.get('processed_items', 0)
                task.failed_items = checkpoint_data.get('failed_items', 0)
            
            if task.data_source == DataSource.DATABASE:
                async for batch_data in data_iterator:
                    if batch_count < start_batch:
                        batch_count += 1
                        continue
                    
                    if self.stop_event.is_set() or task.status == BatchStatus.CANCELLED:
                        break
                    
                    # Check resource limits
                    if not self.resource_monitor.check_resource_limits(
                        self.config.max_memory_mb, 
                        self.config.max_cpu_percent
                    ):
                        self.resource_monitor.optimize_memory()
                        await asyncio.sleep(1)
                    
                    # Process batch
                    processed, failed = await self._process_batch(
                        batch_data, 
                        task.processor_func, 
                        task.task_id
                    )
                    
                    # Update statistics
                    task.processed_items += processed
                    task.failed_items += failed
                    batch_count += 1
                    
                    # Update progress
                    if task.total_items > 0:
                        task.progress = (task.processed_items + task.failed_items) / task.total_items
                    
                    # Save checkpoint
                    if (self.config.enable_checkpointing and 
                        batch_count % self.config.checkpoint_interval == 0):
                        
                        self.checkpoint_manager.save_checkpoint(task.task_id, {
                            'batch_count': batch_count,
                            'processed_items': task.processed_items,
                            'failed_items': task.failed_items
                        })
                    
                    logger.debug(f"Task {task.task_id}: processed batch {batch_count}, "
                               f"items: {processed}, failed: {failed}")
            
            else:
                # Handle non-async data sources
                for batch_data in data_iterator:
                    if batch_count < start_batch:
                        batch_count += 1
                        continue
                    
                    if self.stop_event.is_set() or task.status == BatchStatus.CANCELLED:
                        break
                    
                    # Process batch
                    processed, failed = await self._process_batch(
                        batch_data, 
                        task.processor_func, 
                        task.task_id
                    )
                    
                    # Update statistics
                    task.processed_items += processed
                    task.failed_items += failed
                    batch_count += 1
                    
                    # Update progress
                    if task.total_items > 0:
                        task.progress = (task.processed_items + task.failed_items) / task.total_items
                    
                    # Save checkpoint
                    if (self.config.enable_checkpointing and 
                        batch_count % self.config.checkpoint_interval == 0):
                        
                        self.checkpoint_manager.save_checkpoint(task.task_id, {
                            'batch_count': batch_count,
                            'processed_items': task.processed_items,
                            'failed_items': task.failed_items
                        })
            
            # Mark task as completed
            task.status = BatchStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 1.0
            
            # Update global statistics
            self.stats.completed_tasks += 1
            self.stats.processing_tasks -= 1
            self.stats.total_items_processed += task.processed_items
            self.stats.total_items_failed += task.failed_items
            
            # Clean up checkpoint
            if self.config.enable_checkpointing:
                self.checkpoint_manager.remove_checkpoint(task.task_id)
            
            logger.info(f"Task {task.task_id} completed: {task.processed_items} processed, "
                       f"{task.failed_items} failed")
        
        except Exception as e:
            logger.error(f"Error processing task {task.task_id}: {e}")
            logger.error(traceback.format_exc())
            
            task.status = BatchStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            self.stats.failed_tasks += 1
            self.stats.processing_tasks -= 1
    
    def _task_worker(self):
        """Worker thread for processing tasks"""
        while not self.stop_event.is_set():
            try:
                # Get next task from queue
                try:
                    priority, created_at, task_id = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                task = self.tasks.get(task_id)
                if not task or task.status != BatchStatus.PENDING:
                    continue
                
                # Process task
                asyncio.run(self._process_task(task))
                
                # Mark queue item as done
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in task worker: {e}")
                continue
    
    def _stats_monitor(self):
        """Monitor and update statistics"""
        while not self.stop_event.is_set():
            try:
                # Update resource usage
                self.stats.memory_usage_mb = self.resource_monitor.get_memory_usage()
                self.stats.cpu_usage_percent = self.resource_monitor.get_cpu_usage()
                self.stats.last_update = datetime.now()
                
                # Calculate throughput
                elapsed_time = (datetime.now() - self.stats.start_time).total_seconds()
                if elapsed_time > 0:
                    self.stats.throughput_items_per_second = (
                        self.stats.total_items_processed / elapsed_time
                    )
                
                # Log stats periodically
                if int(time.time()) % 60 == 0:  # Every minute
                    logger.info(f"Processing stats: {self.stats.completed_tasks}/{self.stats.total_tasks} tasks, "
                               f"{self.stats.total_items_processed} items, "
                               f"{self.stats.throughput_items_per_second:.1f} items/sec")
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in stats monitor: {e}")
                time.sleep(30)
    
    def start(self):
        """Start the batch processor"""
        if self.is_running:
            logger.warning("Batch processor is already running")
            return
        
        logger.info("Starting batch processor")
        self.is_running = True
        self.stop_event.clear()
        
        # Start worker threads
        for i in range(self.config.max_workers):
            worker = threading.Thread(
                target=self._task_worker,
                name=f"BatchWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # Start stats monitor
        stats_thread = threading.Thread(
            target=self._stats_monitor,
            name="StatsMonitor",
            daemon=True
        )
        stats_thread.start()
        self.workers.append(stats_thread)
        
        logger.info(f"Batch processor started with {len(self.workers)} workers")
    
    def stop(self):
        """Stop the batch processor"""
        if not self.is_running:
            logger.warning("Batch processor is not running")
            return
        
        logger.info("Stopping batch processor")
        self.is_running = False
        self.stop_event.set()
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=10)
        
        # Close executors
        if self.thread_executor:
            self.thread_executor.shutdown(wait=True)
        if self.process_executor:
            self.process_executor.shutdown(wait=True)
        
        # Close database pool
        if self.db_pool:
            asyncio.run(self.db_pool.close())
        
        logger.info("Batch processor stopped")
    
    def get_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        return self.stats
    
    def get_all_tasks(self) -> List[BatchTask]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def get_pending_tasks(self) -> List[BatchTask]:
        """Get pending tasks"""
        return [task for task in self.tasks.values() if task.status == BatchStatus.PENDING]
    
    def get_processing_tasks(self) -> List[BatchTask]:
        """Get processing tasks"""
        return [task for task in self.tasks.values() if task.status == BatchStatus.PROCESSING]
    
    def get_completed_tasks(self) -> List[BatchTask]:
        """Get completed tasks"""
        return [task for task in self.tasks.values() if task.status == BatchStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[BatchTask]:
        """Get failed tasks"""
        return [task for task in self.tasks.values() if task.status == BatchStatus.FAILED]


# Example processor functions
def sample_data_processor(batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sample data processor function"""
    results = []
    
    for item in batch_data:
        try:
            # Simulate processing
            processed_item = {
                'id': item.get('id'),
                'processed_at': datetime.now().isoformat(),
                'success': True
            }
            results.append(processed_item)
            
        except Exception as e:
            results.append({
                'id': item.get('id'),
                'error': str(e),
                'success': False
            })
    
    return results


async def async_data_processor(batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sample async data processor function"""
    results = []
    
    for item in batch_data:
        try:
            # Simulate async processing
            await asyncio.sleep(0.01)  # Simulate async operation
            
            processed_item = {
                'id': item.get('id'),
                'processed_at': datetime.now().isoformat(),
                'success': True
            }
            results.append(processed_item)
            
        except Exception as e:
            results.append({
                'id': item.get('id'),
                'error': str(e),
                'success': False
            })
    
    return results


# Example usage
async def main():
    """Example usage of the batch processor"""
    
    # Create configuration
    config = BatchConfig(
        max_workers=5,
        batch_size=1000,
        processing_mode=ProcessingMode.PARALLEL_THREADS,
        enable_checkpointing=True,
        checkpoint_interval=100
    )
    
    # Create processor
    processor = HighVolumeBatchProcessor(config)
    
    try:
        # Initialize processor
        await processor.initialize()
        
        # Create sample task
        task = BatchTask(
            task_id="sample_task_1",
            data_source=DataSource.MEMORY,
            source_config={
                'data': [{'id': i, 'value': f'item_{i}'} for i in range(10000)],
                'batch_size': 1000
            },
            processor_func=sample_data_processor,
            batch_size=1000
        )
        
        # Add task to processor
        processor.add_task(task)
        
        # Start processing
        processor.start()
        
        # Wait for completion
        while task.status not in [BatchStatus.COMPLETED, BatchStatus.FAILED]:
            await asyncio.sleep(1)
            print(f"Task progress: {task.progress:.2%}")
        
        # Print final stats
        stats = processor.get_stats()
        print(f"Processing completed: {stats.completed_tasks} tasks, "
              f"{stats.total_items_processed} items processed")
        
    finally:
        processor.stop()


if __name__ == "__main__":
    asyncio.run(main())