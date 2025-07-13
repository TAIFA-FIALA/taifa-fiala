"""
Enhanced TAIFA Database Models
Includes all models with relationships and new lookup tables based on competitor analysis
"""

# Import all models to ensure they're registered with SQLAlchemy
from app.models.funding import FundingOpportunity
from app.models.organization import Organization
from app.models.lookups import FundingType, AIDomain, GeographicScope, CommunityUser
from app.models.domains import AIDomain as DomainAlias  # Keep existing import if needed
from app.models.sources import DataSource
from app.models.rfp import RFP

# Export all models for easy importing
__all__ = [
    # Core models (enhanced)
    "FundingOpportunity",
    "Organization", 
    
    # New lookup models
    "FundingType",
    "AIDomain", 
    "GeographicScope",
    "CommunityUser",
    
    # Existing models (maintain compatibility)
    "DataSource",
    "RFP",
    
    # Legacy alias
    "DomainAlias",
]

# Model relationships summary for reference:
"""
Enhanced Relationship Structure:

FundingOpportunity:
├── organization (One-to-Many → Organization)
├── type (One-to-Many → FundingType) 
├── submitted_by (One-to-Many → CommunityUser)
├── ai_domains (Many-to-Many → AIDomain)
└── geographic_scopes (Many-to-Many → GeographicScope)

Organization:
├── funding_opportunities (One-to-Many ← FundingOpportunity)
└── geographic_focus (Many-to-Many → GeographicScope)

AIDomain:
├── opportunities (Many-to-Many ← FundingOpportunity)
├── parent_domain (Self-referential)
└── sub_domains (Self-referential)

GeographicScope:
├── opportunities (Many-to-Many ← FundingOpportunity)
├── organizations (Many-to-Many ← Organization)
├── parent_scope (Self-referential)
└── sub_scopes (Self-referential)

CommunityUser:
└── submitted_opportunities (One-to-Many ← FundingOpportunity)

FundingType:
└── opportunities (One-to-Many ← FundingOpportunity)
"""
