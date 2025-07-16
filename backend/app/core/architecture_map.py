"""
Data Ingestion Architecture Map & Documentation
==============================================

Complete architecture mapping for data ingestion modules with clear pathways,
fault isolation, and quality control mechanisms.

Architecture Overview:
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DATA INGESTION ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   RSS Feed  │  │   Serper    │  │    User     │  │   Crawl4AI  │              │
│  │   Module    │  │   Module    │  │ Submission  │  │   Module    │              │
│  │             │  │             │  │   Module    │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘              │
│          │                │                │                │                      │
│          └────────────────┼────────────────┼────────────────┘                      │
│                           │                │                                       │
│                           ▼                ▼                                       │
│                  ┌─────────────────────────────────────────┐                      │
│                  │        INGESTION ROUTER                 │                      │
│                  │    (Queue Classification)               │                      │
│                  └─────────────────────────────────────────┘                      │
│                                   │                                               │
│                                   ▼                                               │
│                  ┌─────────────────────────────────────────┐                      │
│                  │      CONTENT CLASSIFIER                 │                      │
│                  │  (Announcement vs Opportunity)          │                      │
│                  └─────────────────────────────────────────┘                      │
│                                   │                                               │
│                                   ▼                                               │
│                  ┌─────────────────────────────────────────┐                      │
│                  │       DUPLICATE DETECTOR                │                      │
│                  │   (Advanced Similarity Check)           │                      │
│                  └─────────────────────────────────────────┘                      │
│                                   │                                               │
│                                   ▼                                               │
│                  ┌─────────────────────────────────────────┐                      │
│                  │        AI VALIDATOR                     │                      │
│                  │    (Quality & Legitimacy Check)         │                      │
│                  └─────────────────────────────────────────┘                      │
│                                   │                                               │
│                                   ▼                                               │
│                  ┌─────────────────────────────────────────┐                      │
│                  │         DATA ENHANCER                   │                      │
│                  │     (Crawl4AI Deep Extraction)          │                      │
│                  └─────────────────────────────────────────┘                      │
│                                   │                                               │
│                                   ▼                                               │
│                  ┌─────────────────────────────────────────┐                      │
│                  │        FINAL VALIDATOR                  │                      │
│                  │      (Confidence Scoring)               │                      │
│                  └─────────────────────────────────────────┘                      │
│                                   │                                               │
│                          ┌────────┴────────┐                                      │
│                          ▼                 ▼                                      │
│                 ┌─────────────┐   ┌─────────────┐                                 │
│                 │ AUTO-APPROVE│   │   REVIEW    │                                 │
│                 │   QUEUE     │   │   QUEUE     │                                 │
│                 └─────────────┘   └─────────────┘                                 │
│                          │                 │                                      │
│                          ▼                 ▼                                      │
│                 ┌─────────────────────────────────────────┐                      │
│                 │           DATABASE                       │                      │
│                 │        (Published)                       │                      │
│                 └─────────────────────────────────────────┘                      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# ARCHITECTURE COMPONENTS MAPPING
# =============================================================================

class ModuleType(Enum):
    """Types of ingestion modules"""
    RSS_FEED = "rss_feed"
    SERPER_SEARCH = "serper_search"
    USER_SUBMISSION = "user_submission"
    CRAWL4AI_EXTRACTION = "crawl4ai_extraction"
    MANUAL_ADMIN = "manual_admin"

class ModuleStatus(Enum):
    """Status of ingestion modules"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"

class ContentType(Enum):
    """Types of content detected"""
    FUNDING_OPPORTUNITY = "funding_opportunity"
    FUNDING_ANNOUNCEMENT = "funding_announcement"
    NEWS_ARTICLE = "news_article"
    PRESS_RELEASE = "press_release"
    BLOG_POST = "blog_post"
    DUPLICATE = "duplicate"
    IRRELEVANT = "irrelevant"

class ProcessingStage(Enum):
    """Stages in the processing pipeline"""
    INGESTION = "ingestion"
    CLASSIFICATION = "classification"
    DUPLICATE_CHECK = "duplicate_check"
    VALIDATION = "validation"
    ENHANCEMENT = "enhancement"
    FINAL_VALIDATION = "final_validation"
    ROUTING = "routing"
    STORAGE = "storage"

# =============================================================================
# MODULE DEFINITIONS
# =============================================================================

@dataclass
class ModuleConfig:
    """Configuration for each ingestion module"""
    module_type: ModuleType
    name: str
    enabled: bool = True
    priority: int = 1
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_count: int = 3
    circuit_breaker_threshold: int = 5  # failures before opening
    quality_threshold: float = 0.6
    
    # Module-specific settings
    settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModuleHealth:
    """Health metrics for each module"""
    module_type: ModuleType
    status: ModuleStatus
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    avg_processing_time: float = 0.0
    quality_score: float = 0.0
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-1)"""
        if self.success_count + self.failure_count == 0:
            return 1.0
        
        success_rate = self.success_count / (self.success_count + self.failure_count)
        
        # Time penalty for recent failures
        time_penalty = 0.0
        if self.last_failure and self.last_success:
            if self.last_failure > self.last_success:
                time_penalty = 0.2
        
        return max(0.0, (success_rate * 0.5) + (self.quality_score * 0.3) + (0.2 - time_penalty))

# =============================================================================
# INGESTION MODULES
# =============================================================================

class IngestionModule:
    """Base class for all ingestion modules"""
    
    def __init__(self, config: ModuleConfig):
        self.config = config
        self.health = ModuleHealth(
            module_type=config.module_type,
            status=ModuleStatus.ACTIVE
        )
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        
    async def ingest(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main ingestion method - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def health_check(self) -> ModuleHealth:
        """Check module health"""
        return self.health
    
    def update_health_metrics(self, success: bool, processing_time: float, quality_score: float = 0.0):
        """Update health metrics"""
        if success:
            self.health.success_count += 1
            self.health.last_success = datetime.now()
            self.circuit_breaker_failures = 0
        else:
            self.health.failure_count += 1
            self.health.last_failure = datetime.now()
            self.circuit_breaker_failures += 1
            
        self.health.avg_processing_time = (
            (self.health.avg_processing_time * (self.health.success_count + self.health.failure_count - 1) + processing_time) /
            (self.health.success_count + self.health.failure_count)
        )
        
        if quality_score > 0:
            self.health.quality_score = (self.health.quality_score + quality_score) / 2
        
        # Circuit breaker logic
        if self.circuit_breaker_failures >= self.config.circuit_breaker_threshold:
            self.circuit_breaker_open = True
            self.health.status = ModuleStatus.FAILED
            self.logger.error(f"Circuit breaker opened for {self.config.name}")

class RSSFeedModule(IngestionModule):
    """RSS feed ingestion module"""
    
    async def ingest(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest RSS feed data"""
        if self.circuit_breaker_open:
            self.logger.warning(f"Circuit breaker open for {self.config.name}")
            return []
        
        start_time = datetime.now()
        
        try:
            feed_url = source_data.get('feed_url')
            if not feed_url:
                raise ValueError("Missing feed_url in source_data")
            
            # RSS processing logic here
            # This would integrate with the existing RSS processing code
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(True, processing_time, 0.8)
            
            return []  # Placeholder
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(False, processing_time)
            self.logger.error(f"RSS ingestion failed: {e}")
            return []

class SerperSearchModule(IngestionModule):
    """Serper search ingestion module"""
    
    async def ingest(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest Serper search results"""
        if self.circuit_breaker_open:
            self.logger.warning(f"Circuit breaker open for {self.config.name}")
            return []
        
        start_time = datetime.now()
        
        try:
            search_query = source_data.get('query')
            if not search_query:
                raise ValueError("Missing query in source_data")
            
            # Serper processing logic here
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(True, processing_time, 0.7)
            
            return []  # Placeholder
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(False, processing_time)
            self.logger.error(f"Serper ingestion failed: {e}")
            return []

class UserSubmissionModule(IngestionModule):
    """User submission ingestion module"""
    
    async def ingest(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest user submission data"""
        if self.circuit_breaker_open:
            self.logger.warning(f"Circuit breaker open for {self.config.name}")
            return []
        
        start_time = datetime.now()
        
        try:
            submission_data = source_data.get('submission_data')
            if not submission_data:
                raise ValueError("Missing submission_data in source_data")
            
            # User submission processing logic here
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(True, processing_time, 0.9)  # Higher quality from users
            
            return []  # Placeholder
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(False, processing_time)
            self.logger.error(f"User submission ingestion failed: {e}")
            return []

class Crawl4AIModule(IngestionModule):
    """Crawl4AI ingestion module"""
    
    async def ingest(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest with Crawl4AI"""
        if self.circuit_breaker_open:
            self.logger.warning(f"Circuit breaker open for {self.config.name}")
            return []
        
        start_time = datetime.now()
        
        try:
            url = source_data.get('url')
            if not url:
                raise ValueError("Missing url in source_data")
            
            # Crawl4AI processing logic here
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(True, processing_time, 0.85)  # High quality
            
            return []  # Placeholder
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_health_metrics(False, processing_time)
            self.logger.error(f"Crawl4AI ingestion failed: {e}")
            return []

# =============================================================================
# CONTENT CLASSIFICATION SYSTEM
# =============================================================================

class ContentClassifier:
    """Classifies content type to filter out announcements from actual opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns for different content types
        self.announcement_patterns = [
            r'announces?\s+(funding|grant|investment)',
            r'(company|organization|foundation)\s+receives?\s+funding',
            r'funding\s+announcement',
            r'investment\s+announcement',
            r'awarded\s+grant',
            r'secures?\s+funding',
            r'raises?\s+\$\d+',
            r'funding\s+round',
            r'investment\s+round',
            r'(startup|company)\s+gets?\s+funding'
        ]
        
        self.opportunity_patterns = [
            r'apply\s+(for|to)',
            r'application\s+(deadline|due)',
            r'eligible\s+(for|to)',
            r'accepting\s+applications',
            r'call\s+for\s+proposals',
            r'rfp\s+|request\s+for\s+proposal',
            r'funding\s+available',
            r'grant\s+opportunity',
            r'investment\s+opportunity',
            r'applications?\s+(open|accepted|invited)',
            r'deadline\s+for\s+applications?',
            r'submit\s+proposals?'
        ]
        
        self.duplicate_indicators = [
            r'previously\s+reported',
            r'as\s+reported\s+earlier',
            r'update\s+on\s+previous',
            r'follow-up\s+to',
            r'earlier\s+announcement'
        ]
    
    async def classify_content(self, content: Dict[str, Any]) -> ContentType:
        """Classify content type using pattern matching and AI"""
        try:
            title = content.get('title', '').lower()
            description = content.get('description', '').lower()
            text = f"{title} {description}"
            
            # Check for duplicate indicators first
            import re
            if any(re.search(pattern, text) for pattern in self.duplicate_indicators):
                return ContentType.DUPLICATE
            
            # Count pattern matches
            announcement_matches = sum(1 for pattern in self.announcement_patterns if re.search(pattern, text))
            opportunity_matches = sum(1 for pattern in self.opportunity_patterns if re.search(pattern, text))
            
            # Decision logic
            if opportunity_matches > announcement_matches:
                return ContentType.FUNDING_OPPORTUNITY
            elif announcement_matches > opportunity_matches:
                return ContentType.FUNDING_ANNOUNCEMENT
            else:
                # Use AI for ambiguous cases
                return await self._ai_classify_content(content)
                
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            return ContentType.IRRELEVANT
    
    async def _ai_classify_content(self, content: Dict[str, Any]) -> ContentType:
        """Use AI to classify ambiguous content"""
        try:
            import openai
            
            client = openai.AsyncOpenAI()
            
            prompt = f"""
            Classify this content as one of:
            1. FUNDING_OPPORTUNITY - Actual funding you can apply for
            2. FUNDING_ANNOUNCEMENT - News about someone receiving funding
            3. NEWS_ARTICLE - General news article
            4. PRESS_RELEASE - Company press release
            5. IRRELEVANT - Not related to funding
            
            Title: {content.get('title', '')}
            Description: {content.get('description', '')}
            
            Return only the classification name.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            classification = response.choices[0].message.content.strip()
            
            # Map to enum
            classification_map = {
                'FUNDING_OPPORTUNITY': ContentType.FUNDING_OPPORTUNITY,
                'FUNDING_ANNOUNCEMENT': ContentType.FUNDING_ANNOUNCEMENT,
                'NEWS_ARTICLE': ContentType.NEWS_ARTICLE,
                'PRESS_RELEASE': ContentType.PRESS_RELEASE,
                'IRRELEVANT': ContentType.IRRELEVANT
            }
            
            return classification_map.get(classification, ContentType.IRRELEVANT)
            
        except Exception as e:
            self.logger.error(f"AI classification failed: {e}")
            return ContentType.IRRELEVANT

# =============================================================================
# ADVANCED DUPLICATE DETECTION
# =============================================================================

class DuplicateDetector:
    """Advanced duplicate detection system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.similarity_threshold = 0.85
        self.title_threshold = 0.9
        
    async def check_duplicate(self, content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Check if content is duplicate using multiple methods"""
        try:
            # Method 1: Exact title match
            title = content.get('title', '').strip().lower()
            for existing in existing_content:
                existing_title = existing.get('title', '').strip().lower()
                if title == existing_title:
                    return True, f"Exact title match: {existing.get('id')}"
            
            # Method 2: Title similarity
            title_similarity = await self._calculate_title_similarity(content, existing_content)
            if title_similarity['is_duplicate']:
                return True, f"Title similarity: {title_similarity['match_id']}"
            
            # Method 3: Content similarity
            content_similarity = await self._calculate_content_similarity(content, existing_content)
            if content_similarity['is_duplicate']:
                return True, f"Content similarity: {content_similarity['match_id']}"
            
            # Method 4: URL/Link match
            url_match = await self._check_url_match(content, existing_content)
            if url_match['is_duplicate']:
                return True, f"URL match: {url_match['match_id']}"
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Duplicate check failed: {e}")
            return False, None
    
    async def _calculate_title_similarity(self, content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate title similarity using fuzzy matching"""
        try:
            from difflib import SequenceMatcher
            
            title = content.get('title', '').strip().lower()
            
            for existing in existing_content:
                existing_title = existing.get('title', '').strip().lower()
                
                # Calculate similarity ratio
                similarity = SequenceMatcher(None, title, existing_title).ratio()
                
                if similarity >= self.title_threshold:
                    return {
                        'is_duplicate': True,
                        'match_id': existing.get('id'),
                        'similarity': similarity
                    }
            
            return {'is_duplicate': False}
            
        except Exception as e:
            self.logger.error(f"Title similarity calculation failed: {e}")
            return {'is_duplicate': False}
    
    async def _calculate_content_similarity(self, content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate content similarity using TF-IDF"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            description = content.get('description', '').strip().lower()
            
            # Prepare text corpus
            texts = [description]
            existing_texts = []
            existing_ids = []
            
            for existing in existing_content:
                existing_desc = existing.get('description', '').strip().lower()
                if existing_desc:
                    texts.append(existing_desc)
                    existing_texts.append(existing_desc)
                    existing_ids.append(existing.get('id'))
            
            if not existing_texts:
                return {'is_duplicate': False}
            
            # Calculate TF-IDF
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Check for high similarity
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[max_similarity_idx]
            
            if max_similarity >= self.similarity_threshold:
                return {
                    'is_duplicate': True,
                    'match_id': existing_ids[max_similarity_idx],
                    'similarity': max_similarity
                }
            
            return {'is_duplicate': False}
            
        except Exception as e:
            self.logger.error(f"Content similarity calculation failed: {e}")
            return {'is_duplicate': False}
    
    async def _check_url_match(self, content: Dict[str, Any], existing_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for URL/link matches"""
        try:
            url = content.get('link', '').strip()
            if not url:
                return {'is_duplicate': False}
            
            for existing in existing_content:
                existing_url = existing.get('link', '').strip()
                if url == existing_url:
                    return {
                        'is_duplicate': True,
                        'match_id': existing.get('id')
                    }
            
            return {'is_duplicate': False}
            
        except Exception as e:
            self.logger.error(f"URL match check failed: {e}")
            return {'is_duplicate': False}

# =============================================================================
# PROCESSING PIPELINE COORDINATOR
# =============================================================================

class ProcessingPipelineCoordinator:
    """Coordinates the entire processing pipeline"""
    
    def __init__(self):
        self.modules = {}
        self.content_classifier = ContentClassifier()
        self.duplicate_detector = DuplicateDetector()
        self.logger = logging.getLogger(__name__)
        
        # Initialize modules
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize all ingestion modules"""
        module_configs = [
            ModuleConfig(ModuleType.RSS_FEED, "rss_feed_module", rate_limit=200),
            ModuleConfig(ModuleType.SERPER_SEARCH, "serper_search_module", rate_limit=100),
            ModuleConfig(ModuleType.USER_SUBMISSION, "user_submission_module", rate_limit=50),
            ModuleConfig(ModuleType.CRAWL4AI_EXTRACTION, "crawl4ai_module", rate_limit=30),
        ]
        
        for config in module_configs:
            if config.module_type == ModuleType.RSS_FEED:
                self.modules[config.module_type] = RSSFeedModule(config)
            elif config.module_type == ModuleType.SERPER_SEARCH:
                self.modules[config.module_type] = SerperSearchModule(config)
            elif config.module_type == ModuleType.USER_SUBMISSION:
                self.modules[config.module_type] = UserSubmissionModule(config)
            elif config.module_type == ModuleType.CRAWL4AI_EXTRACTION:
                self.modules[config.module_type] = Crawl4AIModule(config)
    
    async def process_content(self, module_type: ModuleType, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process content through the complete pipeline"""
        try:
            processing_id = str(uuid.uuid4())
            
            # Stage 1: Ingestion
            module = self.modules.get(module_type)
            if not module:
                raise ValueError(f"Module {module_type} not found")
            
            if module.circuit_breaker_open:
                return {
                    'success': False,
                    'error': f'Module {module_type} circuit breaker open',
                    'processing_id': processing_id
                }
            
            raw_content = await module.ingest(source_data)
            
            if not raw_content:
                return {
                    'success': False,
                    'error': 'No content extracted',
                    'processing_id': processing_id
                }
            
            processed_items = []
            
            for item in raw_content:
                # Stage 2: Content Classification
                content_type = await self.content_classifier.classify_content(item)
                
                if content_type == ContentType.FUNDING_ANNOUNCEMENT:
                    self.logger.info(f"Filtered out funding announcement: {item.get('title', 'Unknown')}")
                    continue
                
                if content_type == ContentType.IRRELEVANT:
                    self.logger.info(f"Filtered out irrelevant content: {item.get('title', 'Unknown')}")
                    continue
                
                # Stage 3: Duplicate Detection
                # This would check against existing database content
                existing_content = []  # Placeholder - would fetch from database
                is_duplicate, match_info = await self.duplicate_detector.check_duplicate(item, existing_content)
                
                if is_duplicate:
                    self.logger.info(f"Filtered out duplicate: {item.get('title', 'Unknown')} - {match_info}")
                    continue
                
                # Add processing metadata
                item['processing_id'] = processing_id
                item['content_type'] = content_type.value
                item['module_type'] = module_type.value
                item['processed_at'] = datetime.now().isoformat()
                
                processed_items.append(item)
            
            return {
                'success': True,
                'processed_items': processed_items,
                'processing_id': processing_id,
                'filtered_count': len(raw_content) - len(processed_items)
            }
            
        except Exception as e:
            self.logger.error(f"Processing pipeline failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_id': processing_id
            }
    
    async def get_module_health(self) -> Dict[str, Any]:
        """Get health status of all modules"""
        health_status = {}
        
        for module_type, module in self.modules.items():
            health = await module.health_check()
            health_status[module_type.value] = {
                'status': health.status.value,
                'health_score': health.calculate_health_score(),
                'success_rate': health.success_count / (health.success_count + health.failure_count) if (health.success_count + health.failure_count) > 0 else 0,
                'avg_processing_time': health.avg_processing_time,
                'quality_score': health.quality_score,
                'last_success': health.last_success.isoformat() if health.last_success else None,
                'last_failure': health.last_failure.isoformat() if health.last_failure else None
            }
        
        return health_status
    
    async def disable_module(self, module_type: ModuleType):
        """Disable a specific module"""
        if module_type in self.modules:
            self.modules[module_type].health.status = ModuleStatus.DISABLED
            self.logger.info(f"Module {module_type.value} disabled")
    
    async def enable_module(self, module_type: ModuleType):
        """Enable a specific module"""
        if module_type in self.modules:
            self.modules[module_type].health.status = ModuleStatus.ACTIVE
            self.modules[module_type].circuit_breaker_open = False
            self.modules[module_type].circuit_breaker_failures = 0
            self.logger.info(f"Module {module_type.value} enabled")

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of the processing pipeline"""
    coordinator = ProcessingPipelineCoordinator()
    
    # Process RSS feed
    rss_data = {
        'feed_url': 'https://example.com/rss',
        'feed_id': 'example_feed'
    }
    
    result = await coordinator.process_content(ModuleType.RSS_FEED, rss_data)
    print(f"RSS Processing Result: {result}")
    
    # Get module health
    health = await coordinator.get_module_health()
    print(f"Module Health: {health}")

if __name__ == "__main__":
    asyncio.run(example_usage())