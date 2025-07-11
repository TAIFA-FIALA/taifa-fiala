from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class RFP(Base):
    """Request for Proposals (RFP) opportunities"""
    __tablename__ = "rfps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    amount_usd = Column(Float)
    currency = Column(String(10), default="USD")
    link = Column(String(500))
    contact_email = Column(String(255))
    status = Column(String(50), default="open")
    categories = Column(Text) # Stored as JSON string or comma-separated

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", backref="rfps")

    def __repr__(self):
        return f"<RFP(id={self.id}, title='{self.title}', organization_id={self.organization_id})>"
