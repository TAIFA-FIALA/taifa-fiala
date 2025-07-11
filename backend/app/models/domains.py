from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class AIDomain(Base):
    """AI domains and focus areas"""
    __tablename__ = "ai_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("ai_domains.id"))
    
    # Self-referential relationship for hierarchical categories
    parent = relationship("AIDomain", remote_side=[id])
    children = relationship("AIDomain")

class FundingCategory(Base):
    """Funding categories (Research, Implementation, etc.)"""
    __tablename__ = "funding_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("funding_categories.id"))
    
    # Self-referential relationship
    parent = relationship("FundingCategory", remote_side=[id])
    children = relationship("FundingCategory")
