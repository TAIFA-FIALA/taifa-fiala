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
    """Enhanced organizations table with monitoring and performance tracking"""
    __tablename__ = "organizations"
    
    # Core identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    type = Column(String(20), default="funder", index=True)  # foundation, government, corporation, university, ngo
    
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
    
    # Status and timestamps
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    funding_opportunities = relationship("FundingOpportunity", back_populates="organization")
    geographic_focus = relationship("GeographicScope",
                                  secondary=organization_geographic_focus,
                                  back_populates="organizations")
    
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
        if self.funding_opportunities:
            return max(opp.discovered_date for opp in self.funding_opportunities)
        return None
    
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
