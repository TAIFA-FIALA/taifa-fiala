from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class FundingType(Base):
    """Types of funding opportunities (Grant, Prize, Scholarship, Investment, etc.)"""
    __tablename__ = "funding_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    typical_amount_range = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Classification fields
    category = Column(String(20), nullable=False, index=True)  # 'grant', 'investment', 'prize', 'other'
    requires_equity = Column(Boolean, default=False)
    requires_repayment = Column(Boolean, default=False)
    average_processing_time_days = Column(Integer)
    success_rate_percentage = Column(Integer)
    required_stage = Column(String(50))  # 'idea', 'prototype', 'mvp', 'revenue', 'growth'
    
    # Relationships
    opportunities = relationship("FundingOpportunity", back_populates="type")
    
    def __repr__(self):
        return f"<FundingType(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    @property
    def is_investment(self):
        """Check if this funding type is an investment type"""
        return self.category == 'investment'
    
    @property
    def is_grant(self):
        """Check if this funding type is a grant type"""
        return self.category == 'grant'

class AIDomain(Base):
    """AI application domains (Healthcare, Agriculture, etc.)"""
    __tablename__ = "ai_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    parent_domain_id = Column(Integer, ForeignKey('ai_domains.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Self-referential relationship for hierarchical domains
    parent_domain = relationship("AIDomain", remote_side=[id], back_populates="sub_domains")
    sub_domains = relationship("AIDomain", back_populates="parent_domain")
    
    # Many-to-many relationship with funding opportunities
    opportunities = relationship("FundingOpportunity", 
                               secondary="funding_opportunity_ai_domains",
                               back_populates="ai_domains")
    
    def __repr__(self):
        return f"<AIDomain(id={self.id}, name='{self.name}')>"

class GeographicScope(Base):
    """Geographic scopes (Countries, Regions, Continents)"""
    __tablename__ = "geographic_scopes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(10), index=True)  # ISO country code
    type = Column(String(20), default='country', index=True)  # country, region, continent, global
    parent_scope_id = Column(Integer, ForeignKey('geographic_scopes.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Self-referential relationship for hierarchical scopes
    parent_scope = relationship("GeographicScope", remote_side=[id], back_populates="sub_scopes")
    sub_scopes = relationship("GeographicScope", back_populates="parent_scope")
    
    # Many-to-many relationships
    opportunities = relationship("FundingOpportunity",
                               secondary="funding_opportunity_geographic_scopes",
                               back_populates="geographic_scopes")
    organizations = relationship("Organization",
                               secondary="organization_geographic_focus", 
                               back_populates="geographic_focus")
    
    def __repr__(self):
        return f"<GeographicScope(id={self.id}, name='{self.name}', type='{self.type}')>"

class CommunityUser(Base):
    """Community users who contribute to the platform"""
    __tablename__ = "community_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    reputation_score = Column(Integer, default=0)
    contributions_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    submitted_opportunities = relationship("FundingOpportunity", back_populates="submitted_by")
    
    def __repr__(self):
        return f"<CommunityUser(id={self.id}, username='{self.username}', reputation={self.reputation_score})>"
