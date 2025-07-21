"""
Example Usage of the AI-Powered Funding Intelligence Pipeline
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"

This file demonstrates how to use the funding intelligence pipeline components.
"""

import asyncio
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the funding intelligence components
from . import (
    FundingIntelligencePipeline,
    ProcessingMode,
    create_funding_intelligence_pipeline,
    get_module_info
)


async def example_full_pipeline():
    """
    Example: Run the complete funding intelligence pipeline
    """
    logger.info("=== Full Pipeline Example ===")
    
    # Create pipeline with default configuration
    pipeline = create_funding_intelligence_pipeline()
    
    # Initialize database connections
    await pipeline.initialize_database_connections()
    
    # Run the complete pipeline
    stats = await pipeline.process_funding_intelligence(
        search_mode="comprehensive",
        processing_mode=ProcessingMode.BATCH
    )
    
    logger.info(f"Pipeline completed with stats: {stats}")
    
    # Get pipeline status
    status = await pipeline.get_pipeline_status()
    logger.info(f"Pipeline status: {status}")
    
    return stats


async def example_search_funding_intelligence():
    """
    Example: Search for funding intelligence using semantic search
    """
    logger.info("=== Semantic Search Example ===")
    
    pipeline = create_funding_intelligence_pipeline()
    
    # Search for AI intelligence feed
    query = "AI startups Africa machine learning funding grants"
    results = await pipeline.search_funding_intelligence(query)
    
    logger.info(f"Search results for '{query}': {results}")
    
    return results


async def example_investigate_signal():
    """
    Example: Investigate a specific funding signal
    """
    logger.info("=== Signal Investigation Example ===")
    
    pipeline = create_funding_intelligence_pipeline()
    
    # Investigate a specific signal
    signal_id = "signal_123"
    investigation = await pipeline.investigate_specific_signal(signal_id)
    
    logger.info(f"Investigation results: {investigation}")
    
    return investigation


async def example_scheduled_pipeline():
    """
    Example: Run scheduled pipeline (commented out to avoid long-running process)
    """
    logger.info("=== Scheduled Pipeline Example ===")
    
    pipeline = create_funding_intelligence_pipeline()
    
    # This would run continuously every 6 hours
    # await pipeline.run_scheduled_pipeline(interval_hours=6)
    
    logger.info("Scheduled pipeline would run every 6 hours")


async def example_component_usage():
    """
    Example: Use individual components
    """
    logger.info("=== Individual Component Usage ===")
    
    # Import individual components
    from .search_strategy import WideNetSearchModule
    from .content_analyzer import AIFundingIntelligence
    from .entity_extraction import FundingEntityExtractor
    from .opportunity_predictor import OpportunityPredictor
    
    # 1. Search for content
    search_module = WideNetSearchModule()
    search_results = await search_module.cast_net("targeted")
    logger.info(f"Search found {len(search_results.get('content', []))} items")
    
    # 2. Analyze content
    content_analyzer = AIFundingIntelligence()
    if search_results.get('content'):
        analyzed = await content_analyzer.analyze_for_funding_relevance(search_results['content'][0])
        logger.info(f"Content analysis: {analyzed.has_funding_implications}")
    
    # 3. Extract entities
    entity_extractor = FundingEntityExtractor()
    if search_results.get('content'):
        entities = await entity_extractor.extract_entities(
            search_results['content'][0].get('content', '')
        )
        logger.info(f"Extracted entities: {list(entities.keys())}")
    
    # 4. Predict opportunities
    opportunity_predictor = OpportunityPredictor()
    mock_events = [{'signal_type': 'partnership_announcement', 'content': 'Test content'}]
    opportunities = await opportunity_predictor.predict_opportunities(mock_events)
    logger.info(f"Predicted {len(opportunities)} opportunities")


async def example_vector_database():
    """
    Example: Use vector database for semantic search
    """
    logger.info("=== Vector Database Example ===")
    
    # Check if required environment variables are set
    if not os.getenv('PINECONE_API_KEY'):
        logger.warning("PINECONE_API_KEY not set, skipping vector database example")
        return
    
    from .vector_intelligence import FundingIntelligenceVectorDB
    
    # Create vector database connection
    vector_db = FundingIntelligenceVectorDB(use_integrated_embedding=True)
    
    # Example funding signal data
    signal_data = {
        'id': 'test_signal_1',
        'title': 'Google AI for Africa Initiative',
        'content': 'Google announces new AI initiative for African startups with $10M funding',
        'signal_type': 'partnership_announcement',
        'funding_type': 'direct',
        'confidence_score': 0.9,
        'extracted_entities': {
            'funders': ['Google'],
            'recipients': ['African startups'],
            'amounts': ['$10M'],
            'locations': ['Africa']
        }
    }
    
    # Upsert to vector database
    success = await vector_db.upsert_funding_signal(signal_data)
    logger.info(f"Vector upsert successful: {success}")
    
    # Search similar content
    similar_results = await vector_db.semantic_search(
        "AI funding Africa startups",
        document_type="funding_signal",
        top_k=5
    )
    logger.info(f"Found {len(similar_results)} similar signals")


async def example_database_schema():
    """
    Example: Show how to apply the database schema
    """
    logger.info("=== Database Schema Example ===")
    
    logger.info("To apply the funding intelligence schema to Supabase:")
    logger.info("1. Set environment variables:")
    logger.info("   export SUPABASE_URL='your-supabase-url'")
    logger.info("   export SUPABASE_API_KEY='your-api-key'")
    logger.info("2. Run the setup script:")
    logger.info("   python scripts/supabase_funding_intelligence.py")
    logger.info("3. Or use the SQL migration:")
    logger.info("   python scripts/apply_funding_intelligence_schema.py")


def print_module_info():
    """Print module information"""
    info = get_module_info()
    logger.info("=== Module Information ===")
    logger.info(f"Name: {info['name']}")
    logger.info(f"Version: {info['version']}")
    logger.info(f"Author: {info['author']}")
    logger.info(f"Description: {info['description']}")
    logger.info(f"Components: {info['components']}")
    logger.info(f"Default config: {info['default_config']}")


async def main():
    """
    Main function to run all examples
    """
    logger.info("🚀 Starting Funding Intelligence Pipeline Examples")
    
    # Print module information
    print_module_info()
    
    # Run examples
    try:
        # Example 1: Individual components
        await example_component_usage()
        
        # Example 2: Search functionality
        await example_search_funding_intelligence()
        
        # Example 3: Signal investigation
        await example_investigate_signal()
        
        # Example 4: Vector database (if configured)
        await example_vector_database()
        
        # Example 5: Database schema info
        await example_database_schema()
        
        # Example 6: Full pipeline (commented out as it requires full setup)
        # await example_full_pipeline()
        
        # Example 7: Scheduled pipeline info
        await example_scheduled_pipeline()
        
        logger.info("✅ All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())