"""
Validation and ETL Processing Models
===================================

Models to support the enhanced ETL pipeline with validation,
duplicate detection, and processing tracking.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class ValidationResult(Base):
    """Validation results for intelligence feed"""
    __tablename__ = "validation_results"
    
    id = Column(String(50), primary_key=True, index=True)  # UUID
    opportunity_id = Column(Integer, ForeignKey('africa_intelligence_feed.id'), nullable=True, index=True)
    
    # Validation status and scoring
    status = Column(String(20), default='pending', index=True)  # pending, approved, rejected, needs_review
    confidence_score = Column(Float, index=True)
    confidence_level = Column(String(10), index=True)  # very_high, high, medium, low, very_low
    
    # Quality metrics
    completeness_score = Column(Float)
    relevance_score = Column(Float)
    legitimacy_score = Column(Float)
    
    # Validation flags and notes
    validation_flags = Column(JSONB)  # List of validation flags
    validation_notes = Column(Text)
    auto_approval_eligible = Column(Boolean, default=False)
    requires_human_review = Column(Boolean, default=True)
    
    # Validator information
    validator = Column(String(50), default='ai_system')  # ai_system, human, hybrid
    validated_by_user_id = Column(Integer, ForeignKey('community_users.id'), nullable=True)
    
    # Processing metadata
    processing_time = Column(Float)  # seconds
    validated_data = Column(JSONB)  # Validated/extracted data
    raw_data = Column(JSONB)  # Original raw data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    validated_at = Column(DateTime(timezone=True))
    
    # Relationships
    opportunity = relationship("AfricaIntelligenceItem", back_populates="validation_results")
    validated_by_user = relationship("CommunityUser")
    
    def __repr__(self):
        return f"<ValidationResult(id={self.id}, status='{self.status}', confidence={self.confidence_score})>"

class DuplicateDetection(Base):
    """Duplicate detection results"""
    __tablename__ = "duplicate_detections"
    
    id = Column(String(50), primary_key=True, index=True)  # UUID
    original_opportunity_id = Column(Integer, ForeignKey('africa_intelligence_feed.id'), index=True)
    duplicate_opportunity_id = Column(Integer, ForeignKey('africa_intelligence_feed.id'), index=True)
    
    # Detection information
    duplicate_type = Column(String(30), index=True)  # exact_match, title_similarity, content_similarity, etc.
    confidence_score = Column(Float, index=True)
    similarity_score = Column(Float)
    
    # Action taken
    action = Column(String(20), index=True)  # reject, merge, mark_related, enhance_original, manual_review
    action_taken_at = Column(DateTime(timezone=True))
    action_taken_by = Column(String(50))
    
    # Detection details
    detection_method = Column(String(50))  # The specific algorithm used
    detection_details = Column(JSONB)  # Additional details about the match
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    original_opportunity = relationship("AfricaIntelligenceItem", foreign_keys=[original_opportunity_id])
    duplicate_opportunity = relationship("AfricaIntelligenceItem", foreign_keys=[duplicate_opportunity_id])
    
    def __repr__(self):
        return f"<DuplicateDetection(id={self.id}, type='{self.duplicate_type}', confidence={self.confidence_score})>"

class ProcessingJob(Base):
    """Processing job tracking"""
    __tablename__ = "processing_jobs"
    
    id = Column(String(50), primary_key=True, index=True)  # UUID
    job_type = Column(String(30), index=True)  # ingestion, validation, enhancement, organization_enrichment, etc.
    module_type = Column(String(30), index=True)  # rss_feed, serper_search, user_submission, crawl4ai, enrichment_pipeline
    
    # Job status
    status = Column(String(20), default='queued', index=True)  # queued, processing, completed, failed
    priority = Column(Integer, default=2, index=True)  # 1=critical, 2=high, 3=medium, 4=low
    
    # Processing metadata
    source_data = Column(JSONB)  # Input data
    result_data = Column(JSONB)  # Output data
    metadata = Column(JSONB)  # Additional job metadata (organization_id, enrichment_type, etc.)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Performance metrics
    processing_time = Column(Float)  # seconds
    items_processed = Column(Integer, default=0)
    items_succeeded = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"

class ModuleHealth(Base):
    """Module health tracking"""
    __tablename__ = "module_health"
    
    id = Column(Integer, primary_key=True, index=True)
    module_type = Column(String(30), unique=True, index=True)  # rss_feed, serper_search, etc.
    
    # Health status
    status = Column(String(20), default='active', index=True)  # active, degraded, failed, disabled, maintenance
    last_success = Column(DateTime(timezone=True))
    last_failure = Column(DateTime(timezone=True))
    
    # Performance metrics
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_processing_time = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    
    # Circuit breaker state
    circuit_breaker_open = Column(Boolean, default=False)
    circuit_breaker_failures = Column(Integer, default=0)
    circuit_breaker_threshold = Column(Integer, default=5)
    
    # Configuration
    enabled = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)  # requests per minute
    timeout = Column(Integer, default=30)  # seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
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
    
    def __repr__(self):
        return f"<ModuleHealth(module='{self.module_type}', status='{self.status}')>"

class ContentFingerprint(Base):
    """Content fingerprints for duplicate detection"""
    __tablename__ = "content_fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey('africa_intelligence_feed.id'), unique=True, index=True)
    
    # Fingerprint hashes
    title_hash = Column(String(64), index=True)
    content_hash = Column(String(64), index=True)
    semantic_hash = Column(String(64), index=True)
    url_hash = Column(String(64), index=True)
    signature_hash = Column(String(64), index=True)
    
    # Extracted metadata
    organization_name = Column(String(255), index=True)
    funding_amount = Column(Float, index=True)
    funding_currency = Column(String(10))
    announcement_date = Column(DateTime(timezone=True))
    deadline_date = Column(Date)
    url_domain = Column(String(255), index=True)
    
    # Key phrases and metadata
    key_phrases = Column(JSONB)  # List of key phrases
    extraction_metadata = Column(JSONB)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    opportunity = relationship("AfricaIntelligenceItem", back_populates="content_fingerprint")
    
    def __repr__(self):
        return f"<ContentFingerprint(id={self.id}, opportunity_id={self.opportunity_id})>"

class SourceQuality(Base):
    """Source quality tracking"""
    __tablename__ = "source_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), unique=True, index=True)
    source_type = Column(String(30), index=True)  # rss, website, api, etc.
    
    # Quality metrics
    accuracy_score = Column(Float, default=0.0)  # 0-1 based on validation success
    duplicate_rate = Column(Float, default=0.0)  # 0-1 percentage of duplicates
    processing_success_rate = Column(Float, default=0.0)  # 0-1 processing success
    content_relevance_score = Column(Float, default=0.0)  # 0-1 relevance to AI funding
    
    # Usage statistics
    total_items_processed = Column(Integer, default=0)
    successful_items = Column(Integer, default=0)
    duplicate_items = Column(Integer, default=0)
    invalid_items = Column(Integer, default=0)
    
    # Source metadata
    last_processed = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    quality_grade = Column(String(1), index=True)  # A, B, C, D, F
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def update_quality_metrics(self):
        """Update quality metrics based on current statistics"""
        if self.total_items_processed > 0:
            self.processing_success_rate = self.successful_items / self.total_items_processed
            self.duplicate_rate = self.duplicate_items / self.total_items_processed
        
        # Calculate overall quality score
        quality_score = (
            self.accuracy_score * 0.3 +
            self.processing_success_rate * 0.3 +
            self.content_relevance_score * 0.2 +
            (1 - self.duplicate_rate) * 0.2
        )
        
        # Assign quality grade
        if quality_score >= 0.9:
            self.quality_grade = 'A'
        elif quality_score >= 0.8:
            self.quality_grade = 'B'
        elif quality_score >= 0.7:
            self.quality_grade = 'C'
        elif quality_score >= 0.6:
            self.quality_grade = 'D'
        else:
            self.quality_grade = 'F'
    
    def __repr__(self):
        return f"<SourceQuality(source='{self.source_name}', grade='{self.quality_grade}')>"