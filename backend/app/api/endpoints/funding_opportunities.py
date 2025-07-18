from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import AfricaIntelligenceItem, Organization, AIDomain, FundingType, GeographicScope
from app.schemas.funding import (
    AfricaIntelligenceItemResponse, AfricaIntelligenceItemCreate, AfricaIntelligenceItemUpdate,
    GrantFundingSpecific, InvestmentFundingSpecific
)

router = APIRouter()

#
# Core Intelligence Item Endpoints (from funding.py)
#

@router.get("/", response_model=List[AfricaIntelligenceItemResponse])
async def get_africa_intelligence_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    currency: Optional[str] = Query("USD"),
    deadline_after: Optional[datetime] = Query(None),
    deadline_before: Optional[datetime] = Query(None),
    organization_id: Optional[int] = Query(None),
    ai_domain: Optional[str] = Query(None),
    funding_type: Optional[str] = Query(None, description="Filter by funding type category: 'grant', 'investment', 'prize', or 'other'"),
    requires_equity: Optional[bool] = Query(None, description="Filter for opportunities requiring equity"),
    db: AsyncSession = Depends(get_db)
):
    """Get intelligence feed with optional filtering"""
    # Check if db is a Supabase client or SQLAlchemy session
    if hasattr(db, 'table'):  # Supabase client
        query = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*)')

        # Apply filters
        if status:
            query = query.filter('status', 'eq', status)
        if min_amount:
            query = query.or_(f'amount_exact.gte.{min_amount},amount_min.gte.{min_amount}')
        if max_amount:
            query = query.or_(f'amount_exact.lte.{max_amount},amount_max.lte.{max_amount}')
        if deadline_after:
            query = query.filter('deadline', 'gte', deadline_after.isoformat())
        if deadline_before:
            query = query.filter('deadline', 'lte', deadline_before.isoformat())
        if organization_id:
            query = query.filter('organization_id', 'eq', organization_id)
        if funding_type:
            query = query.filter('funding_types.category', 'eq', funding_type)
        if requires_equity is not None:
            query = query.filter('funding_types.requires_equity', 'eq', requires_equity)

        # Execute query with pagination
        response = query.range(skip, skip + limit - 1).execute()
        opportunities = response.data
    else:  # SQLAlchemy session
        query = db.query(AfricaIntelligenceItem).join(AfricaIntelligenceItem.type)
    
        # Apply filters
        if status:
            query = query.filter(AfricaIntelligenceItem.status == status)
        if min_amount:
            # Use the new numeric amount fields
            query = query.filter(
                (AfricaIntelligenceItem.amount_exact >= min_amount) |
                (AfricaIntelligenceItem.amount_min >= min_amount)
            )
        if max_amount:
            # Use the new numeric amount fields
            query = query.filter(
                (AfricaIntelligenceItem.amount_exact <= max_amount) |
                (AfricaIntelligenceItem.amount_max <= max_amount) |
                (AfricaIntelligenceItem.amount_max == None, AfricaIntelligenceItem.amount_exact <= max_amount)
            )
        if deadline_after:
            query = query.filter(AfricaIntelligenceItem.deadline >= deadline_after)
        if deadline_before:
            query = query.filter(AfricaIntelligenceItem.deadline <= deadline_before)
        if organization_id:
            query = query.filter(AfricaIntelligenceItem.organization_id == organization_id)
        if funding_type:
            # Filter by the funding type category
            query = query.filter(FundingType.category == funding_type)
        if requires_equity is not None:
            query = query.filter(FundingType.requires_equity == requires_equity)
    
        # Execute query with pagination
        opportunities = query.offset(skip).limit(limit).all()
    
    # Prepare responses with type-specific data
    results = []
    for opp in opportunities:
        response = AfricaIntelligenceItemResponse.from_orm(opp)
        
        # Add type-specific data
        response.is_grant = opp.is_grant
        response.is_investment = opp.is_investment
        response.funding_category = opp.funding_category
        
        if opp.is_grant and opp.grant_properties:
            response.grant_specific = GrantFundingSpecific(**opp.grant_properties)
        
        if opp.is_investment and opp.investment_properties:
            response.investment_specific = InvestmentFundingSpecific(**opp.investment_properties)
        
        results.append(response)
    
    return results


@router.get("/{opportunity_id}", response_model=AfricaIntelligenceItemResponse)
async def get_intelligence_item(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific intelligence item by ID"""
    opportunity = db.query(AfricaIntelligenceItem).filter(AfricaIntelligenceItem.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    
    # Create response with type-specific data
    response = AfricaIntelligenceItemResponse.from_orm(opportunity)
    
    # Add type-specific data
    response.is_grant = opportunity.is_grant
    response.is_investment = opportunity.is_investment
    response.funding_category = opportunity.funding_category
    
    if opportunity.is_grant and opportunity.grant_properties:
        response.grant_specific = GrantFundingSpecific(**opportunity.grant_properties)
    
    if opportunity.is_investment and opportunity.investment_properties:
        response.investment_specific = InvestmentFundingSpecific(**opportunity.investment_properties)
    
    return response


@router.post("/", response_model=AfricaIntelligenceItemResponse)
async def create_intelligence_item(
    opportunity: AfricaIntelligenceItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new intelligence item"""
    # Validate the funding type exists and get its category
    funding_type = db.query(FundingType).filter(FundingType.id == opportunity.funding_type_id).first()
    if not funding_type:
        raise HTTPException(status_code=404, detail="Funding type not found")
    
    # Prepare base opportunity data
    opportunity_data = opportunity.dict(exclude={"grant_specific", "investment_specific"})
    db_opportunity = AfricaIntelligenceItem(**opportunity_data)
    
    # Add type-specific fields based on funding type category
    if funding_type.category == 'grant' and opportunity.grant_specific:
        grant_data = opportunity.grant_specific.dict()
        for key, value in grant_data.items():
            if value is not None:  # Only set non-None values
                setattr(db_opportunity, key, value)
    
    if funding_type.category == 'investment' and opportunity.investment_specific:
        investment_data = opportunity.investment_specific.dict()
        for key, value in investment_data.items():
            if value is not None:  # Only set non-None values
                setattr(db_opportunity, key, value)
    
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    
    # Create response with type-specific data
    response = AfricaIntelligenceItemResponse.from_orm(db_opportunity)
    response.is_grant = db_opportunity.is_grant
    response.is_investment = db_opportunity.is_investment
    response.funding_category = db_opportunity.funding_category
    
    if db_opportunity.is_grant and db_opportunity.grant_properties:
        response.grant_specific = GrantFundingSpecific(**db_opportunity.grant_properties)
    
    if db_opportunity.is_investment and db_opportunity.investment_properties:
        response.investment_specific = InvestmentFundingSpecific(**db_opportunity.investment_properties)
    
    return response


@router.get("/grants/", response_model=List[AfricaIntelligenceItemResponse])
async def get_grants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    renewable: Optional[bool] = Query(None, description="Filter for renewable grants"),
    project_based: Optional[bool] = Query(None, description="Filter for project-based grants"),
    min_duration: Optional[int] = Query(None, description="Minimum grant duration in months"),
    db: AsyncSession = Depends(get_db)
):
    """Get grant intelligence feed with specialized filters"""
    query = db.query(AfricaIntelligenceItem).join(AfricaIntelligenceItem.type)
    
    # Filter by grant type
    query = query.filter(FundingType.category == 'grant')
    
    # Apply specialized grant filters
    if renewable is not None:
        query = query.filter(AfricaIntelligenceItem.renewable == renewable)
    if project_based is not None:
        query = query.filter(AfricaIntelligenceItem.project_based == project_based)
    if min_duration is not None:
        query = query.filter(AfricaIntelligenceItem.grant_duration_months >= min_duration)
    
    # Execute query with pagination
    grants = query.offset(skip).limit(limit).all()
    
    # Prepare responses with type-specific data
    results = []
    for grant in grants:
        response = AfricaIntelligenceItemResponse.from_orm(grant)
        response.is_grant = True
        response.is_investment = False
        response.funding_category = 'grant'
        
        if grant.grant_properties:
            response.grant_specific = GrantFundingSpecific(**grant.grant_properties)
        
        results.append(response)
    
    return results


@router.get("/investments/", response_model=List[AfricaIntelligenceItemResponse])
async def get_investments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    max_equity: Optional[float] = Query(None, description="Maximum equity percentage required"),
    min_valuation_cap: Optional[float] = Query(None, description="Minimum valuation cap"),
    db: AsyncSession = Depends(get_db)
):
    """Get investment intelligence feed with specialized filters"""
    query = db.query(AfricaIntelligenceItem).join(AfricaIntelligenceItem.type)
    
    # Filter by investment type
    query = query.filter(FundingType.category == 'investment')
    
    # Apply specialized investment filters
    if max_equity is not None:
        query = query.filter(AfricaIntelligenceItem.equity_percentage <= max_equity)
    if min_valuation_cap is not None:
        query = query.filter(AfricaIntelligenceItem.valuation_cap >= min_valuation_cap)
    
    # Execute query with pagination
    investments = query.offset(skip).limit(limit).all()
    
    # Prepare responses with type-specific data
    results = []
    for investment in investments:
        response = AfricaIntelligenceItemResponse.from_orm(investment)
        response.is_grant = False
        response.is_investment = True
        response.funding_category = 'investment'
        
        if investment.investment_properties:
            response.investment_specific = InvestmentFundingSpecific(**investment.investment_properties)
        
        results.append(response)
    
    return results


@router.get("/search/", response_model=List[AfricaIntelligenceItemResponse])
async def search_africa_intelligence_feed(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    funding_type: Optional[str] = Query(None, description="Limit search to specific funding type: 'grant', 'investment', etc."),
    db: AsyncSession = Depends(get_db)
):
    """Search intelligence feed by title or description"""
    search_term = f"%{q}%"
    query = db.query(AfricaIntelligenceItem)
    
    # Apply search filter
    query = query.filter(
        AfricaIntelligenceItem.title.ilike(search_term) | 
        AfricaIntelligenceItem.description.ilike(search_term)
    )
    
    # Apply funding type filter if specified
    if funding_type:
        query = query.join(AfricaIntelligenceItem.type)
        query = query.filter(FundingType.category == funding_type)
    
    opportunities = query.limit(limit).all()
    
    # Prepare responses with type-specific data
    results = []
    for opp in opportunities:
        response = AfricaIntelligenceItemResponse.from_orm(opp)
        
        response.is_grant = opp.is_grant
        response.is_investment = opp.is_investment
        response.funding_category = opp.funding_category
        
        if opp.is_grant and opp.grant_properties:
            response.grant_specific = GrantFundingSpecific(**opp.grant_properties)
        
        if opp.is_investment and opp.investment_properties:
            response.investment_specific = InvestmentFundingSpecific(**opp.investment_properties)
        
        results.append(response)
    
    return results


#
# Stage Matching Endpoints (from opportunities.py)
#

@router.get("/stage-matching")
async def get_stage_matched_opportunities(
    stage: str = Query(None, description="Funding stage to match (e.g., 'Pre-seed', 'Seed', 'Series A')"),
    domain: str = Query(None, description="AI domain to filter by"),
    country: str = Query(None, description="Country to filter by"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get intelligence feed matched to a specific stage and optionally filtered by domain and country.
    This endpoint helps founders find opportunities appropriate for their current funding stage.
    """
    # In a real implementation, this would query the database based on the parameters
    # For demo purposes, we'll return representative stage-appropriate opportunities
    
    stages = ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"]
    if stage and stage not in stages:
        return {"error": f"Invalid stage. Must be one of: {', '.join(stages)}"}
    
    # Default to seed if no stage specified
    current_stage = stage or "Seed"
    
    # Match opportunities based on stage
    if current_stage == "Pre-seed":
        opportunities = [
            {
                "id": 101,
                "title": "African Innovation Challenge",
                "organization": "African Development Bank",
                "funding_amount": "Up to $25,000",
                "deadline": "2024-08-15",
                "stage_appropriate": True,
                "requirements": "Idea stage, proof of concept",
                "success_rate": "15%",
                "application_complexity": "Low"
            },
            {
                "id": 102,
                "title": "AI for Good Incubator",
                "organization": "Google for Startups Africa",
                "funding_amount": "Up to $15,000",
                "deadline": "2024-09-01",
                "stage_appropriate": True,
                "requirements": "MVP or proof of concept",
                "success_rate": "8%",
                "application_complexity": "Medium"
            },
            {
                "id": 103,
                "title": "Women in AI Entrepreneurship Grant",
                "organization": "UN Women",
                "funding_amount": "Up to $20,000",
                "deadline": "2024-10-30",
                "stage_appropriate": True,
                "requirements": "Female-led ventures, idea stage acceptable",
                "success_rate": "12%",
                "application_complexity": "Medium"
            }
        ]
    elif current_stage == "Seed":
        opportunities = [
            {
                "id": 201,
                "title": "Africa AI Accelerator Program",
                "organization": "Microsoft 4Afrika",
                "funding_amount": "$50,000 - $150,000",
                "deadline": "2024-08-30",
                "stage_appropriate": True,
                "requirements": "Working product, some traction",
                "success_rate": "10%",
                "application_complexity": "High"
            },
            {
                "id": 202,
                "title": "Tech for Climate Action Fund",
                "organization": "World Bank Climate Initiative",
                "funding_amount": "Up to $100,000",
                "deadline": "2024-09-15",
                "stage_appropriate": True,
                "requirements": "Product with climate impact potential",
                "success_rate": "7%",
                "application_complexity": "Very High"
            },
            {
                "id": 203,
                "title": "Catalytic Africa Fund",
                "organization": "AfriLabs",
                "funding_amount": "$75,000 - $200,000",
                "deadline": "2024-11-01",
                "stage_appropriate": True,
                "requirements": "Product with early traction, revenue preferred",
                "success_rate": "5%",
                "application_complexity": "High"
            }
        ]
    elif current_stage == "Series A":
        opportunities = [
            {
                "id": 301,
                "title": "Africa Growth Fund",
                "organization": "IFC Ventures",
                "funding_amount": "$500,000 - $2M",
                "deadline": "2024-10-15",
                "stage_appropriate": True,
                "requirements": "Proven revenue model, market traction",
                "success_rate": "3%",
                "application_complexity": "Very High"
            },
            {
                "id": 302,
                "title": "AI for Development Impact Fund",
                "organization": "Bill & Melinda Gates Foundation",
                "funding_amount": "$750,000 - $1.5M",
                "deadline": "2024-09-30",
                "stage_appropriate": True,
                "requirements": "Clear impact metrics, scaling plan",
                "success_rate": "2%",
                "application_complexity": "Very High"
            }
        ]
    elif current_stage == "Series B":
        opportunities = [
            {
                "id": 401,
                "title": "Africa Scale-Up Fund",
                "organization": "Softbank Africa",
                "funding_amount": "$3M - $10M",
                "deadline": "2024-12-01",
                "stage_appropriate": True,
                "requirements": "Significant revenue, expanding market share",
                "success_rate": "1.5%",
                "application_complexity": "Extremely High"
            }
        ]
    else:  # Series C+
        opportunities = [
            {
                "id": 501,
                "title": "African Growth Champions",
                "organization": "Africa Development Bank",
                "funding_amount": "$15M+",
                "deadline": "2024-11-15",
                "stage_appropriate": True,
                "requirements": "Market leader, expansion plans",
                "success_rate": "1%",
                "application_complexity": "Extremely High"
            }
        ]
    
    # Apply domain filter if specified
    if domain:
        opportunities = [opp for opp in opportunities if domain.lower() in opp["title"].lower()]
    
    # Apply country filter if specified
    if country:
        # This is simplified - in a real implementation, we'd have country data
        # Here we're just simulating country filtering
        opportunities = opportunities[:max(1, len(opportunities) - 1)]
    
    # Add guidance based on stage
    if current_stage == "Pre-seed":
        guidance = {
            "focus_areas": ["Clear problem statement", "Unique value proposition", "Early prototype"],
            "common_pitfalls": ["Lack of market validation", "Unrealistic funding expectations", "Over-engineering MVP"],
            "success_tips": ["Focus on problem-solution fit", "Build minimal viable product", "Network with angel investors"]
        }
    elif current_stage == "Seed":
        guidance = {
            "focus_areas": ["User traction metrics", "Clear business model", "Early revenue indicators"],
            "common_pitfalls": ["Scaling too early", "Ignoring unit economics", "Weak go-to-market strategy"],
            "success_tips": ["Demonstrate product-market fit", "Build key partnerships", "Show clear growth metrics"]
        }
    elif current_stage == "Series A":
        guidance = {
            "focus_areas": ["Revenue growth", "Scalable processes", "Market expansion plans"],
            "common_pitfalls": ["Unproven unit economics", "Weak management team", "Unclear differentiation"],
            "success_tips": ["Focus on consistent revenue", "Build strong team", "Clear path to profitability"]
        }
    else:  # Series B+
        guidance = {
            "focus_areas": ["Profitability path", "International expansion", "Industry leadership"],
            "common_pitfalls": ["Failure to adapt to market changes", "Overlooking competition", "Poor capital allocation"],
            "success_tips": ["Focus on sustainable growth", "Consider strategic partnerships", "Build for exit or IPO"]
        }
    
    return {
        "stage": current_stage,
        "opportunities": opportunities,
        "total_matched": len(opportunities),
        "guidance": guidance,
        "timestamp": datetime.now().isoformat()
    }


#
# Additional Integrated Endpoints
#

@router.get("/geographic-availability")
async def get_geographic_availability(db: AsyncSession = Depends(get_db)):
    """
    Get intelligence feed availability by geographic region
    This endpoint helps users understand which regions have available funding
    """
    # In a real implementation, this would query intelligence feed by geography
    # For now, we'll return a representative response
    
    geography_data = [
        {"region": "East Africa", "opportunity_count": 23, "total_funding": 5400000},
        {"region": "West Africa", "opportunity_count": 35, "total_funding": 8700000},
        {"region": "Southern Africa", "opportunity_count": 19, "total_funding": 6300000},
        {"region": "North Africa", "opportunity_count": 12, "total_funding": 3100000},
        {"region": "Central Africa", "opportunity_count": 7, "total_funding": 1500000}
    ]
    
    return {
        "geographic_availability": geography_data,
        "total_opportunities": sum(item["opportunity_count"] for item in geography_data),
        "total_funding": sum(item["total_funding"] for item in geography_data),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/domain-funding")
async def get_domain_funding(db: AsyncSession = Depends(get_db)):
    """
    Get intelligence feed by AI domain
    This endpoint helps users understand which AI domains receive the most funding
    """
    # In a real implementation, this would query intelligence feed by domain
    # For now, we'll return a representative response
    
    domain_data = [
        {"domain": "Healthcare", "opportunity_count": 18, "total_funding": 7200000},
        {"domain": "Agriculture", "opportunity_count": 15, "total_funding": 5800000},
        {"domain": "Education", "opportunity_count": 12, "total_funding": 3500000},
        {"domain": "Financial Services", "opportunity_count": 22, "total_funding": 8100000},
        {"domain": "Climate & Energy", "opportunity_count": 14, "total_funding": 4700000},
        {"domain": "Infrastructure", "opportunity_count": 8, "total_funding": 2900000},
        {"domain": "General AI", "opportunity_count": 7, "total_funding": 1800000}
    ]
    
    return {
        "domain_funding": domain_data,
        "total_opportunities": sum(item["opportunity_count"] for item in domain_data),
        "total_funding": sum(item["total_funding"] for item in domain_data),
        "timestamp": datetime.now().isoformat()
    }
