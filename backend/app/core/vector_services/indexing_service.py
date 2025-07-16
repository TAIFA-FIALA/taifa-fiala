"""
Vector Indexing Integration for ETL Pipeline
============================================

This module integrates Pinecone vector database indexing into the ETL pipeline,
specifically focusing on processing data from various sources and providing semantic search capabilities.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

from ..etl_architecture import ETLTask, PipelineStage, Priority, ProcessingResult
from .pinecone_config import PineconeConfig, VectorIndexType, default_config
from ...models.funding import FundingOpportunity
from ...models.organization import Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VectorIndexingService:
    """Service for indexing ETL pipeline data in Pinecone vector database"""
    
    def __init__(self, config: PineconeConfig = default_config):
        self.config = config
        self.pinecone_client = None
        self.index = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize connection to Pinecone"""
        if self.initialized:
            return True
            
        if not self.config.api_key:
            self.logger.error("Pinecone API key not provided")
            return False
            
        try:
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(api_key=self.config.api_key)
            
            # Check if index exists
            index_list = self.pinecone_client.list_indexes()
            if self.config.index_name not in index_list.names():
                self.logger.error(f"Index {self.config.index_name} does not exist")
                return False
                
            # Get the index
            self.index = self.pinecone_client.Index(self.config.index_name)
            self.initialized = True
            self.logger.info(f"Successfully connected to Pinecone index: {self.config.index_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"Pinecone initialization error: {e}")
            return False
    
    async def process_indexing_task(self, task: ETLTask) -> ProcessingResult:
        """Process an indexing task based on data type"""
        if not await self.initialize():
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error="Vector indexing service not initialized"
            )
            
        data_type = task.payload.get('data_type')
        
        # Route to appropriate processor based on data type
        try:
            if data_type == 'funding_opportunity':
                return await self._index_funding_opportunity(task)
            elif data_type == 'organization':
                return await self._index_organization(task)
            elif data_type == 'crawl4ai_result':
                return await self._index_crawl4ai_result(task)
            elif data_type == 'rss_feed_result':
                return await self._index_rss_feed_result(task)
            else:
                return ProcessingResult(
                    task_id=task.id,
                    stage=PipelineStage.INDEXING,
                    success=False,
                    error=f"Unknown data type for indexing: {data_type}"
                )
        except Exception as e:
            self.logger.error(f"Error processing indexing task {task.id}: {e}")
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
