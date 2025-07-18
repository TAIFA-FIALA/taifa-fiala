from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


# Association tables
founder_underrepresented_groups = Table(
    "founder_underrepresented_groups",
    Base.metadata,
    Column("founder_id", Integer, ForeignKey("featured_founders.id")),
    Column("group_id", Integer, ForeignKey("underrepresented_groups.id")),
)

organization_collaboration = Table(
    "organization_collaboration",
    Base.metadata,
    Column("collaboration_id", Integer, ForeignKey("collaboration_suggestions.id")),
    Column("organization_id", Integer, ForeignKey("organizations.id")),
)


class GenderFundingData(Base):
    """Model for tracking gender distribution of funding."""
    __tablename__ = "gender_funding_data"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(50), nullable=False)
    funding_amount = Column(Float, default=0.0)
    opportunity_count = Column(Integer, default=0)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="gender_funding_data")


class UnderrepresentedGroup(Base):
    """Model for tracking different underrepresented groups in funding."""
    __tablename__ = "underrepresented_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    founders = relationship(
        "FeaturedFounder", 
        secondary=founder_underrepresented_groups, 
        back_populates="groups"
    )
    inclusion_metrics = relationship("InclusionMetric", back_populates="group")


class InclusionMetric(Base):
    """Model for tracking inclusion metrics across different dimensions."""
    __tablename__ = "inclusion_metrics"

    id = Column(Integer, primary_key=True, index=True)
    funding_percentage = Column(Float, default=0.0)
    opportunity_count = Column(Integer, default=0)
    total_funding = Column(Float, default=0.0)
    change_from_previous_year = Column(Float, default=0.0)
    metric_type = Column(String(50), nullable=False)  # regional, language, demographic
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    group_id = Column(Integer, ForeignKey("underrepresented_groups.id"), nullable=True)
    group = relationship("UnderrepresentedGroup", back_populates="inclusion_metrics")
    
    region_id = Column(Integer, ForeignKey("geographic_scopes.id"), nullable=True)
    region = relationship("GeographicScope")


class FeaturedFounder(Base):
    """Model for featured founders with focus on underrepresented groups."""
    __tablename__ = "featured_founders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=False)
    organization_name = Column(String(200), nullable=False)
    funding_secured = Column(Float, default=0.0)
    story = Column(Text)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    groups = relationship(
        "UnderrepresentedGroup",
        secondary=founder_underrepresented_groups,
        back_populates="founders"
    )
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")
    ai_domain_id = Column(Integer, ForeignKey("ai_domains.id"), nullable=True)
    ai_domain = relationship("AIDomain")


class FundingStageMetric(Base):
    """Model for tracking funding stage distribution and progression."""
    __tablename__ = "funding_stage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(String(50), nullable=False)
    opportunity_count = Column(Integer, default=0)
    avg_funding = Column(Float, default=0.0)
    total_funding = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    avg_months_in_stage = Column(Float, default=0.0)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StageProgression(Base):
    """Model for tracking stage progression rates."""
    __tablename__ = "stage_progression"

    id = Column(Integer, primary_key=True, index=True)
    from_stage = Column(String(50), nullable=False)
    to_stage = Column(String(50), nullable=False)
    progression_rate = Column(Float, default=0.0)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollaborationSuggestion(Base):
    """Model for collaboration suggestions between organizations."""
    __tablename__ = "collaboration_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    collaboration_potential = Column(Integer, nullable=False)
    rationale = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organizations = relationship(
        "Organization",
        secondary=organization_collaboration,
        back_populates="collaboration_suggestions"
    )
    suggested_opportunities = relationship("SuggestedOpportunity", back_populates="collaboration")


class SuggestedOpportunity(Base):
    """Model for opportunities suggested for collaborations."""
    __tablename__ = "suggested_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    
    # Relationships
    collaboration_id = Column(Integer, ForeignKey("collaboration_suggestions.id"))
    collaboration = relationship("CollaborationSuggestion", back_populates="suggested_opportunities")
    intelligence_item_id = Column(Integer, ForeignKey("africa_intelligence_feed.id"), nullable=True)
    intelligence_item = relationship("AfricaIntelligenceItem")
