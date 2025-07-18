"""
Vector Database Integration for LLM-Powered Content Search
========================================================

Integrates vector database capabilities with the existing ETL pipeline
for enhanced content search, Q&A, and opportunity comparisons.

Architecture:
- Pinecone for vector storage and similarity search
- OpenAI embeddings for content vectorization
- Metadata filtering for enhanced search precision
- Real-time indexing through ETL pipeline integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import openai
from pinecone.spec import ServerlessSpec

from app.core.pinecone_client import get_pinecone_client
from app.core.etl_architecture import ETLTask, PipelineStage, ProcessingResult
from app.models.funding import AfricaIntelligenceItem
from app.models.validation import ValidationResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# VECTOR DATABASE CONFIGURATION
# =============================================================================

class VectorIndexType(Enum):
    """Types of vector indexes"""
    OPPORTUNITIES = "opportunities"
    ORGANIZATIONS = "organizations"
    VALIDATION_RESULTS = "validation_results"
    CONTENT_SUMMARIES = "content_summaries"

class EmbeddingModel(Enum):
    """Supported embedding models"""
    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"

@dataclass
class VectorConfig:
    """Configuration for vector database operations"""
    
    # Pinecone Configuration
    pinecone_environment: str = "us-east1-gcp"
    
    # Index Configuration
    dimension: int = 1536  # OpenAI ada-002 dimension
    metric: str = "cosine"
    index_name: str = "taifa-funding-tracker"
    
    # Embedding Configuration
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_3_SMALL
    max_content_length: int = 8000  # tokens
    batch_size: int = 100
    
    # Search Configuration
    top_k: int = 20
    similarity_threshold: float = 0.7
    
    # Performance Configuration
    max_workers: int = 10
    timeout: int = 30

@dataclass
class VectorDocument:
    """Document for vector indexing"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    namespace: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Pinecone"""
        return {
            'id': self.id,
            'values': self.embedding,
            'metadata': self.metadata
        }

@dataclass
class SearchResult:
    """Search result with similarity score"""
    document_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    opportunity_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'document_id': self.document_id,
            'content': self.content,
            'similarity_score': self.similarity_score,
            'metadata': self.metadata,
            'opportunity_id': self.opportunity_id
        }

# =============================================================================
# VECTOR DATABASE MANAGER
# =============================================================================

class VectorDatabaseManager:
    """Manages vector database operations for intelligence feed"""
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.openai_client = openai.AsyncOpenAI()
        self.pinecone_client = None
        self.index = None
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        
    async def initialize(self):
        """Initialize Pinecone connection and index"""
        try:
            # Initialize Pinecone
            self.pinecone_client = get_pinecone_client()
            if not self.pinecone_client:
                raise ConnectionError("Failed to initialize Pinecone client.")
            
            # Create index if it doesn't exist
            if self.config.index_name not in self.pinecone_client.list_indexes().names():
                await self._create_index()
            
            # Connect to index
            self.index = self.pinecone_client.Index(self.config.index_name)
            
            self.logger.info(f"Vector database initialized: {self.config.index_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    async def _create_index(self):
        """Create Pinecone index"""
        try:
            self.pinecone_client.create_index(
                name=self.config.index_name,
                dimension=self.config.dimension,
                metric=self.config.metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region=self.config.pinecone_environment
                )
            )
            
            self.logger.info(f"Created Pinecone index: {self.config.index_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to create index: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using OpenAI"""
        try:
            # Process in batches to avoid rate limits
            embeddings = []
            
            for i in range(0, len(texts), self.config.batch_size):
                batch = texts[i:i + self.config.batch_size]
                
                # Truncate texts to max length
                batch = [text[:self.config.max_content_length] for text in batch]
                
                response = await self.openai_client.embeddings.create(
                    model=self.config.embedding_model.value,
                    input=batch,
                    encoding_format="float"
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def index_intelligence_item(self, opportunity: AfricaIntelligenceItem) -> bool:
        """Index a intelligence item in the vector database"""
        try:
            # Prepare content for embedding
            content = self._prepare_opportunity_content(opportunity)
            
            # Generate embedding
            embeddings = await self.generate_embeddings([content])
            
            # Prepare metadata
            metadata = self._prepare_opportunity_metadata(opportunity)
            
            # Create vector document
            document = VectorDocument(
                id=f"opportunity_{opportunity.id}",
                content=content,
                embedding=embeddings[0],
                metadata=metadata,
                namespace=VectorIndexType.OPPORTUNITIES.value
            )
            
            # Upsert to Pinecone
            await self._upsert_documents([document])
            
            self.logger.info(f"Indexed opportunity {opportunity.id} in vector database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to index opportunity {opportunity.id}: {e}")
            return False
    
    async def index_validation_result(self, validation_result: ValidationResult) -> bool:
        """Index validation result for improved search"""
        try:
            # Prepare content from validation data
            content = self._prepare_validation_content(validation_result)
            
            # Generate embedding
            embeddings = await self.generate_embeddings([content])
            
            # Prepare metadata
            metadata = self._prepare_validation_metadata(validation_result)
            
            # Create vector document
            document = VectorDocument(
                id=f"validation_{validation_result.id}",
                content=content,
                embedding=embeddings[0],
                metadata=metadata,
                namespace=VectorIndexType.VALIDATION_RESULTS.value
            )
            
            # Upsert to Pinecone
            await self._upsert_documents([document])
            
            self.logger.info(f"Indexed validation result {validation_result.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to index validation result {validation_result.id}: {e}")
            return False
    
    async def batch_index_opportunities(self, opportunities: List[AfricaIntelligenceItem]) -> Dict[str, Any]:
        """Batch index multiple opportunities"""
        try:
            # Prepare all content
            contents = [self._prepare_opportunity_content(opp) for opp in opportunities]
            
            # Generate embeddings in batches
            embeddings = await self.generate_embeddings(contents)
            
            # Prepare documents
            documents = []
            for i, opportunity in enumerate(opportunities):
                metadata = self._prepare_opportunity_metadata(opportunity)
                
                document = VectorDocument(
                    id=f"opportunity_{opportunity.id}",
                    content=contents[i],
                    embedding=embeddings[i],
                    metadata=metadata,
                    namespace=VectorIndexType.OPPORTUNITIES.value
                )
                documents.append(document)
            
            # Batch upsert
            await self._upsert_documents(documents)
            
            result = {
                'success': True,
                'indexed_count': len(opportunities),
                'failed_count': 0
            }
            
            self.logger.info(f"Batch indexed {len(opportunities)} opportunities")
            return result
            
        except Exception as e:
            self.logger.error(f"Batch indexing failed: {e}")
            return {
                'success': False,
                'indexed_count': 0,
                'failed_count': len(opportunities),
                'error': str(e)
            }
    
    async def semantic_search(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                            top_k: Optional[int] = None) -> List[SearchResult]:
        """Perform semantic search across opportunities"""
        try:
            # Generate query embedding
            query_embeddings = await self.generate_embeddings([query])
            
            # Prepare filter
            pinecone_filter = self._prepare_search_filter(filters) if filters else None
            
            # Search in Pinecone
            search_results = await self._search_vectors(
                query_embeddings[0], 
                filter=pinecone_filter,
                top_k=top_k or self.config.top_k,
                namespace=VectorIndexType.OPPORTUNITIES.value
            )
            
            # Convert to SearchResult objects
            results = []
            for match in search_results.matches:
                result = SearchResult(
                    document_id=match.id,
                    content=match.metadata.get('content', ''),
                    similarity_score=match.score,
                    metadata=match.metadata,
                    opportunity_id=match.metadata.get('opportunity_id')
                )
                results.append(result)
            
            # Filter by similarity threshold
            results = [r for r in results if r.similarity_score >= self.config.similarity_threshold]
            
            self.logger.info(f"Semantic search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []
    
    async def find_similar_opportunities(self, opportunity_id: int, top_k: int = 10) -> List[SearchResult]:
        """Find opportunities similar to a given opportunity"""
        try:
            # Get the opportunity vector
            opportunity_vector = await self._get_opportunity_vector(opportunity_id)
            
            if not opportunity_vector:
                return []
            
            # Search for similar vectors
            search_results = await self._search_vectors(
                opportunity_vector,
                top_k=top_k + 1,  # +1 to exclude the original
                namespace=VectorIndexType.OPPORTUNITIES.value
            )
            
            # Convert and filter out the original opportunity
            results = []
            for match in search_results.matches:
                if match.metadata.get('opportunity_id') != opportunity_id:
                    result = SearchResult(
                        document_id=match.id,
                        content=match.metadata.get('content', ''),
                        similarity_score=match.score,
                        metadata=match.metadata,
                        opportunity_id=match.metadata.get('opportunity_id')
                    )
                    results.append(result)
            
            return results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Failed to find similar opportunities: {e}")
            return []
    
    async def answer_question(self, question: str, context_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Answer questions about intelligence feed using RAG"""
        try:
            # Search for relevant context
            search_results = await self.semantic_search(
                question,
                filters=context_filter,
                top_k=5
            )
            
            if not search_results:
                return {
                    'answer': 'I could not find relevant information to answer your question.',
                    'confidence': 0.0,
                    'sources': []
                }
            
            # Prepare context for LLM
            context = self._prepare_qa_context(search_results)
            
            # Generate answer using OpenAI
            answer_response = await self._generate_answer(question, context)
            
            return {
                'answer': answer_response['answer'],
                'confidence': answer_response['confidence'],
                'sources': [r.to_dict() for r in search_results[:3]],
                'context_used': len(search_results)
            }
            
        except Exception as e:
            self.logger.error(f"Question answering failed: {e}")
            return {
                'answer': 'An error occurred while processing your question.',
                'confidence': 0.0,
                'sources': [],
                'error': str(e)
            }
    
    async def compare_opportunities(self, opportunity_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple opportunities using AI"""
        try:
            # Get opportunity data
            opportunities_data = []
            for opp_id in opportunity_ids:
                vector_data = await self._get_opportunity_data(opp_id)
                if vector_data:
                    opportunities_data.append(vector_data)
            
            if len(opportunities_data) < 2:
                return {
                    'comparison': 'Need at least 2 opportunities to compare.',
                    'opportunities': opportunities_data
                }
            
            # Generate comparison using AI
            comparison = await self._generate_comparison(opportunities_data)
            
            return {
                'comparison': comparison,
                'opportunities': opportunities_data,
                'compared_count': len(opportunities_data)
            }
            
        except Exception as e:
            self.logger.error(f"Opportunity comparison failed: {e}")
            return {
                'comparison': 'An error occurred during comparison.',
                'opportunities': [],
                'error': str(e)
            }
    
    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================
    
    def _prepare_opportunity_content(self, opportunity: AfricaIntelligenceItem) -> str:
        """Prepare opportunity content for embedding"""
        content_parts = [
            f"Title: {opportunity.title}",
            f"Description: {opportunity.description or 'No description'}",
            f"Organization: {opportunity.organization_name or 'Unknown'}",
            f"Amount: {opportunity.funding_amount or 'Not specified'}",
            f"Type: {opportunity.funding_category or 'General'}",
            f"Deadline: {opportunity.deadline or 'No deadline'}",
            f"Status: {opportunity.status or 'Unknown'}"
        ]
        
        # Add grant-specific information
        if opportunity.is_grant:
            grant_props = opportunity.grant_properties
            if grant_props:
                content_parts.append(f"Grant Duration: {grant_props.get('duration_months', 'Not specified')} months")
                content_parts.append(f"Renewable: {'Yes' if grant_props.get('renewable') else 'No'}")
                content_parts.append(f"Reporting Required: {grant_props.get('reporting_requirements', 'Not specified')}")
        
        # Add investment-specific information
        if opportunity.is_investment:
            investment_props = opportunity.investment_properties
            if investment_props:
                content_parts.append(f"Equity Required: {investment_props.get('equity_percentage', 'Not specified')}%")
                content_parts.append(f"Expected ROI: {investment_props.get('expected_roi', 'Not specified')}%")
        
        # Add geographic and domain information
        if opportunity.geographic_scope_names:
            content_parts.append(f"Geographic Scope: {', '.join(opportunity.geographic_scope_names)}")
        
        if opportunity.ai_domain_names:
            content_parts.append(f"AI Domains: {', '.join(opportunity.ai_domain_names)}")
        
        return "\n".join(content_parts)
    
    def _prepare_opportunity_metadata(self, opportunity: AfricaIntelligenceItem) -> Dict[str, Any]:
        """Prepare metadata for opportunity"""
        metadata = {
            'opportunity_id': opportunity.id,
            'title': opportunity.title,
            'organization_name': opportunity.organization_name or '',
            'funding_amount': str(opportunity.funding_amount or ''),
            'currency': opportunity.currency or 'USD',
            'status': opportunity.status or 'unknown',
            'deadline': opportunity.deadline.isoformat() if opportunity.deadline else None,
            'is_grant': opportunity.is_grant,
            'is_investment': opportunity.is_investment,
            'content_type': opportunity.content_type or 'intelligence_item',
            'validation_status': opportunity.validation_status or 'pending',
            'confidence_score': opportunity.validation_confidence_score or 0.0,
            'geographic_scopes': opportunity.geographic_scope_names or [],
            'ai_domains': opportunity.ai_domain_names or [],
            'created_at': opportunity.discovered_date.isoformat() if opportunity.discovered_date else None,
            'source_type': opportunity.source_type or 'unknown'
        }
        
        # Convert lists to strings for Pinecone compatibility
        metadata['geographic_scopes'] = json.dumps(metadata['geographic_scopes'])
        metadata['ai_domains'] = json.dumps(metadata['ai_domains'])
        
        return metadata
    
    def _prepare_validation_content(self, validation_result: ValidationResult) -> str:
        """Prepare validation result content for embedding"""
        content_parts = [
            f"Validation Status: {validation_result.status}",
            f"Confidence Score: {validation_result.confidence_score}",
            f"Validation Notes: {validation_result.validation_notes or 'No notes'}",
            f"Completeness Score: {validation_result.completeness_score}",
            f"Relevance Score: {validation_result.relevance_score}",
            f"Legitimacy Score: {validation_result.legitimacy_score}",
        ]
        
        if validation_result.validated_data:
            content_parts.append(f"Validated Data: {json.dumps(validation_result.validated_data, indent=2)}")
        
        return "\n".join(content_parts)
    
    def _prepare_validation_metadata(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """Prepare metadata for validation result"""
        return {
            'validation_id': validation_result.id,
            'opportunity_id': validation_result.opportunity_id,
            'status': validation_result.status,
            'confidence_score': validation_result.confidence_score or 0.0,
            'confidence_level': validation_result.confidence_level or 'unknown',
            'completeness_score': validation_result.completeness_score or 0.0,
            'relevance_score': validation_result.relevance_score or 0.0,
            'legitimacy_score': validation_result.legitimacy_score or 0.0,
            'validator': validation_result.validator or 'unknown',
            'created_at': validation_result.created_at.isoformat() if validation_result.created_at else None
        }
    
    def _prepare_search_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare filters for Pinecone search"""
        pinecone_filter = {}
        
        if 'funding_type' in filters:
            if filters['funding_type'] == 'grant':
                pinecone_filter['is_grant'] = True
            elif filters['funding_type'] == 'investment':
                pinecone_filter['is_investment'] = True
        
        if 'status' in filters:
            pinecone_filter['status'] = filters['status']
        
        if 'min_confidence' in filters:
            pinecone_filter['confidence_score'] = {'$gte': filters['min_confidence']}
        
        if 'organization' in filters:
            pinecone_filter['organization_name'] = filters['organization']
        
        if 'source_type' in filters:
            pinecone_filter['source_type'] = filters['source_type']
        
        return pinecone_filter
    
    async def _upsert_documents(self, documents: List[VectorDocument]):
        """Upsert documents to Pinecone"""
        try:
            # Convert to Pinecone format
            vectors = [doc.to_dict() for doc in documents]
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=documents[0].namespace)
            
        except Exception as e:
            self.logger.error(f"Failed to upsert documents: {e}")
            raise
    
    async def _search_vectors(self, query_vector: List[float], filter: Optional[Dict[str, Any]] = None, 
                            top_k: int = 10, namespace: str = "default"):
        """Search vectors in Pinecone"""
        try:
            return self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter,
                namespace=namespace
            )
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            raise
    
    async def _get_opportunity_vector(self, opportunity_id: int) -> Optional[List[float]]:
        """Get vector for a specific opportunity"""
        try:
            result = self.index.fetch(
                ids=[f"opportunity_{opportunity_id}"],
                namespace=VectorIndexType.OPPORTUNITIES.value
            )
            
            if result.vectors:
                return result.vectors[f"opportunity_{opportunity_id}"].values
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get opportunity vector: {e}")
            return None
    
    async def _get_opportunity_data(self, opportunity_id: int) -> Optional[Dict[str, Any]]:
        """Get opportunity data from vector database"""
        try:
            result = self.index.fetch(
                ids=[f"opportunity_{opportunity_id}"],
                namespace=VectorIndexType.OPPORTUNITIES.value
            )
            
            if result.vectors:
                vector_data = result.vectors[f"opportunity_{opportunity_id}"]
                return {
                    'id': opportunity_id,
                    'metadata': vector_data.metadata,
                    'title': vector_data.metadata.get('title', ''),
                    'content': vector_data.metadata.get('content', '')
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get opportunity data: {e}")
            return None
    
    def _prepare_qa_context(self, search_results: List[SearchResult]) -> str:
        """Prepare context for question answering"""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"Document {i}:")
            context_parts.append(f"Title: {result.metadata.get('title', 'Unknown')}")
            context_parts.append(f"Content: {result.content}")
            context_parts.append(f"Relevance Score: {result.similarity_score:.3f}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def _generate_answer(self, question: str, context: str) -> Dict[str, Any]:
        """Generate answer using OpenAI"""
        try:
            prompt = f"""
            You are an AI assistant specializing in African AI intelligence feed. 
            Based on the following context, answer the user's question accurately and concisely.
            
            Context:
            {context}
            
            Question: {question}
            
            Please provide a helpful answer based on the context. If the context doesn't contain 
            enough information to answer the question, say so clearly.
            
            Also provide a confidence score (0-1) for your answer.
            
            Format your response as JSON:
            {{
                "answer": "your detailed answer here",
                "confidence": 0.8
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            self.logger.error(f"Answer generation failed: {e}")
            return {
                'answer': 'I encountered an error while generating the answer.',
                'confidence': 0.0
            }
    
    async def _generate_comparison(self, opportunities_data: List[Dict[str, Any]]) -> str:
        """Generate comparison between opportunities"""
        try:
            context = ""
            for i, opp in enumerate(opportunities_data, 1):
                context += f"Opportunity {i}:\n"
                context += f"Title: {opp.get('title', 'Unknown')}\n"
                context += f"Content: {opp.get('content', 'No content')}\n\n"
            
            prompt = f"""
            Compare the following intelligence feed for African AI development:
            
            {context}
            
            Please provide a detailed comparison highlighting:
            1. Key similarities and differences
            2. Funding amounts and terms
            3. Eligibility requirements
            4. Application processes
            5. Which might be better for different types of applicants
            
            Format your response as a clear, structured comparison.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Comparison generation failed: {e}")
            return "I encountered an error while generating the comparison."

# =============================================================================
# ETL PIPELINE INTEGRATION
# =============================================================================

class VectorETLProcessor:
    """Integrates vector database with ETL pipeline"""
    
    def __init__(self, vector_manager: VectorDatabaseManager):
        self.vector_manager = vector_manager
        self.logger = logging.getLogger(__name__)
    
    async def process_validated_opportunity(self, opportunity: AfricaIntelligenceItem, 
                                         validation_result: ValidationResult) -> ProcessingResult:
        """Process validated opportunity for vector indexing"""
        try:
            # Index opportunity if validation passed
            if validation_result.status in ['approved', 'auto_approved']:
                success = await self.vector_manager.index_intelligence_item(opportunity)
                
                if success:
                    return ProcessingResult(
                        task_id=f"vector_index_{opportunity.id}",
                        stage=PipelineStage.INDEXING,
                        success=True,
                        data={'indexed_opportunity_id': opportunity.id}
                    )
            
            # Index validation result for search enhancement
            await self.vector_manager.index_validation_result(validation_result)
            
            return ProcessingResult(
                task_id=f"vector_validation_{validation_result.id}",
                stage=PipelineStage.INDEXING,
                success=True,
                data={'indexed_validation_id': validation_result.id}
            )
            
        except Exception as e:
            self.logger.error(f"Vector ETL processing failed: {e}")
            return ProcessingResult(
                task_id=f"vector_error_{opportunity.id}",
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
    
    async def batch_process_opportunities(self, opportunities: List[AfricaIntelligenceItem]) -> ProcessingResult:
        """Batch process opportunities for vector indexing"""
        try:
            # Filter approved opportunities
            approved_opportunities = [
                opp for opp in opportunities 
                if opp.validation_status in ['approved', 'auto_approved']
            ]
            
            if not approved_opportunities:
                return ProcessingResult(
                    task_id="vector_batch_empty",
                    stage=PipelineStage.INDEXING,
                    success=True,
                    data={'message': 'No approved opportunities to index'}
                )
            
            # Batch index
            result = await self.vector_manager.batch_index_opportunities(approved_opportunities)
            
            return ProcessingResult(
                task_id="vector_batch_index",
                stage=PipelineStage.INDEXING,
                success=result['success'],
                data=result
            )
            
        except Exception as e:
            self.logger.error(f"Batch vector processing failed: {e}")
            return ProcessingResult(
                task_id="vector_batch_error",
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of vector database"""
    import os
    
    config = VectorConfig(
        pinecone_api_key=os.getenv('PINECONE_API_KEY'),
        embedding_model=EmbeddingModel.OPENAI_3_SMALL
    )
    
    vector_manager = VectorDatabaseManager(config)
    await vector_manager.initialize()
    
    # Example semantic search
    results = await vector_manager.semantic_search(
        query="AI funding for healthcare startups in Kenya",
        filters={'funding_type': 'grant', 'min_confidence': 0.8}
    )
    
    print(f"Found {len(results)} relevant opportunities")
    
    # Example Q&A
    qa_result = await vector_manager.answer_question(
        question="What are the requirements for Series A funding in Nigeria?",
        context_filter={'funding_type': 'investment'}
    )
    
    print(f"Answer: {qa_result['answer']}")
    print(f"Confidence: {qa_result['confidence']}")

if __name__ == "__main__":
    asyncio.run(example_usage())