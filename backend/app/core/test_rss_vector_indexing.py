"""
Test RSS Feed Integration with Pinecone Vector Indexing
======================================================

This script demonstrates the streamlined process for:
1. Fetching RSS feeds from known funders and AI organizations
2. Processing the feeds through your ETL pipeline
3. Indexing the opportunities in Pinecone with minimal validation (trusted sources)
4. Testing vector search capabilities with the Microsoft multilingual model

The focus is on speed and efficiency since these are known reliable sources.
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

import feedparser

from etl_architecture import ETLTask, PipelineStage, Priority
from etl_tasks import IngestionResult, process_rss_feed_task
from vector_indexing import vector_indexing_service, index_rss_feed_results
from vector_db_config import VectorIndexType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test RSS Feeds - curated list of AI funding sources with African focus
TEST_FEEDS = [
    {
        'feed_url': 'https://blog.google/outreach-initiatives/entrepreneurs/feed/',
        'feed_id': 'google_entrepreneurs',
        'description': 'Google Entrepreneur Initiatives'
    },
    {
        'feed_url': 'https://www.gatesfoundation.org/rss',
        'feed_id': 'gates_foundation',
        'description': 'Gates Foundation Announcements'
    },
    {
        'feed_url': 'https://www.worldbank.org/en/news/rss.xml',
        'feed_id': 'world_bank',
        'description': 'World Bank News'
    },
    {
        'feed_url': 'https://www.rockefellerfoundation.org/feed/',
        'feed_id': 'rockefeller',
        'description': 'Rockefeller Foundation News'
    }
]

async def test_rss_feed_indexing():
    """Test processing RSS feeds and indexing in Pinecone"""
    
    # Initialize the vector database service
    logger.info("Initializing vector database connection...")
    await vector_indexing_service.initialize()
    
    all_opportunities = []
    
    # Process each RSS feed
    for feed_info in TEST_FEEDS:
        feed_url = feed_info['feed_url']
        feed_id = feed_info['feed_id']
        
        logger.info(f"Processing RSS feed: {feed_url} ({feed_info['description']})")
        
        # Step 1: Create an ETL task for the RSS feed
        rss_task = ETLTask(
            id=f"test_rss_{feed_id}_{datetime.now().timestamp()}",
            stage=PipelineStage.INGESTION,
            priority=Priority.HIGH,
            created_at=datetime.now(),
            payload={
                'feed_url': feed_url,
                'feed_id': feed_id
            }
        )
        
        # Step 2: Process the RSS task
        logger.info(f"Fetching and extracting data from {feed_url}...")
        rss_result: IngestionResult = await process_rss_feed_task(rss_task)
        
        if not rss_result.success:
            logger.error(f"Failed to process RSS feed {feed_url}: {rss_result.error}")
            continue
        
        opportunities = rss_result.data.get('opportunities', [])
        logger.info(f"Successfully processed {feed_url}")
        logger.info(f"Found {len(opportunities)} opportunities")
        all_opportunities.extend(opportunities)
        
        # Step 3: Index the results in Pinecone (using the streamlined process for trusted sources)
        logger.info(f"Indexing {len(opportunities)} opportunities from {feed_url} in vector database...")
        indexing_result = await index_rss_feed_results(rss_result.data)
        
        if not indexing_result.success:
            logger.error(f"Failed to index opportunities from {feed_url}: {indexing_result.error}")
            continue
        
        indexed_count = indexing_result.data.get('indexed_count', 0)
        logger.info(f"Successfully indexed {indexed_count} opportunities from {feed_url}")
    
    logger.info(f"Total opportunities processed: {len(all_opportunities)}")
    logger.info("RSS feed processing and indexing completed")
    
    return all_opportunities

async def test_multilingual_search():
    """Test multilingual vector search on indexed RSS feed data"""
    # Initialize the vector database service if not already initialized
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Test queries in multiple languages
    test_queries = [
        # English
        "African startup funding for AI initiatives",
        # French
        "Financement pour l'innovation en Afrique",
        # Simple query
        "Grant opportunities for women in tech"
    ]
    
    logger.info("\nTesting vector search capabilities with multiple languages...")
    
    for query in test_queries:
        logger.info(f"\nSearching with query: '{query}'")
        
        try:
            # Use the Pinecone index directly for search (leveraging Microsoft's multilingual model)
            results = vector_indexing_service.index.query(
                top_k=5,
                namespace=VectorIndexType.OPPORTUNITIES.value,
                text=query,
                include_metadata=True,
                filter={
                    "source_type": {"$eq": "rss"}  # Filter to only show RSS results
                }
            )
            
            logger.info(f"Found {len(results.matches)} results")
            
            if not results.matches:
                logger.info("No matches found for this query.")
                continue
                
            for i, match in enumerate(results.matches):
                logger.info(f"{i+1}. Score: {match.score:.4f} - ID: {match.id}")
                
                if hasattr(match, 'metadata') and match.metadata:
                    metadata = match.metadata
                    logger.info(f"   Feed: {metadata.get('feed_id', 'Unknown')}")
                    logger.info(f"   Title: {metadata.get('title', 'Unknown')}")
                    logger.info(f"   Link: {metadata.get('link', 'No link')}")
                    
                    # Show geographic scope if available
                    geo_scopes = metadata.get('geographic_scopes')
                    if geo_scopes:
                        logger.info(f"   Geographic Scopes: {geo_scopes}")
                        
                    # Show confidence score
                    logger.info(f"   Confidence: {metadata.get('confidence_score', 'Unknown')}")
                    
            logger.info("-" * 60)
            
        except Exception as e:
            logger.error(f"Error testing vector search: {e}")

async def run_tests():
    """Run the complete RSS feed to vector database test"""
    try:
        # First, process the RSS feeds and index them
        opportunities = await test_rss_feed_indexing()
        
        # Wait a moment to ensure indexing is complete
        logger.info("Waiting 5 seconds for indexing to complete...")
        await asyncio.sleep(5)
        
        # Then test search capabilities
        await test_multilingual_search()
        
        logger.info("\nAll tests completed successfully!")
        return opportunities
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    try:
        opportunities = asyncio.run(run_tests())
        logger.info(f"Successfully processed and indexed {len(opportunities)} opportunities from trusted RSS feeds")
    except Exception as e:
        logger.error(f"Failed to run RSS vector indexing tests: {e}")
