from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base

class FundingOpportunity(Base):
    """Main table for funding opportunities"""
    __tablename__ = "funding_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    amount = Column(Numeric(15, 2))  # Max amount in local currency
    currency = Column(String(3), default="USD")  # ISO currency code
    amount_usd = Column(Numeric(15, 2))  # Converted to USD for comparison
    
    # Dates
    deadline = Column(DateTime(timezone=True))
    announcement_date = Column(DateTime(timezone=True))
    start_date = Column(DateTime(timezone=True))
    
    # Status and metadata
    status = Column(String(20), default="active")
    source_url = Column(String(1000))
    contact_info = Column(Text)
    
    # Geographic scope
    geographical_scope = Column(Text)  # JSON or comma-separated countries
    eligibility_criteria = Column(Text)
    
    # AI focus areas (will be populated via many-to-many)
    application_deadline = Column(DateTime(timezone=True))
    max_funding_period_months = Column(Integer)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_checked = Column(DateTime(timezone=True))
    
    # Foreign keys
    source_organization_id = Column(Integer, ForeignKey("organizations.id"))
    data_source_id = Column(Integer, ForeignKey("data_sources.id"))
    
    def __repr__(self):
        return f"<FundingOpportunity(id={self.id}, title='{self.title}')>"
