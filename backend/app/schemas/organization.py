from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class OrganizationBase(BaseModel):
    """Base schema for organizations"""
    name: str
    type: str = "funder"
    country: Optional[str] = None
    region: Optional[str] = None
    website: Optional[HttpUrl] = None
    email: Optional[str] = None
    description: Optional[str] = None
    funding_capacity: Optional[str] = None
    focus_areas: Optional[str] = None
    established_year: Optional[int] = None

class OrganizationCreate(OrganizationBase):
    """Schema for creating organizations"""
    pass

class OrganizationUpdate(BaseModel):
    """Schema for updating organizations"""
    name: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    website: Optional[HttpUrl] = None
    email: Optional[str] = None
    description: Optional[str] = None
    funding_capacity: Optional[str] = None
    focus_areas: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    """Schema for organization responses"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
