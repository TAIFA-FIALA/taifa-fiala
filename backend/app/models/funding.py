from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Date, Numeric, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.base import Base

# Import junction table definitions
from sqlalchemy import Table
intelligence_item_ai_domains = Table(
    'intelligence_item_ai_domains',
    Base.metadata,
    Column('intelligence_item_id', Integer, ForeignKey('africa_intelligence_feed.id', ondelete='CASCADE'), primary_key=True),
    Column('ai_domain_id', Integer, ForeignKey('ai_domains.id', ondelete='CASCADE'), primary_key=True)
)

intelligence_item_geographic_scopes = Table(
    'intelligence_item_geographic_scopes', 
    Base.metadata,
    Column('intelligence_item_id', Integer, ForeignKey('africa_intelligence_feed.id', ondelete='CASCADE'), primary_key=True),
    Column('geographic_scope_id', Integer, ForeignKey('geographic_scopes.id', ondelete='CASCADE'), primary_key=True)
)

class AfricaIntelligenceItem(Base):
    """Enhanced intelligence feed table with competitor analysis insights"""
    __tablename__ = "africa_intelligence_feed"
    
    # Core identification
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    source_url = Column(Text, nullable=False)
    application_url = Column(Text)
    
    # Organization relationships (both old and new for backward compatibility)
    organization_name = Column(Text)  # Keep for backward compatibility
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)  # Legacy field
    
    # New differentiated organization relationships
    provider_organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    recipient_organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    
    # Enhanced funding details (based on competitor analysis)
    funding_type_id = Column(Integer, ForeignKey('funding_types.id'), index=True)
    status = Column(String(20), default='open', index=True)  # open, closed, under_review
    funding_amount = Column(Text)  # Keep as text for flexibility
    
    # Enhanced funding amount fields to support all three funding patterns
    total_funding_pool = Column(Float, nullable=True)  # Total funding available for disbursement
    funding_type = Column(String(20), default='per_project_range', index=True)  # total_pool, per_project_exact, per_project_range
    min_amount_per_project = Column(Float, nullable=True)  # Minimum funding per project
    max_amount_per_project = Column(Float, nullable=True)  # Maximum funding per project
    exact_amount_per_project = Column(Float, nullable=True)  # Fixed amount per project
    estimated_project_count = Column(Integer, nullable=True)  # Expected number of projects to fund
    project_count_range = Column(JSONB, nullable=True)  # Range of projects: {"min": int, "max": int}
    
    # Legacy amount fields for backward compatibility
    amount_min = Column(Float, nullable=True)  # Minimum funding amount (numeric)
    amount_max = Column(Float, nullable=True)  # Maximum funding amount (numeric)
    amount_exact = Column(Float, nullable=True)  # Exact amount if specified
    currency = Column(String(10), default='USD', index=True)  # USD, EUR, GBP, etc.
    
    # Enhanced timing and process fields
    deadline = Column(Date)
    deadline_urgency = Column(String(10), index=True)  # Computed: urgent, moderate, low, expired, unknown
    application_deadline_type = Column(String(20), default='fixed', index=True)  # rolling, fixed, multiple_rounds
    announcement_date = Column(Date)
    funding_start_date = Column(Date)
    project_duration = Column(String(100))  # Expected project timeline
    
    # Enhanced application and selection process
    application_process = Column(Text)  # How to apply
    selection_criteria = Column(JSONB)  # What they're looking for (JSON array)
    
    # Enhanced targeting and focus areas
    target_audience = Column(JSONB)  # Who can apply (startups, researchers, etc.) - JSON array
    ai_subsectors = Column(JSONB)  # Specific AI focus areas - JSON array
    development_stage = Column(JSONB)  # Early stage, growth stage, etc. - JSON array
    collaboration_required = Column(Boolean, nullable=True)  # Must involve partnerships
    gender_focused = Column(Boolean, nullable=True)  # Women-focused initiatives
    youth_focused = Column(Boolean, nullable=True)  # Youth-specific programs
    
    # Enhanced reporting and compliance
    reporting_requirements = Column(JSONB)  # Ongoing obligations - JSON array
    
    # Grant-specific fields
    grant_reporting_requirements = Column(Text)  # Required for grants - legacy field
    grant_duration_months = Column(Integer)  # Duration of grant funding
    grant_renewable = Column(Boolean, default=False)  # Can the grant be renewed?
    no_strings_attached = Column(Boolean)  # True if no ownership or repayment required
    project_based = Column(Boolean, default=True)  # Is funding for specific project vs general ops?
    
    # Enhanced grant-specific fields
    interim_reporting_required = Column(Boolean, nullable=True)
    final_report_required = Column(Boolean, nullable=True)
    financial_reporting_frequency = Column(String(20))  # monthly, quarterly, annually
    intellectual_property_rights = Column(Text)
    publication_requirements = Column(Text)
    
    # Investment-specific fields
    equity_percentage = Column(Float)  # % of equity required for investment
    valuation_cap = Column(Float)  # Valuation cap for convertible notes
    interest_rate = Column(Float)  # For debt financing
    repayment_terms = Column(Text)  # Repayment structure
    investor_rights = Column(Text)  # Special rights requested by investors
    post_investment_support = Column(Text)  # Mentoring, network, etc.
    expected_roi = Column(Float)  # Expected return on investment percentage
    
    # Enhanced investment-specific fields
    liquidation_preference = Column(Text)
    board_representation = Column(Boolean, nullable=True)
    anti_dilution_protection = Column(Text)
    drag_along_rights = Column(Boolean, nullable=True)
    tag_along_rights = Column(Boolean, nullable=True)
    
    # Prize and competition-specific fields
    competition_phases = Column(JSONB)  # List of competition phases
    judging_criteria = Column(JSONB)  # List of judging criteria
    submission_format = Column(Text)
    presentation_required = Column(Boolean, nullable=True)
    team_size_limit = Column(Integer)
    intellectual_property_ownership = Column(Text)
    
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
    
    # ETL Pipeline Fields
    # Enhanced duplicate detection
    title_hash = Column(String(64), index=True)
    semantic_hash = Column(String(64), index=True)
    url_hash = Column(String(64), index=True)
    
    # Content classification
    content_type = Column(String(50), default='intelligence_item', index=True)
    content_classification_confidence = Column(Float)
    classification_method = Column(String(50))
    
    # Validation tracking
    validation_status = Column(String(20), default='pending', index=True)
    validation_confidence_score = Column(Float)
    validation_flags = Column(JSONB)
    validation_notes = Column(Text)
    validated_at = Column(DateTime(timezone=True))
    validated_by = Column(String(50))
    requires_human_review = Column(Boolean, default=True)
    
    # Module tracking
    ingestion_module = Column(String(50), index=True)
    processing_id = Column(String(50), index=True)
    processing_metadata = Column(JSONB)
    
    # Multilingual support
    detected_language = Column(String(5), default='en')
    translation_status = Column(JSONB)
    is_multilingual = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id], back_populates="africa_intelligence_feed")  # Legacy relationship
    type = relationship("FundingType")
    
    # New differentiated organization relationships
    provider_organization = relationship("Organization", foreign_keys=[provider_organization_id], back_populates="provided_funding")
    recipient_organization = relationship("Organization", foreign_keys=[recipient_organization_id], back_populates="received_funding")
    submitted_by = relationship("CommunityUser", back_populates="submitted_opportunities")
    
    # Many-to-many relationships
    ai_domains = relationship("AIDomain", 
                             secondary=intelligence_item_ai_domains,
                             back_populates="opportunities")
    geographic_scopes = relationship("GeographicScope",
                                   secondary=intelligence_item_geographic_scopes, 
                                   back_populates="opportunities")
    
    # ETL Pipeline relationships
    validation_results = relationship("ValidationResult", back_populates="opportunity")
    content_fingerprint = relationship("ContentFingerprint", back_populates="opportunity", uselist=False)
    
    # Type-specific properties and methods
    @property
    def is_grant(self):
        """Check if this intelligence item is a grant"""
        return self.type and self.type.is_grant
    
    @property
    def is_investment(self):
        """Check if this intelligence item is an investment"""
        return self.type and self.type.is_investment
    
    @property
    def funding_category(self):
        """Get the funding category (grant, investment, prize, other)"""
        return self.type.category if self.type else "unknown"
    
    @property
    def provider_is_granting_agency(self):
        """Check if the provider is a granting agency"""
        return self.provider_organization and self.provider_organization.provider_type == "granting_agency"
    
    @property
    def provider_is_venture_capital(self):
        """Check if the provider is a venture capital group"""
        return self.provider_organization and self.provider_organization.provider_type == "venture_capital"
    
    @property
    def recipient_is_grantee(self):
        """Check if the recipient is a grantee organization"""
        return self.recipient_organization and self.recipient_organization.recipient_type == "grantee"
    
    @property
    def recipient_is_startup(self):
        """Check if the recipient is a startup"""
        return self.recipient_organization and self.recipient_organization.recipient_type == "startup"
    
    @property
    def requires_equity(self):
        """Check if equity is required for this opportunity"""
        if self.type:
            return self.type.requires_equity
        # Fallback based on equity_percentage field
        return bool(self.equity_percentage)
        
    @property
    def grant_properties(self):
        """Get grant-specific properties if this is a grant"""
        if not self.is_grant:
            return None
            
        return {
            "reporting_requirements": self.reporting_requirements,
            "duration_months": self.grant_duration_months,
            "renewable": self.renewable,
            "no_strings_attached": self.no_strings_attached,
            "project_based": self.project_based
        }
    
    @property
    def investment_properties(self):
        """Get investment-specific properties if this is an investment"""
        if not self.is_investment:
            return None
            
        return {
            "equity_percentage": self.equity_percentage,
            "valuation_cap": self.valuation_cap,
            "interest_rate": self.interest_rate,
            "repayment_terms": self.repayment_terms,
            "investor_rights": self.investor_rights,
            "post_investment_support": self.post_investment_support,
            "expected_roi": self.expected_roi
        }
    
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
        return f"<AfricaIntelligenceItem(id={self.id}, title='{self.title[:50]}...', status='{self.status}')>"
