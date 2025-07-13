"""
Source Classifier Module

Classifies submitted sources by type and determines appropriate monitoring
strategies, technical requirements, and expected performance characteristics.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

import feedparser
from bs4 import BeautifulSoup


class SourceType(Enum):
    """Enumeration of source types"""
    RSS_FEED = "rss_feed"
    NEWSLETTER = "newsletter"
    DYNAMIC_WEBPAGE = "dynamic_webpage"
    STATIC_WEBPAGE = "static_webpage"
    API = "api"
    PDF_PUBLICATION = "pdf_publication"
    SOCIAL_MEDIA = "social_media"
    UNKNOWN = "unknown"


@dataclass
class SourceClassification:
    """Result of source classification"""
    source_type: SourceType
    confidence: float
    monitoring_strategy: str
    setup_difficulty: str  # easy, medium, hard
    expected_reliability: str  # high, medium, low
    update_frequency_estimate: str
    technical_requirements: List[str]
    monitoring_config: Dict[str, Any]
    dedup_strategy: str
    notes: str


@dataclass
class MonitoringConfig:
    """Configuration for monitoring a specific source"""
    source_type: SourceType
    check_frequency: str  # cron expression or interval
    timeout_seconds: int
    retry_attempts: int
    parsing_strategy: str
    selector_config: Dict[str, str]  # CSS selectors for web scraping
    headers: Dict[str, str]
    rate_limit: str
    notification_settings: Dict[str, Any]


class SourceClassifier:
    """Classifies sources and determines monitoring strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'TAIFA-SourceClassifier/1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def classify_source(self, url: str, additional_info: Dict[str, Any] = None) -> SourceClassification:
        """
        Classify a source and determine optimal monitoring strategy
        
        Args:
            url: URL of the source to classify
            additional_info: Additional information from submission form
            
        Returns:
            SourceClassification with type and monitoring recommendations
        """
        self.logger.info(f"Classifying source: {url}")
        
        # Initial classification based on URL patterns
        initial_type = self._classify_by_url_pattern(url)
        
        # Enhance classification with content analysis
        enhanced_classification = await self._enhance_with_content_analysis(url, initial_type)
        
        # Generate monitoring configuration
        monitoring_config = self._generate_monitoring_config(enhanced_classification, additional_info)
        
        # Create final classification
        classification = SourceClassification(
            source_type=enhanced_classification["type"],
            confidence=enhanced_classification["confidence"],
            monitoring_strategy=enhanced_classification["strategy"],
            setup_difficulty=enhanced_classification["difficulty"],
            expected_reliability=enhanced_classification["reliability"],
            update_frequency_estimate=enhanced_classification["frequency"],
            technical_requirements=enhanced_classification["requirements"],
            monitoring_config=monitoring_config,
            dedup_strategy=enhanced_classification["dedup_strategy"],
            notes=enhanced_classification["notes"]
        )
        
        self.logger.info(f"Classification complete: {classification.source_type.value} (confidence: {classification.confidence:.2f})")
        return classification
    
    def _classify_by_url_pattern(self, url: str) -> Dict[str, Any]:
        """Initial classification based on URL patterns"""
        url_lower = url.lower()
        parsed = urlparse(url)
        
        # RSS/Atom feed patterns
        rss_patterns = ['rss', 'feed', 'atom', '.xml']
        if any(pattern in url_lower for pattern in rss_patterns):
            return {
                "type": SourceType.RSS_FEED,
                "confidence": 0.9,
                "reason": "URL contains RSS/feed patterns"
            }
        
        # API patterns
        api_patterns = ['/api/', 'api.', 'rest.', '/v1/', '/v2/', 'json']
        if any(pattern in url_lower for pattern in api_patterns):
            return {
                "type": SourceType.API,
                "confidence": 0.8,
                "reason": "URL contains API patterns"
            }
        
        # PDF patterns
        if url_lower.endswith('.pdf'):
            return {
                "type": SourceType.PDF_PUBLICATION,
                "confidence": 1.0,
                "reason": "Direct PDF link"
            }
        
        # Social media patterns
        social_domains = ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com']
        if any(domain in parsed.netloc for domain in social_domains):
            return {
                "type": SourceType.SOCIAL_MEDIA,
                "confidence": 0.95,
                "reason": "Social media domain"
            }
        
        # Newsletter/subscription patterns
        newsletter_patterns = ['newsletter', 'subscribe', 'mailinglist', 'updates']
        if any(pattern in url_lower for pattern in newsletter_patterns):
            return {
                "type": SourceType.NEWSLETTER,
                "confidence": 0.7,
                "reason": "URL contains newsletter patterns"
            }
        
        # Default to webpage
        return {
            "type": SourceType.DYNAMIC_WEBPAGE,
            "confidence": 0.5,
            "reason": "Default webpage classification"
        }
    
    async def _enhance_with_content_analysis(self, url: str, initial_classification: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance classification with actual content analysis"""
        try:
            # If initial classification is high confidence, use it
            if initial_classification["confidence"] >= 0.9:
                return await self._get_source_characteristics(initial_classification["type"], url)
            
            # Fetch and analyze content
            async with self.session.get(url) as response:
                content_type = response.headers.get('content-type', '').lower()
                content = await response.text()
                
                # Check if it's actually an RSS feed
                if self._is_rss_content(content, content_type):
                    return await self._get_source_characteristics(SourceType.RSS_FEED, url)
                
                # Check if it's a dynamic webpage (JavaScript heavy)
                soup = BeautifulSoup(content, 'html.parser')
                if self._is_dynamic_webpage(soup):
                    return await self._get_source_characteristics(SourceType.DYNAMIC_WEBPAGE, url)
                
                # Check if it appears to be a static webpage
                if self._is_static_webpage(soup):
                    return await self._get_source_characteristics(SourceType.STATIC_WEBPAGE, url)
                
                # Default to original classification
                return await self._get_source_characteristics(initial_classification["type"], url)
                
        except Exception as e:
            self.logger.warning(f"Content analysis failed for {url}: {e}")
            return await self._get_source_characteristics(initial_classification["type"], url)
    
    def _is_rss_content(self, content: str, content_type: str) -> bool:
        """Check if content is RSS/Atom feed"""
        if 'xml' in content_type:
            return True
        
        # Check for RSS/Atom XML elements
        content_lower = content.lower()
        rss_indicators = ['<rss', '<feed', '<atom', '<channel>', '<item>', '<entry>']
        return any(indicator in content_lower for indicator in rss_indicators)
    
    def _is_dynamic_webpage(self, soup: BeautifulSoup) -> bool:
        """Check if webpage is heavily JavaScript-dependent"""
        # Count script tags
        script_tags = soup.find_all('script')
        
        # Check for common SPA frameworks
        spa_indicators = ['react', 'angular', 'vue', 'backbone', 'ember']
        content_text = str(soup).lower()
        
        has_spa_indicators = any(indicator in content_text for indicator in spa_indicators)
        has_many_scripts = len(script_tags) > 5
        
        # Check if content is mostly empty (indicating client-side rendering)
        text_content = soup.get_text().strip()
        has_minimal_content = len(text_content) < 500
        
        return has_spa_indicators or (has_many_scripts and has_minimal_content)
    
    def _is_static_webpage(self, soup: BeautifulSoup) -> bool:
        """Check if webpage is mostly static content"""
        # Look for substantial text content
        text_content = soup.get_text().strip()
        has_substantial_content = len(text_content) > 1000
        
        # Check for typical static content patterns
        static_indicators = [
            soup.find_all('article'),
            soup.find_all('section'),
            soup.find_all('div', class_=['content', 'post', 'article'])
        ]
        
        has_structured_content = any(len(elements) > 0 for elements in static_indicators)
        
        return has_substantial_content and has_structured_content
    
    async def _get_source_characteristics(self, source_type: SourceType, url: str) -> Dict[str, Any]:
        """Get characteristics for a specific source type"""
        characteristics = {
            SourceType.RSS_FEED: {
                "type": SourceType.RSS_FEED,
                "confidence": 0.95,
                "strategy": "rss_polling",
                "difficulty": "easy",
                "reliability": "high",
                "frequency": "real_time",
                "requirements": ["feedparser"],
                "dedup_strategy": "guid_based",
                "notes": "RSS feeds provide structured data and are ideal for real-time monitoring"
            },
            
            SourceType.API: {
                "type": SourceType.API,
                "confidence": 0.9,
                "strategy": "api_polling",
                "difficulty": "easy",
                "reliability": "high",
                "frequency": "scheduled",
                "requirements": ["api_key", "documentation"],
                "dedup_strategy": "id_based",
                "notes": "APIs provide structured data but may require authentication"
            },
            
            SourceType.NEWSLETTER: {
                "type": SourceType.NEWSLETTER,
                "confidence": 0.8,
                "strategy": "email_monitoring",
                "difficulty": "medium",
                "reliability": "medium",
                "frequency": "email_triggered",
                "requirements": ["email_parser", "imap_access"],
                "dedup_strategy": "content_hash",
                "notes": "Newsletters require email monitoring setup"
            },
            
            SourceType.DYNAMIC_WEBPAGE: {
                "type": SourceType.DYNAMIC_WEBPAGE,
                "confidence": 0.7,
                "strategy": "headless_scraping",
                "difficulty": "hard",
                "reliability": "variable",
                "frequency": "scheduled_scraping",
                "requirements": ["playwright", "css_selectors"],
                "dedup_strategy": "url_content_hybrid",
                "notes": "Dynamic pages require JavaScript rendering and are more fragile"
            },
            
            SourceType.STATIC_WEBPAGE: {
                "type": SourceType.STATIC_WEBPAGE,
                "confidence": 0.8,
                "strategy": "html_scraping",
                "difficulty": "medium",
                "reliability": "medium",
                "frequency": "scheduled_scraping",
                "requirements": ["beautifulsoup", "css_selectors"],
                "dedup_strategy": "url_content_hybrid",
                "notes": "Static pages are easier to scrape but require change detection"
            },
            
            SourceType.PDF_PUBLICATION: {
                "type": SourceType.PDF_PUBLICATION,
                "confidence": 0.9,
                "strategy": "pdf_monitoring",
                "difficulty": "medium",
                "reliability": "low",
                "frequency": "periodic_check",
                "requirements": ["pdf_parser", "ocr"],
                "dedup_strategy": "content_hash",
                "notes": "PDF monitoring requires document parsing and OCR capabilities"
            },
            
            SourceType.SOCIAL_MEDIA: {
                "type": SourceType.SOCIAL_MEDIA,
                "confidence": 0.85,
                "strategy": "social_api",
                "difficulty": "hard",
                "reliability": "low",
                "frequency": "api_polling",
                "requirements": ["social_api_key", "rate_limiting"],
                "dedup_strategy": "post_id",
                "notes": "Social media requires API access and careful rate limiting"
            }
        }
        
        return characteristics.get(source_type, {
            "type": SourceType.UNKNOWN,
            "confidence": 0.3,
            "strategy": "manual_review",
            "difficulty": "unknown",
            "reliability": "unknown",
            "frequency": "unknown",
            "requirements": ["manual_assessment"],
            "dedup_strategy": "content_hash",
            "notes": "Unknown source type requires manual assessment"
        })
    
    def _generate_monitoring_config(self, classification: Dict[str, Any], additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate monitoring configuration based on classification"""
        source_type = classification["type"]
        additional_info = additional_info or {}
        
        base_configs = {
            SourceType.RSS_FEED: {
                "check_frequency": "*/15 * * * *",  # Every 15 minutes
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "parsing_strategy": "feedparser",
                "headers": {"User-Agent": "TAIFA-RSS/1.0"},
                "rate_limit": "4/minute"
            },
            
            SourceType.API: {
                "check_frequency": "0 */2 * * *",  # Every 2 hours
                "timeout_seconds": 60,
                "retry_attempts": 5,
                "parsing_strategy": "json_api",
                "headers": {"User-Agent": "TAIFA-API/1.0", "Accept": "application/json"},
                "rate_limit": "1/minute"
            },
            
            SourceType.NEWSLETTER: {
                "check_frequency": "email_triggered",
                "timeout_seconds": 120,
                "retry_attempts": 2,
                "parsing_strategy": "email_parser",
                "headers": {},
                "rate_limit": "unlimited"
            },
            
            SourceType.DYNAMIC_WEBPAGE: {
                "check_frequency": "0 8,20 * * *",  # Twice daily
                "timeout_seconds": 180,
                "retry_attempts": 3,
                "parsing_strategy": "playwright",
                "headers": {"User-Agent": "TAIFA-Browser/1.0"},
                "rate_limit": "1/hour",
                "selector_config": {
                    "opportunity_container": ".funding-opportunity, .grant, .award",
                    "title": "h1, h2, .title, .heading",
                    "description": ".description, .summary, p",
                    "deadline": ".deadline, .due-date, .expires",
                    "amount": ".amount, .funding, .prize"
                }
            },
            
            SourceType.STATIC_WEBPAGE: {
                "check_frequency": "0 6,18 * * *",  # Twice daily
                "timeout_seconds": 60,
                "retry_attempts": 3,
                "parsing_strategy": "beautifulsoup",
                "headers": {"User-Agent": "TAIFA-Scraper/1.0"},
                "rate_limit": "2/hour",
                "selector_config": {
                    "opportunity_container": ".funding-opportunity, .grant, .award",
                    "title": "h1, h2, .title, .heading",
                    "description": ".description, .summary, p",
                    "deadline": ".deadline, .due-date, .expires",
                    "amount": ".amount, .funding, .prize"
                }
            }
        }
        
        config = base_configs.get(source_type, {
            "check_frequency": "0 12 * * *",  # Daily
            "timeout_seconds": 120,
            "retry_attempts": 2,
            "parsing_strategy": "manual",
            "headers": {"User-Agent": "TAIFA-Monitor/1.0"},
            "rate_limit": "1/day"
        })
        
        # Add notification settings
        config["notification_settings"] = {
            "success_webhook": True,
            "error_threshold": 3,
            "notify_on_new_opportunities": True,
            "email_alerts": additional_info.get("preferred_contact") == "email"
        }
        
        return config


async def test_source_classifier():
    """Test function for source classifier"""
    test_urls = [
        "https://example.org/rss/funding-opportunities.xml",
        "https://foundation.org/newsletter/signup",
        "https://university.edu/research/funding",
        "https://api.grants.gov/opportunities",
        "https://twitter.com/GrantsDaily",
        "https://reports.example.org/annual-report.pdf"
    ]
    
    async with SourceClassifier() as classifier:
        for url in test_urls:
            classification = await classifier.classify_source(url)
            print(f"\nURL: {url}")
            print(f"Type: {classification.source_type.value}")
            print(f"Confidence: {classification.confidence:.2f}")
            print(f"Strategy: {classification.monitoring_strategy}")
            print(f"Difficulty: {classification.setup_difficulty}")
            print(f"Reliability: {classification.expected_reliability}")


if __name__ == "__main__":
    asyncio.run(test_source_classifier())
