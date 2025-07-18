from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class AfricaIntelligenceItemBase(BaseModel):
    """Base schema for intelligence feed"""
    title: str
    description: Optional[str] = None
    # Funding amount fields
    amount: Optional[Decimal] = None  # Legacy compatibility
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    amount_exact: Optional[Decimal] = None
    currency: str = "USD"
    amount_usd: Optional[Decimal] = None
    # Timing fields
    deadline: Optional[datetime] = None
    announcement_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    status: str = "active"
    # Contact and general info
    source_url: Optional[HttpUrl] = None
    application_url: Optional[HttpUrl] = None
    contact_info: Optional[str] = None
    geographical_scope: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    application_deadline: Optional[datetime] = None
    max_funding_period_months: Optional[int] = None


class GrantFundingSpecific(BaseModel):
    """Grant-specific funding fields"""
    reporting_requirements: Optional[str] = None
    grant_duration_months: Optional[int] = None
    renewable: bool = False
    no_strings_attached: Optional[bool] = None
    project_based: bool = True


class InvestmentFundingSpecific(BaseModel):
    """Investment-specific funding fields"""
    equity_percentage: Optional[float] = None
    valuation_cap: Optional[Decimal] = None
    interest_rate: Optional[float] = None
    repayment_terms: Optional[str] = None
    investor_rights: Optional[str] = None
    post_investment_support: Optional[str] = None
    expected_roi: Optional[float] = None

class AfricaIntelligenceItemCreate(AfricaIntelligenceItemBase):
    """Schema for creating intelligence feed"""
    # Legacy organization relationship
    source_organization_id: Optional[int] = None 
    data_source_id: Optional[int] = None
    
    # New differentiated organization relationships
    provider_organization_id: Optional[int] = None
    recipient_organization_id: Optional[int] = None
    
    # Funding type classification
    funding_type_id: int  # Funding type ID is required
    
    # Optional type-specific fields
    grant_specific: Optional[GrantFundingSpecific] = None
    investment_specific: Optional[InvestmentFundingSpecific] = None
    
    @validator('investment_specific')
    def validate_investment_fields(cls, v, values):
        from app.models import FundingType
        # This would be checked in the API endpoint with a db query
        # Here we're just setting up the validation structure
        return v
    
    @validator('grant_specific')
    def validate_grant_fields(cls, v, values):
        from app.models import FundingType
        # This would be checked in the API endpoint with a db query
        # Here we're just setting up the validation structure
        return v

class AfricaIntelligenceItemUpdate(BaseModel):
    """Schema for updating intelligence feed"""
    title: Optional[str] = None
    description: Optional[str] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    amount_exact: Optional[Decimal] = None
    currency: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    contact_info: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    
    # Organization relationships
    provider_organization_id: Optional[int] = None
    recipient_organization_id: Optional[int] = None
    
    # Classification
    funding_type_id: Optional[int] = None
    
    # Type-specific fields
    grant_specific: Optional[GrantFundingSpecific] = None
    investment_specific: Optional[InvestmentFundingSpecific] = None


class OrganizationBase(BaseModel):
    """Base schema for organizations (for embedding in responses)"""
    id: int
    name: str
    type: str
    
    # Organization role classification
    role: str = "provider"  # provider, recipient, both
    provider_type: Optional[str] = None  # granting_agency, venture_capital, angel_investor, accelerator
    recipient_type: Optional[str] = None  # grantee, startup, research_institution, non_profit
    
    # Helper fields for frontend
    is_granting_agency: bool = False
    is_venture_capital: bool = False
    is_grantee: bool = False
    is_startup: bool = False
    
    # Basic information
    country: Optional[str] = None
    website: Optional[HttpUrl] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set helper fields
        self.is_granting_agency = self.provider_type == "granting_agency"
        self.is_venture_capital = self.provider_type == "venture_capital"
        self.is_grantee = self.recipient_type == "grantee"
        self.is_startup = self.recipient_type == "startup"

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

class FundingTypeBase(BaseModel):
    """Base schema for funding types (for embedding)"""
    id: int
    name: str
    description: Optional[str] = None
    category: str  # 'grant', 'investment', 'prize', 'other'
    requires_equity: bool = False
    requires_repayment: bool = False
    typical_amount_range: Optional[str] = None

class AfricaIntelligenceItemResponse(AfricaIntelligenceItemBase):
    """Schema for intelligence item responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    
    # Legacy organization relationship
    source_organization: Optional[OrganizationBase] = None
    
    # New differentiated organization relationships
    provider_organization: Optional[OrganizationBase] = None
    recipient_organization: Optional[OrganizationBase] = None
    
    # Helper properties for organization types
    provider_is_granting_agency: bool = False
    provider_is_venture_capital: bool = False
    recipient_is_grantee: bool = False
    recipient_is_startup: bool = False
    
    # Related entities
    ai_domains: List[AIDomainBase] = []
    funding_type: Optional[FundingTypeBase] = None
    
    # Type-specific data
    grant_specific: Optional[GrantFundingSpecific] = None
    investment_specific: Optional[InvestmentFundingSpecific] = None
    is_grant: bool = False
    is_investment: bool = False
    funding_category: str = "other"
    
    model_config = {
        "from_attributes": True
    }

class AfricaIntelligenceItemList(BaseModel):
    """Schema for paginated intelligence item lists"""
    items: List[AfricaIntelligenceItemResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
