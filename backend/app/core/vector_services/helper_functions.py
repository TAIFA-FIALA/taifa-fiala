"""
Vector Indexing Helper Functions
===============================

This module contains standalone helper functions for vector indexing operations,
providing a simplified interface for other parts of the application.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..etl_architecture import ETLTask, PipelineStage, Priority, ProcessingResult
from .indexing_service import VectorIndexingService, vector_indexing_service

logger = logging.getLogger(__name__)

# Helper functions for direct use from other modules
async def index_funding_opportunity(opportunity: Dict[str, Any], priority: Priority = Priority.NORMAL) -> ProcessingResult:
    """Index a single funding opportunity directly
    
    Args:
        opportunity: The opportunity data to index
        priority: Priority level for indexing task
        
    Returns:
        ProcessingResult with indexing status and details
    """
    task_id = f"idx_opp_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,
        created_at=datetime.now(),
        payload={
            'data_type': 'funding_opportunity',
            'funding_opportunity': opportunity
        }
    )
    
    # Initialize if needed
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Process directly
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result

async def index_organization(organization: Dict[str, Any], priority: Priority = Priority.NORMAL) -> ProcessingResult:
    """Index a single organization directly
    
    Args:
        organization: The organization data to index
        priority: Priority level for indexing task
        
    Returns:
        ProcessingResult with indexing status and details
    """
    task_id = f"idx_org_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,
        created_at=datetime.now(),
        payload={
            'data_type': 'organization',
            'organization': organization
        }
    )
    
    # Initialize if needed
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Process directly
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result

async def index_crawl4ai_results(crawl_results: Dict[str, Any], priority: Priority = Priority.MEDIUM) -> ProcessingResult:
    """Index crawl4ai results directly
    
    Args:
        crawl_results: The crawl4ai results to index
        priority: Priority level for indexing task
        
    Returns:
        ProcessingResult with indexing status and details
    """
    task_id = f"idx_crawl4ai_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,
        created_at=datetime.now(),
        payload={
            'data_type': 'crawl4ai_result',
            'data': crawl_results
        }
    )
    
    # Initialize if needed
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Process directly
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result

async def index_rss_feed_results(rss_results: Dict[str, Any], priority: Priority = Priority.HIGH) -> ProcessingResult:
    """Index RSS feed results directly
    
    Args:
        rss_results: The RSS feed results to index
        priority: Priority level for indexing task
        
    Returns:
        ProcessingResult with indexing status and details
    """
    task_id = f"idx_rss_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,
        created_at=datetime.now(),
        payload={
            'data_type': 'rss_feed_result',
            'data': rss_results
        }
    )
    
    # Initialize if needed
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Process directly
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result
