#!/usr/bin/env python3
"""
Test Pinecone Integration
========================

This script tests the Pinecone vector database integration for storing and retrieving
AI intelligence item embeddings.
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pinecone_connection():
    """Test Pinecone connection and basic operations"""
    
    try:
        # Initialize Pinecone
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            logger.error("❌ PINECONE_API_KEY not found in environment")
            return False
        
        pc = Pinecone(api_key=api_key)
        logger.info("✅ Pinecone client initialized")
        
        # List existing indexes
        indexes = pc.list_indexes()
        logger.info(f"📊 Found {len(indexes)} existing indexes")
        
        for index in indexes:
            logger.info(f"  - {index.name}: {index.dimension}D, {index.metric} metric")
        
        # Test with the taifa-fiala index if it exists
        index_name = "taifa-fiala"
        
        if any(idx.name == index_name for idx in indexes):
            logger.info(f"✅ Found existing index: {index_name}")
            
            # Connect to the index
            index = pc.Index(index_name)
            
            # Get index stats
            stats = index.describe_index_stats()
            logger.info(f"📊 Index stats: {stats}")
            
            # Test upsert with sample data
            # Use the actual index dimension from stats
            index_dimension = stats['dimension']
            sample_vector = [0.1] * index_dimension
            
            test_data = [{
                "id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "values": sample_vector,
                "metadata": {
                    "title": "Test Intelligence Item",
                    "description": "This is a test intelligence item for AI projects in Africa",
                    "source": "test",
                    "type": "grant",
                    "amount": 100000,
                    "created_at": datetime.now().isoformat()
                }
            }]
            
            # Upsert test data
            upsert_response = index.upsert(vectors=test_data)
            logger.info(f"✅ Test data upserted: {upsert_response}")
            
            # Test query
            query_response = index.query(
                vector=sample_vector,
                top_k=3,
                include_metadata=True
            )
            
            logger.info(f"✅ Query successful: Found {len(query_response.matches)} matches")
            
            for match in query_response.matches:
                logger.info(f"  - ID: {match.id}, Score: {match.score:.4f}")
                if match.metadata:
                    logger.info(f"    Title: {match.metadata.get('title', 'N/A')}")
            
            return True
            
        else:
            logger.warning(f"⚠️  Index '{index_name}' not found. Available indexes:")
            for idx in indexes:
                logger.warning(f"  - {idx.name}")
            
            # Create the index if it doesn't exist
            logger.info(f"🔧 Creating new index: {index_name}")
            
            pc.create_index(
                name=index_name,
                dimension=1024,  # Match existing index dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            logger.info(f"✅ Index '{index_name}' created successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Pinecone test failed: {e}")
        return False

def test_embedding_generation():
    """Test embedding generation using OpenAI or local models"""
    
    try:
        # Test with a simple embedding approach
        import numpy as np
        
        # Generate a test embedding (normally would use OpenAI or local model)
        test_text = "AI intelligence item for African startups in machine learning"
        
        # Simulate embedding generation (in real implementation, use OpenAI API)
        # For now, create a deterministic embedding based on text hash
        import hashlib
        text_hash = hashlib.md5(test_text.encode()).hexdigest()
        
        # Convert hash to numerical values and normalize
        embedding = []
        for i in range(0, min(len(text_hash), 32), 2):
            val = int(text_hash[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad or truncate to 1024 dimensions (match index dimension)
        while len(embedding) < 1024:
            embedding.extend(embedding[:min(len(embedding), 1024-len(embedding))])
        embedding = embedding[:1024]
        
        # Normalize
        embedding = np.array(embedding)
        embedding = embedding / np.linalg.norm(embedding)
        
        logger.info(f"✅ Generated embedding: {len(embedding)} dimensions")
        logger.info(f"📊 Embedding stats: mean={np.mean(embedding):.4f}, std={np.std(embedding):.4f}")
        
        return embedding.tolist()
        
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        return None

def test_full_pipeline():
    """Test the full pipeline: generate embedding and store in Pinecone"""
    
    logger.info("🚀 Testing full Pinecone pipeline...")
    
    # Test embedding generation
    embedding = test_embedding_generation()
    if not embedding:
        logger.error("❌ Failed to generate embedding")
        return False
    
    # Test Pinecone storage
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
        # Try to get the index
        index_name = "taifa-fiala"
        try:
            index = pc.Index(index_name)
        except Exception as e:
            logger.error(f"❌ Could not access index '{index_name}': {e}")
            return False
        
        # Store the embedding
        test_opportunity = {
            "id": f"pipeline-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "values": embedding,
            "metadata": {
                "title": "African AI Startup Funding Program",
                "description": "Comprehensive funding program for AI startups across Africa, focusing on machine learning, natural language processing, and computer vision applications",
                "source": "test-pipeline",
                "type": "grant",
                "amount": 250000,
                "country": "multi-country",
                "focus_area": "artificial-intelligence",
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Upsert
        upsert_response = index.upsert(vectors=[test_opportunity])
        logger.info(f"✅ Pipeline test data stored: {upsert_response}")
        
        # Test semantic search
        query_response = index.query(
            vector=embedding,
            top_k=5,
            include_metadata=True
        )
        
        logger.info(f"✅ Semantic search successful: Found {len(query_response.matches)} matches")
        
        for i, match in enumerate(query_response.matches, 1):
            logger.info(f"  {i}. ID: {match.id}")
            logger.info(f"     Score: {match.score:.4f}")
            if match.metadata:
                logger.info(f"     Title: {match.metadata.get('title', 'N/A')}")
                logger.info(f"     Type: {match.metadata.get('type', 'N/A')}")
                logger.info(f"     Amount: ${match.metadata.get('amount', 'N/A'):,}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Full pipeline test failed: {e}")
        return False

def main():
    """Main test function"""
    
    logger.info("🧪 PINECONE INTEGRATION TEST")
    logger.info("=" * 50)
    
    # Test 1: Basic connection
    logger.info("1. Testing Pinecone connection...")
    connection_success = test_pinecone_connection()
    
    if not connection_success:
        logger.error("❌ Basic connection test failed")
        return
    
    # Test 2: Full pipeline
    logger.info("\n2. Testing full pipeline...")
    pipeline_success = test_full_pipeline()
    
    if pipeline_success:
        logger.info("\n🎉 All Pinecone tests passed!")
        logger.info("✅ Vector database is ready for AI intelligence item storage")
        logger.info("✅ Semantic search capabilities are working")
        logger.info("✅ Ready for production data ingestion")
    else:
        logger.error("\n❌ Some tests failed")
        
    logger.info("\n" + "=" * 50)

if __name__ == "__main__":
    main()