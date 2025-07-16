"""
Test script for integrating Crawl4AI with Pinecone Vector Indexing
==================================================================

This script demonstrates the end-to-end process of:
1. Crawling funding opportunities using Crawl4AI
2. Processing the extracted data through your ETL pipeline
3. Indexing the opportunities in Pinecone with the Microsoft multilingual model
4. Testing vector search capabilities with multilingual queries
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any


from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

from etl_architecture import ETLTask, PipelineStage, Priority
from etl_tasks import IngestionResult, process_crawl4ai_task
from vector_indexing import vector_indexing_service, index_crawl4ai_results
from vector_db_config import VectorIndexType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables


# Test URLs - funding opportunities for African AI initiatives
TEST_URLS = [
    "https://www.convergence.finance/funding-opportunities",
    "https://www.gatesfoundation.org/ideas/articles/artificial-intelligence-funding-announcement",
    "https://africa.googleblog.com/2023/10/applications-are-open-for-google-for.html",
    "https://aimultiple.com/african-venture-capital"
]

async def test_crawl_and_index():
    """Test crawling URLs and indexing the extracted data"""
    
    # Initialize the vector database service
    logger.info("Initializing vector database connection...")
    await vector_indexing_service.initialize()
    
    # Process each URL
    for url in TEST_URLS:
        logger.info(f"Processing URL: {url}")
        
        # Step 1: Create an ETL task for crawl4ai
        crawl_task = ETLTask(
            id=f"test_crawl_{datetime.now().timestamp()}",
            stage=PipelineStage.INGESTION,
            priority=Priority.HIGH,
            created_at=datetime.now(),
            payload={
                'url': url,
                'context': 'African AI funding opportunity',
                'extraction_type': 'funding_opportunity'
            }
        )
        
        # Step 2: Process the crawl task
        logger.info(f"Crawling and extracting data from {url}...")
        crawl_result: IngestionResult = await process_crawl4ai_task(crawl_task)
        
        if not crawl_result.success:
            logger.error(f"Failed to crawl {url}: {crawl_result.error}")
            continue
        
        logger.info(f"Successfully crawled {url}")
        logger.info(f"Found {len(crawl_result.data.get('opportunities', []))} opportunities")
        
        # Step 3: Index the results in Pinecone
        logger.info("Indexing extracted opportunities in vector database...")
        indexing_result = await index_crawl4ai_results(crawl_result.data)
        
        if not indexing_result.success:
            logger.error(f"Failed to index opportunities: {indexing_result.error}")
            continue
        
        logger.info(f"Successfully indexed {indexing_result.data.get('indexed_count', 0)} opportunities")
    
    logger.info("Crawl and index process completed")

async def test_vector_search():
    """Test multilingual vector search capabilities"""
    # Initialize the vector database service if not already initialized
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Test queries in multiple languages to verify multilingual capabilities
    test_queries = [
        # English
        "AI funding for healthcare startups in East Africa",
        # French
        "Financement pour les startups technologiques en Afrique de l'Ouest",
        # Swahili (approximate)
        "Ufadhili wa AI kwa biashara chipukizi Afrika"
    ]
    
    for query in test_queries:
        logger.info(f"Testing vector search with query: '{query}'")
        
        try:
            # Use the Pinecone index directly for search
            results = vector_indexing_service.index.query(
                top_k=5,
                namespace=VectorIndexType.OPPORTUNITIES.value,
                text=query,  # Pinecone will use Microsoft multilingual model
                include_metadata=True
            )
            
            logger.info(f"Found {len(results.matches)} results")
            for i, match in enumerate(results.matches):
                logger.info(f"{i+1}. Score: {match.score:.4f} - ID: {match.id}")
                if hasattr(match, 'metadata') and match.metadata:
                    logger.info(f"   Title: {match.metadata.get('title', 'Unknown')}")
                    logger.info(f"   Funding: {match.metadata.get('funding_amount', 'Unknown')} {match.metadata.get('currency', '')}")
                    
                    # Show equity-aware metadata if available
                    geo_scopes = match.metadata.get('geographic_scopes')
                    if geo_scopes:
                        logger.info(f"   Geographic Scopes: {geo_scopes}")
                    
                    for indicator in ["women_focus", "youth_focus", "underserved_focus"]:
                        if indicator in match.metadata:
                            logger.info(f"   {indicator.replace('_', ' ').title()}: {match.metadata.get(indicator)}")
            
            logger.info("-" * 50)
            
        except Exception as e:
            logger.error(f"Error testing vector search: {e}")

async def run_all_tests():
    """Run all test functions"""
    # First, crawl and index
    await test_crawl_and_index()
    
    # Then test search capabilities
    logger.info("\nTesting vector search capabilities...")
    await test_vector_search()
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
