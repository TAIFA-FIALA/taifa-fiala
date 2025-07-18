"""
Vector database services package for TAIFA-FIALA.
Handles semantic search functionality via Pinecone.
"""

from .pinecone_config import PineconeConfig, VectorIndexType, default_config
from .indexing_service import (
    VectorIndexingService, 
    vector_indexing_service,
    index_intelligence_item, 
    index_organization,
    index_crawl4ai_results,
    index_rss_feed_results
)
