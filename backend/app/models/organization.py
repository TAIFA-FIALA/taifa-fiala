from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.core.database import Base

class Organization(Base):
    """Organizations that provide or receive funding"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    type = Column(String(20), default="funder")
    
    # Contact and location
    country = Column(String(100))
    region = Column(String(100))  # Sub-Saharan Africa, North Africa, etc.
    website = Column(String(500))
    email = Column(String(200))
    description = Column(Text)
    
    # Funding characteristics
    funding_capacity = Column(String(50))  # Large, Medium, Small
    focus_areas = Column(Text)  # JSON array of focus areas
    established_year = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', type='{self.type}')>"
