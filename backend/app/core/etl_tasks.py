"""
Specialized ETL Tasks for Multi-Method Data Ingestion
===================================================

Robust task definitions for handling diverse data sources:
- RSS feeds with AI-powered content extraction
- Serper search API with relevance scoring
- User submissions with validation
- Crawl4AI web scraping with intelligent parsing
- Manual admin submissions

Focus on speed: Discovery → Extraction → Review → Publishing
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import time
import requests
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from app.core.llm_provider import get_smart_llm_provider, TaskType, validate_content, check_relevance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# LIGHTWEIGHT RATE LIMITING
# =============================================================================

class SimpleRateLimiter:
    """Simple in-memory rate limiter for API calls"""
    
    def __init__(self):
        self._calls = {}
    
    def can_make_request(self, resource: str, max_calls: int, window_seconds: int = 60) -> bool:
        """Check if we can make a request within rate limits"""
        now = time.time()
        
        if resource not in self._calls:
            self._calls[resource] = []
        
        # Remove old calls outside the window
        self._calls[resource] = [call_time for call_time in self._calls[resource] 
                                if now - call_time < window_seconds]
        
        # Check if we're under the limit
        if len(self._calls[resource]) < max_calls:
            self._calls[resource].append(now)
            return True
        
        return False
    
    def wait_time(self, resource: str, window_seconds: int = 60) -> float:
        """Get time to wait before next request is allowed"""
        if resource not in self._calls or not self._calls[resource]:
            return 0.0
        
        oldest_call = min(self._calls[resource])
        wait_time = window_seconds - (time.time() - oldest_call)
        return max(0.0, wait_time)

# Global rate limiter instance
rate_limiter = SimpleRateLimiter()

# Simple cache for external API results
_serper_cache = {}
_crawl4ai_cache = {}
_cache_ttl = 3600  # 1 hour

def _cleanup_cache():
    """Clean up expired cache entries"""
    now = time.time()
    
    # Clean Serper cache
    expired_keys = [k for k, (_, timestamp) in _serper_cache.items() 
                   if now - timestamp > _cache_ttl]
    for key in expired_keys:
        del _serper_cache[key]
    
    # Clean Crawl4AI cache
    expired_keys = [k for k, (_, timestamp) in _crawl4ai_cache.items() 
                   if now - timestamp > _cache_ttl]
    for key in expired_keys:
        del _crawl4ai_cache[key]

# =============================================================================
# SPECIALIZED DATA INGESTION TASKS
# =============================================================================

@dataclass
class IngestionResult:
    """Result of data ingestion with AI validation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    validation_notes: Optional[str] = None
    requires_human_review: bool = False
    extraction_method: str = "unknown"
    processing_time: float = 0.0
    error: Optional[str] = None

class AIValidationConfig:
    """Configuration for AI-powered validation"""
    
    # Confidence Thresholds
    AUTO_APPROVE_THRESHOLD = 0.85
    HUMAN_REVIEW_THRESHOLD = 0.65
    AUTO_REJECT_THRESHOLD = 0.30
    
    # Validation Prompts
    OPPORTUNITY_VALIDATION_PROMPT = """
    You are an AI assistant specializing in African AI intelligence feed. 
    Analyze the following content and extract intelligence item information.
    
    Content to analyze:
    {content}
    
    Please extract and validate:
    1. Is this a legitimate intelligence item? (Yes/No)
    2. Title of the opportunity
    3. Organization/Funder name
    4. Funding amount (if specified)
    5. Deadline date
    6. Geographic focus (Africa-specific?)
    7. AI/Technology relevance
    8. Application requirements
    9. Confidence score (0-1)
    10. Any red flags or concerns
    
    Return as JSON with high confidence scores only for clear, legitimate opportunities.
    """
    
    RELEVANCE_SCORING_PROMPT = """
    Rate the relevance of this intelligence item for African AI development (0-1):
    
    Content: {content}
    
    Scoring criteria:
    - Geographic relevance to Africa (0.3 weight)
    - AI/Technology focus (0.4 weight)  
    - Legitimacy and clarity (0.3 weight)
    
    Return JSON with: {{"relevance_score": 0.0-1.0, "reasoning": "explanation"}}
    """

# =============================================================================
# RSS FEED PROCESSING TASKS
# =============================================================================

async def process_rss_feed_task(task: ETLTask) -> IngestionResult:
    """Process RSS feed with AI-powered content extraction"""
    start_time = datetime.now()
    
    try:
        payload = task.payload
        feed_url = payload.get('feed_url')
        feed_id = payload.get('feed_id')
        
        if not feed_url:
            return IngestionResult(
                success=False,
                error="Missing feed_url in payload",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        logger.info(f"Processing RSS feed: {feed_url}")
        
        # Fetch RSS feed
        import feedparser
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            logger.warning(f"RSS feed has parsing issues: {feed_url}")
        
        opportunities = []
        
        for entry in feed.entries[:20]:  # Process latest 20 entries
            try:
                # Extract content with AI
                content = entry.get('summary', '') or entry.get('description', '')
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # AI-powered relevance check
                relevance_result = await _check_ai_relevance(content, title)
                
                if relevance_result['relevance_score'] > 0.6:
                    # Deep content extraction with Crawl4AI
                    extracted_data = await _extract_with_crawl4ai(link, content)
                    
                    if extracted_data['success']:
                        opportunity = {
                            'title': title,
                            'description': content,
                            'link': link,
                            'source_type': 'rss',
                            'source_id': feed_id,
                            'raw_content': content,
                            'extracted_data': extracted_data['data'],
                            'confidence_score': extracted_data['confidence_score'],
                            'published_date': entry.get('published'),
                            'requires_review': extracted_data['confidence_score'] < AIValidationConfig.AUTO_APPROVE_THRESHOLD
                        }
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.error(f"Error processing RSS entry: {e}")
                continue
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = IngestionResult(
            success=True,
            data={
                'opportunities': opportunities,
                'feed_url': feed_url,
                'feed_id': feed_id,
                'processed_count': len(opportunities)
            },
            confidence_score=0.8,  # RSS feeds are generally reliable
            extraction_method='rss_ai',
            processing_time=processing_time,
            requires_human_review=any(opp['requires_review'] for opp in opportunities)
        )
        
        # Automatically index in vector database if opportunities were found
        if opportunities and len(opportunities) > 0:
            try:
                # Dynamically import to avoid circular imports
                from .vector_indexing import index_rss_feed_results
                
                # Schedule vector indexing asynchronously
                asyncio.create_task(index_rss_feed_results(result.data))
                logger.info(f"Scheduled vector indexing for {len(opportunities)} opportunities from RSS feed: {feed_url}")
            except Exception as e:
                logger.warning(f"Failed to schedule vector indexing for RSS feed: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"RSS processing failed: {e}")
        return IngestionResult(
            success=False,
            error=str(e),
            processing_time=(datetime.now() - start_time).total_seconds()
        )

# =============================================================================
# SERPER SEARCH API TASKS
# =============================================================================

async def process_serper_search_task(task: ETLTask) -> IngestionResult:
    """Process Serper search results with AI validation"""
    start_time = datetime.now()
    
    try:
        payload = task.payload
        search_query = payload.get('query')
        search_type = payload.get('search_type', 'search')
        
        if not search_query:
            return IngestionResult(
                success=False,
                error="Missing search query in payload",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        logger.info(f"Processing Serper search: {search_query}")
        
        # Execute Serper search
        serper_results = await _execute_serper_search(search_query, search_type)
        
        if not serper_results['success']:
            return IngestionResult(
                success=False,
                error=serper_results['error'],
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        opportunities = []
        
        for result in serper_results['data']['organic'][:10]:  # Process top 10 results
            try:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                
                # AI relevance scoring
                relevance_result = await _check_ai_relevance(snippet, title)
                
                if relevance_result['relevance_score'] > 0.5:
                    # Deep extraction with Crawl4AI
                    extracted_data = await _extract_with_crawl4ai(link, snippet)
                    
                    if extracted_data['success']:
                        opportunity = {
                            'title': title,
                            'description': snippet,
                            'link': link,
                            'source_type': 'serper',
                            'source_id': f"serper_{search_query}",
                            'search_query': search_query,
                            'extracted_data': extracted_data['data'],
                            'confidence_score': extracted_data['confidence_score'],
                            'relevance_score': relevance_result['relevance_score'],
                            'requires_review': extracted_data['confidence_score'] < AIValidationConfig.AUTO_APPROVE_THRESHOLD
                        }
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.error(f"Error processing Serper result: {e}")
                continue
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return IngestionResult(
            success=True,
            data={
                'opportunities': opportunities,
                'search_query': search_query,
                'processed_count': len(opportunities)
            },
            confidence_score=0.7,  # Serper results need more validation
            extraction_method='serper_ai',
            processing_time=processing_time,
            requires_human_review=any(opp['requires_review'] for opp in opportunities)
        )
        
    except Exception as e:
        logger.error(f"Serper processing failed: {e}")
        return IngestionResult(
            success=False,
            error=str(e),
            processing_time=(datetime.now() - start_time).total_seconds()
        )

# =============================================================================
# USER SUBMISSION TASKS
# =============================================================================

async def process_user_submission_task(task: ETLTask) -> IngestionResult:
    """Process user submission with enhanced validation"""
    start_time = datetime.now()
    
    try:
        payload = task.payload
        submission_data = payload.get('submission_data')
        user_id = payload.get('user_id')
        
        if not submission_data:
            return IngestionResult(
                success=False,
                error="Missing submission data in payload",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        logger.info(f"Processing user submission from user: {user_id}")
        
        # Enhanced validation for user submissions
        validation_result = await _validate_user_submission(submission_data)
        
        if validation_result['confidence_score'] > AIValidationConfig.AUTO_APPROVE_THRESHOLD:
            # High confidence - minimal review needed
            requires_review = False
        elif validation_result['confidence_score'] > AIValidationConfig.HUMAN_REVIEW_THRESHOLD:
            # Medium confidence - human review required
            requires_review = True
        else:
            # Low confidence - likely invalid
            return IngestionResult(
                success=False,
                error="Submission failed validation checks",
                confidence_score=validation_result['confidence_score'],
                validation_notes=validation_result.get('notes'),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        # If URL provided, enhance with Crawl4AI
        enhanced_data = submission_data.copy()
        if submission_data.get('url'):
            crawl_result = await _extract_with_crawl4ai(
                submission_data['url'], 
                submission_data.get('description', '')
            )
            if crawl_result['success']:
                enhanced_data.update(crawl_result['data'])
        
        opportunity = {
            'title': submission_data.get('title'),
            'description': submission_data.get('description'),
            'link': submission_data.get('url'),
            'source_type': 'user_submission',
            'source_id': f"user_{user_id}",
            'user_id': user_id,
            'original_submission': submission_data,
            'enhanced_data': enhanced_data,
            'confidence_score': validation_result['confidence_score'],
            'requires_review': requires_review,
            'validation_notes': validation_result.get('notes')
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return IngestionResult(
            success=True,
            data={
                'opportunities': [opportunity],
                'user_id': user_id,
                'processed_count': 1
            },
            confidence_score=validation_result['confidence_score'],
            extraction_method='user_submission_ai',
            processing_time=processing_time,
            requires_human_review=requires_review
        )
        
    except Exception as e:
        logger.error(f"User submission processing failed: {e}")
        return IngestionResult(
            success=False,
            error=str(e),
            processing_time=(datetime.now() - start_time).total_seconds()
        )

# =============================================================================
# CRAWL4AI SPECIALIZED TASKS
# =============================================================================

async def process_crawl4ai_task(task: ETLTask) -> IngestionResult:
    """Process URL with Crawl4AI and advanced AI extraction"""
    start_time = datetime.now()
    
    try:
        payload = task.payload
        url = payload.get('url')
        context = payload.get('context', '')
        extraction_type = payload.get('extraction_type', 'intelligence_item')
        
        if not url:
            return IngestionResult(
                success=False,
                error="Missing URL in payload",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        logger.info(f"Processing Crawl4AI extraction: {url}")
        
        # Advanced Crawl4AI extraction
        extraction_result = await _extract_with_crawl4ai(url, context, extraction_type)
        
        if not extraction_result['success']:
            return IngestionResult(
                success=False,
                error=extraction_result['error'],
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        extracted_data = extraction_result['data']
        
        # Additional AI validation
        validation_result = await _validate_extracted_content(extracted_data)
        
        opportunity = {
            'title': extracted_data.get('title'),
            'description': extracted_data.get('description'),
            'link': url,
            'source_type': 'crawl4ai',
            'source_id': f"crawl4ai_{hash(url)}",
            'extracted_data': extracted_data,
            'confidence_score': validation_result['confidence_score'],
            'requires_review': validation_result['confidence_score'] < AIValidationConfig.AUTO_APPROVE_THRESHOLD,
            'validation_notes': validation_result.get('notes'),
            'extraction_method': extraction_type
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return IngestionResult(
            success=True,
            data={
                'opportunities': [opportunity],
                'url': url,
                'processed_count': 1
            },
            confidence_score=validation_result['confidence_score'],
            extraction_method='crawl4ai_advanced',
            processing_time=processing_time,
            requires_human_review=opportunity['requires_review']
        )
        
    except Exception as e:
        logger.error(f"Crawl4AI processing failed: {e}")
        return IngestionResult(
            success=False,
            error=str(e),
            processing_time=(datetime.now() - start_time).total_seconds()
        )

# =============================================================================
# AI-POWERED HELPER FUNCTIONS
# =============================================================================

async def _check_ai_relevance(content: str, title: str) -> Dict[str, Any]:
    """Check relevance using AI with smart provider routing"""
    try:
        # Use the convenience function which automatically routes to optimal provider
        result = await check_relevance(title, content)
        return result
        
    except Exception as e:
        logger.error(f"AI relevance check failed: {e}")
        return {"relevance_score": 0.5, "reasoning": "AI check failed"}

async def _validate_user_submission(submission_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user submission with AI using smart provider routing"""
    try:
        provider = get_smart_llm_provider()
        
        prompt = f"""
        Validate this user-submitted intelligence item:
        
        Data: {json.dumps(submission_data, indent=2)}
        
        Check for:
        1. Completeness of required fields
        2. Legitimacy indicators
        3. Relevance to African AI funding
        4. Potential red flags
        
        Return JSON with confidence_score (0-1) and validation notes.
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        response = await provider.chat_completion(
            task_type=TaskType.VALIDATION,
            messages=messages,
            max_tokens=500,
            temperature=0.1
        )
        
        result = json.loads(response.content)
        return result
        
    except Exception as e:
        logger.error(f"User submission validation failed: {e}")
        return {"confidence_score": 0.5, "notes": "Validation failed"}

async def _validate_extracted_content(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted content with AI using smart provider routing"""
    try:
        # Use the smart LLM provider with automatic DeepSeek/OpenAI routing
        content_json = json.dumps(extracted_data, indent=2)
        result = await validate_content(content_json, "ETL extracted content validation")
        
        return result
        
    except Exception as e:
        logger.error(f"Content validation failed: {e}")
        return {"confidence_score": 0.5, "notes": "Validation failed"}

async def _extract_with_crawl4ai(url: str, context: str, extraction_type: str = 'intelligence_item') -> Dict[str, Any]:
    """Extract content using Crawl4AI with AI processing and rate limiting"""
    try:
        # Check cache first
        cache_key = f"crawl4ai:{hash(url)}:{extraction_type}"
        now = time.time()
        
        if cache_key in _crawl4ai_cache:
            cached_result, timestamp = _crawl4ai_cache[cache_key]
            if now - timestamp < _cache_ttl:
                logger.debug(f"Using cached Crawl4AI result for URL: {url[:50]}...")
                return cached_result
        
        # Check rate limit (reasonable limit for web scraping)
        if not rate_limiter.can_make_request("crawl4ai", max_calls=30, window_seconds=60):
            wait_time = rate_limiter.wait_time("crawl4ai", window_seconds=60)
            logger.warning(f"Crawl4AI rate limit reached. Waiting {wait_time:.1f} seconds")
            await asyncio.sleep(min(wait_time, 10))  # Cap wait time at 10 seconds
        
        # Clean up cache periodically
        if len(_crawl4ai_cache) > 100:  # Arbitrary threshold
            _cleanup_cache()
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Custom extraction strategy for intelligence feed
            extraction_strategy = LLMExtractionStrategy(
                provider="openai/gpt-4o-mini",
                api_token=None,  # Uses environment variable
                instruction=f"""
                Extract intelligence item information from this webpage:
                
                Look for:
                1. Funding opportunity title
                2. Organization/funder name
                3. Funding amount and currency
                4. Application deadline
                5. Eligibility criteria
                6. Geographic focus
                7. Sector focus (AI/tech relevance)
                8. Application process
                9. Contact information
                
                Context: {context}
                
                Return as JSON with confidence score (0-1) for each field.
                """,
                schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "organization": {"type": "string"},
                        "amount": {"type": "string"},
                        "currency": {"type": "string"},
                        "deadline": {"type": "string"},
                        "eligibility": {"type": "string"},
                        "geographic_focus": {"type": "string"},
                        "sector_focus": {"type": "string"},
                        "application_process": {"type": "string"},
                        "contact_info": {"type": "string"},
                        "confidence_score": {"type": "number"}
                    }
                }
            )
            
            result = await crawler.arun(
                url=url,
                extraction_strategy=extraction_strategy,
                bypass_cache=True,
                js_code="""
                // Remove cookie banners and popups
                const selectors = ['.cookie-banner', '.popup', '.modal', '.overlay'];
                selectors.forEach(sel => {
                    const elements = document.querySelectorAll(sel);
                    elements.forEach(el => el.remove());
                });
                """,
                wait_for="body"
            )
            
            if result.success:
                extracted_data = json.loads(result.extracted_content)
                
                result_data = {
                    'success': True,
                    'data': extracted_data,
                    'confidence_score': extracted_data.get('confidence_score', 0.7),
                    'raw_content': result.markdown[:5000]  # Truncate for storage
                }
                
                # Cache the result
                _crawl4ai_cache[cache_key] = (result_data, now)
                return result_data
            else:
                error_result = {
                    'success': False,
                    'error': f"Crawl4AI extraction failed: {result.error_message}"
                }
                # Don't cache errors, but return them
                return error_result
                
    except Exception as e:
        logger.error(f"Crawl4AI extraction failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def _execute_serper_search(query: str, search_type: str = 'search') -> Dict[str, Any]:
    """Execute Serper search with rate limiting and caching"""
    try:
        # Check cache first
        cache_key = f"serper:{hash(query)}:{search_type}"
        now = time.time()
        
        if cache_key in _serper_cache:
            cached_result, timestamp = _serper_cache[cache_key]
            if now - timestamp < _cache_ttl:
                logger.debug(f"Using cached Serper result for query: {query[:50]}...")
                return cached_result
        
        # Check rate limit (Serper allows 100 requests/hour for free tier)
        if not rate_limiter.can_make_request("serper_api", max_calls=90, window_seconds=3600):
            wait_time = rate_limiter.wait_time("serper_api", window_seconds=3600)
            logger.warning(f"Serper API rate limit reached. Waiting {wait_time:.1f} seconds")
            await asyncio.sleep(min(wait_time, 60))  # Cap wait time at 1 minute
        
        import os
        api_key = os.getenv('SERPER_API_KEY')
        
        if not api_key:
            return {'success': False, 'error': 'Missing SERPER_API_KEY'}
        
        url = f"https://google.serper.dev/{search_type}"
        payload = {
            'q': query,
            'gl': 'us',
            'hl': 'en',
            'num': 10
        }
        
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = {'success': True, 'data': response.json()}
            _serper_cache[cache_key] = (result, now)
            return result
        else:
            return {'success': False, 'error': f'Serper API error: {response.status_code}'}
            
    except Exception as e:
        logger.error(f"Serper search failed: {e}")
        return {'success': False, 'error': str(e)}

# =============================================================================
# CELERY TASK WRAPPERS
# =============================================================================

def create_celery_tasks(celery_app: Celery):
    """Create Celery task wrappers for all ingestion methods"""
    
    @celery_app.task(bind=True, max_retries=3)
    def process_rss_feed(self, task_data: Dict[str, Any]):
        """Celery task for RSS feed processing"""
        try:
            task = ETLTask(**task_data)
            result = asyncio.run(process_rss_feed_task(task))
            return result.__dict__
        except Exception as e:
            logger.error(f"RSS task failed: {e}")
            raise self.retry(countdown=60, exc=e)
    
    @celery_app.task(bind=True, max_retries=3)
    def process_serper_search(self, task_data: Dict[str, Any]):
        """Celery task for Serper search processing"""
        try:
            task = ETLTask(**task_data)
            result = asyncio.run(process_serper_search_task(task))
            return result.__dict__
        except Exception as e:
            logger.error(f"Serper task failed: {e}")
            raise self.retry(countdown=60, exc=e)
    
    @celery_app.task(bind=True, max_retries=2)
    def process_user_submission(self, task_data: Dict[str, Any]):
        """Celery task for user submission processing"""
        try:
            task = ETLTask(**task_data)
            result = asyncio.run(process_user_submission_task(task))
            return result.__dict__
        except Exception as e:
            logger.error(f"User submission task failed: {e}")
            raise self.retry(countdown=30, exc=e)
    
    @celery_app.task(bind=True, max_retries=3)
    def process_crawl4ai_extraction(self, task_data: Dict[str, Any]):
        """Celery task for Crawl4AI processing"""
        try:
            task = ETLTask(**task_data)
            result = asyncio.run(process_crawl4ai_task(task))
            return result.__dict__
        except Exception as e:
            logger.error(f"Crawl4AI task failed: {e}")
            raise self.retry(countdown=60, exc=e)
    
    return {
        'process_rss_feed': process_rss_feed,
        'process_serper_search': process_serper_search,
        'process_user_submission': process_user_submission,
        'process_crawl4ai_extraction': process_crawl4ai_extraction
    }