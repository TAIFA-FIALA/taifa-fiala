from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Junction table for organization geographic focus
organization_geographic_focus = Table(
    'organization_geographic_focus',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
    Column('geographic_scope_id', Integer, ForeignKey('geographic_scopes.id', ondelete='CASCADE'), primary_key=True)
)

class Organization(Base):
    """Enhanced organizations table with monitoring and performance tracking.
    
    Organizations can be classified as funding providers (granting agencies, venture capital),
    funding recipients (grantees, startups), or both. This model supports tracking the
    relationships between funding providers and recipients.
    """
    __tablename__ = "organizations"
    
    # Core identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    
    # Organization type classification
    type = Column(String(20), default="funder", index=True)  # foundation, government, corporation, university, ngo
    
    # Organization role in funding ecosystem
    role = Column(String(20), default="provider", index=True)  # provider, recipient, both
    provider_type = Column(String(20), nullable=True, index=True)  # granting_agency, venture_capital, angel_investor, accelerator
    recipient_type = Column(String(20), nullable=True, index=True)  # grantee, startup, research_institution, non_profit
    
    # Stage classification for startups/recipients
    startup_stage = Column(String(30), nullable=True)  # idea, seed, early, growth, mature, etc.
    
    # Funding classification for providers
    funding_model = Column(String(30), nullable=True)  # grants_only, equity_only, mixed, debt, etc.
    
    # Contact and location
    country = Column(String(100))
    region = Column(String(100))  # Sub-Saharan Africa, North Africa, etc.
    website = Column(String(500))
    email = Column(String(200))
    description = Column(Text)
    
    # Enhanced organization profile
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    
    # Funding characteristics
    funding_capacity = Column(String(50))  # Large, Medium, Small
    focus_areas = Column(Text)  # JSON array of focus areas
    established_year = Column(Integer)
    
    # AI and Africa relevance scoring (based on competitor analysis)
    ai_relevance_score = Column(Integer, default=0, index=True)  # 0-100: % of AI-related funding
    africa_relevance_score = Column(Integer, default=0, index=True)  # 0-100: % of Africa-relevant funding
    
    # Monitoring configuration
    source_type = Column(String(20), default='manual', index=True)  # rss, newsletter, webpage, api, manual
    update_frequency = Column(String(20))  # daily, weekly, monthly, ad-hoc
    funding_announcement_url = Column(Text)  # Specific page for funding announcements
    monitoring_status = Column(String(20), default='active', index=True)  # active, pilot, deprecated
    monitoring_reliability = Column(Integer, default=100)  # 0-100: uptime percentage
    
    # Performance metrics (based on data collection results)
    opportunities_discovered = Column(Integer, default=0)
    unique_opportunities_added = Column(Integer, default=0)
    duplicate_rate = Column(Integer, default=0)  # 0-100: percentage of duplicates
    data_completeness_score = Column(Integer, default=0)  # 0-100: quality of data provided
    
    # Community features
    community_rating = Column(Numeric(2,1))  # 1.0-5.0 rating from community
    
    # Enrichment tracking
    enrichment_status = Column(String(20), default='pending', index=True)  # pending, in_progress, completed, failed
    enrichment_completeness = Column(Integer, default=0)  # 0-100: percentage of fields populated
    last_enrichment_attempt = Column(DateTime(timezone=True))
    enrichment_sources = Column(Text)  # JSON array of data sources used
    
    # Cultural and heritage context
    founding_story = Column(Text)  # Organization's founding narrative
    cultural_significance = Column(Text)  # Cultural importance and context
    local_partnerships = Column(Text)  # JSON array of local partnerships
    community_impact = Column(Text)  # Description of community impact
    
    # Extended profile data
    logo_url = Column(String(500))
    mission_statement = Column(Text)
    vision_statement = Column(Text)
    leadership_team = Column(Text)  # JSON array of key leaders
    notable_achievements = Column(Text)  # JSON array of achievements
    awards_recognition = Column(Text)  # JSON array of awards
    
    # Social media and online presence
    linkedin_url = Column(String(500))
    twitter_handle = Column(String(100))
    facebook_url = Column(String(500))
    instagram_url = Column(String(500))
    
    # Financial and operational context
    annual_budget_range = Column(String(50))  # e.g., "1M-5M USD"
    staff_size_range = Column(String(50))  # e.g., "10-50 employees"
    languages_supported = Column(Text)  # JSON array of languages
    
    # Impact metrics
    total_funding_distributed = Column(Numeric(15,2))  # Total funding amount distributed
    beneficiaries_count = Column(Integer)  # Number of beneficiaries served
    success_stories = Column(Text)  # JSON array of success stories
    
    # Status and timestamps
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    africa_intelligence_feed = relationship("AfricaIntelligenceItem", back_populates="organization")
    user_submissions = relationship("UserSubmission", back_populates="organization", cascade="all, delete-orphan")
    monitoring_data = relationship("MonitoringData", back_populates="organization", cascade="all, delete-orphan")
    scraping_configurations = relationship("ScrapingConfiguration", back_populates="organization", cascade="all, delete-orphan")
    
    # New relationships for funding flows
    provided_funding = relationship("AfricaIntelligenceItem", 
                                  foreign_keys="[AfricaIntelligenceItem.provider_organization_id]",
                                  back_populates="provider_organization")
    received_funding = relationship("AfricaIntelligenceItem", 
                                   foreign_keys="[AfricaIntelligenceItem.recipient_organization_id]",
                                   back_populates="recipient_organization")
    geographic_focus = relationship("GeographicScope",
                                  secondary=organization_geographic_focus,
                                  back_populates="organizations")
    
    # Equity analytics relationships
    gender_funding_data = relationship("GenderFundingData", back_populates="organization")
    collaboration_suggestions = relationship(
        "CollaborationSuggestion",
        secondary="organization_collaboration", 
        back_populates="organizations"
    )
    
    # Computed properties for monitoring insights
    @property
    def success_rate(self):
        """Calculate success rate of unique opportunities vs total discovered"""
        if self.opportunities_discovered == 0:
            return 0
        return round((self.unique_opportunities_added / self.opportunities_discovered) * 100, 1)
    
    @property
    def monitoring_health(self):
        """Get overall monitoring health status"""
        if self.monitoring_reliability >= 95:
            return 'excellent'
        elif self.monitoring_reliability >= 80:
            return 'good'
        elif self.monitoring_reliability >= 60:
            return 'fair'
        else:
            return 'poor'
    
    @property
    def ai_relevance_level(self):
        """Get AI relevance category"""
        if self.ai_relevance_score >= 80:
            return 'high'
        elif self.ai_relevance_score >= 50:
            return 'medium'
        elif self.ai_relevance_score >= 20:
            return 'low'
        else:
            return 'minimal'
    
    @property
    def africa_relevance_level(self):
        """Get Africa relevance category"""
        if self.africa_relevance_score >= 80:
            return 'high'
        elif self.africa_relevance_score >= 50:
            return 'medium'
        elif self.africa_relevance_score >= 20:
            return 'low'
        else:
            return 'minimal'
    
    @property
    def data_quality_grade(self):
        """Get data quality letter grade"""
        if self.data_completeness_score >= 90:
            return 'A'
        elif self.data_completeness_score >= 80:
            return 'B'
        elif self.data_completeness_score >= 70:
            return 'C'
        elif self.data_completeness_score >= 60:
            return 'D'
        else:
            return 'F'
    
    @property
    def monitoring_status_display(self):
        """Get user-friendly monitoring status"""
        status_map = {
            'active': '🟢 Active',
            'pilot': '🟡 Pilot',
            'deprecated': '🔴 Deprecated',
            'inactive': '⚫ Inactive'
        }
        return status_map.get(self.monitoring_status, self.monitoring_status)
    
    @property
    def geographic_focus_names(self):
        """Get list of geographic focus area names"""
        return [scope.name for scope in self.geographic_focus]
    
    @property
    def primary_geographic_focus(self):
        """Get primary geographic focus (first one)"""
        return self.geographic_focus[0].name if self.geographic_focus else None
    
    @property
    def organization_type_display(self):
        """Get user-friendly organization type"""
        type_map = {
            'foundation': '🏛️ Foundation',
            'government': '🏛️ Government Agency',
            'corporation': '🏢 Corporation',
            'university': '🎓 University',
            'ngo': '🌍 NGO',
            'funder': '💰 Funder',
            'multilateral': '🌐 Multilateral Org'
        }
        return type_map.get(self.type, f"📋 {self.type.title()}")
    
    @property
    def is_high_value_source(self):
        """Determine if this is a high-value funding source"""
        return (
            self.ai_relevance_score >= 60 and
            self.africa_relevance_score >= 60 and
            self.unique_opportunities_added >= 5 and
            self.data_completeness_score >= 70
        )
    
    @property
    def last_activity(self):
        """Get timestamp of last opportunity added"""
        if self.africa_intelligence_feed:
            return max(opp.discovered_date for opp in self.africa_intelligence_feed)
        return None
    
    @property
    def enrichment_status_display(self):
        """Get user-friendly enrichment status"""
        status_map = {
            'pending': '⏳ Pending',
            'in_progress': '🔄 In Progress',
            'completed': '✅ Completed',
            'failed': '❌ Failed'
        }
        return status_map.get(self.enrichment_status, self.enrichment_status)
    
    @property
    def enrichment_completeness_grade(self):
        """Get enrichment completeness letter grade"""
        if self.enrichment_completeness >= 90:
            return 'A'
        elif self.enrichment_completeness >= 80:
            return 'B'
        elif self.enrichment_completeness >= 70:
            return 'C'
        elif self.enrichment_completeness >= 60:
            return 'D'
        else:
            return 'F'
    
    @property
    def needs_enrichment(self):
        """Check if organization needs enrichment"""
        return (
            self.enrichment_status in ['pending', 'failed'] or
            self.enrichment_completeness < 70 or
            (self.last_enrichment_attempt and 
             (func.now() - self.last_enrichment_attempt).days > 30)
        )
    
    def update_performance_metrics(self, discovered: int = 0, unique_added: int = 0, 
                                 duplicates: int = 0, data_quality: int = None):
        """Update performance metrics"""
        if discovered > 0:
            self.opportunities_discovered += discovered
        if unique_added > 0:
            self.unique_opportunities_added += unique_added
        if discovered > 0:
            total_duplicates = duplicates
            self.duplicate_rate = round((total_duplicates / discovered) * 100, 1)
        if data_quality is not None:
            self.data_completeness_score = data_quality
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', type='{self.type}', ai_relevance={self.ai_relevance_score}%)>"
