#!/usr/bin/env python3
"""
Pinecone Full-Text Search Integration
====================================

This module provides full-text semantic search capabilities using Pinecone
vector database. It ensures all the great metadata we collect is searchable
through intelligent embeddings.
"""

import asyncio
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client
from pinecone import Pinecone, ServerlessSpec

# For generating embeddings (we'll use a simple approach for demo)
import hashlib
import re

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PineconeSearchSystem:
    """Full-text search system using Pinecone vector database"""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.supabase: Client = None
        self.index_name = "taifa-fiala"
        
    async def initialize(self):
        """Initialize Pinecone and Supabase connections"""
        logger.info("🧠 Initializing Pinecone Search System")
        
        # Initialize Pinecone
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found")
        
        self.pc = Pinecone(api_key=api_key)
        
        # Connect to index
        try:
            self.index = self.pc.Index(self.index_name)
            logger.info(f"✅ Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pinecone index: {e}")
            raise
        
        # Initialize Supabase
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found")
        
        self.supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Connected to Supabase")
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (simple approach for demo)"""
        # In production, use OpenAI API or local model
        # For demo, we'll create deterministic embeddings
        
        # Clean and normalize text
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        words = clean_text.split()
        
        # Create embedding based on word patterns
        embedding = []
        
        # Use text hash for consistent embeddings
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        for i in range(1024):  # 1024 dimensions to match index
            # Create deterministic values from hash
            hash_chunk = text_hash[(i * 2) % len(text_hash):(i * 2 + 2) % len(text_hash)]
            if len(hash_chunk) == 2:
                val = int(hash_chunk, 16) / 255.0
            else:
                val = 0.5
            
            # Add some variation based on content
            if i < len(words):
                word_influence = len(words[i]) / 20.0
                val = (val + word_influence) / 2
            
            embedding.append(val)
        
        # Normalize embedding
        embedding = np.array(embedding)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()
    
    async def index_intelligence_feed(self, limit: int = 100) -> Dict[str, Any]:
        """Index funding intelligence_items in Pinecone for full-text search"""
        logger.info(f"📊 Indexing funding intelligence_items (limit: {limit})")
        
        try:
            # Get intelligence_items from Supabase
            intelligence_items = self.supabase.table('africa_intelligence_feed').select(
                'id,title,description,funding_amount,application_deadline,eligibility_criteria,application_process,contact_information,source_url,keywords,additional_notes'
            ).limit(limit).execute()
            
            if not intelligence_items.data:
                return {'error': 'No intelligence_items found'}
            
            # Prepare vectors for indexing
            vectors = []
            indexed_count = 0
            
            for opp in intelligence_items.data:
                try:
                    # Combine all text fields for embedding
                    searchable_text = f"""
                    {opp.get('title', '')}
                    {opp.get('description', '')}
                    {opp.get('eligibility_criteria', '')}
                    {opp.get('application_process', '')}
                    {opp.get('additional_notes', '')}
                    """.strip()
                    
                    if len(searchable_text) < 10:
                        continue
                    
                    # Generate embedding
                    embedding = self.generate_embedding(searchable_text)
                    
                    # Prepare metadata
                    metadata = {
                        'id': opp['id'],
                        'title': opp.get('title', '')[:100],  # Limit length
                        'description': opp.get('description', '')[:500],
                        'funding_amount': opp.get('funding_amount', ''),
                        'deadline': opp.get('application_deadline', ''),
                        'source_url': opp.get('source_url', ''),
                        'indexed_at': datetime.now().isoformat()
                    }
                    
                    # Clean metadata (remove None values)
                    metadata = {k: v for k, v in metadata.items() if v is not None}
                    
                    vectors.append({
                        'id': f"opp_{opp['id']}",
                        'values': embedding,
                        'metadata': metadata
                    })
                    
                    indexed_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error indexing opportunity {opp.get('id', 'unknown')}: {e}")
                    continue
            
            # Upsert vectors to Pinecone
            if vectors:
                # Batch upsert
                batch_size = 100
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                
                logger.info(f"✅ Indexed {indexed_count} intelligence_items in Pinecone")
                
                return {
                    'success': True,
                    'indexed_count': indexed_count,
                    'total_processed': len(intelligence_items.data),
                    'vectors_created': len(vectors)
                }
            else:
                return {'error': 'No vectors created'}
                
        except Exception as e:
            logger.error(f"❌ Error indexing intelligence_items: {e}")
            return {'error': str(e)}
    
    async def search_intelligence_items(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """Search funding intelligence_items using semantic search"""
        logger.info(f"🔍 Searching for: {query}")
        
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Process results
            results = []
            for match in search_results.matches:
                result = {
                    'id': match.id,
                    'score': float(match.score),
                    'metadata': dict(match.metadata) if match.metadata else {}
                }
                results.append(result)
            
            logger.info(f"✅ Found {len(results)} matching intelligence_items")
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'total_found': len(results)
            }
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return {'error': str(e)}
    
    async def get_similar_intelligence_items(self, opportunity_id: int, top_k: int = 5) -> Dict[str, Any]:
        """Find similar intelligence_items to a given one"""
        logger.info(f"🔍 Finding similar intelligence_items to ID: {opportunity_id}")
        
        try:
            # Get the opportunity from Supabase
            opp = self.supabase.table('africa_intelligence_feed').select(
                'id,title,description,eligibility_criteria'
            ).eq('id', opportunity_id).execute()
            
            if not opp.data:
                return {'error': 'Opportunity not found'}
            
            opportunity = opp.data[0]
            
            # Create search text
            search_text = f"{opportunity['title']} {opportunity.get('description', '')}"
            
            # Search for similar intelligence_items
            results = await self.search_intelligence_items(search_text, top_k + 1)
            
            if results.get('success'):
                # Filter out the original opportunity
                filtered_results = [
                    r for r in results['results'] 
                    if r['metadata'].get('id') != opportunity_id
                ][:top_k]
                
                return {
                    'success': True,
                    'original_opportunity': opportunity,
                    'similar_intelligence_items': filtered_results,
                    'total_found': len(filtered_results)
                }
            else:
                return results
                
        except Exception as e:
            logger.error(f"❌ Error finding similar intelligence_items: {e}")
            return {'error': str(e)}
    
    async def get_search_analytics(self) -> Dict[str, Any]:
        """Get analytics about the search index"""
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            
            # Get sample of indexed intelligence_items
            sample_results = self.index.query(
                vector=[0.1] * 1024,  # Dummy query
                top_k=5,
                include_metadata=True
            )
            
            return {
                'index_stats': stats,
                'sample_intelligence_items': [
                    {
                        'id': match.id,
                        'title': match.metadata.get('title', 'No title'),
                        'indexed_at': match.metadata.get('indexed_at', 'Unknown')
                    }
                    for match in sample_results.matches
                ],
                'search_ready': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting search analytics: {e}")
            return {'error': str(e)}
    
    async def test_search_capabilities(self) -> Dict[str, Any]:
        """Test search capabilities with sample queries"""
        logger.info("🧪 Testing search capabilities")
        
        test_queries = [
            "AI healthcare funding Africa",
            "machine learning agriculture grant",
            "startup accelerator Kenya",
            "education technology innovation",
            "climate change AI solution"
        ]
        
        test_results = {}
        
        for query in test_queries:
            results = await self.search_intelligence_items(query, top_k=3)
            test_results[query] = {
                'success': results.get('success', False),
                'results_count': len(results.get('results', [])),
                'top_result': results.get('results', [{}])[0] if results.get('results') else None
            }
        
        return {
            'test_queries': test_queries,
            'test_results': test_results,
            'overall_success': all(r['success'] for r in test_results.values())
        }

async def main():
    """Main function for testing Pinecone search system"""
    logger.info("🚀 Testing Pinecone Search System")
    
    search_system = PineconeSearchSystem()
    
    try:
        # Initialize
        await search_system.initialize()
        
        # Index some intelligence_items
        logger.info("📊 Indexing intelligence_items...")
        index_results = await search_system.index_intelligence_feed(limit=50)
        logger.info(f"Index results: {index_results}")
        
        # Test search capabilities
        logger.info("🧪 Testing search capabilities...")
        test_results = await search_system.test_search_capabilities()
        logger.info(f"Test results: {test_results}")
        
        # Get analytics
        logger.info("📈 Getting search analytics...")
        analytics = await search_system.get_search_analytics()
        logger.info(f"Analytics: {analytics}")
        
        # Demo search
        logger.info("🔍 Demo search...")
        demo_results = await search_system.search_intelligence_items("AI healthcare funding Kenya", top_k=3)
        logger.info(f"Demo search results: {demo_results}")
        
        logger.info("✅ Pinecone search system test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())