"""
Vector Database Configuration
===========================

Configuration settings for Pinecone vector database integration,
including environment variables, index settings, and performance tuning.
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

class VectorIndexType(Enum):
    """Types of vector indexes/namespaces"""
    OPPORTUNITIES = "opportunities"
    ORGANIZATIONS = "organizations"  
    VALIDATION_RESULTS = "validation_results"
    CONTENT_SUMMARIES = "content_summaries"
    GEOGRAPHIC_ANALYSIS = "geographic_analysis"
    SECTORAL_ANALYSIS = "sectoral_analysis"
    INCLUSION_SIGNALS = "inclusion_signals"

class EmbeddingProvider(Enum):
    """Provider of embedding model"""
    OPENAI = "openai"
    MICROSOFT = "microsoft"
    PINECONE = "pinecone"
    NVIDIA = "nvidia"

class EmbeddingModel(Enum):
    """Supported embedding models"""
    OPENAI_ADA_002 = "text-embedding-ada-002"  # Legacy model
    OPENAI_3_SMALL = "text-embedding-3-small"  # Better performance/cost balance
    OPENAI_3_LARGE = "text-embedding-3-large"  # Highest quality
    MICROSOFT_MULTILINGUAL_E5 = "multilingual-e5-large"  # Microsoft model with multilingual support
    NVIDIA_LLAMA_EMBED = "llama-text-embed-v2"  # NVIDIA model
    PINECONE_SPARSE = "pinecone-sparse-english-v0"  # Pinecone sparse embeddings

@dataclass
class PineconeConfig:
    """Pinecone configuration settings"""
    
    # API Configuration
    api_key: str = os.environ.get("PINECONE_API_KEY", "")
    
    # Index Configuration
    index_name: str = os.environ.get("PINECONE_INDEX_NAME", "taifa-fiala")
    dimension: int = 1024  # Microsoft multilingual-e5-large dimension is 1024
    metric: str = "cosine"  # Cosine similarity is best for semantic search
    cloud: str = "aws"  # Options: aws, gcp, azure
    region: str = "us-east-1"  # Using standard region for cost-effectiveness (can change later)
    
    # Serverless Configuration
    spec_type: str = "serverless"  # Options: serverless, pod
    
    # Embedding Configuration
    embedding_provider: EmbeddingProvider = EmbeddingProvider.MICROSOFT
    embedding_model: str = "multilingual-e5-large"  # Microsoft's multilingual model
    use_hosted_model: bool = True  # Using Pinecone's hosted embedding model
    
    # Performance Configuration 
    timeout: int = 30  # Seconds
    batch_size: int = 100  # Vectors per batch for upsert operations
    
    # Search Configuration
    top_k: int = 20  # Default number of results to return
    similarity_threshold: float = 0.75  # Minimum similarity score
    
    # Equity-Aware Configuration
    equity_metadata_fields: list = None  # Fields specifically for equity analysis
    
    def __post_init__(self):
        """Set up default equity metadata fields if not provided"""
        if self.equity_metadata_fields is None:
            self.equity_metadata_fields = [
                "geographic_scopes", 
                "ai_domains",
                "funding_stage", 
                "inclusion_indicators",
                "equity_score",
                "bias_flags",
                "underserved_focus",
                "women_focus",
                "youth_focus",
                "funding_type",
                "funding_category",
                "organization_role",
                "provider_type",
                "recipient_type",
                "startup_stage"
            ]
    
    def get_tags(self) -> Dict[str, str]:
        """Get tags for the index"""
        return {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "project": "taifa-fiala",
            "purpose": "equity-aware-funding",
            "language_support": "multilingual"
        }
    
    def get_serverless_spec(self) -> Dict[str, Any]:
        """Get serverless specification"""
        return {
            "cloud": self.cloud,
            "region": self.region
        }

# Default configuration instance
default_config = PineconeConfig()
