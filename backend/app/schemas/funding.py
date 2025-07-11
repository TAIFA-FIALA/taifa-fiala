from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class FundingOpportunityBase(BaseModel):
    """Base schema for funding opportunities"""
    title: str
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: str = "USD"
    amount_usd: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    announcement_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    status: str = "active"
    source_url: Optional[HttpUrl] = None
    contact_info: Optional[str] = None
    geographical_scope: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    application_deadline: Optional[datetime] = None
    max_funding_period_months: Optional[int] = None

class FundingOpportunityCreate(FundingOpportunityBase):
    """Schema for creating funding opportunities"""
    source_organization_id: Optional[int] = None
    data_source_id: Optional[int] = None

class FundingOpportunityUpdate(BaseModel):
    """Schema for updating funding opportunities"""
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    contact_info: Optional[str] = None
    eligibility_criteria: Optional[str] = None


class OrganizationBase(BaseModel):
    """Base schema for organizations (for embedding in responses)"""
    id: int
    name: str
    type: str
    country: Optional[str] = None
    website: Optional[HttpUrl] = None

class AIDomainBase(BaseModel):
    """Base schema for AI domains (for embedding)"""
    id: int
    name: str
    description: Optional[str] = None

class FundingCategoryBase(BaseModel):
    """Base schema for funding categories (for embedding)"""
    id: int
    name: str
    description: Optional[str] = None

class FundingOpportunityResponse(FundingOpportunityBase):
    """Schema for funding opportunity responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    
    # Related objects
    source_organization: Optional[OrganizationBase] = None
    ai_domains: List[AIDomainBase] = []
    categories: List[FundingCategoryBase] = []
    
    class Config:
        from_attributes = True

class FundingOpportunityList(BaseModel):
    """Schema for paginated funding opportunity lists"""
    items: List[FundingOpportunityResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
