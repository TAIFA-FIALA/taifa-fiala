"""
Funding Intelligence Module

AI-Powered Funding Intelligence Pipeline
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"

This module provides comprehensive funding intelligence capabilities:
- Enhanced search with expanded query strategies
- AI-powered content analysis and classification
- Entity extraction and relationship mapping
- Opportunity prediction and pattern recognition
- Vector database integration for semantic search
- Database storage and management
- Pipeline coordination and orchestration

Key Components:
- FundingIntelligencePipeline: Main coordinator
- WideNetSearchModule: Enhanced search strategies
- AIFundingIntelligence: AI content analysis
- FundingEntityExtractor: Entity extraction
- FundingRelationshipMapper: Relationship mapping
- OpportunityPredictor: Opportunity prediction
- FundingIntelligenceVectorDB: Vector database integration
- VectorSearchService: Semantic search services
"""

from .pipeline_coordinator import FundingIntelligencePipeline, ProcessingMode, ProcessingStats
from .search_strategy import WideNetSearchModule, EnhancedSearchStrategy, SearchType
from .content_analyzer import (
    AIFundingIntelligence, 
    FundingEventClassifier,
    CrossContentIntelligence,
    IntelligentDeduplication,
    FundingIntelligence,
    FundingEventType
)
from .entity_extraction import (
    FundingEntityExtractor,
    FundingRelationshipMapper,
    FundingTimelineBuilder,
    Entity,
    Relationship,
    EntityType,
    RelationshipType
)
from .opportunity_predictor import (
    OpportunityPredictor,
    SuccessStoryAnalyzer,
    FundingResearchAgent,
    OpportunityPrediction,
    OpportunityType
)
from .vector_intelligence import (
    FundingIntelligenceVectorDB,
    VectorSearchService,
    VectorDocument
)

__all__ = [
    # Main pipeline
    "FundingIntelligencePipeline",
    "ProcessingMode",
    "ProcessingStats",
    
    # Search components
    "WideNetSearchModule",
    "EnhancedSearchStrategy",
    "SearchType",
    
    # Content analysis
    "AIFundingIntelligence",
    "FundingEventClassifier",
    "CrossContentIntelligence",
    "IntelligentDeduplication",
    "FundingIntelligence",
    "FundingEventType",
    
    # Entity extraction
    "FundingEntityExtractor",
    "FundingRelationshipMapper",
    "FundingTimelineBuilder",
    "Entity",
    "Relationship",
    "EntityType",
    "RelationshipType",
    
    # Opportunity prediction
    "OpportunityPredictor",
    "SuccessStoryAnalyzer",
    "FundingResearchAgent",
    "OpportunityPrediction",
    "OpportunityType",
    
    # Vector intelligence
    "FundingIntelligenceVectorDB",
    "VectorSearchService",
    "VectorDocument",
]

# Version information
__version__ = "1.0.0"
__author__ = "AI-Africa-Funding-Tracker"
__description__ = "AI-Powered Funding Intelligence Pipeline"

# Module configuration
DEFAULT_CONFIG = {
    "use_vector_db": True,
    "use_integrated_embedding": True,
    "default_search_mode": "comprehensive",
    "processing_mode": "batch",
    "vector_index_name": "funding-intelligence",
    "vector_namespace": "funding-intelligence",
    "batch_size": 100,
    "max_concurrent_requests": 10,
    "confidence_threshold": 0.7,
    "priority_threshold": 70,
    "deduplication_threshold": 0.8,
}

def create_funding_intelligence_pipeline(config: dict = None) -> FundingIntelligencePipeline:
    """
    Factory function to create a configured funding intelligence pipeline
    
    Args:
        config: Optional configuration dictionary to override defaults
        
    Returns:
        Configured FundingIntelligencePipeline instance
    """
    if config is None:
        config = DEFAULT_CONFIG
    else:
        # Merge with defaults
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        config = merged_config
    
    return FundingIntelligencePipeline(
        use_vector_db=config.get("use_vector_db", True),
        use_integrated_embedding=config.get("use_integrated_embedding", True)
    )

def get_module_info() -> dict:
    """Get module information"""
    return {
        "name": "funding_intelligence",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": len(__all__),
        "default_config": DEFAULT_CONFIG,
    }