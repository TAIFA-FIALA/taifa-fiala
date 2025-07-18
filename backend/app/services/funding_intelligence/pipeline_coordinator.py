"""
Main Funding Intelligence Pipeline Coordinator
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"

This orchestrates all the funding intelligence components:
- Search strategy and content ingestion
- AI-powered content analysis
- Entity extraction and relationship mapping
- Opportunity prediction
- Vector database integration
- Database storage and management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Local imports
from .search_strategy import WideNetSearchModule, EnhancedSearchStrategy
from .content_analyzer import AIFundingIntelligence, CrossContentIntelligence, IntelligentDeduplication
from .entity_extraction import FundingEntityExtractor, FundingRelationshipMapper, FundingTimelineBuilder
from .opportunity_predictor import OpportunityPredictor, SuccessStoryAnalyzer, FundingResearchAgent
from .vector_intelligence import FundingIntelligenceVectorDB, VectorSearchService

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"


@dataclass
class ProcessingStats:
    """Statistics for pipeline processing"""
    total_content_processed: int = 0
    funding_signals_found: int = 0
    entities_extracted: int = 0
    relationships_mapped: int = 0
    opportunities_predicted: int = 0
    vector_documents_created: int = 0
    database_records_created: int = 0
    processing_time_seconds: float = 0.0
    errors_encountered: int = 0


class FundingIntelligencePipeline:
    """
    Main pipeline coordinator that orchestrates all funding intelligence components
    """
    
    def __init__(self, use_vector_db: bool = True, use_integrated_embedding: bool = True):
        # Initialize all components
        self.search_module = WideNetSearchModule()
        self.content_analyzer = AIFundingIntelligence()
        self.cross_content_analyzer = CrossContentIntelligence()
        self.deduplication_service = IntelligentDeduplication()
        
        self.entity_extractor = FundingEntityExtractor()
        self.relationship_mapper = FundingRelationshipMapper()
        self.timeline_builder = FundingTimelineBuilder()
        
        self.opportunity_predictor = OpportunityPredictor()
        self.success_analyzer = SuccessStoryAnalyzer()
        self.research_agent = FundingResearchAgent()
        
        # Vector database integration
        self.use_vector_db = use_vector_db
        if self.use_vector_db:
            self.vector_db = FundingIntelligenceVectorDB(use_integrated_embedding)
            self.vector_search_service = VectorSearchService()
        else:
            self.vector_db = None
            self.vector_search_service = None
        
        # Database connections (to be initialized)
        self.supabase_client = None
        
        # Processing state
        self.processing_stats = ProcessingStats()
        self.is_processing = False
    
    async def initialize_database_connections(self):
        """Initialize database connections"""
        try:
            # TODO: Initialize Supabase client
            # from supabase import create_client
            # self.supabase_client = create_client(url, key)
            logger.info("Database connections initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    async def process_funding_intelligence(self, 
                                         search_mode: str = "comprehensive",
                                         processing_mode: ProcessingMode = ProcessingMode.BATCH) -> ProcessingStats:
        """
        Main processing pipeline for funding intelligence
        
        Args:
            search_mode: 'simple', 'targeted', 'comprehensive'
            processing_mode: How to process the content
        """
        if self.is_processing:
            logger.warning("Pipeline is already processing, skipping new request")
            return self.processing_stats
        
        start_time = datetime.now()
        self.is_processing = True
        self.processing_stats = ProcessingStats()
        
        try:
            logger.info(f"Starting funding intelligence pipeline with {search_mode} search mode")
            
            # Step 1: Content Ingestion
            logger.info("Step 1: Content Ingestion")
            raw_content = await self._ingest_content(search_mode)
            self.processing_stats.total_content_processed = len(raw_content)
            
            # Step 2: AI Content Analysis
            logger.info("Step 2: AI Content Analysis")
            analyzed_content = await self._analyze_content(raw_content)
            self.processing_stats.funding_signals_found = len(analyzed_content)
            
            # Step 3: Entity Extraction and Relationship Mapping
            logger.info("Step 3: Entity Extraction and Relationship Mapping")
            enriched_content = await self._extract_entities_and_relationships(analyzed_content)
            
            # Step 4: Deduplication
            logger.info("Step 4: Deduplication")
            deduplicated_content = await self._deduplicate_content(enriched_content)
            
            # Step 5: Cross-Content Pattern Analysis
            logger.info("Step 5: Cross-Content Pattern Analysis")
            patterns = await self._analyze_patterns(deduplicated_content)
            
            # Step 6: Opportunity Prediction
            logger.info("Step 6: Opportunity Prediction")
            opportunities = await self._predict_opportunities(deduplicated_content)
            self.processing_stats.opportunities_predicted = len(opportunities)
            
            # Step 7: Vector Database Storage
            if self.use_vector_db:
                logger.info("Step 7: Vector Database Storage")
                await self._store_in_vector_db(deduplicated_content, opportunities)
            
            # Step 8: Database Storage
            logger.info("Step 8: Database Storage")
            await self._store_in_database(deduplicated_content, opportunities, patterns)
            
            # Step 9: Generate Insights
            logger.info("Step 9: Generate Insights")
            insights = await self._generate_insights(deduplicated_content, opportunities, patterns)
            
            # Calculate processing time
            end_time = datetime.now()
            self.processing_stats.processing_time_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"Pipeline completed successfully in {self.processing_stats.processing_time_seconds:.2f}s")
            logger.info(f"Processed {self.processing_stats.total_content_processed} items, "
                       f"found {self.processing_stats.funding_signals_found} funding signals, "
                       f"predicted {self.processing_stats.opportunities_predicted} opportunities")
            
            return self.processing_stats
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            self.processing_stats.errors_encountered += 1
            raise
        finally:
            self.is_processing = False
    
    async def _ingest_content(self, search_mode: str) -> List[Dict[str, Any]]:
        """Step 1: Ingest content from various sources"""
        try:
            # Use the wide net search module
            search_results = await self.search_module.cast_net(search_mode)
            
            # Add timestamp and source tracking
            for item in search_results.get('content', []):
                item['pipeline_ingested_at'] = datetime.now().isoformat()
                item['pipeline_search_mode'] = search_mode
            
            return search_results.get('content', [])
            
        except Exception as e:
            logger.error(f"Content ingestion failed: {e}")
            self.processing_stats.errors_encountered += 1
            return []
    
    async def _analyze_content(self, raw_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 2: Analyze content with AI for funding relevance"""
        try:
            # Process content in batches for efficiency
            analyzed_content = await self.content_analyzer.process_raw_content(raw_content)
            
            # Filter for high-priority content
            high_priority_content = [
                item for item in analyzed_content 
                if item.get('analysis', {}).get('priority_score', 0) >= 50
            ]
            
            logger.info(f"Analyzed {len(raw_content)} items, {len(high_priority_content)} high-priority")
            return high_priority_content
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            self.processing_stats.errors_encountered += 1
            return []
    
    async def _extract_entities_and_relationships(self, 
                                                analyzed_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 3: Extract entities and map relationships"""
        try:
            enriched_content = []
            
            for item in analyzed_content:
                content_text = item.get('original', {}).get('content', '')
                
                # Extract entities
                entities = await self.entity_extractor.extract_entities(content_text)
                
                # Map relationships
                relationships = await self.relationship_mapper.map_relationships(entities, content_text)
                
                # Add to item
                item['extracted_entities'] = entities
                item['extracted_relationships'] = relationships
                
                enriched_content.append(item)
            
            # Update stats
            total_entities = sum(len(item.get('extracted_entities', {})) for item in enriched_content)
            total_relationships = sum(len(item.get('extracted_relationships', [])) for item in enriched_content)
            
            self.processing_stats.entities_extracted = total_entities
            self.processing_stats.relationships_mapped = total_relationships
            
            return enriched_content
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            self.processing_stats.errors_encountered += 1
            return analyzed_content
    
    async def _deduplicate_content(self, enriched_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 4: Intelligent deduplication"""
        try:
            # TODO: Implement database lookup for existing content
            existing_db = []  # Would be populated from database
            
            deduplicated_content = []
            
            for item in enriched_content:
                dedup_result = await self.deduplication_service.deduplicate_with_intelligence(
                    item, existing_db
                )
                
                if not dedup_result.get('is_duplicate', False):
                    deduplicated_content.append(item)
                else:
                    logger.info(f"Deduplicated item: {item.get('original', {}).get('title', 'Unknown')}")
            
            logger.info(f"Deduplicated {len(enriched_content)} to {len(deduplicated_content)} items")
            return deduplicated_content
            
        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            self.processing_stats.errors_encountered += 1
            return enriched_content
    
    async def _analyze_patterns(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 5: Analyze patterns across content"""
        try:
            patterns = await self.cross_content_analyzer.find_funding_patterns(content)
            logger.info(f"Found {len(patterns)} funding patterns")
            return patterns
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            self.processing_stats.errors_encountered += 1
            return []
    
    async def _predict_opportunities(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 6: Predict funding opportunities"""
        try:
            # Extract events from content
            events = []
            for item in content:
                event = {
                    'signal_type': item.get('analysis', {}).get('event_type', 'unknown'),
                    'content': item.get('original', {}).get('content', ''),
                    'extracted_entities': item.get('extracted_entities', {}),
                    'created_at': item.get('original', {}).get('created_at', datetime.now())
                }
                events.append(event)
            
            # Predict opportunities
            opportunities = await self.opportunity_predictor.predict_opportunities(events)
            
            # Convert to dictionary format
            opportunity_dicts = []
            for opp in opportunities:
                opp_dict = {
                    'opportunity_type': opp.opportunity_type.value,
                    'title': opp.title,
                    'description': opp.description,
                    'predicted_funder': opp.predicted_funder,
                    'estimated_amount': opp.estimated_amount,
                    'confidence': opp.confidence,
                    'expected_timeline': opp.expected_timeline,
                    'expected_date': opp.expected_date.isoformat() if opp.expected_date else None,
                    'rationale': opp.rationale,
                    'target_sectors': opp.target_sectors,
                    'target_regions': opp.target_regions,
                    'created_at': datetime.now().isoformat()
                }
                opportunity_dicts.append(opp_dict)
            
            return opportunity_dicts
            
        except Exception as e:
            logger.error(f"Opportunity prediction failed: {e}")
            self.processing_stats.errors_encountered += 1
            return []
    
    async def _store_in_vector_db(self, content: List[Dict[str, Any]], 
                                opportunities: List[Dict[str, Any]]) -> None:
        """Step 7: Store in vector database"""
        try:
            if not self.vector_db:
                return
            
            # Store funding signals
            for item in content:
                signal_data = {
                    'title': item.get('original', {}).get('title', ''),
                    'content': item.get('original', {}).get('content', ''),
                    'signal_type': item.get('analysis', {}).get('event_type', 'unknown'),
                    'funding_type': item.get('analysis', {}).get('funding_type', 'unknown'),
                    'confidence_score': item.get('analysis', {}).get('confidence', 0.0),
                    'priority_score': item.get('analysis', {}).get('priority_score', 0),
                    'extracted_entities': item.get('extracted_entities', {}),
                    'key_insights': item.get('analysis', {}).get('key_insights', ''),
                    'created_at': datetime.now().isoformat()
                }
                
                await self.vector_db.upsert_funding_signal(signal_data)
                self.processing_stats.vector_documents_created += 1
            
            # Store opportunities
            for opp in opportunities:
                await self.vector_db.upsert_funding_opportunity(opp)
                self.processing_stats.vector_documents_created += 1
            
            logger.info(f"Stored {self.processing_stats.vector_documents_created} documents in vector DB")
            
        except Exception as e:
            logger.error(f"Vector database storage failed: {e}")
            self.processing_stats.errors_encountered += 1
    
    async def _store_in_database(self, content: List[Dict[str, Any]], 
                               opportunities: List[Dict[str, Any]], 
                               patterns: List[Dict[str, Any]]) -> None:
        """Step 8: Store in relational database"""
        try:
            # TODO: Implement database storage
            # This would use the Supabase client to store in the funding intelligence tables
            
            # Mock storage for now
            for item in content:
                self.processing_stats.database_records_created += 1
            
            for opp in opportunities:
                self.processing_stats.database_records_created += 1
            
            for pattern in patterns:
                self.processing_stats.database_records_created += 1
            
            logger.info(f"Stored {self.processing_stats.database_records_created} records in database")
            
        except Exception as e:
            logger.error(f"Database storage failed: {e}")
            self.processing_stats.errors_encountered += 1
    
    async def _generate_insights(self, content: List[Dict[str, Any]], 
                               opportunities: List[Dict[str, Any]], 
                               patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 9: Generate insights and summary"""
        try:
            insights = {
                'summary': {
                    'total_signals': len(content),
                    'total_opportunities': len(opportunities),
                    'total_patterns': len(patterns),
                    'generated_at': datetime.now().isoformat()
                },
                'top_funders': [],
                'top_sectors': [],
                'trending_themes': [],
                'urgent_opportunities': [],
                'recommended_actions': []
            }
            
            # Extract top funders
            funder_counts = {}
            for item in content:
                entities = item.get('extracted_entities', {})
                for funder in entities.get('funders', []):
                    funder_counts[funder] = funder_counts.get(funder, 0) + 1
            
            insights['top_funders'] = sorted(funder_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Extract urgent opportunities
            urgent_opportunities = [
                opp for opp in opportunities 
                if opp.get('expected_timeline') == 'immediate' and opp.get('confidence', 0) > 0.7
            ]
            insights['urgent_opportunities'] = urgent_opportunities[:5]
            
            # Generate recommendations
            recommendations = []
            if urgent_opportunities:
                recommendations.append("Review urgent opportunities immediately")
            if len(opportunities) > 10:
                recommendations.append("Prioritize high-confidence opportunities")
            if len(patterns) > 5:
                recommendations.append("Analyze patterns for funding strategy optimization")
            
            insights['recommended_actions'] = recommendations
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            self.processing_stats.errors_encountered += 1
            return {}
    
    async def search_funding_intelligence(self, query: str) -> Dict[str, Any]:
        """
        Search across funding intelligence using vector similarity
        """
        try:
            if not self.vector_search_service:
                raise ValueError("Vector search service not available")
            
            results = await self.vector_search_service.intelligent_opportunity_discovery(query)
            return results
            
        except Exception as e:
            logger.error(f"Funding intelligence search failed: {e}")
            return {"error": str(e)}
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'is_processing': self.is_processing,
            'last_run_stats': {
                'total_content_processed': self.processing_stats.total_content_processed,
                'funding_signals_found': self.processing_stats.funding_signals_found,
                'opportunities_predicted': self.processing_stats.opportunities_predicted,
                'processing_time_seconds': self.processing_stats.processing_time_seconds,
                'errors_encountered': self.processing_stats.errors_encountered
            },
            'components_status': {
                'vector_db_available': self.vector_db is not None,
                'database_connected': self.supabase_client is not None
            }
        }
    
    async def run_scheduled_pipeline(self, interval_hours: int = 6) -> None:
        """
        Run the pipeline on a scheduled basis
        """
        logger.info(f"Starting scheduled pipeline with {interval_hours} hour interval")
        
        while True:
            try:
                # Run the pipeline
                await self.process_funding_intelligence(
                    search_mode="comprehensive",
                    processing_mode=ProcessingMode.SCHEDULED
                )
                
                # Wait for next interval
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Scheduled pipeline failed: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def investigate_specific_signal(self, signal_id: str) -> Dict[str, Any]:
        """
        Use the research agent to investigate a specific signal
        """
        try:
            # TODO: Retrieve signal from database
            signal_data = {"id": signal_id, "title": "Mock Signal"}
            
            # Use research agent for deep investigation
            investigation_result = await self.research_agent.investigate_lead(signal_data)
            
            return investigation_result
            
        except Exception as e:
            logger.error(f"Signal investigation failed: {e}")
            return {"error": str(e)}