from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Date, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Import junction table definitions
from sqlalchemy import Table
funding_opportunity_ai_domains = Table(
    'funding_opportunity_ai_domains',
    Base.metadata,
    Column('funding_opportunity_id', Integer, ForeignKey('funding_opportunities.id', ondelete='CASCADE'), primary_key=True),
    Column('ai_domain_id', Integer, ForeignKey('ai_domains.id', ondelete='CASCADE'), primary_key=True)
)

funding_opportunity_geographic_scopes = Table(
    'funding_opportunity_geographic_scopes', 
    Base.metadata,
    Column('funding_opportunity_id', Integer, ForeignKey('funding_opportunities.id', ondelete='CASCADE'), primary_key=True),
    Column('geographic_scope_id', Integer, ForeignKey('geographic_scopes.id', ondelete='CASCADE'), primary_key=True)
)

class FundingOpportunity(Base):
    """Enhanced funding opportunities table with competitor analysis insights"""
    __tablename__ = "funding_opportunities"
    
    # Core identification
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    source_url = Column(Text, nullable=False)
    application_url = Column(Text)
    
    # Organization relationships (both old and new for backward compatibility)
    organization_name = Column(Text)  # Keep for backward compatibility
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    
    # Enhanced funding details (based on competitor analysis)
    type_id = Column(Integer, ForeignKey('funding_types.id'), index=True)
    status = Column(String(20), default='open', index=True)  # open, closed, under_review
    funding_amount = Column(Text)  # Keep as text for flexibility
    currency = Column(String(10), default='USD', index=True)  # USD, EUR, GBP, etc.
    deadline = Column(Date)
    deadline_urgency = Column(String(10), index=True)  # Computed: urgent, moderate, low, expired, unknown
    
    # Community and quality features
    community_rating = Column(Numeric(2,1), index=True)  # 1.0-5.0 rating
    application_tips = Column(Text)  # Community-contributed guidance
    submitted_by_user_id = Column(Integer, ForeignKey('community_users.id'))
    verified = Column(Boolean, default=False)
    
    # Performance tracking
    view_count = Column(Integer, default=0)
    application_count = Column(Integer, default=0)
    
    # Flexible categorization
    tags = Column(JSONB)  # Flexible tagging system
    
    # Source tracking
    source_type = Column(Text)
    source_name = Column(Text)
    search_query = Column(Text)
    
    # Relevance scores
    ai_relevance_score = Column(Float)
    africa_relevance_score = Column(Float)
    funding_relevance_score = Column(Float)
    overall_relevance_score = Column(Float)
    
    # Metadata
    content_hash = Column(Text, unique=True)
    raw_data = Column(JSONB)
    discovered_date = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Processing flags
    parsed_with_ai = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    # Multilingual support
    detected_language = Column(String(5), default='en')
    translation_status = Column(JSONB)
    is_multilingual = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="funding_opportunities")
    type = relationship("FundingType", back_populates="opportunities")
    submitted_by = relationship("CommunityUser", back_populates="submitted_opportunities")
    
    # Many-to-many relationships
    ai_domains = relationship("AIDomain", 
                             secondary=funding_opportunity_ai_domains,
                             back_populates="opportunities")
    geographic_scopes = relationship("GeographicScope",
                                   secondary=funding_opportunity_geographic_scopes, 
                                   back_populates="opportunities")
    
    # Virtual attributes for compatibility with existing code
    @property
    def amount(self):
        """Backward compatibility property"""
        return self.funding_amount
        
    @property
    def geographical_scope(self):
        """Backward compatibility - get first geographic scope"""
        if self.geographic_scopes:
            return self.geographic_scopes[0].name
        if self.raw_data and 'geographical_scope' in self.raw_data:
            return self.raw_data['geographical_scope']
        return None
        
    @property
    def eligibility_criteria(self):
        """Backward compatibility property"""
        if self.raw_data and 'eligibility_criteria' in self.raw_data:
            return self.raw_data['eligibility_criteria']
        return None
        
    @property
    def funding_type_name(self):
        """Get funding type name"""
        return self.type.name if self.type else None
        
    @property
    def organization_name_display(self):
        """Get organization name from relationship or fallback to text field"""
        return self.organization.name if self.organization else self.organization_name
        
    @property
    def ai_domain_names(self):
        """Get list of AI domain names"""
        return [domain.name for domain in self.ai_domains]
        
    @property
    def geographic_scope_names(self):
        """Get list of geographic scope names"""
        return [scope.name for scope in self.geographic_scopes]
        
    @property
    def urgency_level(self):
        """Get urgency level for deadline"""
        return self.deadline_urgency or 'unknown'
        
    @property
    def urgency_color(self):
        """Get color code for urgency display"""
        urgency_colors = {
            'urgent': 'red',
            'moderate': 'yellow', 
            'low': 'green',
            'expired': 'gray',
            'unknown': 'blue'
        }
        return urgency_colors.get(self.urgency_level, 'blue')
        
    @property
    def days_until_deadline(self):
        """Calculate days until deadline"""
        if not self.deadline:
            return None
        from datetime import date
        delta = self.deadline - date.today()
        return delta.days if delta.days >= 0 else 0
        
    @property
    def is_deadline_approaching(self):
        """Check if deadline is within 30 days"""
        days = self.days_until_deadline
        return days is not None and 0 <= days <= 30
        
    def __repr__(self):
        return f"<FundingOpportunity(id={self.id}, title='{self.title[:50]}...', status='{self.status}')>"
