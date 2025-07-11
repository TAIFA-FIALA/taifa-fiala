from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class RFPBase(BaseModel):
    """Base schema for Request for Proposals (RFP)"""
    title: str
    description: str
    organization_id: int
    deadline: datetime
    amount_usd: Optional[float] = None
    currency: Optional[str] = "USD"
    link: Optional[HttpUrl] = None
    contact_email: Optional[str] = None
    status: str = "open" # e.g., open, closed, awarded
    categories: Optional[List[str]] = [] # e.g., AI, Education, Health

class RFPCreate(RFPBase):
    """Schema for creating RFPs"""
    pass

class RFPResponse(RFPBase):
    """Schema for RFP responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
