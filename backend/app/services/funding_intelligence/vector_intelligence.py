"""
Pinecone Vector Intelligence Integration for Funding Intelligence
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
Updated for Pinecone SDK v5.0.0+
"""

import asyncio
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass, field

# Vector and embedding imports
from pinecone import Pinecone, ServerlessSpec
import openai
from openai import OpenAI

# Local imports
from .content_analyzer import FundingIntelligence, FundingEventType
from .entity_extraction import Entity, Relationship

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Represents a document in the vector database"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    def to_pinecone_format(self) -> Dict[str, Any]:
        """Convert to Pinecone format for the updated SDK"""
        return {
            "id": self.id,
            "values": self.embedding,
            "metadata": {
                **self.metadata,
                "content": self.content[:1000]  # Truncate content for metadata
            }
        }
    
    def to_pinecone_record_format(self) -> Dict[str, Any]:
        """Convert to Pinecone record format for upsert_records (integrated embedding)"""
        return {
            "_id": self.id,
            "chunk_text": self.content,
            **self.metadata
        }


class FundingIntelligenceVectorDB:
    """
    Pinecone vector database integration for funding intelligence
    Enables semantic search and similarity matching for intelligence feed
    Updated for Pinecone SDK v5.0.0+
    """
    
    def __init__(self, use_integrated_embedding: bool = True):
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.pinecone_environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Initialize OpenAI if not using integrated embedding
        self.use_integrated_embedding = use_integrated_embedding
        if not self.use_integrated_embedding:
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set when not using integrated embedding")
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
        
        # Index configuration
        self.index_name = "funding-intelligence"
        self.dimension = 1536  # OpenAI text-embedding-ada-002 dimension
        self.metric = "cosine"
        self.namespace = "funding-intelligence"
        
        # Initialize index
        self.index = self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or create Pinecone index using updated SDK"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                
                # Create index with serverless spec (updated syntax)
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                
                # Wait for index to be ready
                logger.info("Waiting for index to be ready...")
                import time
                time.sleep(60)  # Wait for index initialization
            
            # Get index host for connection
            index_description = self.pc.describe_index(self.index_name)
            index_host = index_description.host
            
            # Connect to index using host
            index = self.pc.Index(host=index_host)
            logger.info(f"Connected to Pinecone index: {self.index_name} at {index_host}")
            
            return index
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def upsert_funding_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Add or update a funding signal in the vector database
        """
        try:
            # Create document content for embedding
            content_parts = []
            
            # Add title and content
            if signal.get('title'):
                content_parts.append(f"Title: {signal['title']}")
            if signal.get('content'):
                content_parts.append(f"Content: {signal['content']}")
            
            # Add analysis insights
            if signal.get('key_insights'):
                content_parts.append(f"Key Insights: {signal['key_insights']}")
            
            # Add entity information
            if signal.get('extracted_entities'):
                entities = signal['extracted_entities']
                if entities.get('funders'):
                    content_parts.append(f"Funders: {', '.join(entities['funders'])}")
                if entities.get('recipients'):
                    content_parts.append(f"Recipients: {', '.join(entities['recipients'])}")
                if entities.get('amounts'):
                    content_parts.append(f"Amounts: {', '.join(entities['amounts'])}")
                if entities.get('locations'):
                    content_parts.append(f"Locations: {', '.join(entities['locations'])}")
            
            # Combine content
            full_content = " | ".join(content_parts)
            
            # Create document ID
            doc_id = f"signal_{signal.get('id', hashlib.md5(full_content.encode()).hexdigest())}"
            
            # Prepare metadata
            metadata = {
                "type": "funding_signal",
                "signal_type": signal.get('signal_type', 'unknown'),
                "funding_type": signal.get('funding_type', 'unknown'),
                "timeline": signal.get('timeline', 'unknown'),
                "confidence_score": signal.get('confidence_score', 0.0),
                "priority_score": signal.get('priority_score', 0),
                "created_at": signal.get('created_at', datetime.now().isoformat()),
                "source_type": signal.get('source_type', 'unknown'),
                "has_funding_implications": signal.get('funding_implications', False),
                "event_type": signal.get('event_type', 'unknown'),
                "estimated_amount": signal.get('estimated_amount', ''),
                "expected_funding_date": signal.get('expected_funding_date', ''),
                "investigation_status": signal.get('investigation_status', 'pending')
            }
            
            # Add entities to metadata
            if signal.get('extracted_entities'):
                entities = signal['extracted_entities']
                metadata.update({
                    "funders": entities.get('funders', []),
                    "recipients": entities.get('recipients', []),
                    "locations": entities.get('locations', []),
                    "amounts": entities.get('amounts', [])
                })
            
            if self.use_integrated_embedding:
                # Use integrated embedding (upsert_records)
                record = {
                    "_id": doc_id,
                    "chunk_text": full_content,
                    **metadata
                }
                
                self.index.upsert_records(
                    namespace=self.namespace,
                    records=[record]
                )
            else:
                # Use traditional vector upsert
                embedding = await self.generate_embedding(full_content)
                
                vector_doc = VectorDocument(
                    id=doc_id,
                    content=full_content,
                    metadata=metadata,
                    embedding=embedding
                )
                
                self.index.upsert(
                    vectors=[vector_doc.to_pinecone_format()],
                    namespace=self.namespace
                )
            
            logger.info(f"Upserted funding signal to vector DB: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert funding signal: {e}")
            return False
    
    async def upsert_funding_entity(self, entity: Dict[str, Any]) -> bool:
        """
        Add or update a funding entity in the vector database
        """
        try:
            # Create content for embedding
            content_parts = []
            
            # Add basic information
            if entity.get('name'):
                content_parts.append(f"Name: {entity['name']}")
            if entity.get('entity_type'):
                content_parts.append(f"Type: {entity['entity_type']}")
            if entity.get('entity_subtype'):
                content_parts.append(f"Subtype: {entity['entity_subtype']}")
            if entity.get('description'):
                content_parts.append(f"Description: {entity['description']}")
            if entity.get('location'):
                content_parts.append(f"Location: {entity['location']}")
            if entity.get('sector'):
                content_parts.append(f"Sector: {entity['sector']}")
            
            # Add funding focus areas
            if entity.get('funding_focus_areas'):
                focus_areas = entity['funding_focus_areas']
                if isinstance(focus_areas, list):
                    content_parts.append(f"Focus Areas: {', '.join(focus_areas)}")
                elif isinstance(focus_areas, str):
                    content_parts.append(f"Focus Areas: {focus_areas}")
            
            # Add capacity information
            if entity.get('estimated_funding_capacity'):
                content_parts.append(f"Funding Capacity: ${entity['estimated_funding_capacity']:,}")
            
            if entity.get('typical_funding_range'):
                content_parts.append(f"Typical Range: {entity['typical_funding_range']}")
            
            # Combine content
            full_content = " | ".join(content_parts)
            
            # Generate embedding
            embedding = await self.generate_embedding(full_content)
            
            # Create document ID
            doc_id = f"entity_{entity.get('id', hashlib.md5(full_content.encode()).hexdigest())}"
            
            # Prepare metadata
            metadata = {
                "type": "funding_entity",
                "entity_type": entity.get('entity_type', 'unknown'),
                "entity_subtype": entity.get('entity_subtype', ''),
                "location": entity.get('location', ''),
                "sector": entity.get('sector', ''),
                "confidence": entity.get('confidence', 0.0),
                "importance_score": entity.get('importance_score', 0),
                "verification_status": entity.get('verification_status', 'unverified'),
                "created_at": entity.get('created_at', datetime.now().isoformat()),
                "mention_count": entity.get('mention_count', 0),
                "estimated_funding_capacity": entity.get('estimated_funding_capacity', 0),
                "typical_funding_range": entity.get('typical_funding_range', '')
            }
            
            # Add focus areas
            if entity.get('funding_focus_areas'):
                metadata["funding_focus_areas"] = entity['funding_focus_areas']
            
            # Create vector document
            vector_doc = VectorDocument(
                id=doc_id,
                content=full_content,
                metadata=metadata,
                embedding=embedding
            )
            
            # Upsert to Pinecone using updated SDK
            self.index.upsert(
                vectors=[vector_doc.to_pinecone_format()],
                namespace="funding-intelligence"
            )
            
            logger.info(f"Upserted funding entity to vector DB: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert funding entity: {e}")
            return False
    
    async def upsert_intelligence_item(self, opportunity: Dict[str, Any]) -> bool:
        """
        Add or update a intelligence item in the vector database
        """
        try:
            # Create content for embedding
            content_parts = []
            
            # Add opportunity details
            if opportunity.get('title'):
                content_parts.append(f"Title: {opportunity['title']}")
            if opportunity.get('description'):
                content_parts.append(f"Description: {opportunity['description']}")
            if opportunity.get('predicted_funder'):
                content_parts.append(f"Funder: {opportunity['predicted_funder']}")
            if opportunity.get('estimated_amount'):
                content_parts.append(f"Amount: {opportunity['estimated_amount']}")
            if opportunity.get('target_sectors'):
                content_parts.append(f"Sectors: {', '.join(opportunity['target_sectors'])}")
            if opportunity.get('target_regions'):
                content_parts.append(f"Regions: {', '.join(opportunity['target_regions'])}")
            if opportunity.get('key_requirements'):
                content_parts.append(f"Requirements: {', '.join(opportunity['key_requirements'])}")
            if opportunity.get('rationale'):
                content_parts.append(f"Rationale: {opportunity['rationale']}")
            
            # Combine content
            full_content = " | ".join(content_parts)
            
            # Generate embedding
            embedding = await self.generate_embedding(full_content)
            
            # Create document ID
            doc_id = f"opportunity_{opportunity.get('id', hashlib.md5(full_content.encode()).hexdigest())}"
            
            # Prepare metadata
            metadata = {
                "type": "intelligence_item",
                "opportunity_type": opportunity.get('opportunity_type', 'unknown'),
                "predicted_funder": opportunity.get('predicted_funder', ''),
                "estimated_amount": opportunity.get('estimated_amount', ''),
                "confidence": opportunity.get('confidence', 0.0),
                "expected_timeline": opportunity.get('expected_timeline', 'unknown'),
                "expected_date": opportunity.get('expected_date', ''),
                "target_sectors": opportunity.get('target_sectors', []),
                "target_regions": opportunity.get('target_regions', []),
                "created_at": datetime.now().isoformat(),
                "prediction_source": opportunity.get('prediction_source', 'ai_analysis')
            }
            
            # Create vector document
            vector_doc = VectorDocument(
                id=doc_id,
                content=full_content,
                metadata=metadata,
                embedding=embedding
            )
            
            # Upsert to Pinecone using updated SDK
            self.index.upsert(
                vectors=[vector_doc.to_pinecone_format()],
                namespace="funding-intelligence"
            )
            
            logger.info(f"Upserted intelligence item to vector DB: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert intelligence item: {e}")
            return False
    
    async def semantic_search(self, query: str, document_type: str = None, 
                            top_k: int = 10, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform semantic search across funding intelligence documents
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Prepare filter
            filter_dict = {}
            if document_type:
                filter_dict["type"] = document_type
            
            # Search Pinecone using updated SDK
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None,
                namespace="funding-intelligence"
            )
            
            # Process results
            results = []
            for match in search_response.matches:
                if match.score >= min_score:
                    result = {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata,
                        "content": match.metadata.get("content", "")
                    }
                    results.append(result)
            
            logger.info(f"Semantic search returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def find_similar_opportunities(self, opportunity_text: str, 
                                       top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar intelligence feed based on text description
        """
        return await self.semantic_search(
            query=opportunity_text,
            document_type="intelligence_item",
            top_k=top_k,
            min_score=0.7
        )
    
    async def find_relevant_funders(self, project_description: str, 
                                  top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find funders relevant to a project description
        """
        return await self.semantic_search(
            query=project_description,
            document_type="funding_entity",
            top_k=top_k,
            min_score=0.6
        )
    
    async def find_similar_signals(self, signal_content: str, 
                                 top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar funding signals for pattern recognition
        """
        return await self.semantic_search(
            query=signal_content,
            document_type="funding_signal",
            top_k=top_k,
            min_score=0.7
        )
    
    async def enhanced_opportunity_matching(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhanced opportunity matching based on user profile
        """
        # Build comprehensive query from user profile
        query_parts = []
        
        # Add sectors
        if user_profile.get('sectors'):
            query_parts.append(f"Sectors: {', '.join(user_profile['sectors'])}")
        
        # Add location
        if user_profile.get('location'):
            query_parts.append(f"Location: {user_profile['location']}")
        
        # Add focus areas
        if user_profile.get('focus_areas'):
            query_parts.append(f"Focus: {', '.join(user_profile['focus_areas'])}")
        
        # Add funding range
        if user_profile.get('funding_range'):
            query_parts.append(f"Funding range: {user_profile['funding_range']}")
        
        # Add organization type
        if user_profile.get('organization_type'):
            query_parts.append(f"Organization type: {user_profile['organization_type']}")
        
        # Add project description
        if user_profile.get('project_description'):
            query_parts.append(f"Project: {user_profile['project_description']}")
        
        query = " | ".join(query_parts)
        
        # Search for opportunities
        opportunities = await self.semantic_search(
            query=query,
            document_type="intelligence_item",
            top_k=20,
            min_score=0.5
        )
        
        # Search for relevant funders
        funders = await self.semantic_search(
            query=query,
            document_type="funding_entity",
            top_k=20,
            min_score=0.5
        )
        
        # Search for relevant signals
        signals = await self.semantic_search(
            query=query,
            document_type="funding_signal",
            top_k=20,
            min_score=0.5
        )
        
        # Combine and rank results
        all_results = []
        
        for opp in opportunities:
            opp['result_type'] = 'opportunity'
            opp['relevance_score'] = opp['score'] * 1.2  # Boost opportunities
            all_results.append(opp)
        
        for funder in funders:
            funder['result_type'] = 'funder'
            funder['relevance_score'] = funder['score'] * 1.1  # Boost funders
            all_results.append(funder)
        
        for signal in signals:
            signal['result_type'] = 'signal'
            signal['relevance_score'] = signal['score']  # Keep original score
            all_results.append(signal)
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return all_results[:15]  # Return top 15 results
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
    
    async def batch_upsert_signals(self, signals: List[Dict[str, Any]], 
                                 batch_size: int = 100) -> int:
        """
        Batch upsert multiple funding signals
        """
        success_count = 0
        
        for i in range(0, len(signals), batch_size):
            batch = signals[i:i + batch_size]
            
            for signal in batch:
                if await self.upsert_funding_signal(signal):
                    success_count += 1
            
            # Small delay between batches to avoid rate limits
            await asyncio.sleep(1)
        
        logger.info(f"Batch upserted {success_count}/{len(signals)} signals")
        return success_count
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents from the vector database"""
        try:
            self.index.delete(ids=ids, namespace="funding-intelligence")
            logger.info(f"Deleted {len(ids)} documents from vector DB")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    async def cleanup_old_documents(self, days_old: int = 30) -> int:
        """
        Clean up documents older than specified days
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_str = cutoff_date.isoformat()
            
            # Query for old documents
            # Note: This is a simplified approach - in production, you'd want
            # to implement proper pagination for large datasets
            
            # For now, return 0 (cleanup not implemented)
            logger.info(f"Cleanup for documents older than {days_old} days not implemented")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup old documents: {e}")
            return 0


class VectorSearchService:
    """
    High-level service for vector search operations
    """
    
    def __init__(self):
        self.vector_db = FundingIntelligenceVectorDB()
    
    async def intelligent_opportunity_discovery(self, search_query: str) -> Dict[str, Any]:
        """
        Intelligent opportunity discovery using vector search
        """
        try:
            # Perform multi-faceted search
            results = await self.vector_db.semantic_search(
                query=search_query,
                top_k=20,
                min_score=0.5
            )
            
            # Categorize results
            opportunities = [r for r in results if r['metadata'].get('type') == 'intelligence_item']
            funders = [r for r in results if r['metadata'].get('type') == 'funding_entity']
            signals = [r for r in results if r['metadata'].get('type') == 'funding_signal']
            
            # Generate insights
            insights = await self._generate_search_insights(results, search_query)
            
            return {
                "query": search_query,
                "total_results": len(results),
                "opportunities": opportunities[:10],
                "funders": funders[:10],
                "signals": signals[:10],
                "insights": insights,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Intelligent opportunity discovery failed: {e}")
            return {"error": str(e)}
    
    async def _generate_search_insights(self, results: List[Dict[str, Any]], 
                                      query: str) -> Dict[str, Any]:
        """Generate insights from search results"""
        insights = {
            "top_funders": [],
            "common_sectors": [],
            "funding_ranges": [],
            "geographic_focus": [],
            "trending_themes": []
        }
        
        # Extract funder information
        funders = [r for r in results if r['metadata'].get('type') == 'funding_entity']
        if funders:
            insights["top_funders"] = [f['metadata'].get('name', 'Unknown') for f in funders[:5]]
        
        # Extract sector information
        sectors = set()
        for result in results:
            if result['metadata'].get('target_sectors'):
                sectors.update(result['metadata']['target_sectors'])
        insights["common_sectors"] = list(sectors)[:5]
        
        # Extract funding ranges
        amounts = set()
        for result in results:
            if result['metadata'].get('estimated_amount'):
                amounts.add(result['metadata']['estimated_amount'])
        insights["funding_ranges"] = list(amounts)[:5]
        
        # Extract geographic focus
        locations = set()
        for result in results:
            if result['metadata'].get('location'):
                locations.add(result['metadata']['location'])
            if result['metadata'].get('target_regions'):
                locations.update(result['metadata']['target_regions'])
        insights["geographic_focus"] = list(locations)[:5]
        
        return insights