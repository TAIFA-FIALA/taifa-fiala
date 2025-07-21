"""
Enhanced TAIFA Database Models
Includes all models with relationships and new lookup tables based on competitor analysis
"""

# Import all models to ensure they're registered with SQLAlchemy
# Import order is important to avoid circular imports

# Import base first
from app.core.base import Base, metadata

# Then import models
from .funding import AfricaIntelligenceItem
from .organization import Organization
from .lookups import FundingType, AIDomain, GeographicScope, CommunityUser
from .domains import AIDomain as DomainAlias  # Keep existing import if needed
from .sources import DataSource
from .rfp import RFP
from .equity import (
    GenderFundingData, UnderrepresentedGroup, InclusionMetric, 
    FeaturedFounder, FundingStageMetric, StageProgression,
    CollaborationSuggestion, SuggestedOpportunity
)
from .validation import (
    ValidationResult, DuplicateDetection, ProcessingJob, 
    ModuleHealth, ContentFingerprint, SourceQuality
)

# This will ensure all models are imported and registered with SQLAlchemy
# before creating any database tables
__all__ = [
    # Core models (enhanced)
    "AfricaIntelligenceItem",
    "Organization", 
    
    # New lookup models
    "FundingType",
    "AIDomain",
    "GeographicScope",
    "CommunityUser",
    
    # Domain models
    "DomainAlias",
    
    # Source tracking
    "DataSource",
    
    # RFP model
    "RFP",
    
    # Equity and inclusion models
    "GenderFundingData",
    "UnderrepresentedGroup",
    "InclusionMetric",
    "FeaturedFounder",
    "FundingStageMetric",
    "StageProgression",
    "CollaborationSuggestion",
    "SuggestedOpportunity",
    
    # Validation and monitoring
    "ValidationResult",
    "DuplicateDetection",
    "ProcessingJob",
    "ModuleHealth",
    "ContentFingerprint",
    "SourceQuality",
]

# Model relationships summary for reference:
"""
Enhanced Relationship Structure:

AfricaIntelligenceItem:
├── organization (One-to-Many → Organization)
├── type (One-to-Many → FundingType) 
├── submitted_by (One-to-Many → CommunityUser)
├── ai_domains (Many-to-Many → AIDomain)
└── geographic_scopes (Many-to-Many → GeographicScope)

Organization:
├── africa_intelligence_feed (One-to-Many ← AfricaIntelligenceItem)
└── geographic_focus (Many-to-Many → GeographicScope)

AIDomain:
├── opportunities (Many-to-Many ← AfricaIntelligenceItem)
├── parent_domain (Self-referential)
└── sub_domains (Self-referential)

GeographicScope:
├── opportunities (Many-to-Many ← AfricaIntelligenceItem)
├── organizations (Many-to-Many ← Organization)
├── parent_scope (Self-referential)
└── sub_scopes (Self-referential)

CommunityUser:
└── submitted_opportunities (One-to-Many ← AfricaIntelligenceItem)

FundingType:
└── opportunities (One-to-Many ← AfricaIntelligenceItem)
"""
