"""
Advanced Vector Search Testing for TAIFA-FIALA
==============================================

This script demonstrates the advanced vector search capabilities with filtering 
based on organization roles (provider/recipient) and funding type categories 
(grant/investment) in the TAIFA-FIALA platform.
"""

import asyncio
import os
import logging
from datetime import datetime, timedelta
from pprint import pprint
from dotenv import load_dotenv

from vector_indexing import VectorIndexingService, index_rss_feed_results
from vector_db_config import PineconeConfig, VectorIndexType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables


# Check required environment variables
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')

if not pinecone_api_key or not pinecone_index_name:
    print("\nEnvironment Setup Required:")
    print("----------------------------")
    print("Please set the following environment variables in your .env file:")
    if not pinecone_api_key:
        print("- PINECONE_API_KEY: Your Pinecone API key")
    if not pinecone_index_name:
        print("- PINECONE_INDEX_NAME: Name of your Pinecone index")
    print("\nExample .env file:")
    print("PINECONE_API_KEY=your-api-key-here")
    print("PINECONE_INDEX_NAME=taifa-fiala-index")
    print("\nMake sure your Pinecone index is created with dimensionality 1024 (for multilingual-e5-large).")
    exit(1)

async def run_vector_search_tests():
    """Run a series of advanced vector search tests demonstrating filters"""
    
    # Initialize the vector indexing service
    vector_service = VectorIndexingService()
    await vector_service.initialize()
    
    print("\n==== TAIFA-FIALA Advanced Vector Search Testing ====\n")
    
    # 1. Test searching for grant opportunities from granting agencies
    print("\n=== Test 1: Searching for Grant Funding Opportunities ===")
    grant_query = "research grants for AI projects in Africa"
    grant_results = await search_with_filters(
        vector_service, 
        query=grant_query,
        filters={
            "is_grant": True,
            "provider_type": "granting_agency"
        },
        top_k=3
    )
    
    # 2. Test searching for investment opportunities for startups
    print("\n=== Test 2: Searching for Investment Funding Opportunities ===")
    investment_query = "seed funding for AI startups in Nigeria"
    investment_results = await search_with_filters(
        vector_service,
        query=investment_query,
        filters={
            "is_investment": True,
            "recipient_type": "startup"
        },
        top_k=3
    )
    
    # 3. Test searching for accelerator programs with equity component
    print("\n=== Test 3: Searching for Accelerator Programs with Equity Component ===")
    accelerator_query = "AI accelerator programs in Africa"
    accelerator_results = await search_with_filters(
        vector_service,
        query=accelerator_query,
        filters={
            "provider_type": "accelerator",
            "equity_percentage": {"$exists": True}
        },
        top_k=3
    )
    
    # 4. Test searching for long-term grants (duration over 12 months)
    print("\n=== Test 4: Searching for Long-Term Grants ===")
    long_term_query = "long-term research funding for AI projects"
    long_term_results = await search_with_filters(
        vector_service,
        query=long_term_query,
        filters={
            "is_grant": True,
            "grant_duration_months": {"$gt": "12"}
        },
        top_k=3
    )
    
    # 5. Test multilingual query on the same dataset
    print("\n=== Test 5: Multilingual Query (French) ===")
    french_query = "financement pour projets d'intelligence artificielle en Afrique"
    french_results = await search_with_filters(
        vector_service,
        query=french_query,
        filters={},  # No filters to see all results
        top_k=3
    )
    
    # 6. Test searching for recent RSS feed results only
    print("\n=== Test 6: Recent RSS Feed Results Only ===")
    recent_query = "recent AI funding opportunities"
    recent_results = await search_with_filters(
        vector_service,
        query=recent_query,
        filters={
            "source_type": "rss"
        },
        top_k=3
    )
    
    print("\n==== Advanced Vector Search Testing Complete ====\n")

async def search_with_filters(vector_service, query, filters, top_k=5):
    """Execute vector search with filters and print results"""
    print(f"\nQuery: '{query}'")
    print(f"Filters: {filters}")
    
    try:
        # Perform search with filters
        search_results = vector_service.index.query(
            namespace=VectorIndexType.OPPORTUNITIES.value,
            top_k=top_k,
            filter=filters,
            include_metadata=True,
            use_hosted_model=True,
            host_text=query
        )
        
        # Print results
        if search_results and len(search_results['matches']) > 0:
            print(f"\nFound {len(search_results['matches'])} results:")
            for i, match in enumerate(search_results['matches']):
                print(f"\n--- Result {i+1} (Score: {match['score']:.4f}) ---")
                metadata = match['metadata']
                print(f"Title: {metadata.get('title', 'No title')}")
                print(f"Source: {metadata.get('source_type', 'Unknown source')}")
                
                # Print funding type info
                if metadata.get('is_grant'):
                    print("Type: Grant Funding")
                    if 'grant_duration_months' in metadata:
                        print(f"Duration: {metadata['grant_duration_months']} months")
                    if 'grant_renewable' in metadata:
                        print(f"Renewable: {metadata['grant_renewable']}")
                elif metadata.get('is_investment'):
                    print("Type: Investment Funding")
                    if 'equity_percentage' in metadata:
                        print(f"Equity: {metadata['equity_percentage']}%")
                
                # Print organization info
                if 'provider_type' in metadata:
                    print(f"Provider Type: {metadata['provider_type']}")
                if 'recipient_type' in metadata:
                    print(f"Recipient Type: {metadata['recipient_type']}")
                
                # Print URL for verification
                if 'link' in metadata:
                    print(f"Link: {metadata['link']}")
        else:
            print("No results found")
        
        return search_results
        
    except Exception as e:
        print(f"Search failed: {e}")
        return None

# Optional: Add sample RSS data to test vector indexing
async def add_sample_rss_data():
    """Add sample RSS data to test vector indexing and retrieval"""
    
    # Sample RSS feed extraction result with organization roles and funding types
    sample_rss_result = {
        'opportunities': [
            {
                'title': 'AI Research Grant for Climate Change in Africa',
                'description': 'Funding for AI research addressing climate change challenges in Africa.',
                'link': 'https://example.org/climate-ai-grant',
                'published_date': datetime.now().isoformat(),
                'confidence_score': 0.9,
                'requires_review': False,
                'extracted_data': {
                    'funding_amount': '250000 USD',
                    'deadline': (datetime.now() + timedelta(days=30)).isoformat(),
                    'geographic_focus': ['Africa', 'Sub-Saharan Africa'],
                    'ai_focus': ['Computer Vision', 'Climate AI'],
                    'provider_organization_name': 'Global Climate Foundation',
                    'provider_organization_id': '12345',
                    'provider_type': 'granting_agency',
                    'recipient_type': 'research_institution',
                    'funding_type': 'research_grant',
                    'is_grant': True,
                    'grant_properties': {
                        'duration_months': 24,
                        'renewable': True,
                        'reporting_requirements': 'Quarterly'
                    }
                }
            },
            {
                'title': 'Seed Investment for AI Healthcare Startups',
                'description': 'Early-stage funding for AI startups in healthcare sector in Africa.',
                'link': 'https://example.org/ai-healthcare-investment',
                'published_date': datetime.now().isoformat(),
                'confidence_score': 0.85,
                'requires_review': False,
                'extracted_data': {
                    'funding_amount': '500000 USD',
                    'deadline': (datetime.now() + timedelta(days=45)).isoformat(),
                    'geographic_focus': ['Nigeria', 'Kenya', 'South Africa'],
                    'ai_focus': ['Healthcare AI', 'Machine Learning'],
                    'provider_organization_name': 'TechVentures Africa',
                    'provider_organization_id': '67890',
                    'provider_type': 'venture_capital',
                    'recipient_type': 'startup',
                    'startup_stage': 'seed',
                    'funding_type': 'seed_investment',
                    'is_investment': True,
                    'investment_properties': {
                        'equity_percentage': 10,
                        'valuation_cap': '5000000 USD',
                        'expected_roi': 25
                    }
                }
            },
            {
                'title': 'AI Accelerator Program for African Startups',
                'description': 'Three-month accelerator program with funding for AI startups.',
                'link': 'https://example.org/ai-accelerator',
                'published_date': datetime.now().isoformat(),
                'confidence_score': 0.88,
                'requires_review': False,
                'extracted_data': {
                    'funding_amount': '100000 USD',
                    'deadline': (datetime.now() + timedelta(days=60)).isoformat(),
                    'geographic_focus': ['Pan-African'],
                    'ai_focus': ['General AI', 'AI Applications'],
                    'provider_organization_name': 'AfricaAI Hub',
                    'provider_organization_id': '54321',
                    'provider_type': 'accelerator',
                    'recipient_type': 'startup',
                    'startup_stage': 'early',
                    'funding_type': 'accelerator',
                    'is_investment': True,
                    'investment_properties': {
                        'equity_percentage': 7,
                        'valuation_cap': '3000000 USD'
                    }
                }
            }
        ],
        'feed_url': 'https://example.org/ai-funding-feed',
        'feed_id': 'sample_feed_001',
        'processed_count': 3
    }
    
    # Index the sample data
    print("\n=== Adding Sample RSS Feed Data ===")
    result = await index_rss_feed_results(sample_rss_result)
    print(f"Indexing result: {result.success}")
    if result.data:
        print(f"Indexed {result.data.get('indexed_count', 0)} opportunities")
    
    # Give Pinecone a moment to process the indexing
    await asyncio.sleep(2)

if __name__ == "__main__":
    # Add optional sample data first (uncomment to test with fresh data)
    # asyncio.run(add_sample_rss_data())
    
    # Run the search tests
    asyncio.run(run_vector_search_tests())
