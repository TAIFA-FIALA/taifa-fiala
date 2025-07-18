"""
Test script for Pinecone vector database integration
with Microsoft's multilingual-e5-large embedding model.
"""

import os
import asyncio
import logging

from pinecone import Pinecone, ServerlessSpec

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "taifa-fiala")

async def test_pinecone_connection():
    """Test basic connection to Pinecone"""
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        
        # List available indexes
        indexes = pc.list_indexes()
        logger.info(f"Available indexes: {indexes}")
        
        if index_name in indexes.names():
            logger.info(f"Index '{index_name}' exists!")
            
            # Connect to the index
            index = pc.Index(index_name)
            
            # Get index stats
            stats = index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            
            return True
        else:
            logger.error(f"Index '{index_name}' not found!")
            return False
            
    except Exception as e:
        logger.error(f"Error connecting to Pinecone: {e}")
        return False

async def test_multilingual_embedding():
    """Test the Microsoft multilingual embedding model"""
    try:
        # Initialize Pinecone client and connect to index
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        # Test queries in multiple languages to verify multilingual capabilities
        test_queries = [
            # English
            "AI funding for healthcare startups in Kenya",
            # French
            "Financement de l'IA pour les startups de santé au Kenya",
            # Swahili
            "Ufadhili wa AI kwa kampuni chipukizi za afya nchini Kenya"
        ]
        
        for query in test_queries:
            logger.info(f"Testing query in different language: '{query}'")
            
            # Use the hosted embedding model with the query text
            results = index.query(
                top_k=3,
                text=query,  # Pinecone will embed this using the Microsoft model
                include_metadata=True
            )
            
            logger.info(f"Found {len(results.matches)} results")
            for match in results.matches:
                logger.info(f"Score: {match.score:.4f} - ID: {match.id}")
                if hasattr(match, 'metadata') and match.metadata:
                    logger.info(f"Metadata: {match.metadata}")
            
            logger.info("-" * 50)
            
        return True
            
    except Exception as e:
        logger.error(f"Error testing multilingual capabilities: {e}")
        return False

async def insert_test_data():
    """Insert test data to verify indexing with hosted embeddings"""
    try:
        # Initialize Pinecone client and connect to index
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        # Sample data with equity-aware metadata
        test_data = [
            {
                "id": "test-opportunity-1",
                "text": """
                Healthcare AI Innovation Grant
                This intelligence item supports innovative AI solutions in healthcare
                with a focus on underserved communities in Kenya, Uganda, and Tanzania.
                Grants range from $25,000 to $100,000 for early-stage startups.
                Special consideration for women-led enterprises.
                """,
                "metadata": {
                    "title": "Healthcare AI Innovation Grant",
                    "funding_category": "grant",
                    "funding_amount": "100000",
                    "geographic_scopes": "east_africa,kenya,uganda,tanzania",
                    "ai_domains": "healthcare,ml,data_analytics",
                    "women_focus": True,
                    "underserved_focus": True,
                    "funding_stage": "early"
                }
            },
            {
                "id": "test-opportunity-2",
                "text": """
                West African Fintech Investment Fund
                Providing seed investments for fintech startups in Ghana, Nigeria, and Senegal.
                Focusing on mobile payment solutions and financial inclusion.
                Investment range: $50,000 - $250,000 with equity requirements between 5-10%.
                Looking for ventures with proven traction and youth-led initiatives.
                """,
                "metadata": {
                    "title": "West African Fintech Investment Fund",
                    "funding_category": "investment",
                    "funding_amount": "250000",
                    "geographic_scopes": "west_africa,ghana,nigeria,senegal",
                    "ai_domains": "fintech,mobile_payments",
                    "youth_focus": True,
                    "underserved_focus": False,
                    "funding_stage": "seed"
                }
            },
            {
                "id": "test-opportunity-3",
                "text": """
                Programme d'Innovation Numérique pour l'Afrique Francophone
                Financement pour des solutions numériques innovantes au Sénégal, 
                Côte d'Ivoire, et Maroc. Focus sur l'intelligence artificielle
                et l'apprentissage automatique pour l'agriculture et l'éducation.
                Subventions de 20 000€ à 75 000€ avec mentorat technique.
                """,
                "metadata": {
                    "title": "Programme d'Innovation Numérique",
                    "funding_category": "grant", 
                    "funding_amount": "75000",
                    "geographic_scopes": "west_africa,senegal,ivory_coast,morocco",
                    "ai_domains": "agriculture,education,ml",
                    "youth_focus": True,
                    "women_focus": True,
                    "funding_stage": "early"
                }
            }
        ]
        
        logger.info(f"Inserting {len(test_data)} test documents")
        
        # Insert each document using hosted embeddings
        for item in test_data:
            logger.info(f"Indexing document: {item['id']}")
            
            # Upsert with text field for hosted embedding
            index.upsert(
                vectors=[{
                    "id": item["id"],
                    "metadata": item["metadata"],
                    # No embedding values provided - using hosted model
                }],
                namespace="opportunities",
                use_hosted_model=True,  # Enable hosted embedding
                host_text=item["text"]  # Text to embed
            )
            
        logger.info("Test data inserted successfully")
        return True
            
    except Exception as e:
        logger.error(f"Error inserting test data: {e}")
        return False

async def run_tests():
    """Run all tests"""
    # First test basic connection
    connection_ok = await test_pinecone_connection()
    if not connection_ok:
        logger.error("Connection test failed! Check your API key and index name.")
        return
    
    # Try to insert some test data
    insert_ok = await insert_test_data()
    if not insert_ok:
        logger.warning("Insert test failed! Check the Pinecone logs for details.")
    
    # Test multilingual capabilities
    multilingual_ok = await test_multilingual_embedding()
    if not multilingual_ok:
        logger.warning("Multilingual test failed!")
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    asyncio.run(run_tests())
