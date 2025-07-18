"""
Simple Validation Service for TAIFA Unified Scraper
Validates individual intelligence feed for quality and relevance
"""

import re
import logging
from typing import Dict, List, Any
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ValidationService:
    """Simple validation service for intelligence feed"""
    
    def __init__(self):
        # Keywords that indicate AI/tech relevance
        self.ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
            'neural networks', 'computer vision', 'natural language processing', 'nlp',
            'robotics', 'automation', 'digital transformation', 'tech', 'technology',
            'innovation', 'startup', 'fintech', 'healthtech', 'agtech', 'edtech',
            'data science', 'analytics', 'software', 'app', 'digital', 'cyber',
            'blockchain', 'iot', 'internet of things', 'cloud computing'
        ]
        
        # Keywords that indicate African relevance  
        self.africa_keywords = [
            'africa', 'african', 'sub-saharan', 'saharan', 'east africa', 'west africa',
            'north africa', 'southern africa', 'nigeria', 'kenya', 'ghana', 'south africa',
            'uganda', 'tanzania', 'rwanda', 'egypt', 'morocco', 'ethiopia', 'senegal',
            'cote divoire', 'ivory coast', 'mali', 'burkina faso', 'cameroon', 'zimbabwe',
            'zambia', 'botswana', 'mozambique', 'madagascar', 'tunisia', 'algeria',
            'developing countries', 'emerging markets', 'global south', 'lmic',
            'low and middle income', 'francophone', 'anglophone'
        ]
        
        # Keywords that indicate funding/grants
        self.funding_keywords = [
            'grant', 'grants', 'funding', 'fund', 'prize', 'award', 'scholarship',
            'fellowship', 'competition', 'accelerator', 'incubator', 'investment',
            'seed funding', 'venture capital', 'vc', 'angel', 'loan', 'credit',
            'financial support', 'stipend', 'subsidy', 'call for proposals',
            'rfp', 'application', 'apply', 'submit', 'deadline', 'opportunity'
        ]
        
        # Red flag keywords that might indicate low relevance
        self.red_flags = [
            'expired', 'closed', 'deadline passed', 'no longer accepting',
            'internal only', 'invite only', 'by invitation', 'restricted',
            'members only', 'staff only', 'employees only'
        ]
    
    async def validate_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single intelligence item
        
        Returns:
            Dict with score, flags, and validation details
        """
        try:
            # Extract text content for analysis
            title = opportunity.get('title', '').lower()
            description = opportunity.get('description', '').lower()
            organization = opportunity.get('organization_name', '').lower()
            
            # Combine all text for analysis
            full_text = f"{title} {description} {organization}"
            
            # Calculate relevance scores
            ai_score = self._calculate_keyword_score(full_text, self.ai_keywords)
            africa_score = self._calculate_keyword_score(full_text, self.africa_keywords)
            funding_score = self._calculate_keyword_score(full_text, self.funding_keywords)
            
            # Check for red flags
            red_flag_score = self._calculate_keyword_score(full_text, self.red_flags)
            
            # Validate URL
            url_score = self._validate_url(opportunity.get('source_url', ''))
            
            # Validate amount if present
            amount_score = self._validate_amount(opportunity.get('amount'))
            
            # Calculate overall score
            base_score = (ai_score * 0.3 + africa_score * 0.3 + funding_score * 0.2 + 
                         url_score * 0.1 + amount_score * 0.1)
            
            # Apply red flag penalty
            final_score = max(0, base_score - (red_flag_score * 0.5))
            
            # Generate validation flags
            flags = self._generate_flags(opportunity, ai_score, africa_score, 
                                       funding_score, red_flag_score)
            
            return {
                "score": round(final_score, 3),
                "flags": flags,
                "details": {
                    "ai_relevance": round(ai_score, 3),
                    "africa_relevance": round(africa_score, 3),
                    "funding_relevance": round(funding_score, 3),
                    "url_validity": round(url_score, 3),
                    "amount_validity": round(amount_score, 3),
                    "red_flags": round(red_flag_score, 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating opportunity: {e}")
            return {
                "score": 0.5,  # Neutral score on error
                "flags": ["validation_error"],
                "details": {"error": str(e)}
            }
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matches"""
        if not text or not keywords:
            return 0.0
        
        matches = 0
        total_weight = 0
        
        for keyword in keywords:
            # Count occurrences of each keyword
            count = text.count(keyword.lower())
            if count > 0:
                # Weight longer keywords more heavily
                weight = len(keyword.split()) * count
                matches += weight
                total_weight += weight
        
        # Normalize score based on text length and keyword density
        text_length = len(text.split())
        if text_length == 0:
            return 0.0
        
        # Score is based on keyword density, capped at 1.0
        density_score = min(1.0, (matches / max(text_length, 10)) * 10)
        return density_score
    
    def _validate_url(self, url: str) -> float:
        """Validate URL format and structure"""
        if not url:
            return 0.0
        
        try:
            parsed = urlparse(url)
            
            # Basic URL structure checks
            if not parsed.scheme or not parsed.netloc:
                return 0.2
            
            # Check for valid scheme
            if parsed.scheme not in ['http', 'https']:
                return 0.3
            
            # Prefer HTTPS
            score = 0.8 if parsed.scheme == 'https' else 0.6
            
            # Check for reasonable path
            if parsed.path and len(parsed.path) > 1:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception:
            return 0.1
    
    def _validate_amount(self, amount: Any) -> float:
        """Validate funding amount if present"""
        if amount is None:
            return 0.7  # Neutral score if no amount provided
        
        try:
            # Convert to float if string
            if isinstance(amount, str):
                # Remove currency symbols and commas
                cleaned = re.sub(r'[^\d.]', '', amount)
                amount = float(cleaned)
            
            amount = float(amount)
            
            # Check for reasonable funding amounts
            if amount < 0:
                return 0.0  # Negative amounts are invalid
            elif amount < 100:
                return 0.3  # Very small amounts might be questionable
            elif amount > 100000000:  # 100 million
                return 0.4  # Very large amounts might be questionable
            else:
                return 1.0  # Reasonable amount
                
        except (ValueError, TypeError):
            return 0.2  # Invalid amount format
    
    def _generate_flags(self, opportunity: Dict[str, Any], ai_score: float, 
                       africa_score: float, funding_score: float, red_flag_score: float) -> List[str]:
        """Generate validation flags for manual review"""
        flags = []
        
        # Low relevance flags
        if ai_score < 0.3:
            flags.append("low_ai_relevance")
        
        if africa_score < 0.2:
            flags.append("low_africa_relevance")
        
        if funding_score < 0.3:
            flags.append("low_funding_relevance")
        
        # Red flag warnings
        if red_flag_score > 0.3:
            flags.append("potential_red_flags")
        
        # Missing critical information
        if not opportunity.get('title'):
            flags.append("missing_title")
        
        if not opportunity.get('description') or len(opportunity.get('description', '')) < 20:
            flags.append("insufficient_description")
        
        if not opportunity.get('source_url'):
            flags.append("missing_url")
        
        # Organization validation
        if not opportunity.get('organization_name'):
            flags.append("missing_organization")
        
        # Deadline validation
        deadline = opportunity.get('deadline')
        if deadline:
            try:
                if isinstance(deadline, str):
                    # Try to parse various date formats
                    deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    if deadline_date < datetime.now():
                        flags.append("expired_deadline")
            except Exception:
                flags.append("invalid_deadline_format")
        
        return flags

# Create a global instance for import
validation_service = ValidationService()
