from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class AfricaIntelligenceItemBase(BaseModel):
    """Base schema for intelligence feed"""
    title: Optional[str] = None
    description: Optional[str] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    application_deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    eligibility_criteria: Optional[dict] = None
    ai_domains: Optional[dict] = None
    geographic_scopes: Optional[dict] = None
    funding_type_id: Optional[int] = None
    provider_organization_id: Optional[int] = None
    recipient_organization_id: Optional[int] = None
    grant_reporting_requirements: Optional[str] = None
    grant_duration_months: Optional[int] = None
    grant_renewable: Optional[bool] = None
    equity_percentage: Optional[float] = None
    valuation_cap: Optional[Decimal] = None
    interest_rate: Optional[float] = None
    expected_roi: Optional[float] = None
    status: Optional[str] = None
    additional_resources: Optional[dict] = None
    equity_focus_details: Optional[dict] = None
    women_focus: Optional[bool] = None
    underserved_focus: Optional[bool] = None
    youth_focus: Optional[bool] = None
    funding_type: Optional[str] = None
    funding_amount: Optional[str] = None
    application_process: Optional[str] = None
    contact_information: Optional[str] = None
    additional_notes: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    collected_at: Optional[datetime] = None
    keywords: Optional[dict] = None
    content_category: Optional[str] = 'general'
    relevance_score: Optional[Decimal] = 0.5
    ai_extracted: Optional[bool] = False
    geographic_focus: Optional[str] = None
    sector_tags: Optional[List[str]] = None


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
    ai_domains: Optional[List[AIDomainBase]] = None
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
    items: List[AfricaIntelligenceItemBase]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class OrganizationBase(BaseModel):
    """Enhanced base schema for organizations"""
    id: int
    name: str
    type: str
    
    # Enhanced organization role classification
    role: str = "provider"  # provider, recipient, both
    provider_type: Optional[str] = None  # granting_agency, venture_capital, angel_investor, accelerator, government, foundation
    recipient_type: Optional[str] = None  # grantee, startup, research_institution, non_profit, sme, individual
    
    # Helper fields for frontend
    is_granting_agency: bool = False
    is_venture_capital: bool = False
    is_government: bool = False
    is_foundation: bool = False
    is_grantee: bool = False
    is_startup: bool = False
    is_research_institution: bool = False
    
    # Enhanced basic information
    country: Optional[str] = None
    region: Optional[str] = None
    website: Optional[HttpUrl] = None
    focus_areas: Optional[List[str]] = []
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set helper fields
        self.is_granting_agency = self.provider_type == "granting_agency"
        self.is_venture_capital = self.provider_type == "venture_capital"
        self.is_government = self.provider_type == "government"
        self.is_foundation = self.provider_type == "foundation"
        self.is_grantee = self.recipient_type == "grantee"
        self.is_startup = self.recipient_type == "startup"
        self.is_research_institution = self.recipient_type == "research_institution"

class AIDomainBase(BaseModel):
    """Enhanced base schema for AI domains"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None  # 'technical', 'application', 'sector'
    maturity_level: Optional[str] = None  # 'emerging', 'developing', 'mature'

class FundingCategoryBase(BaseModel):
    """Enhanced base schema for funding categories"""
    id: int
    name: str
    description: Optional[str] = None
    typical_amount_range: Optional[str] = None
    typical_duration: Optional[str] = None

class FundingTypeBase(BaseModel):
    """Enhanced base schema for funding types"""
    id: int
    name: str
    description: Optional[str] = None
    category: str  # 'grant', 'investment', 'prize', 'loan', 'other'
    requires_equity: bool = False
    requires_repayment: bool = False
    typical_amount_range: Optional[str] = None
    typical_duration: Optional[str] = None
    application_complexity: Optional[str] = None  # 'low', 'medium', 'high', 'very_high'
    success_rate: Optional[float] = None  # Estimated success rate 0-1

class AfricaIntelligenceItemResponse(AfricaIntelligenceItemBase):
    """Enhanced schema for intelligence item responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    
    # Legacy organization relationship
    source_organization: Optional[OrganizationBase] = None
    
    # Enhanced differentiated organization relationships
    provider_organization: Optional[OrganizationBase] = None
    recipient_organization: Optional[OrganizationBase] = None
    
    # Enhanced helper properties for organization types
    provider_is_granting_agency: bool = False
    provider_is_venture_capital: bool = False
    provider_is_government: bool = False
    provider_is_foundation: bool = False
    recipient_is_grantee: bool = False
    recipient_is_startup: bool = False
    recipient_is_research_institution: bool = False
    
    # Enhanced related entities
    ai_domains: Optional[List[AIDomainBase]] = None
    funding_type: Optional[FundingTypeBase] = None
    
    # Enhanced type-specific data
    grant_specific: Optional[GrantFundingSpecific] = None
    investment_specific: Optional[InvestmentFundingSpecific] = None
    prize_specific: Optional[GrantFundingSpecific] = None
    is_grant: bool = False
    is_investment: bool = False
    is_prize: bool = False
    funding_category: str = "other"
    
    # Enhanced metadata
    urgency_level: Optional[str] = None  # 'urgent', 'moderate', 'low', 'expired'
    days_until_deadline: Optional[int] = None
    is_deadline_approaching: bool = False
    
    # Enhanced targeting indicators
    suitable_for_startups: bool = False
    suitable_for_researchers: bool = False
    suitable_for_smes: bool = False
    suitable_for_individuals: bool = False
    
    model_config = {
        "from_attributes": True
    }

class AfricaIntelligenceItemList(BaseModel):
    """Enhanced schema for paginated intelligence item lists"""
    items: List[AfricaIntelligenceItemResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
    
    # Enhanced filtering metadata
    filters_applied: Optional[dict] = None
    total_funding_amount: Optional[Decimal] = None  # Sum of all funding in results
    funding_type_breakdown: Optional[dict] = None  # Count by funding type
    geographic_breakdown: Optional[dict] = None  # Count by geography
    deadline_urgency_breakdown: Optional[dict] = None  # Count by urgency level

# Enhanced ETL and data collection schemas
class ETLJobBase(BaseModel):
    """Schema for ETL job tracking"""
    id: int
    job_type: str  # 'rss_feed', 'web_scraping', 'api_fetch', 'manual_entry'
    status: str  # 'pending', 'running', 'completed', 'failed'
    source_name: str
    source_url: Optional[str] = None
    
    # Enhanced job metrics
    items_discovered: int = 0
    items_processed: int = 0
    items_created: int = 0
    items_updated: int = 0
    items_failed: int = 0
    
    # Enhanced error tracking
    error_log: Optional[List[str]] = []
    validation_errors: Optional[List[str]] = []
    data_quality_score: Optional[float] = None  # 0-1 score
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

class DataQualityReport(BaseModel):
    """Schema for data quality reporting"""
    total_opportunities: int
    complete_opportunities: int  # Have all required fields
    incomplete_opportunities: int
    
    # Enhanced quality metrics
    financial_data_completeness: float  # 0-1
    contact_data_completeness: float
    deadline_data_completeness: float
    geographic_data_completeness: float
    
    # Data consistency checks
    currency_consistency_score: float
    date_format_consistency_score: float
    organization_name_consistency_score: float
    
    # Enhanced validation results
    validation_errors_by_type: dict
    data_freshness_score: float  # How recent is the data
    
    generated_at: datetime

class SearchFilters(BaseModel):
    """Enhanced schema for search filtering"""
    # Financial filters
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    funding_types: Optional[List[str]] = None
    currencies: Optional[List[str]] = None
    
    # Geographic filters
    countries: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    
    # Temporal filters
    deadline_after: Optional[datetime] = None
    deadline_before: Optional[datetime] = None
    announced_after: Optional[datetime] = None
    announced_before: Optional[datetime] = None
    urgency_levels: Optional[List[str]] = None
    
    # Process filters
    application_deadline_types: Optional[List[str]] = None
    requires_registration: Optional[bool] = None
    collaboration_required: Optional[bool] = None
    
    # Targeting filters
    target_audiences: Optional[List[str]] = None
    ai_subsectors: Optional[List[str]] = None
    development_stages: Optional[List[str]] = None
    gender_focused: Optional[bool] = None
    youth_focused: Optional[bool] = None
    
    # Organization filters
    provider_types: Optional[List[str]] = None
    recipient_types: Optional[List[str]] = None
    
    # Status filters
    is_active: Optional[bool] = None
    is_open: Optional[bool] = None
    
    # Enhanced search options
    sort_by: str = "deadline"  # 'deadline', 'amount', 'relevance', 'created_at'
    sort_order: str = "asc"  # 'asc', 'desc'
    include_expired: bool = False
    
class SearchResponse(BaseModel):
    """Enhanced schema for search responses"""
    results: AfricaIntelligenceItemList
    filters_applied: SearchFilters
    search_metadata: dict
    suggestions: Optional[List[str]] = None  # Search suggestions
    related_opportunities: Optional[List[AfricaIntelligenceItemResponse]] = None

# Funding Opportunity Card Schema
class FundingAnnouncementCardResponse(AfricaIntelligenceItemResponse):
    """Schema for FundingAnnouncementCard component with all required fields"""
    # Core fields
    organization: str
    is_active: bool = True
    is_open: bool = True
    sector: str = "Other"
    country: str = "Multiple"
    region: Optional[str] = None
    eligibility_criteria: List[str] = []
    details_url: str
    requires_registration: bool = False
    tags: List[str] = []
    
    # Enhanced financial information
    total_funding_pool: Optional[float] = None
    funding_type: str = "per_project_range"  # total_pool, per_project_exact, per_project_range
    min_amount_per_project: Optional[float] = None
    max_amount_per_project: Optional[float] = None
    exact_amount_per_project: Optional[float] = None
    estimated_project_count: Optional[int] = None
    project_count_range: Optional[dict] = None
    
    # Application & process information
    application_process: Optional[str] = None
    selection_criteria: List[str] = []
    application_deadline_type: str = "fixed"  # rolling, fixed, multiple_rounds
    announcement_date: Optional[datetime] = None
    funding_start_date: Optional[datetime] = None
    project_duration: Optional[str] = None
    reporting_requirements: List[str] = []
    
    # Targeting & focus
    target_audience: List[str] = []
    ai_subsectors: List[str] = []
    development_stage: List[str] = []
    collaboration_required: bool = False
    gender_focused: bool = False
    youth_focused: bool = False
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('is_active', pre=True, always=True)
    def set_is_active(cls, v, values):
        return values.get('status', 'open').lower() == 'open'
    
    @validator('is_open', pre=True, always=True)
    def set_is_open(cls, v, values):
        deadline = values.get('deadline')
        if not deadline:
            return True
        from datetime import datetime
        return deadline >= datetime.now().date()
    
    @validator('sector', pre=True, always=True)
    def set_sector(cls, v, values):
        if v:
            return v
        if values.get('ai_domains') and len(values['ai_domains']) > 0:
            return values['ai_domains'][0].name
        return "Other"
    
    @validator('country', pre=True, always=True)
    def set_country(cls, v, values):
        if v:
            return v
        if values.get('geographical_scopes') and len(values['geographical_scopes']) > 0:
            return values['geographical_scopes'][0].split(',')[0]
        return "Multiple"
    
    @validator('eligibility_criteria', pre=True, always=True)
    def set_eligibility_criteria(cls, v, values):
        if v:
            return v if isinstance(v, list) else [v]
        return values.get('selection_criteria', [])
    
    @validator('tags', pre=True, always=True)
    def generate_tags(cls, v, values):
        """Generate tags based on opportunity properties"""
        tags = set()
        
        # Add funding type tags
        funding_type = values.get('funding_type')
        if funding_type:
            tags.add(funding_type.replace('_', ' ').title())
        
        # Add funding category tags
        funding_category = values.get('funding_category', '').lower()
        if funding_category:
            tags.add(funding_category.title())
        
        # Add AI domain tags
        for domain in values.get('ai_domains', []):
            if hasattr(domain, 'name') and domain.name:
                tags.add(domain.name)
        
        # Add target audience tags
        for audience in values.get('target_audience', []):
            if audience:
                tags.add(audience.replace('_', ' ').title())
        
        # Add special focus tags
        if values.get('gender_focused'):
            tags.add('Women Focused')
        if values.get('youth_focused'):
            tags.add('Youth Focused')
        if values.get('collaboration_required'):
            tags.add('Collaboration Required')
        
        # Add deadline urgency tags
        deadline = values.get('deadline')
        if deadline:
            from datetime import datetime
            days_left = (deadline - datetime.now().date()).days
            if days_left < 0:
                tags.add('Expired')
            elif days_left <= 7:
                tags.add('Deadline Soon')
            elif days_left <= 30:
                tags.add('Upcoming Deadline')
        
        # Add any existing tags
        if v and isinstance(v, list):
            tags.update(v)
        
        return list(tags)

# Enhanced analytics schemas
class FundingAnalytics(BaseModel):
    """Schema for funding analytics"""
    total_opportunities: int
    total_funding_amount: Decimal
    average_funding_amount: Decimal
    
    # Enhanced breakdowns
    funding_by_type: dict
    funding_by_geography: dict
    funding_by_sector: dict
    funding_by_month: dict
    
    # Enhanced trends
    growth_rate: float  # Month over month
    seasonal_patterns: dict
    success_rate_by_type: dict
    
    # Enhanced insights
    top_funders: List[dict]
    emerging_sectors: List[str]
    underserved_regions: List[str]
    
    generated_at: datetime
    period_start: datetime
    period_end: datetime