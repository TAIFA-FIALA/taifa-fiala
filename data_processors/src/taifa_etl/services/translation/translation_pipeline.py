"""
TAIFA Independent Translation Pipeline
Multi-entry point translation service with queue-based processing
"""

import json
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import time
from abc import ABC, abstractmethod

# Translation provider imports
import openai
from azure.cognitiveservices.language.translatortext import TranslatorTextClient
from azure.cognitiveservices.language.translatortext.models import TranslatorTextClientConfiguration

# Database imports (adapt to your actual setup)
from app.core.database import get_db

class TranslationPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TranslationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWED = "reviewed"

class ContentType(Enum):
    FUNDING_OPPORTUNITY = "intelligence_item"
    ORGANIZATION_PROFILE = "organization_profile"
    USER_CONTENT = "user_content"
    MANUAL_SUBMISSION = "manual_submission"
    COMMUNITY_CORRECTION = "community_correction"
    NEWSLETTER = "newsletter"

class TranslationSource(Enum):
    ETL_PIPELINE = "etl_pipeline"
    MANUAL_SUBMISSION = "manual_submission"
    COMMUNITY_FEEDBACK = "community_feedback"
    ORGANIZATION_ENRICHMENT = "organization_enrichment"
    USER_REQUEST = "user_request"

@dataclass
class TranslationRequest:
    """Standardized translation request"""
    id: str
    source: TranslationSource
    content_type: ContentType
    content_id: Optional[int]
    source_language: str
    target_language: str
    content: Dict[str, str]  # Field name -> text content
    priority: TranslationPriority
    context: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    scheduled_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.scheduled_at is None:
            self.scheduled_at = self.created_at

@dataclass
class TranslationResult:
    """Translation result with quality metadata"""
    request_id: str
    translated_content: Dict[str, str]
    translation_service: str
    confidence_scores: Dict[str, float]
    processing_time_ms: int
    character_count: int
    cost_estimate: float
    quality_flags: List[str] = None
    human_review_required: bool = False
    
    def __post_init__(self):
        if self.quality_flags is None:
            self.quality_flags = []

class TranslationProvider(ABC):
    """Abstract base class for translation providers"""
    
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str, context: Dict = None) -> Tuple[str, float]:
        """Translate text and return (translated_text, confidence_score)"""
        pass
    
    @abstractmethod
    def get_cost_per_character(self) -> float:
        """Get cost per character for this provider"""
        pass
    
    @abstractmethod
    def get_daily_limit(self) -> int:
        """Get daily character limit for this provider"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name"""
        pass

class AzureTranslationProvider(TranslationProvider):
    """Azure Translator Text API provider"""
    
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
        self.endpoint = f"https://api.cognitive.microsofttranslator.com/"
        self.cost_per_char = 0.00001  # $10 per million characters
        self.daily_limit = 2000000
    
    async def translate(self, text: str, source_lang: str, target_lang: str, context: Dict = None) -> Tuple[str, float]:
        """Translate using Azure Translator"""
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json'
        }
        
        body = [{
            'text': text
        }]
        
        # Add context if available
        if context and context.get('content_type'):
            body[0]['textType'] = 'html' if 'html' in context.get('content_type', '') else 'plain'
        
        url = f"{self.endpoint}translate?api-version=3.0&from={source_lang}&to={target_lang}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=body) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_text = result[0]['translations'][0]['text']
                        
                        # Azure doesn't provide confidence scores directly
                        # We estimate based on text characteristics
                        confidence = self._estimate_confidence(text, translated_text)
                        
                        return translated_text, confidence
                    else:
                        raise Exception(f"Azure translation failed: {response.status}")
        
        except Exception as e:
            logging.error(f"Azure translation error: {e}")
            raise
    
    def _estimate_confidence(self, source: str, target: str) -> float:
        """Estimate translation confidence based on text characteristics"""
        # Simple heuristic - in production, you might use more sophisticated methods
        if len(target) == 0:
            return 0.0
        
        # Check for reasonable length ratio
        length_ratio = len(target) / len(source)
        if 0.5 <= length_ratio <= 2.0:
            return 0.9
        elif 0.3 <= length_ratio <= 3.0:
            return 0.7
        else:
            return 0.5
    
    def get_cost_per_character(self) -> float:
        return self.cost_per_char
    
    def get_daily_limit(self) -> int:
        return self.daily_limit
    
    def get_name(self) -> str:
        return "azure_translator"

class DeepLTranslationProvider(TranslationProvider):
    """DeepL API provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api-free.deepl.com/v2/translate"  # Use api.deepl.com for pro
        self.cost_per_char = 0.000025  # $20 per million characters
        self.daily_limit = 500000
    
    async def translate(self, text: str, source_lang: str, target_lang: str, context: Dict = None) -> Tuple[str, float]:
        """Translate using DeepL"""
        
        headers = {
            'Authorization': f'DeepL-Auth-Key {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'text': text,
            'source_lang': source_lang.upper(),
            'target_lang': target_lang.upper(),
            'preserve_formatting': '1'
        }
        
        # Add formality if translating to French (more formal for institutional content)
        if target_lang.lower() == 'fr' and context and context.get('content_type') == ContentType.FUNDING_OPPORTUNITY:
            data['formality'] = 'more'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_text = result['translations'][0]['text']
                        
                        # DeepL provides confidence via detected_source_language reliability
                        confidence = 0.95  # DeepL generally high quality
                        
                        return translated_text, confidence
                    else:
                        raise Exception(f"DeepL translation failed: {response.status}")
        
        except Exception as e:
            logging.error(f"DeepL translation error: {e}")
            raise
    
    def get_cost_per_character(self) -> float:
        return self.cost_per_char
    
    def get_daily_limit(self) -> int:
        return self.daily_limit
    
    def get_name(self) -> str:
        return "deepl"

class OpenAITranslationProvider(TranslationProvider):
    """OpenAI GPT-4 translation provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
        self.cost_per_char = 0.000150  # Estimated based on GPT-4 pricing
        self.daily_limit = 100000  # Conservative estimate
    
    async def translate(self, text: str, source_lang: str, target_lang: str, context: Dict = None) -> Tuple[str, float]:
        """Translate using OpenAI GPT-4"""
        
        # Create context-aware prompt
        content_type = context.get('content_type', 'general') if context else 'general'
        
        system_prompt = self._build_system_prompt(source_lang, target_lang, content_type)
        user_prompt = self._build_user_prompt(text, context)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=len(text) * 2  # Rough estimate for translation length
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # GPT-4 generally produces high-quality translations
            confidence = 0.92
            
            return translated_text, confidence
        
        except Exception as e:
            logging.error(f"OpenAI translation error: {e}")
            raise
    
    def _build_system_prompt(self, source_lang: str, target_lang: str, content_type: str) -> str:
        """Build context-aware system prompt"""
        
        lang_map = {
            'en': 'English',
            'fr': 'French',
            'ar': 'Arabic',
            'pt': 'Portuguese'
        }
        
        source_lang_name = lang_map.get(source_lang, source_lang)
        target_lang_name = lang_map.get(target_lang, target_lang)
        
        base_prompt = f"""You are a professional translator specializing in African development and AI/technology content. 
        Translate the following text from {source_lang_name} to {target_lang_name}."""
        
        if content_type == ContentType.FUNDING_OPPORTUNITY.value:
            base_prompt += """
            
            This is intelligence item content. Please:
            - Maintain all technical terms and proper nouns accurately
            - Keep funding amounts, dates, and contact information exactly as provided
            - Use formal, professional language appropriate for institutional communication
            - Preserve the structure and formatting of the original text
            - Ensure African context and terminology is handled appropriately"""
        
        elif content_type == ContentType.ORGANIZATION_PROFILE.value:
            base_prompt += """
            
            This is organizational profile content. Please:
            - Maintain organization names and official titles exactly
            - Use formal language appropriate for institutional descriptions
            - Preserve all contact information and website URLs
            - Keep technical and sector-specific terminology accurate"""
        
        base_prompt += "\n\nProvide only the translation, no additional comments or explanations."
        
        return base_prompt
    
    def _build_user_prompt(self, text: str, context: Dict = None) -> str:
        """Build user prompt with context"""
        prompt = f"Please translate the following text:\n\n{text}"
        
        if context and context.get('terminology'):
            prompt += f"\n\nImportant terminology to preserve: {context['terminology']}"
        
        return prompt
    
    def get_cost_per_character(self) -> float:
        return self.cost_per_char
    
    def get_daily_limit(self) -> int:
        return self.daily_limit
    
    def get_name(self) -> str:
        return "openai_gpt4"

class GoogleTranslationProvider(TranslationProvider):
    """Google Cloud Translation API provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://translation.googleapis.com/language/translate/v2"
        self.cost_per_char = 0.000020  # $20 per million characters
        self.daily_limit = 500000
    
    async def translate(self, text: str, source_lang: str, target_lang: str, context: Dict = None) -> Tuple[str, float]:
        """Translate using Google Cloud Translation"""
        
        params = {
            'key': self.api_key,
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_text = result['data']['translations'][0]['translatedText']
                        
                        # Google provides confidence in some cases
                        confidence = 0.88  # Good quality baseline
                        
                        return translated_text, confidence
                    else:
                        raise Exception(f"Google translation failed: {response.status}")
        
        except Exception as e:
            logging.error(f"Google translation error: {e}")
            raise
    
    def get_cost_per_character(self) -> float:
        return self.cost_per_char
    
    def get_daily_limit(self) -> int:
        return self.daily_limit
    
    def get_name(self) -> str:
        return "google_translate"

class ProviderSelector:
    """Smart provider selection based on content type, quality, and cost"""
    
    def __init__(self, providers: Dict[str, TranslationProvider]):
        self.providers = providers
        self.usage_stats = {}  # Track daily usage per provider
        self.quality_scores = {
            "intelligence_item": {
                "deepl": 0.95,
                "openai_gpt4": 0.97,
                "azure_translator": 0.92,
                "google_translate": 0.89
            },
            "organization_profile": {
                "openai_gpt4": 0.96,
                "deepl": 0.93,
                "azure_translator": 0.91,
                "google_translate": 0.88
            },
            "user_content": {
                "google_translate": 0.90,
                "azure_translator": 0.91,
                "deepl": 0.94,
                "openai_gpt4": 0.95
            }
        }
    
    def select_provider(self, content_type: ContentType, priority: TranslationPriority, 
                       character_count: int) -> str:
        """Select best provider based on content type, priority, and availability"""
        
        content_type_str = content_type.value
        
        # Get quality rankings for this content type
        quality_rankings = self.quality_scores.get(content_type_str, self.quality_scores["user_content"])
        
        # Sort providers by quality score
        ranked_providers = sorted(quality_rankings.items(), key=lambda x: x[1], reverse=True)
        
        # Filter by availability and cost considerations
        for provider_name, quality_score in ranked_providers:
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            
            # Check daily limit
            current_usage = self.usage_stats.get(provider_name, 0)
            if current_usage + character_count > provider.get_daily_limit():
                continue
            
            # For high priority content, prefer highest quality regardless of cost
            if priority in [TranslationPriority.HIGH, TranslationPriority.URGENT]:
                return provider_name
            
            # For medium priority, balance quality and cost
            if priority == TranslationPriority.MEDIUM:
                if quality_score >= 0.90:
                    return provider_name
            
            # For low priority, prefer cost-effective options
            if priority == TranslationPriority.LOW:
                if provider.get_cost_per_character() <= 0.000025:  # Cheap options
                    return provider_name
        
        # Fallback to first available provider
        for provider_name, provider in self.providers.items():
            current_usage = self.usage_stats.get(provider_name, 0)
            if current_usage + character_count <= provider.get_daily_limit():
                return provider_name
        
        raise Exception("No translation providers available within daily limits")
    
    def update_usage(self, provider_name: str, character_count: int):
        """Update usage statistics for provider"""
        self.usage_stats[provider_name] = self.usage_stats.get(provider_name, 0) + character_count

class TranslationQueue:
    """Queue manager for translation requests"""
    
    def __init__(self):
        self.queue: List[TranslationRequest] = []
        self.processing: Dict[str, TranslationRequest] = {}
        self.completed: Dict[str, TranslationResult] = {}
        self.failed: Dict[str, Tuple[TranslationRequest, Exception]] = {}
    
    def add_request(self, request: TranslationRequest) -> str:
        """Add translation request to queue"""
        
        # Generate unique request ID
        request.id = self._generate_request_id(request)
        
        # Insert based on priority and scheduled time
        self._insert_by_priority(request)
        
        return request.id
    
    def get_next_batch(self, batch_size: int = 10) -> List[TranslationRequest]:
        """Get next batch of requests to process"""
        
        now = datetime.utcnow()
        available_requests = []
        
        # Get requests that are ready to process
        for request in self.queue[:]:
            if request.scheduled_at <= now and len(available_requests) < batch_size:
                available_requests.append(request)
                self.queue.remove(request)
                self.processing[request.id] = request
        
        return available_requests
    
    def mark_completed(self, request_id: str, result: TranslationResult):
        """Mark request as completed"""
        if request_id in self.processing:
            del self.processing[request_id]
            self.completed[request_id] = result
    
    def mark_failed(self, request_id: str, error: Exception):
        """Mark request as failed"""
        if request_id in self.processing:
            request = self.processing[request_id]
            del self.processing[request_id]
            self.failed[request_id] = (request, error)
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue status"""
        return {
            "pending": len(self.queue),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed)
        }
    
    def _generate_request_id(self, request: TranslationRequest) -> str:
        """Generate unique request ID"""
        content_hash = hashlib.md5(json.dumps(request.content, sort_keys=True).encode()).hexdigest()[:8]
        timestamp = int(time.time())
        return f"{request.source.value}_{content_hash}_{timestamp}"
    
    def _insert_by_priority(self, request: TranslationRequest):
        """Insert request in queue based on priority and scheduled time"""
        
        # Find insertion point
        insert_index = 0
        for i, existing_request in enumerate(self.queue):
            # Higher priority goes first
            if request.priority.value > existing_request.priority.value:
                insert_index = i
                break
            # Same priority, earlier scheduled time goes first
            elif (request.priority.value == existing_request.priority.value and 
                  request.scheduled_at < existing_request.scheduled_at):
                insert_index = i
                break
            insert_index = i + 1
        
        self.queue.insert(insert_index, request)

class TranslationPipelineService:
    """Main translation pipeline service"""
    
    def __init__(self, provider_configs: Dict[str, Dict[str, str]]):
        # Initialize providers
        self.providers = {}
        for provider_name, config in provider_configs.items():
            if provider_name == "azure_translator":
                self.providers[provider_name] = AzureTranslationProvider(config["api_key"], config["region"])
            elif provider_name == "deepl":
                self.providers[provider_name] = DeepLTranslationProvider(config["api_key"])
            elif provider_name == "openai_gpt4":
                self.providers[provider_name] = OpenAITranslationProvider(config["api_key"])
            elif provider_name == "google_translate":
                self.providers[provider_name] = GoogleTranslationProvider(config["api_key"])
        
        # Initialize components
        self.provider_selector = ProviderSelector(self.providers)
        self.queue = TranslationQueue()
        self.is_processing = False
    
    # Entry Point 1: ETL Pipeline
    async def translate_intelligence_item(self, opportunity_id: int, priority: TranslationPriority = TranslationPriority.MEDIUM) -> str:
        """Entry point for intelligence item translation"""
        
        # Get opportunity content from database
        content = await self._get_intelligence_item_content(opportunity_id)
        
        request = TranslationRequest(
            id="",  # Will be generated
            source=TranslationSource.ETL_PIPELINE,
            content_type=ContentType.FUNDING_OPPORTUNITY,
            content_id=opportunity_id,
            source_language="en",  # Assume English source
            target_language="fr",  # Translate to French
            content=content,
            priority=priority,
            context={"content_type": ContentType.FUNDING_OPPORTUNITY.value}
        )
        
        return self.queue.add_request(request)
    
    # Entry Point 2: Manual Submissions
    async def translate_manual_submission(self, content: Dict[str, str], 
                                        source_lang: str = "en", target_lang: str = "fr",
                                        priority: TranslationPriority = TranslationPriority.HIGH) -> str:
        """Entry point for manual content translation"""
        
        request = TranslationRequest(
            id="",
            source=TranslationSource.MANUAL_SUBMISSION,
            content_type=ContentType.MANUAL_SUBMISSION,
            content_id=None,
            source_language=source_lang,
            target_language=target_lang,
            content=content,
            priority=priority,
            context={"content_type": ContentType.MANUAL_SUBMISSION.value}
        )
        
        return self.queue.add_request(request)
    
    # Entry Point 3: Community Corrections
    async def retranslate_community_feedback(self, translation_id: str, 
                                           corrected_content: Dict[str, str],
                                           priority: TranslationPriority = TranslationPriority.HIGH) -> str:
        """Entry point for community translation corrections"""
        
        request = TranslationRequest(
            id="",
            source=TranslationSource.COMMUNITY_FEEDBACK,
            content_type=ContentType.COMMUNITY_CORRECTION,
            content_id=None,
            source_language="fr",  # Assume correction is in French
            target_language="en",  # Back-translate to English for validation
            content=corrected_content,
            priority=priority,
            context={
                "content_type": ContentType.COMMUNITY_CORRECTION.value,
                "original_translation_id": translation_id
            }
        )
        
        return self.queue.add_request(request)
    
    # Entry Point 4: Organization Enrichment
    async def translate_organization_profile(self, organization_id: int,
                                           priority: TranslationPriority = TranslationPriority.MEDIUM) -> str:
        """Entry point for organization profile translation"""
        
        content = await self._get_organization_content(organization_id)
        
        request = TranslationRequest(
            id="",
            source=TranslationSource.ORGANIZATION_ENRICHMENT,
            content_type=ContentType.ORGANIZATION_PROFILE,
            content_id=organization_id,
            source_language="en",
            target_language="fr",
            content=content,
            priority=priority,
            context={"content_type": ContentType.ORGANIZATION_PROFILE.value}
        )
        
        return self.queue.add_request(request)
    
    async def start_processing(self):
        """Start the translation queue processor"""
        self.is_processing = True
        
        while self.is_processing:
            try:
                # Get next batch of requests
                batch = self.queue.get_next_batch(batch_size=5)
                
                if not batch:
                    await asyncio.sleep(30)  # Wait 30 seconds if no requests
                    continue
                
                # Process batch concurrently
                tasks = [self._process_translation_request(request) for request in batch]
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception as e:
                logging.error(f"Translation processing error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def stop_processing(self):
        """Stop the translation queue processor"""
        self.is_processing = False
    
    async def _process_translation_request(self, request: TranslationRequest):
        """Process a single translation request"""
        
        start_time = time.time()
        
        try:
            # Calculate total character count
            total_chars = sum(len(text) for text in request.content.values())
            
            # Select provider
            provider_name = self.provider_selector.select_provider(
                request.content_type, request.priority, total_chars
            )
            provider = self.providers[provider_name]
            
            # Translate each field
            translated_content = {}
            confidence_scores = {}
            total_cost = 0
            
            for field_name, text in request.content.items():
                if text:  # Only translate non-empty content
                    translated_text, confidence = await provider.translate(
                        text, request.source_language, request.target_language, request.context
                    )
                    
                    translated_content[field_name] = translated_text
                    confidence_scores[field_name] = confidence
                    
                    # Calculate cost
                    field_cost = len(text) * provider.get_cost_per_character()
                    total_cost += field_cost
                else:
                    translated_content[field_name] = text
                    confidence_scores[field_name] = 1.0
            
            # Create result
            processing_time = int((time.time() - start_time) * 1000)
            
            result = TranslationResult(
                request_id=request.id,
                translated_content=translated_content,
                translation_service=provider_name,
                confidence_scores=confidence_scores,
                processing_time_ms=processing_time,
                character_count=total_chars,
                cost_estimate=total_cost,
                human_review_required=min(confidence_scores.values()) < 0.85
            )
            
            # Store result
            await self._store_translation_result(request, result)
            
            # Update provider usage
            self.provider_selector.update_usage(provider_name, total_chars)
            
            # Mark completed
            self.queue.mark_completed(request.id, result)
            
            logging.info(f"Translation completed: {request.id} using {provider_name}")
            
        except Exception as e:
            logging.error(f"Translation failed for {request.id}: {e}")
            self.queue.mark_failed(request.id, e)
    
    async def _get_intelligence_item_content(self, opportunity_id: int) -> Dict[str, str]:
        """Get intelligence item content for translation"""
        try:
            # This would query your database
            # For now, return mock data
            return {
                "title": "Sample Intelligence Item",
                "description": "This is a sample intelligence item for AI research in Africa.",
                "summary": "Brief summary of the opportunity."
            }
        except Exception as e:
            logging.error(f"Failed to get intelligence item content: {e}")
            return {}
    
    async def _get_organization_content(self, organization_id: int) -> Dict[str, str]:
        """Get organization content for translation"""
        try:
            # This would query your database
            return {
                "description": "Sample organization description",
                "mission": "Organization mission statement"
            }
        except Exception as e:
            logging.error(f"Failed to get organization content: {e}")
            return {}
    
    async def _store_translation_result(self, request: TranslationRequest, result: TranslationResult):
        """Store translation result in database"""
        try:
            # This would write to your translations table
            # Include all the metadata for tracking and learning
            translation_data = {
                "source_table": self._get_source_table(request.content_type),
                "source_id": request.content_id,
                "target_language": request.target_language,
                "translated_content": result.translated_content,
                "translation_service": result.translation_service,
                "confidence_scores": result.confidence_scores,
                "processing_metadata": {
                    "processing_time_ms": result.processing_time_ms,
                    "character_count": result.character_count,
                    "cost_estimate": result.cost_estimate,
                    "priority": request.priority.value,
                    "source": request.source.value
                }
            }
            
            logging.info(f"Stored translation result for {request.id}")
            
        except Exception as e:
            logging.error(f"Failed to store translation result: {e}")
    
    def _get_source_table(self, content_type: ContentType) -> str:
        """Map content type to database table"""
        mapping = {
            ContentType.FUNDING_OPPORTUNITY: "africa_intelligence_feed",
            ContentType.ORGANIZATION_PROFILE: "organizations",
            ContentType.USER_CONTENT: "user_content",
            ContentType.MANUAL_SUBMISSION: "manual_submissions",
            ContentType.COMMUNITY_CORRECTION: "community_corrections"
        }
        return mapping.get(content_type, "translations")
    
    def get_status(self) -> Dict[str, Any]:
        """Get translation service status"""
        return {
            "queue_status": self.queue.get_queue_status(),
            "provider_usage": self.provider_selector.usage_stats,
            "is_processing": self.is_processing,
            "available_providers": list(self.providers.keys())
        }

# Usage Functions and Integration Points

async def create_translation_service() -> TranslationPipelineService:
    """Create and configure translation service"""
    
    # Load provider configurations from environment
    provider_configs = {
        "azure_translator": {
            "api_key": "your_azure_key",
            "region": "your_region"
        },
        "deepl": {
            "api_key": "your_deepl_key"
        },
        "openai_gpt4": {
            "api_key": "your_openai_key"
        },
        "google_translate": {
            "api_key": "your_google_key"
        }
    }
    
    service = TranslationPipelineService(provider_configs)
    return service

async def webhook_translate_intelligence_item(opportunity_id: int) -> Dict[str, str]:
    """Webhook endpoint for intelligence item translation"""
    
    service = await create_translation_service()
    request_id = await service.translate_intelligence_item(opportunity_id)
    
    return {
        "request_id": request_id,
        "status": "queued",
        "estimated_completion": "within 5 minutes"
    }

async def api_translate_content(content: Dict[str, str], source_lang: str = "en", 
                              target_lang: str = "fr") -> Dict[str, str]:
    """API endpoint for immediate content translation"""
    
    service = await create_translation_service()
    request_id = await service.translate_manual_submission(content, source_lang, target_lang)
    
    return {
        "request_id": request_id,
        "status": "queued",
        "message": "Translation request submitted"
    }

# Example usage
if __name__ == "__main__":
    async def main():
        # Create translation service
        service = await create_translation_service()
        
        # Start processing in background
        asyncio.create_task(service.start_processing())
        
        # Test translation
        content = {
            "title": "AI Research Grant for African Universities",
            "description": "This grant supports artificial intelligence research projects at universities across Africa."
        }
        
        request_id = await service.translate_manual_submission(content)
        print(f"Translation request submitted: {request_id}")
        
        # Wait a bit and check status
        await asyncio.sleep(10)
        status = service.get_status()
        print("Service status:", json.dumps(status, indent=2))
    
    asyncio.run(main())
