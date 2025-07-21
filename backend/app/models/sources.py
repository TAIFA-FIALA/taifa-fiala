from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func

from app.core.base import Base

class DataSource(Base):
    """Data sources for automated collection"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    url = Column(String(1000), nullable=False)
    type = Column(String(20), default="rss")
    
    # Monitoring configuration
    check_interval_minutes = Column(Integer, default=60)
    last_checked = Column(DateTime(timezone=True))
    last_successful_check = Column(DateTime(timezone=True))
    
    # Quality metrics
    reliability_score = Column(Float, default=1.0)  # 0.0 to 1.0
    total_opportunities_found = Column(Integer, default=0)
    successful_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    status_message = Column(Text)  # Last error or status
    
    # Processing configuration
    parser_config = Column(Text)  # JSON configuration for parser
    classification_keywords = Column(Text)  # Keywords for AI classification
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        total = self.successful_checks + self.failed_checks
        if total == 0:
            return 0.0
        return (self.successful_checks / total) * 100
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}', type='{self.type}')>"
