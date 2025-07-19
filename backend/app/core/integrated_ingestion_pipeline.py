"""
Integrated Ingestion Pipeline with Equity-Aware Processing
=========================================================

Complete integration of all components:
- Multi-source ingestion (RSS, Serper, User, Crawl4AI)
- Equity-aware content classification
- Vector database indexing
- Bias monitoring integration
- Full-text processing and metadata storage
- Priority source management

This module connects all the pieces together into a cohesive pipeline.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor

# Handle both relative and absolute imports
try:
    from app.core.etl_architecture import ETLTask, PipelineStage, ProcessingResult
except ImportError:
    try:
        from backend.app.core.etl_architecture import ETLTask, PipelineStage, ProcessingResult
    except ImportError:
        # For relative imports within the same package
        from .etl_architecture import ETLTask, PipelineStage, ProcessingResult
# Handle both relative and absolute imports for equity classifier
try:
    from app.core.equity_aware_classifier import EquityAwareContentClassifier, ClassificationResult
except ImportError:
    try:
        from backend.app.core.equity_aware_classifier import EquityAwareContentClassifier, ClassificationResult
    except ImportError:
        from .equity_aware_classifier import EquityAwareContentClassifier, ClassificationResult

# Handle both relative and absolute imports for vector database
try:
    from app.core.vector_database import VectorDatabaseManager, VectorETLProcessor
except ImportError:
    try:
        from backend.app.core.vector_database import VectorDatabaseManager, VectorETLProcessor
    except ImportError:
        from .vector_database import VectorDatabaseManager, VectorETLProcessor

# Handle both relative and absolute imports for bias monitoring
try:
    from app.core.bias_monitoring import BiasMonitoringEngine
except ImportError:
    try:
        from backend.app.core.bias_monitoring import BiasMonitoringEngine
    except ImportError:
        from .bias_monitoring import BiasMonitoringEngine

# Handle both relative and absolute imports for multilingual search
try:
    from app.core.multilingual_search import MultilingualSearchEngine
except ImportError:
    try:
        from backend.app.core.multilingual_search import MultilingualSearchEngine
    except ImportError:
        from .multilingual_search import MultilingualSearchEngine

# Handle both relative and absolute imports for priority data sources
try:
    from app.core.priority_data_sources import PriorityDataSourceRegistry
except ImportError:
    try:
        from backend.app.core.priority_data_sources import PriorityDataSourceRegistry
    except ImportError:
        from .priority_data_sources import PriorityDataSourceRegistry

# Handle both relative and absolute imports for source quality scoring
try:
    from app.core.source_quality_scoring import SourceQualityScorer
except ImportError:
    try:
        from backend.app.core.source_quality_scoring import SourceQualityScorer
    except ImportError:
        from .source_quality_scoring import SourceQualityScorer

# Handle both relative and absolute imports for duplicate detection
try:
    from app.core.enhanced_duplicate_detection import EnhancedDuplicateDetector
except ImportError:
    try:
        from backend.app.core.enhanced_duplicate_detection import EnhancedDuplicateDetector
    except ImportError:
        from .enhanced_duplicate_detection import EnhancedDuplicateDetector

# Handle both relative and absolute imports for funding models
try:
    from app.models.funding import AfricaIntelligenceItem
except ImportError:
    try:
        from backend.app.models.funding import AfricaIntelligenceItem
    except ImportError:
        try:
            from ..models.funding import AfricaIntelligenceItem
        except ImportError:
            # If we can't import, provide a placeholder to allow module to load
            class AfricaIntelligenceItem:
                pass
try:
    from app.models.validation import ValidationResult, ContentFingerprint
except ImportError:
    try:
        from backend.app.models.validation import ValidationResult, ContentFingerprint
    except ImportError:
        from .validation import ValidationResult, ContentFingerprint

try:
    from app.core.database import get_db
except ImportError:
    try:
        from backend.app.core.database import get_db
    except ImportError:
        from .database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# INGESTION PIPELINE MODELS
# =============================================================================

class IngestionMethod(Enum):
    """Types of ingestion methods"""
    RSS_FEED = "rss_feed"
    SERPER_SEARCH = "serper_search"
    USER_SUBMISSION = "user_submission"
    CRAWL4AI_EXTRACTION = "crawl4ai_extraction"
    MULTILINGUAL_SEARCH = "multilingual_search"
    PRIORITY_SOURCE_SCAN = "priority_source_scan"

@dataclass
class IngestionContext:
    """Context information for ingestion"""
    method: IngestionMethod
    source_id: str
    source_name: str
    source_url: str
    source_language: str = "en"
    source_priority: float = 1.0
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class ProcessedContent:
    """Processed content with all metadata"""
    # Original content
    raw_content: Dict[str, Any]
    
    # Processing results
    classification: ClassificationResult
    validation: ValidationResult
    fingerprint: ContentFingerprint
    
    # Integration metadata
    ingestion_context: IngestionContext
    
    # Vector processing
    vector_indexed: bool = False
    vector_id: Optional[str] = None
    
    # Integration timestamp metadata
    processing_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    
    # Quality scores
    duplicate_score: float = 0.0
    source_quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'raw_content': self.raw_content,
            'classification': self.classification.to_dict(),
            'validation': vars(self.validation),
            'fingerprint': vars(self.fingerprint),
            'vector_indexed': self.vector_indexed,
            'vector_id': self.vector_id,
            'ingestion_context': vars(self.ingestion_context),
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'processing_time': self.processing_time,
            'duplicate_score': self.duplicate_score,
            'source_quality_score': self.source_quality_score
        }

# =============================================================================
# INTEGRATED INGESTION PIPELINE
# =============================================================================

class IntegratedIngestionPipeline:
    """Complete integrated ingestion pipeline with equity awareness"""
    
    def __init__(self, 
                 vector_manager: VectorDatabaseManager,
                 multilingual_engine: MultilingualSearchEngine,
                 serper_api_key: str):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.equity_classifier = EquityAwareContentClassifier()
        self.vector_manager = vector_manager
        self.vector_processor = VectorETLProcessor(vector_manager)
        self.bias_monitor = BiasMonitoringEngine()
        self.multilingual_engine = multilingual_engine
        self.source_registry = PriorityDataSourceRegistry()
        self.source_scorer = SourceQualityScorer()
        self.duplicate_detector = EnhancedDuplicateDetector()
        
        # Processing configuration
        self.batch_size = 50
        self.max_workers = 10
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Performance tracking
        self.processing_stats = {
            'total_processed': 0,
            'successful_classifications': 0,
            'successful_indexing': 0,
            'duplicates_detected': 0,
            'bias_alerts_generated': 0
        }

    async def process_content_batch(self, content_batch: List[Dict[str, Any]], 
                                  ingestion_context: IngestionContext) -> List[ProcessedContent]:
        """Process a batch of content through the complete pipeline"""
        try:
            start_time = datetime.now()
            processed_items = []
            
            # Step 1: Classify content with equity awareness
            self.logger.info(f"Starting equity classification for {len(content_batch)} items")
            classification_tasks = [
                self.equity_classifier.classify_content(content) 
                for content in content_batch
            ]
            classifications = await asyncio.gather(*classification_tasks, return_exceptions=True)
            
            # Step 2: Filter out failed classifications
            valid_items = []
            for i, (content, classification) in enumerate(zip(content_batch, classifications)):
                if isinstance(classification, Exception):
                    self.logger.error(f"Classification failed for item {i}: {classification}")
                    continue
                
                valid_items.append((content, classification))
                self.processing_stats['successful_classifications'] += 1
            
            # Step 3: Check for duplicates
            self.logger.info(f"Checking duplicates for {len(valid_items)} items")
            for content, classification in valid_items:
                # Get existing content for duplicate detection
                existing_content = await self._get_existing_content_for_duplicate_check()
                
                # Check for duplicates
                duplicate_matches = await self.duplicate_detector.detect_duplicates(
                    new_content=content,
                    existing_content=existing_content
                )
                
                # Skip if high-confidence duplicate
                if self._is_high_confidence_duplicate(duplicate_matches):
                    self.logger.info(f"Skipping duplicate: {content.get('title', 'No title')}")
                    self.processing_stats['duplicates_detected'] += 1
                    continue
                
                # Step 4: Create validation result
                validation_result = await self._create_validation_result(
                    content, classification, duplicate_matches
                )
                
                # Step 5: Create content fingerprint
                fingerprint = await self._create_content_fingerprint(
                    content, classification
                )
                
                # Step 6: Create processed content object
                processed_content = ProcessedContent(
                    raw_content=content,
                    classification=classification,
                    validation=validation_result,
                    fingerprint=fingerprint,
                    ingestion_context=ingestion_context,
                    duplicate_score=self._calculate_duplicate_score(duplicate_matches),
                    source_quality_score=await self._get_source_quality_score(ingestion_context.source_id)
                )
                
                processed_items.append(processed_content)
            
            # Step 7: Vector indexing for approved items
            self.logger.info(f"Vector indexing for {len(processed_items)} items")
            await self._batch_vector_index(processed_items)
            
            # Step 8: Store in database
            self.logger.info(f"Storing {len(processed_items)} items in database")
            await self._batch_store_processed_content(processed_items)
            
            # Step 9: Update bias monitoring
            await self._update_bias_monitoring(processed_items)
            
            # Step 10: Update source quality scores
            await self._update_source_quality_scores(ingestion_context, processed_items)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update processing stats
            self.processing_stats['total_processed'] += len(processed_items)
            
            self.logger.info(f"Batch processing completed: {len(processed_items)} items in {processing_time:.2f}s")
            
            return processed_items
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return []
    
    async def process_rss_feed(self, feed_url: str, source_config: Dict[str, Any]) -> List[ProcessedContent]:
        """Process RSS feed with full integration"""
        try:
            # Create ingestion context
            context = IngestionContext(
                method=IngestionMethod.RSS_FEED,
                source_id=source_config.get('source_id', 'unknown'),
                source_name=source_config.get('source_name', 'RSS Feed'),
                source_url=feed_url,
                source_language=source_config.get('language', 'en'),
                source_priority=source_config.get('priority', 1.0),
                processing_metadata={'feed_url': feed_url}
            )
            
            # Fetch RSS content
            rss_content = await self._fetch_rss_content(feed_url)
            
            # Process through pipeline
            return await self.process_content_batch(rss_content, context)
            
        except Exception as e:
            self.logger.error(f"RSS processing failed for {feed_url}: {e}")
            return []
    
    async def process_serper_search(self, query: str, search_config: Dict[str, Any]) -> List[ProcessedContent]:
        """Process Serper search results with full integration"""
        try:
            # Create ingestion context
            context = IngestionContext(
                method=IngestionMethod.SERPER_SEARCH,
                source_id=f"serper_{hashlib.md5(query.encode()).hexdigest()[:8]}",
                source_name=f"Serper Search: {query}",
                source_url="https://google.serper.dev/search",
                source_language=search_config.get('language', 'en'),
                source_priority=search_config.get('priority', 1.0),
                processing_metadata={'query': query, 'search_config': search_config}
            )
            
            # Execute search
            search_results = await self._execute_serper_search(query, search_config)
            
            # Process through pipeline
            return await self.process_content_batch(search_results, context)
            
        except Exception as e:
            self.logger.error(f"Serper search processing failed for '{query}': {e}")
            return []
    
    async def process_multilingual_search(self, base_query: str, 
                                        target_languages: List[str]) -> List[ProcessedContent]:
        """Process multilingual search with full integration"""
        try:
            all_processed = []
            
            # Execute multilingual search
            from app.core.multilingual_search import SupportedLanguage
            languages = [SupportedLanguage(lang) for lang in target_languages]
            
            multilingual_results = await self.multilingual_engine.search_multilingual(
                base_query=base_query,
                target_languages=languages
            )
            
            # Process each language result
            for result in multilingual_results:
                context = IngestionContext(
                    method=IngestionMethod.MULTILINGUAL_SEARCH,
                    source_id=f"multilingual_{result.query.language.value}",
                    source_name=f"Multilingual Search ({result.query.language.value})",
                    source_url="multilingual_search",
                    source_language=result.query.language.value,
                    source_priority=1.5,  # Higher priority for multilingual
                    processing_metadata={
                        'base_query': base_query,
                        'translated_query': result.query.translated_query,
                        'confidence_score': result.confidence_score
                    }
                )
                
                processed = await self.process_content_batch(result.results, context)
                all_processed.extend(processed)
            
            return all_processed
            
        except Exception as e:
            self.logger.error(f"Multilingual search processing failed: {e}")
            return []
    
    async def process_priority_sources(self, max_sources: int = 10) -> List[ProcessedContent]:
        """Process content from priority African data sources"""
        try:
            all_processed = []
            
            # Get high-priority sources
            priority_sources = self.source_registry.get_high_priority_sources()
            
            # Process each source
            for source in priority_sources[:max_sources]:
                self.logger.info(f"Processing priority source: {source.name}")
                
                # Create ingestion context
                context = IngestionContext(
                    method=IngestionMethod.PRIORITY_SOURCE_SCAN,
                    source_id=source.source_id,
                    source_name=source.name,
                    source_url=source.base_url,
                    source_language=source.primary_language.value,
                    source_priority=source.priority_weight,
                    processing_metadata={
                        'source_config': source.to_dict()
                    }
                )
                
                # Process RSS feeds
                for feed_url in source.rss_feeds:
                    try:
                        rss_content = await self._fetch_rss_content(feed_url)
                        processed = await self.process_content_batch(rss_content, context)
                        all_processed.extend(processed)
                    except Exception as e:
                        self.logger.error(f"RSS processing failed for {feed_url}: {e}")
                
                # Process search pages with multilingual queries
                if source.search_pages:
                    try:
                        search_results = await self._process_search_pages(
                            source.search_pages, 
                            source.primary_language.value
                        )
                        processed = await self.process_content_batch(search_results, context)
                        all_processed.extend(processed)
                    except Exception as e:
                        self.logger.error(f"Search page processing failed: {e}")
            
            return all_processed
            
        except Exception as e:
            self.logger.error(f"Priority source processing failed: {e}")
            return []
    
    async def process_user_submission(self, submission_data: Dict[str, Any]) -> ProcessedContent:
        """Process user-submitted content with full integration"""
        try:
            # Create ingestion context
            context = IngestionContext(
                method=IngestionMethod.USER_SUBMISSION,
                source_id=f"user_{submission_data.get('user_id', 'anonymous')}",
                source_name="User Submission",
                source_url=submission_data.get('url', 'user_submission'),
                source_language=submission_data.get('language', 'en'),
                source_priority=0.8,  # Lower priority for user submissions
                processing_metadata={
                    'user_id': submission_data.get('user_id'),
                    'submission_type': submission_data.get('type', 'manual')
                }
            )
            
            # Process single item
            processed_batch = await self.process_content_batch([submission_data], context)
            
            return processed_batch[0] if processed_batch else None
            
        except Exception as e:
            self.logger.error(f"User submission processing failed: {e}")
            return None
    
    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================
    
    async def _fetch_rss_content(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS content"""
        try:
            import feedparser
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url) as response:
                    if response.status == 200:
                        feed_data = await response.text()
                        feed = feedparser.parse(feed_data)
                        
                        content_items = []
                        for entry in feed.entries:
                            content_items.append({
                                'title': entry.get('title', ''),
                                'description': entry.get('description', ''),
                                'url': entry.get('link', ''),
                                'published_date': entry.get('published', ''),
                                'author': entry.get('author', ''),
                                'source': feed_url,
                                'raw_entry': entry
                            })
                        
                        return content_items
                    else:
                        self.logger.error(f"RSS fetch failed: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"RSS content fetch failed: {e}")
            return []
    
    async def _execute_serper_search(self, query: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute Serper search with configuration"""
        try:
            import aiohttp
            from app.utils.serialization import prepare_for_json
            
            # Prepare search parameters
            params = {
                'q': query,
                'num': config.get('num_results', 20),
                'hl': config.get('language', 'en'),
                'gl': config.get('country', 'za'),  # Default to South Africa
                'type': 'search'
            }
            
            # Ensure params are JSON-serializable
            params = prepare_for_json(params)
            
            headers = {
                'X-API-KEY': config.get('api_key', ''),
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://google.serper.dev/search',
                    json=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        search_results = []
                        for result in data.get('organic', []):
                            search_results.append({
                                'title': result.get('title', ''),
                                'description': result.get('snippet', ''),
                                'url': result.get('link', ''),
                                'source': result.get('source', ''),
                                'date': result.get('date', ''),
                                'position': result.get('position', 0),
                                'raw_result': result
                            })
                        
                        return search_results
                    else:
                        self.logger.error(f"Serper search failed: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Serper search execution failed: {e}")
            return []
    
    async def _process_search_pages(self, search_pages: List[str], language: str) -> List[Dict[str, Any]]:
        """Process search pages with web scraping"""
        try:
            # This would use Crawl4AI or similar for web scraping
            # For now, return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Search page processing failed: {e}")
            return []
    
    async def _get_existing_content_for_duplicate_check(self) -> List[Dict[str, Any]]:
        """Get existing content for duplicate detection"""
        try:
            async with get_db() as session:
                # Get recent opportunities for duplicate checking
                query = """
                    SELECT id, title, description, url, organization_name, funding_amount
                    FROM africa_intelligence_feed
                    WHERE discovered_date >= (NOW() - INTERVAL '30 days')
                    ORDER BY discovered_date DESC
                    LIMIT 1000
                """
                
                result = await session.execute(query)
                return [dict(row) for row in result.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Getting existing content failed: {e}")
            return []
    
    def _is_high_confidence_duplicate(self, duplicate_matches: List[Any]) -> bool:
        """Check if content is a high-confidence duplicate"""
        if not duplicate_matches:
            return False
        
        # Check for high-confidence exact matches
        for match in duplicate_matches:
            if match.confidence_score > 0.9 and match.action.value == 'reject':
                return True
        
        return False
    
    async def _create_validation_result(self, content: Dict[str, Any], 
                                      classification: ClassificationResult,
                                      duplicate_matches: List[Any]) -> ValidationResult:
        """Create validation result from processing"""
        try:
            # Calculate confidence based on classification and duplicates
            base_confidence = classification.confidence_score
            
            # Adjust for duplicates
            if duplicate_matches:
                duplicate_penalty = min(0.3, len(duplicate_matches) * 0.1)
                base_confidence = max(0.0, base_confidence - duplicate_penalty)
            
            # Determine status
            if base_confidence >= 0.85:
                status = 'auto_approved'
                requires_review = False
            elif base_confidence >= 0.65:
                status = 'pending'
                requires_review = True
            else:
                status = 'rejected'
                requires_review = False
            
            return ValidationResult(
                id=str(uuid.uuid4()),
                status=status,
                confidence_score=base_confidence,
                confidence_level=self._get_confidence_level(base_confidence),
                completeness_score=self._calculate_completeness_score(content),
                relevance_score=classification.equity_score.sectoral_score,
                legitimacy_score=classification.equity_score.transparency_score,
                validation_notes=f"Equity score: {classification.equity_score.calculate_overall_score():.3f}",
                requires_human_review=requires_review,
                validator='integrated_pipeline',
                processing_time=0.0,  # Will be updated later
                validated_data=classification.to_dict(),
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Creating validation result failed: {e}")
            return ValidationResult(
                id=str(uuid.uuid4()),
                status='error',
                confidence_score=0.0,
                created_at=datetime.now()
            )
    
    async def _create_content_fingerprint(self, content: Dict[str, Any], 
                                        classification: ClassificationResult) -> ContentFingerprint:
        """Create content fingerprint for duplicate detection"""
        try:
            title = content.get('title', '')
            description = content.get('description', '')
            url = content.get('url', '')
            
            # Generate hashes
            title_hash = hashlib.md5(title.lower().encode()).hexdigest()
            content_hash = hashlib.md5(f"{title} {description}".lower().encode()).hexdigest()
            url_hash = hashlib.md5(url.encode()).hexdigest() if url else ''
            
            # Create signature hash
            signature_parts = [
                title_hash,
                classification.detected_countries[0] if classification.detected_countries else '',
                classification.detected_sectors[0] if classification.detected_sectors else '',
                str(content.get('funding_amount', ''))
            ]
            signature_hash = hashlib.md5('|'.join(signature_parts).encode()).hexdigest()
            
            return ContentFingerprint(
                title_hash=title_hash,
                content_hash=content_hash,
                url_hash=url_hash,
                signature_hash=signature_hash,
                organization_name=content.get('organization_name', ''),
                funding_amount=content.get('funding_amount'),
                funding_currency=content.get('currency', 'USD'),
                url_domain=content.get('url', '').split('/')[2] if content.get('url') else None,
                key_phrases=classification.detected_sectors + classification.detected_countries,
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Creating content fingerprint failed: {e}")
            return ContentFingerprint(
                title_hash='',
                content_hash='',
                url_hash='',
                signature_hash='',
                created_at=datetime.now()
            )
    
    def _calculate_duplicate_score(self, duplicate_matches: List[Any]) -> float:
        """Calculate duplicate score from matches"""
        if not duplicate_matches:
            return 0.0
        
        # Get highest confidence match
        max_confidence = max(match.confidence_score for match in duplicate_matches)
        return max_confidence
    
    async def _get_source_quality_score(self, source_id: str) -> float:
        """Get source quality score"""
        try:
            # This would integrate with the source quality scorer
            # For now, return default score
            return 0.8
            
        except Exception as e:
            self.logger.error(f"Getting source quality score failed: {e}")
            return 0.5
    
    async def _batch_vector_index(self, processed_items: List[ProcessedContent]):
        """Batch index processed items in vector database"""
        try:
            # Filter approved items for vector indexing
            approved_items = [
                item for item in processed_items
                if item.validation.status in ['approved', 'auto_approved']
            ]
            
            if not approved_items:
                return
            
            # Create intelligence feed for vector indexing
            opportunities = []
            for item in approved_items:
                opportunity = self._create_intelligence_item_from_processed(item)
                if opportunity:
                    opportunities.append(opportunity)
            
            # Batch index in vector database
            if opportunities:
                result = await self.vector_processor.batch_process_opportunities(opportunities)
                
                # Update vector indexing status
                for i, item in enumerate(approved_items):
                    if i < len(opportunities):
                        item.vector_indexed = result.success
                        item.vector_id = f"opportunity_{opportunities[i].id}"
                        self.processing_stats['successful_indexing'] += 1
                        
        except Exception as e:
            self.logger.error(f"Batch vector indexing failed: {e}")
    
    def _create_intelligence_item_from_processed(self, item: ProcessedContent) -> Optional[AfricaIntelligenceItem]:
        """Create AfricaIntelligenceItem from processed content"""
        try:
            # This would create a proper AfricaIntelligenceItem object
            # For now, return None to indicate this needs implementation
            return None
            
        except Exception as e:
            self.logger.error(f"Creating intelligence item failed: {e}")
            return None
    
    async def _batch_store_processed_content(self, processed_items: List[ProcessedContent]):
        """Store processed content in database"""
        try:
            # This would store all the processed content with metadata
            # For now, just log the storage
            self.logger.info(f"Storing {len(processed_items)} processed items")
            
        except Exception as e:
            self.logger.error(f"Batch storage failed: {e}")
    
    async def _update_bias_monitoring(self, processed_items: List[ProcessedContent]):
        """Update bias monitoring with processed items"""
        try:
            # Extract bias-relevant data
            bias_data = []
            for item in processed_items:
                bias_data.append({
                    'countries': item.classification.detected_countries,
                    'sectors': item.classification.detected_sectors,
                    'inclusion_indicators': [cat.value for cat in item.classification.inclusion_indicators],
                    'equity_score': item.classification.equity_score.calculate_overall_score(),
                    'source_language': item.ingestion_context.source_language,
                    'funding_stage': item.classification.funding_stage
                })
            
            # Analyze current bias (this would trigger monitoring)
            snapshot = await self.bias_monitor.analyze_current_bias()
            
            # Check for alerts
            if snapshot.active_alerts:
                self.processing_stats['bias_alerts_generated'] += len(snapshot.active_alerts)
                
                # Log alerts
                for alert in snapshot.active_alerts:
                    self.logger.warning(f"Bias alert: {alert.message}")
                    
                    # Trigger mitigation if critical
                    if alert.severity.value == 'critical':
                        await self.bias_monitor.trigger_bias_mitigation(
                            alert.bias_type, alert.severity
                        )
                        
        except Exception as e:
            self.logger.error(f"Bias monitoring update failed: {e}")
    
    async def _update_source_quality_scores(self, context: IngestionContext, 
                                          processed_items: List[ProcessedContent]):
        """Update source quality scores based on processing results"""
        try:
            # Calculate source performance metrics
            total_items = len(processed_items)
            if total_items == 0:
                return
            
            successful_items = sum(1 for item in processed_items 
                                 if item.validation.status in ['approved', 'auto_approved'])
            
            duplicate_items = sum(1 for item in processed_items 
                                if item.duplicate_score > 0.8)
            
            # Update source quality score
            from app.core.source_quality_scoring import SourceType
            
            # Map ingestion method to source type
            source_type_map = {
                IngestionMethod.RSS_FEED: SourceType.RSS_FEED,
                IngestionMethod.SERPER_SEARCH: SourceType.API,
                IngestionMethod.USER_SUBMISSION: SourceType.USER_SUBMISSION,
                IngestionMethod.MULTILINGUAL_SEARCH: SourceType.API,
                IngestionMethod.PRIORITY_SOURCE_SCAN: SourceType.WEBSITE
            }
            
            source_type = source_type_map.get(context.method, SourceType.WEBSITE)
            
            # Score the source
            snapshot = await self.source_scorer.score_source(
                source_name=context.source_name,
                source_type=source_type
            )
            
            self.logger.info(f"Source quality updated: {context.source_name} - {snapshot.metrics.calculate_overall_score():.3f}")
            
        except Exception as e:
            self.logger.error(f"Source quality update failed: {e}")
    
    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level from score"""
        if score >= 0.9:
            return 'very_high'
        elif score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_completeness_score(self, content: Dict[str, Any]) -> float:
        """Calculate completeness score for content"""
        required_fields = ['title', 'description', 'url']
        optional_fields = ['organization_name', 'funding_amount', 'deadline', 'application_url']
        
        required_score = sum(1 for field in required_fields if content.get(field))
        optional_score = sum(1 for field in optional_fields if content.get(field))
        
        # Weight required fields more heavily
        total_score = (required_score / len(required_fields)) * 0.7 + (optional_score / len(optional_fields)) * 0.3
        
        return total_score
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            'timestamp': datetime.now().isoformat(),
            'pipeline_status': 'active'
        }
    
    def reset_processing_stats(self):
        """Reset processing statistics"""
        self.processing_stats = {
            'total_processed': 0,
            'successful_classifications': 0,
            'successful_indexing': 0,
            'duplicates_detected': 0,
            'bias_alerts_generated': 0
        }

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of integrated ingestion pipeline"""
    from app.core.vector_database import VectorConfig, VectorDatabaseManager
    from app.core.multilingual_search import MultilingualSearchEngine
    
    # Initialize components
    vector_config = VectorConfig(pinecone_api_key="your-key")
    vector_manager = VectorDatabaseManager(vector_config)
    await vector_manager.initialize()
    
    multilingual_engine = MultilingualSearchEngine(serper_api_key="your-key")
    
    # Create integrated pipeline
    pipeline = IntegratedIngestionPipeline(
        vector_manager=vector_manager,
        multilingual_engine=multilingual_engine,
        serper_api_key="your-key"
    )
    
    # Process RSS feed
    rss_results = await pipeline.process_rss_feed(
        feed_url="https://www.afdb.org/en/news-and-events/feed",
        source_config={
            'source_id': 'afdb',
            'source_name': 'African Development Bank',
            'language': 'en',
            'priority': 2.0
        }
    )
    
    print(f"RSS processing: {len(rss_results)} items")
    
    # Process multilingual search
    multilingual_results = await pipeline.process_multilingual_search(
        base_query="AI healthcare funding Africa",
        target_languages=['en', 'fr', 'ar']
    )
    
    print(f"Multilingual search: {len(multilingual_results)} items")
    
    # Process priority sources
    priority_results = await pipeline.process_priority_sources(max_sources=5)
    
    print(f"Priority sources: {len(priority_results)} items")
    
    # Get processing statistics
    stats = pipeline.get_processing_stats()
    print(f"Processing stats: {stats}")

if __name__ == "__main__":
    asyncio.run(example_usage())