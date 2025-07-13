"""
TAIFA Source Validation Module

This module handles the validation, integration, and monitoring of external funding sources
submitted by community members and institutional partners.

Components:
- SourceValidator: Main validation logic for new source submissions
- DeduplicationPipeline: Multi-layer deduplication system
- SourceClassifier: Categorizes and configures different source types
- PerformanceTracker: Monitors source performance and quality
- SourceValidationOrchestrator: Main orchestrator for the complete workflow

Workflow:
1. Source submission → Initial validation → Classification
2. Approved sources → 30-day pilot monitoring
3. Performance evaluation → Production integration or deprecation
4. Ongoing monitoring and quality assurance
"""

from .source_validator import SourceValidator, SourceSubmission, ValidationResult
from .deduplication import DeduplicationPipeline, OpportunityContent, DuplicateMatch
from .source_classifier import SourceClassifier, SourceClassification, SourceType
from .performance_tracker import PerformanceTracker, SourceMetrics, PerformanceStatus
from .orchestrator import SourceValidationOrchestrator, SourceStatus, SourceSubmissionResult

__all__ = [
    # Main orchestrator
    "SourceValidationOrchestrator",
    
    # Core components
    "SourceValidator",
    "DeduplicationPipeline", 
    "SourceClassifier",
    "PerformanceTracker",
    
    # Data models
    "SourceSubmission",
    "ValidationResult",
    "OpportunityContent",
    "DuplicateMatch",
    "SourceClassification",
    "SourceMetrics",
    "SourceSubmissionResult",
    
    # Enums
    "SourceType",
    "PerformanceStatus",
    "SourceStatus"
]

# Version info
__version__ = "1.0.0"
__description__ = "TAIFA Source Validation and Integration System"
