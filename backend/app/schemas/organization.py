from pydantic import BaseModel, HttpUrl

from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class OrganizationBase(BaseModel):
    """Base schema for organizations"""
    name: str
    
    # Basic classification
    type: str = "funder"  # foundation, government, corporation, university, ngo
    
    # Funding ecosystem role
    role: str = "provider"  # provider, recipient, both
    provider_type: Optional[str] = None  # granting_agency, venture_capital, angel_investor, accelerator
    recipient_type: Optional[str] = None  # grantee, startup, research_institution, non_profit
    
    # Additional classification
    startup_stage: Optional[str] = None  # idea, seed, early, growth, mature, etc.
    funding_model: Optional[str] = None  # grants_only, equity_only, mixed, debt, etc.
    
    # Location and contact
    country: Optional[str] = None
    region: Optional[str] = None
    website: Optional[HttpUrl] = None
    email: Optional[str] = None
    description: Optional[str] = None
    
    # Funding characteristics
    funding_capacity: Optional[str] = None
    focus_areas: Optional[str] = None
    established_year: Optional[int] = None

class OrganizationCreate(OrganizationBase):
    """Schema for creating organizations"""
    pass

class OrganizationUpdate(BaseModel):
    """Schema for updating organizations"""
    # Basic info
    name: Optional[str] = None
    type: Optional[str] = None
    
    # Funding ecosystem role
    role: Optional[str] = None
    provider_type: Optional[str] = None
    recipient_type: Optional[str] = None
    startup_stage: Optional[str] = None
    funding_model: Optional[str] = None
    
    # Location and contact
    country: Optional[str] = None
    website: Optional[HttpUrl] = None
    email: Optional[str] = None
    description: Optional[str] = None
    
    # Funding characteristics
    funding_capacity: Optional[str] = None
    focus_areas: Optional[str] = None
    
    # Status
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    """Schema for organization responses"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Helper fields for frontend
    is_provider: bool = False
    is_recipient: bool = False
    is_granting_agency: bool = False
    is_venture_capital: bool = False
    is_grantee: bool = False
    is_startup: bool = False
    
    class Config:
        from_attributes = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set helper fields based on role and types
        self.is_provider = self.role in ['provider', 'both']
        self.is_recipient = self.role in ['recipient', 'both']
        self.is_granting_agency = self.provider_type == 'granting_agency'
        self.is_venture_capital = self.provider_type == 'venture_capital'
        self.is_grantee = self.recipient_type == 'grantee'
        self.is_startup = self.recipient_type == 'startup'


class FundingRelationship(BaseModel):
    """Schema for funding relationship summary"""
    opportunity_id: int
    title: str
    amount: Optional[Decimal] = None
    funding_category: str
    provider_name: Optional[str] = None
    provider_type: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_type: Optional[str] = None
    startup_stage: Optional[str] = None


class OrganizationWithFundingResponse(OrganizationResponse):
    """Enhanced organization schema with funding relationship data"""
    # Funding relationships
    provided_funding_count: int = 0
    received_funding_count: int = 0
    
    # Latest funding relationships
    provided_funding: List[FundingRelationship] = []
    received_funding: List[FundingRelationship] = []
    
    class Config:
        from_attributes = True
