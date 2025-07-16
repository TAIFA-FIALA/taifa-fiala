from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import distinct, func, and_, or_
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.models import Organization, FundingOpportunity
from app.schemas.organization import OrganizationResponse, OrganizationWithFundingResponse
from app.schemas.funding import FundingOpportunityResponse

router = APIRouter()

@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None, description="Filter by organization type (foundation, government, corporation, etc.)"),
    role: Optional[str] = Query(None, description="Filter by role (provider, recipient, both)"),
    provider_type: Optional[str] = Query(None, description="Filter by provider type (granting_agency, venture_capital, etc.)"),
    recipient_type: Optional[str] = Query(None, description="Filter by recipient type (grantee, startup, etc.)"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """Get organizations with optional filtering including new role-based filters"""
    query = db.query(Organization)
    
    # Apply filters
    if type:
        query = query.filter(Organization.type == type)
    if role:
        query = query.filter(Organization.role == role)
    if provider_type:
        query = query.filter(Organization.provider_type == provider_type)
    if recipient_type:
        query = query.filter(Organization.recipient_type == recipient_type)
    if country:
        query = query.filter(Organization.country.ilike(f"%{country}%"))
    
    organizations = query.filter(Organization.is_active == True).offset(skip).limit(limit).all()
    return organizations

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific organization by ID"""
    organization = db.query(Organization).filter(
        Organization.id == organization_id,
        Organization.is_active == True
    ).first()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


@router.get("/{organization_id}/funding", response_model=OrganizationWithFundingResponse)
async def get_organization_funding(
    organization_id: int,
    limit_relationships: int = Query(5, ge=1, le=20, description="Number of funding relationships to return"),
    db: Session = Depends(get_db)
):
    """Get detailed funding information for an organization, including provided and received funding"""
    # Get the organization with eager loading of relationships
    organization = db.query(Organization).filter(
        Organization.id == organization_id,
        Organization.is_active == True
    ).first()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    # Create the response object
    response = OrganizationWithFundingResponse.from_orm(organization)
    
    # Get provided funding count and latest relationships
    if organization.role in ["provider", "both"]:
        # Count provided funding opportunities
        provided_count = db.query(func.count(FundingOpportunity.id)).filter(
            FundingOpportunity.provider_organization_id == organization_id
        ).scalar() or 0
        
        # Get the latest provided funding opportunities
        provided_funding = db.query(FundingOpportunity).filter(
            FundingOpportunity.provider_organization_id == organization_id
        ).order_by(FundingOpportunity.created_at.desc()).limit(limit_relationships).all()
        
        # Add to response
        response.provided_funding_count = provided_count
        
        # Convert to relationship objects
        for opp in provided_funding:
            recipient_name = None
            recipient_type = None
            startup_stage = None
            
            if opp.recipient_organization:
                recipient_name = opp.recipient_organization.name
                recipient_type = opp.recipient_organization.recipient_type
                startup_stage = opp.recipient_organization.startup_stage
                
            relationship = {
                "opportunity_id": opp.id,
                "title": opp.title,
                "amount": opp.amount_exact or opp.amount_min,
                "funding_category": opp.funding_category,
                "recipient_name": recipient_name,
                "recipient_type": recipient_type,
                "startup_stage": startup_stage
            }
            
            response.provided_funding.append(relationship)
    
    # Get received funding count and latest relationships
    if organization.role in ["recipient", "both"]:
        # Count received funding opportunities
        received_count = db.query(func.count(FundingOpportunity.id)).filter(
            FundingOpportunity.recipient_organization_id == organization_id
        ).scalar() or 0
        
        # Get the latest received funding opportunities
        received_funding = db.query(FundingOpportunity).filter(
            FundingOpportunity.recipient_organization_id == organization_id
        ).order_by(FundingOpportunity.created_at.desc()).limit(limit_relationships).all()
        
        # Add to response
        response.received_funding_count = received_count
        
        # Convert to relationship objects
        for opp in received_funding:
            provider_name = None
            provider_type = None
            
            if opp.provider_organization:
                provider_name = opp.provider_organization.name
                provider_type = opp.provider_organization.provider_type
                
            relationship = {
                "opportunity_id": opp.id,
                "title": opp.title,
                "amount": opp.amount_exact or opp.amount_min,
                "funding_category": opp.funding_category,
                "provider_name": provider_name,
                "provider_type": provider_type
            }
            
            response.received_funding.append(relationship)
    
    return response

@router.get("/countries", response_model=List[str])
async def get_unique_countries(db: Session = Depends(get_db)):
    """Get a list of unique countries from organizations"""
    countries = db.query(distinct(Organization.country)).filter(
        Organization.country != None
    ).order_by(Organization.country).all()
    return [country[0] for country in countries]


@router.get("/providers", response_model=List[OrganizationResponse])
async def get_funding_providers(
    provider_type: Optional[str] = Query(None, description="Filter by specific provider type (granting_agency, venture_capital, angel_investor, accelerator)"),
    min_funding_count: int = Query(0, ge=0, description="Minimum number of funding opportunities provided"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get organizations that provide funding (granting agencies and venture capital groups)"""
    query = db.query(Organization).filter(
        Organization.is_active == True,
        or_(
            Organization.role == "provider",
            Organization.role == "both"
        )
    )
    
    if provider_type:
        query = query.filter(Organization.provider_type == provider_type)
    
    if min_funding_count > 0:
        # Filter organizations that have provided at least min_funding_count opportunities
        query = query.join(Organization.provided_funding)\
            .group_by(Organization.id)\
            .having(func.count(FundingOpportunity.id) >= min_funding_count)
    
    providers = query.offset(skip).limit(limit).all()
    return providers


@router.get("/recipients", response_model=List[OrganizationResponse])
async def get_funding_recipients(
    recipient_type: Optional[str] = Query(None, description="Filter by specific recipient type (grantee, startup, research_institution, non_profit)"),
    startup_stage: Optional[str] = Query(None, description="Filter startups by stage (idea, seed, early, growth, mature)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get organizations that receive funding (grantees and startups)"""
    query = db.query(Organization).filter(
        Organization.is_active == True,
        or_(
            Organization.role == "recipient",
            Organization.role == "both"
        )
    )
    
    if recipient_type:
        query = query.filter(Organization.recipient_type == recipient_type)
    
    if startup_stage:
        query = query.filter(Organization.startup_stage == startup_stage)
    
    recipients = query.offset(skip).limit(limit).all()
    return recipients


@router.get("/funding-relationships", response_model=Dict[str, List[Dict[str, Any]]])
async def get_funding_relationships(
    provider_id: Optional[int] = Query(None, description="Filter by provider organization ID"),
    recipient_id: Optional[int] = Query(None, description="Filter by recipient organization ID"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get funding relationships between providers and recipients"""
    # Query funding opportunities with provider and recipient information
    query = db.query(FundingOpportunity)\
        .options(
            joinedload(FundingOpportunity.provider_organization),
            joinedload(FundingOpportunity.recipient_organization),
            joinedload(FundingOpportunity.type)
        )
    
    # Apply filters
    if provider_id:
        query = query.filter(FundingOpportunity.provider_organization_id == provider_id)
    if recipient_id:
        query = query.filter(FundingOpportunity.recipient_organization_id == recipient_id)
    
    # Get funding opportunities with relationships
    opportunities = query.filter(
        FundingOpportunity.provider_organization_id != None,
        FundingOpportunity.recipient_organization_id != None
    ).limit(limit).all()
    
    # Group by provider type
    relationships = {
        "granting_agencies": [],
        "venture_capital": [],
        "other_funding": []
    }
    
    for opp in opportunities:
        if not opp.provider_organization or not opp.recipient_organization:
            continue
            
        relationship = {
            "opportunity_id": opp.id,
            "title": opp.title,
            "amount": opp.amount_exact or opp.amount_min,
            "provider": {
                "id": opp.provider_organization.id,
                "name": opp.provider_organization.name,
                "provider_type": opp.provider_organization.provider_type
            },
            "recipient": {
                "id": opp.recipient_organization.id,
                "name": opp.recipient_organization.name,
                "recipient_type": opp.recipient_organization.recipient_type,
                "startup_stage": opp.recipient_organization.startup_stage
            },
            "funding_type": opp.funding_category
        }
        
        if opp.provider_organization.provider_type == "granting_agency":
            relationships["granting_agencies"].append(relationship)
        elif opp.provider_organization.provider_type == "venture_capital":
            relationships["venture_capital"].append(relationship)
        else:
            relationships["other_funding"].append(relationship)
    
    return relationships