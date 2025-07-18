"""
Data Validation and Quality Framework
===================================

AI-powered data validation system optimized for speed and accuracy.
Minimal human-in-the-loop confirmation with intelligent auto-approval.
Designed for Streamlit admin interface integration.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import openai
import re
from urllib.parse import urlparse
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# VALIDATION ENUMS AND TYPES
# =============================================================================

class ValidationStatus(Enum):
    """Status of validation process"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    IN_REVIEW = "in_review"
    AUTO_APPROVED = "auto_approved"

class ValidationFlag(Enum):
    """Validation warning flags"""
    DUPLICATE_CONTENT = "duplicate_content"
    SUSPICIOUS_URL = "suspicious_url"
    UNCLEAR_DEADLINE = "unclear_deadline"
    INCOMPLETE_INFO = "incomplete_info"
    IRRELEVANT_CONTENT = "irrelevant_content"
    SCAM_INDICATORS = "scam_indicators"
    EXPIRED_OPPORTUNITY = "expired_opportunity"
    MISSING_CONTACT = "missing_contact"

class ConfidenceLevel(Enum):
    """AI confidence levels"""
    VERY_HIGH = "very_high"  # 0.9-1.0
    HIGH = "high"           # 0.8-0.9
    MEDIUM = "medium"       # 0.6-0.8
    LOW = "low"            # 0.4-0.6
    VERY_LOW = "very_low"  # 0.0-0.4

# =============================================================================
# VALIDATION DATA MODELS
# =============================================================================

@dataclass
class ValidationResult:
    """Result of data validation process"""
    id: str
    status: ValidationStatus
    confidence_score: float
    confidence_level: ConfidenceLevel
    flags: List[ValidationFlag] = field(default_factory=list)
    validation_notes: str = ""
    auto_approval_eligible: bool = False
    requires_human_review: bool = True
    processing_time: float = 0.0
    validated_at: datetime = field(default_factory=datetime.now)
    validator: str = "ai_system"
    
    # Extracted and validated data
    validated_data: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    completeness_score: float = 0.0
    relevance_score: float = 0.0
    legitimacy_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'status': self.status.value,
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level.value,
            'flags': [flag.value for flag in self.flags],
            'validation_notes': self.validation_notes,
            'auto_approval_eligible': self.auto_approval_eligible,
            'requires_human_review': self.requires_human_review,
            'processing_time': self.processing_time,
            'validated_at': self.validated_at.isoformat(),
            'validator': self.validator,
            'validated_data': self.validated_data,
            'raw_data': self.raw_data,
            'completeness_score': self.completeness_score,
            'relevance_score': self.relevance_score,
            'legitimacy_score': self.legitimacy_score
        }

@dataclass
class ValidationConfig:
    """Configuration for validation system"""
    
    # AI Model Configuration
    ai_model: str = "gpt-4o-mini"
    max_tokens: int = 3000
    temperature: float = 0.1
    
    # Confidence Thresholds
    auto_approve_threshold: float = 0.85
    review_threshold: float = 0.65
    reject_threshold: float = 0.30
    
    # Quality Score Weights
    completeness_weight: float = 0.3
    relevance_weight: float = 0.4
    legitimacy_weight: float = 0.3
    
    # Time Limits
    validation_timeout: int = 30  # seconds
    review_timeout: int = 86400   # 24 hours
    
    # Batch Processing
    batch_size: int = 25
    max_parallel_validations: int = 10

# =============================================================================
# CORE VALIDATION ENGINE
# =============================================================================

class DataValidationEngine:
    """Core validation engine with AI-powered analysis"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.openai_client = openai.AsyncOpenAI()
        self.logger = logging.getLogger(__name__)
        
        # Validation caches
        self.duplicate_cache = {}
        self.validation_cache = {}
        
    async def validate_opportunity(self, raw_data: Dict[str, Any], source_type: str) -> ValidationResult:
        """Validate a single intelligence item"""
        start_time = datetime.now()
        validation_id = str(uuid.uuid4())
        
        try:
            # Initialize validation result
            result = ValidationResult(
                id=validation_id,
                status=ValidationStatus.PENDING,
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                raw_data=raw_data
            )
            
            # Step 1: Basic validation checks
            basic_validation = await self._basic_validation_checks(raw_data)
            result.flags.extend(basic_validation['flags'])
            
            # Step 2: Duplicate detection
            duplicate_check = await self._check_for_duplicates(raw_data)
            if duplicate_check['is_duplicate']:
                result.flags.append(ValidationFlag.DUPLICATE_CONTENT)
                result.validation_notes += f"Duplicate detected: {duplicate_check['match_info']}. "
            
            # Step 3: AI-powered content validation
            ai_validation = await self._ai_content_validation(raw_data, source_type)
            result.validated_data = ai_validation['validated_data']
            result.validation_notes += ai_validation['notes']
            
            # Step 4: Calculate quality scores
            quality_scores = await self._calculate_quality_scores(result.validated_data)
            result.completeness_score = quality_scores['completeness']
            result.relevance_score = quality_scores['relevance']
            result.legitimacy_score = quality_scores['legitimacy']
            
            # Step 5: Calculate overall confidence
            result.confidence_score = self._calculate_confidence_score(
                result.completeness_score,
                result.relevance_score,
                result.legitimacy_score,
                len(result.flags)
            )
            
            # Step 6: Determine confidence level and status
            result.confidence_level = self._get_confidence_level(result.confidence_score)
            result.status, result.auto_approval_eligible, result.requires_human_review = self._determine_status(
                result.confidence_score,
                result.flags
            )
            
            # Step 7: Final validation notes
            result.validation_notes += self._generate_validation_summary(result)
            
            # Processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Validation completed for {validation_id}: {result.status.value} (confidence: {result.confidence_score:.3f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed for {validation_id}: {e}")
            return ValidationResult(
                id=validation_id,
                status=ValidationStatus.REJECTED,
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.VERY_LOW,
                validation_notes=f"Validation error: {str(e)}",
                processing_time=(datetime.now() - start_time).total_seconds(),
                raw_data=raw_data
            )
    
    async def batch_validate(self, raw_data_list: List[Dict[str, Any]], source_type: str) -> List[ValidationResult]:
        """Validate multiple opportunities in parallel"""
        semaphore = asyncio.Semaphore(self.config.max_parallel_validations)
        
        async def validate_single(data):
            async with semaphore:
                return await self.validate_opportunity(data, source_type)
        
        # Process in batches
        results = []
        for i in range(0, len(raw_data_list), self.config.batch_size):
            batch = raw_data_list[i:i + self.config.batch_size]
            batch_results = await asyncio.gather(
                *[validate_single(data) for data in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, ValidationResult)]
        
        self.logger.info(f"Batch validation completed: {len(valid_results)}/{len(raw_data_list)} successful")
        return valid_results
    
    # =============================================================================
    # VALIDATION STEP IMPLEMENTATIONS
    # =============================================================================
    
    async def _basic_validation_checks(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation checks for structure and content"""
        flags = []
        
        # Check required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if not raw_data.get(field) or len(str(raw_data[field]).strip()) < 10:
                flags.append(ValidationFlag.INCOMPLETE_INFO)
                break
        
        # Check URL validity
        if raw_data.get('link'):
            if not self._is_valid_url(raw_data['link']):
                flags.append(ValidationFlag.SUSPICIOUS_URL)
        
        # Check deadline
        if raw_data.get('deadline'):
            if not self._is_valid_deadline(raw_data['deadline']):
                flags.append(ValidationFlag.UNCLEAR_DEADLINE)
        
        # Check for scam indicators
        if self._has_scam_indicators(raw_data):
            flags.append(ValidationFlag.SCAM_INDICATORS)
        
        return {'flags': flags}
    
    async def _check_for_duplicates(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for duplicate content using content hashing"""
        try:
            # Create content hash
            content_text = f"{raw_data.get('title', '')}{raw_data.get('description', '')}"
            content_hash = hashlib.md5(content_text.encode()).hexdigest()
            
            # Check cache
            if content_hash in self.duplicate_cache:
                return {
                    'is_duplicate': True,
                    'match_info': f"Similar content found (hash: {content_hash[:8]})"
                }
            
            # Add to cache
            self.duplicate_cache[content_hash] = {
                'first_seen': datetime.now(),
                'data': raw_data
            }
            
            return {'is_duplicate': False}
            
        except Exception as e:
            self.logger.error(f"Duplicate check failed: {e}")
            return {'is_duplicate': False}
    
    async def _ai_content_validation(self, raw_data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """AI-powered content validation and extraction"""
        try:
            prompt = f"""
            Analyze this intelligence item data and validate its legitimacy and relevance for African AI development:
            
            Source Type: {source_type}
            Raw Data: {json.dumps(raw_data, indent=2)}
            
            Please validate and extract:
            1. Title (cleaned and formatted)
            2. Organization/Funder name
            3. Funding amount and currency
            4. Application deadline (standardized format)
            5. Eligibility criteria
            6. Geographic focus (Africa relevance)
            7. Sector focus (AI/Tech relevance)
            8. Application process
            9. Contact information
            10. Legitimacy assessment
            11. Relevance score for African AI (0-1)
            12. Completeness score (0-1)
            13. Overall confidence (0-1)
            
            Return JSON with validated data and assessment scores.
            Focus on accuracy and flag any concerns.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.ai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.validation_timeout
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            return {
                'validated_data': ai_result,
                'notes': ai_result.get('validation_notes', 'AI validation completed. ')
            }
            
        except Exception as e:
            self.logger.error(f"AI validation failed: {e}")
            return {
                'validated_data': raw_data,
                'notes': f"AI validation failed: {str(e)}. "
            }
    
    async def _calculate_quality_scores(self, validated_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality scores for the validated data"""
        try:
            # Completeness score
            required_fields = ['title', 'organization', 'amount', 'deadline', 'eligibility']
            present_fields = sum(1 for field in required_fields if validated_data.get(field))
            completeness = present_fields / len(required_fields)
            
            # Relevance score (from AI)
            relevance = float(validated_data.get('relevance_score', 0.5))
            
            # Legitimacy score (from AI)
            legitimacy = float(validated_data.get('legitimacy_score', 0.5))
            
            return {
                'completeness': completeness,
                'relevance': relevance,
                'legitimacy': legitimacy
            }
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return {'completeness': 0.5, 'relevance': 0.5, 'legitimacy': 0.5}
    
    def _calculate_confidence_score(self, completeness: float, relevance: float, legitimacy: float, flag_count: int) -> float:
        """Calculate overall confidence score"""
        # Weighted score
        base_score = (
            completeness * self.config.completeness_weight +
            relevance * self.config.relevance_weight +
            legitimacy * self.config.legitimacy_weight
        )
        
        # Penalty for flags
        flag_penalty = min(0.1 * flag_count, 0.3)
        
        # Final score
        confidence = max(0.0, base_score - flag_penalty)
        
        return confidence
    
    def _get_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Get confidence level from score"""
        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _determine_status(self, confidence_score: float, flags: List[ValidationFlag]) -> Tuple[ValidationStatus, bool, bool]:
        """Determine validation status and review requirements"""
        # Check for critical flags
        critical_flags = [ValidationFlag.SCAM_INDICATORS, ValidationFlag.DUPLICATE_CONTENT]
        has_critical_flags = any(flag in flags for flag in critical_flags)
        
        if has_critical_flags:
            return ValidationStatus.REJECTED, False, False
        
        # Confidence-based decisions
        if confidence_score >= self.config.auto_approve_threshold:
            return ValidationStatus.AUTO_APPROVED, True, False
        elif confidence_score >= self.config.review_threshold:
            return ValidationStatus.NEEDS_REVIEW, False, True
        else:
            return ValidationStatus.REJECTED, False, False
    
    def _generate_validation_summary(self, result: ValidationResult) -> str:
        """Generate validation summary for admin review"""
        summary = f"Confidence: {result.confidence_level.value.replace('_', ' ').title()} ({result.confidence_score:.3f}). "
        
        if result.flags:
            flag_names = [flag.value.replace('_', ' ').title() for flag in result.flags]
            summary += f"Flags: {', '.join(flag_names)}. "
        
        if result.auto_approval_eligible:
            summary += "Auto-approved based on high confidence. "
        elif result.requires_human_review:
            summary += "Requires human review. "
        
        return summary
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _is_valid_deadline(self, deadline: str) -> bool:
        """Check if deadline is valid and not expired"""
        try:
            # Try to parse various date formats
            import dateparser
            parsed_date = dateparser.parse(deadline)
            if parsed_date:
                return parsed_date > datetime.now()
            return False
        except:
            return False
    
    def _has_scam_indicators(self, raw_data: Dict[str, Any]) -> bool:
        """Check for common scam indicators"""
        scam_keywords = [
            'urgent', 'act now', 'limited time', 'guaranteed',
            'no strings attached', 'free money', 'easy money',
            'click here', 'act fast', 'exclusive offer'
        ]
        
        text_content = f"{raw_data.get('title', '')} {raw_data.get('description', '')}".lower()
        
        return any(keyword in text_content for keyword in scam_keywords)

# =============================================================================
# STREAMLIT ADMIN INTEGRATION
# =============================================================================

class StreamlitValidationInterface:
    """Interface for Streamlit admin validation workflow"""
    
    def __init__(self, validation_engine: DataValidationEngine):
        self.validation_engine = validation_engine
        self.logger = logging.getLogger(__name__)
    
    async def get_review_queue(self, status: ValidationStatus = ValidationStatus.NEEDS_REVIEW) -> List[ValidationResult]:
        """Get opportunities pending review"""
        # This would integrate with your database to fetch pending validations
        # For now, returning empty list as placeholder
        return []
    
    async def approve_opportunity(self, validation_id: str, reviewer_notes: str = "") -> bool:
        """Approve an opportunity from admin interface"""
        try:
            # Update validation status
            # This would integrate with your database
            self.logger.info(f"Opportunity {validation_id} approved by admin")
            return True
        except Exception as e:
            self.logger.error(f"Failed to approve opportunity {validation_id}: {e}")
            return False
    
    async def reject_opportunity(self, validation_id: str, reason: str) -> bool:
        """Reject an opportunity from admin interface"""
        try:
            # Update validation status
            # This would integrate with your database
            self.logger.info(f"Opportunity {validation_id} rejected: {reason}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reject opportunity {validation_id}: {e}")
            return False
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics for admin dashboard"""
        return {
            'total_processed': 0,
            'auto_approved': 0,
            'needs_review': 0,
            'rejected': 0,
            'avg_confidence': 0.0,
            'processing_time': 0.0
        }

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_validation():
    """Example usage of validation system"""
    config = ValidationConfig()
    validator = DataValidationEngine(config)
    
    # Sample data
    raw_data = {
        'title': 'AI Development Grant for African Startups',
        'description': 'This grant supports AI development in African countries...',
        'link': 'https://example.org/grant',
        'deadline': '2024-12-31',
        'amount': '50000',
        'organization': 'Example Foundation'
    }
    
    # Validate
    result = await validator.validate_opportunity(raw_data, 'rss')
    
    print(f"Validation Result:")
    print(f"Status: {result.status.value}")
    print(f"Confidence: {result.confidence_score:.3f}")
    print(f"Requires Review: {result.requires_human_review}")
    print(f"Notes: {result.validation_notes}")

if __name__ == "__main__":
    asyncio.run(example_validation())