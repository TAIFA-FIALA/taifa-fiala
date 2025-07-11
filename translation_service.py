"""
TAIFA-FIALA Translation Service
Core translation engine supporting multiple providers with intelligent routing
"""

import asyncio
import aiohttp
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TranslationProvider(Enum):
    AZURE = "azure_translator"
    GOOGLE = "google_translate"
    DEEPL = "deepl"
    OPENAI = "openai_gpt4"

class ContentType(Enum):
    TITLE = "title"
    DESCRIPTION = "description"
    TECHNICAL = "technical"
    LEGAL = "legal"
    MARKETING = "marketing"

class TranslationService:
    """Intelligent translation service with multiple provider support"""
    
    def __init__(self):
        self.providers = {}
        self.db_connector = None
        self.session = None
        self.provider_configs = {
            TranslationProvider.AZURE: {
                "endpoint": "https://api.cognitive.microsofttranslator.com",
                "api_key": os.getenv("AZURE_TRANSLATOR_KEY"),
                "region": os.getenv("AZURE_TRANSLATOR_REGION", "eastus"),
                "quality_score": 0.92,
                "cost_per_char": 0.00001,
                "best_for": [ContentType.DESCRIPTION, ContentType.LEGAL]
            },
            TranslationProvider.GOOGLE: {
                "endpoint": "https://translation.googleapis.com/language/translate/v2",
                "api_key": os.getenv("GOOGLE_TRANSLATE_API_KEY"),
                "quality_score": 0.89,
                "cost_per_char": 0.000020,
                "best_for": [ContentType.MARKETING]
            },
            TranslationProvider.DEEPL: {
                "endpoint": "https://api-free.deepl.com/v2/translate",
                "api_key": os.getenv("DEEPL_API_KEY"),
                "quality_score": 0.95,
                "cost_per_char": 0.000025,
                "best_for": [ContentType.TITLE, ContentType.TECHNICAL]
            },
            TranslationProvider.OPENAI: {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "quality_score": 0.97,
                "cost_per_char": 0.000150,
                "best_for": [ContentType.TECHNICAL, ContentType.LEGAL]
            }
        }
    
    async def initialize(self):
        """Initialize translation service and database connection"""
        try:
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'TAIFA-FIALA-Translation/1.0'}
            )
            
            # Initialize database connector
            from database.connector import DatabaseConnector
            self.db_connector = DatabaseConnector()
            await self.db_connector.initialize()
            
            # Initialize available providers
            await self._initialize_providers()
            
            logger.info(f"✅ Translation service initialized with {len(self.providers)} providers")
            return True
            
        except Exception as e:
            logger.error(f"❌ Translation service initialization failed: {e}")
            return False
    
    async def _initialize_providers(self):
        """Initialize available translation providers"""
        for provider, config in self.provider_configs.items():
            if config["api_key"]:
                self.providers[provider] = config
                logger.info(f"✅ {provider.value} provider initialized")
            else:
                logger.warning(f"⚠️  {provider.value} API key not found - provider disabled")
    
    async def close(self):
        """Close translation service"""
        if self.session:
            await self.session.close()
        if self.db_connector:
            await self.db_connector.close()
    
    def select_provider(self, content_type: ContentType, target_language: str, text_length: int) -> TranslationProvider:
        """Intelligently select the best translation provider"""
        
        # Filter available providers
        available_providers = list(self.providers.keys())
        if not available_providers:
            raise ValueError("No translation providers available")
        
        # Score providers based on suitability
        provider_scores = {}
        
        for provider in available_providers:
            config = self.provider_configs[provider]
            score = 0
            
            # Base quality score
            score += config["quality_score"] * 50
            
            # Content type preference
            if content_type in config["best_for"]:
                score += 30
            
            # Cost efficiency (inverse - lower cost = higher score)
            cost_factor = 1 / (config["cost_per_char"] * 1000 + 1)
            score += cost_factor * 20
            
            # Language-specific preferences
            if target_language == "fr":
                if provider == TranslationProvider.DEEPL:
                    score += 15  # DeepL is excellent for French
                elif provider == TranslationProvider.AZURE:
                    score += 10  # Azure is good for French
            
            # Text length considerations
            if text_length > 1000:  # Long text
                if provider in [TranslationProvider.AZURE, TranslationProvider.GOOGLE]:
                    score += 10  # Better for batch processing
            else:  # Short text
                if provider == TranslationProvider.DEEPL:
                    score += 5  # Excellent for short, precise translations
            
            provider_scores[provider] = score
        
        # Select provider with highest score
        best_provider = max(provider_scores, key=provider_scores.get)
        logger.debug(f"Selected {best_provider.value} for {content_type.value} (score: {provider_scores[best_provider]:.1f})")
        
        return best_provider
    
    async def translate_text(self, 
                           text: str, 
                           target_language: str, 
                           source_language: str = "auto",
                           content_type: ContentType = ContentType.DESCRIPTION,
                           provider: Optional[TranslationProvider] = None) -> Dict[str, Any]:
        """Translate text using the optimal provider"""
        
        if not text or not text.strip():
            return {"translated_text": "", "provider": None, "confidence": 0.0}
        
        # Auto-select provider if not specified
        if provider is None:
            provider = self.select_provider(content_type, target_language, len(text))
        
        try:
            # Perform translation based on provider
            if provider == TranslationProvider.AZURE:
                result = await self._translate_azure(text, target_language, source_language)
            elif provider == TranslationProvider.GOOGLE:
                result = await self._translate_google(text, target_language, source_language)
            elif provider == TranslationProvider.DEEPL:
                result = await self._translate_deepl(text, target_language, source_language)
            elif provider == TranslationProvider.OPENAI:
                result = await self._translate_openai(text, target_language, source_language, content_type)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Update provider usage statistics
            await self._update_provider_usage(provider, len(text))
            
            return {
                "translated_text": result["translated_text"],
                "provider": provider.value,
                "confidence": result.get("confidence", 0.8),
                "detected_language": result.get("detected_language", source_language)
            }
            
        except Exception as e:
            logger.error(f"Translation failed with {provider.value}: {e}")
            
            # Try fallback provider
            fallback_result = await self._try_fallback_translation(
                text, target_language, source_language, content_type, provider
            )
            
            return fallback_result
    
    async def _translate_azure(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using Azure Translator"""
        config = self.provider_configs[TranslationProvider.AZURE]
        
        headers = {
            'Ocp-Apim-Subscription-Key': config["api_key"],
            'Ocp-Apim-Subscription-Region': config["region"],
            'Content-Type': 'application/json'
        }
        
        body = [{
            'text': text
        }]
        
        params = {
            'api-version': '3.0',
            'to': target_lang
        }
        
        if source_lang != "auto":
            params['from'] = source_lang
        
        url = f"{config['endpoint']}/translate"
        
        async with self.session.post(url, headers=headers, json=body, params=params) as response:
            if response.status == 200:
                result = await response.json()
                translated = result[0]['translations'][0]['text']
                detected_lang = result[0].get('detectedLanguage', {}).get('language', source_lang)
                
                return {
                    "translated_text": translated,
                    "confidence": 0.92,
                    "detected_language": detected_lang
                }
            else:
                raise Exception(f"Azure translation failed: {response.status}")
    
    async def _translate_deepl(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using DeepL"""
        config = self.provider_configs[TranslationProvider.DEEPL]
        
        # DeepL language codes are slightly different
        lang_mapping = {
            'en': 'EN',
            'fr': 'FR',
            'es': 'ES',
            'de': 'DE'
        }
        
        target_lang_code = lang_mapping.get(target_lang, target_lang.upper())
        
        headers = {
            'Authorization': f'DeepL-Auth-Key {config["api_key"]}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'text': text,
            'target_lang': target_lang_code
        }
        
        if source_lang != "auto" and source_lang in lang_mapping:
            data['source_lang'] = lang_mapping[source_lang]
        
        async with self.session.post(config["endpoint"], headers=headers, data=data) as response:
            if response.status == 200:
                result = await response.json()
                translated = result['translations'][0]['text']
                detected_lang = result['translations'][0].get('detected_source_language', source_lang).lower()
                
                return {
                    "translated_text": translated,
                    "confidence": 0.95,
                    "detected_language": detected_lang
                }
            else:
                raise Exception(f"DeepL translation failed: {response.status}")
    
    async def _translate_openai(self, text: str, target_lang: str, source_lang: str, content_type: ContentType) -> Dict[str, Any]:
        """Translate using OpenAI GPT-4 with context awareness"""
        config = self.provider_configs[TranslationProvider.OPENAI]
        
        # Create context-aware prompt
        context_prompts = {
            ContentType.TITLE: "This is a funding opportunity title. Translate precisely while maintaining professional tone.",
            ContentType.DESCRIPTION: "This is a funding opportunity description. Translate accurately while preserving technical terms and maintaining clarity.",
            ContentType.TECHNICAL: "This is technical content about AI/technology funding. Preserve technical terminology and acronyms.",
            ContentType.LEGAL: "This is legal/formal text. Maintain formal register and precise legal terminology.",
            ContentType.MARKETING: "This is marketing content. Maintain persuasive tone and cultural appropriateness."
        }
        
        target_lang_names = {
            'fr': 'French',
            'en': 'English',
            'es': 'Spanish',
            'ar': 'Arabic',
            'pt': 'Portuguese'
        }
        
        target_lang_name = target_lang_names.get(target_lang, target_lang)
        context = context_prompts.get(content_type, context_prompts[ContentType.DESCRIPTION])
        
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        messages = [
            {
                "role": "system", 
                "content": f"You are a professional translator specializing in funding and development content for African contexts. {context} Respond only with the translation, no explanations."
            },
            {
                "role": "user",
                "content": f"Translate the following text to {target_lang_name}:\n\n{text}"
            }
        ]
        
        data = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": len(text) * 2  # Generous token allowance
        }
        
        async with self.session.post(config["endpoint"], headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                translated = result['choices'][0]['message']['content'].strip()
                
                return {
                    "translated_text": translated,
                    "confidence": 0.97,
                    "detected_language": source_lang
                }
            else:
                raise Exception(f"OpenAI translation failed: {response.status}")
    
    async def _try_fallback_translation(self, text: str, target_lang: str, source_lang: str, 
                                      content_type: ContentType, failed_provider: TranslationProvider) -> Dict[str, Any]:
        """Try alternative provider if primary fails"""
        available_providers = [p for p in self.providers.keys() if p != failed_provider]
        
        if not available_providers:
            return {"translated_text": text, "provider": "fallback_original", "confidence": 0.0}
        
        # Select best available alternative
        fallback_provider = self.select_provider(content_type, target_lang, len(text))
        if fallback_provider == failed_provider and len(available_providers) > 1:
            fallback_provider = available_providers[0]
        
        try:
            logger.info(f"Trying fallback provider: {fallback_provider.value}")
            return await self.translate_text(text, target_lang, source_lang, content_type, fallback_provider)
        except Exception as e:
            logger.error(f"Fallback translation also failed: {e}")
            return {"translated_text": text, "provider": "fallback_original", "confidence": 0.0}
    
    async def _update_provider_usage(self, provider: TranslationProvider, character_count: int):
        """Update provider usage statistics"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE translation_services 
                    SET daily_usage = daily_usage + $1
                    WHERE service_name = $2
                """, character_count, provider.value)
        except Exception as e:
            logger.error(f"Failed to update provider usage: {e}")

# Example usage and testing
async def test_translation_service():
    """Test the translation service with sample content"""
    service = TranslationService()
    await service.initialize()
    
    try:
        # Test different content types
        test_cases = [
            {
                "text": "AI Funding Opportunity for African Startups",
                "content_type": ContentType.TITLE,
                "description": "Title translation"
            },
            {
                "text": "This funding opportunity supports artificial intelligence research and implementation projects across Africa, with a focus on healthcare, agriculture, and education applications.",
                "content_type": ContentType.DESCRIPTION,
                "description": "Description translation"
            },
            {
                "text": "Machine learning algorithms and neural networks",
                "content_type": ContentType.TECHNICAL,
                "description": "Technical terms"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {test_case['description']}:")
            print(f"Original: {test_case['text']}")
            
            result = await service.translate_text(
                test_case["text"], 
                "fr", 
                "en", 
                test_case["content_type"]
            )
            
            print(f"French: {result['translated_text']}")
            print(f"Provider: {result['provider']} (Confidence: {result['confidence']:.2f})")
            
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(test_translation_service())