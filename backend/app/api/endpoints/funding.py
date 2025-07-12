from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import FundingOpportunity
from app.schemas.funding import FundingOpportunityResponse, FundingOpportunityCreate

router = APIRouter()

@router.get("/", response_model=List[FundingOpportunityResponse])
async def get_funding_opportunities(
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
    db: Session = Depends(get_db)
):
    """Get funding opportunities with optional filtering"""
    query = db.query(FundingOpportunity)
    
    # Apply filters
    if status:
        query = query.filter(FundingOpportunity.status == status)
    if min_amount:
        query = query.filter(FundingOpportunity.amount_usd >= min_amount)
    if max_amount:
        query = query.filter(FundingOpportunity.amount_usd <= max_amount)
    if deadline_after:
        query = query.filter(FundingOpportunity.deadline >= deadline_after)
    if deadline_before:
        query = query.filter(FundingOpportunity.deadline <= deadline_before)
    if organization_id:
        query = query.filter(FundingOpportunity.source_organization_id == organization_id)
    
    # Execute query with pagination
    opportunities = query.offset(skip).limit(limit).all()
    return opportunities

@router.get("/{opportunity_id}", response_model=FundingOpportunityResponse)
async def get_funding_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific funding opportunity by ID"""
    opportunity = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    
    return opportunity

@router.post("/", response_model=FundingOpportunityResponse)
async def create_funding_opportunity(
    opportunity: FundingOpportunityCreate,
    db: Session = Depends(get_db)
):
    """Create a new funding opportunity"""
    db_opportunity = FundingOpportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@router.get("/search/", response_model=List[FundingOpportunityResponse])
async def search_funding_opportunities(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search funding opportunities by title or description"""
    search_filter = f"%{q}%"
    opportunities = db.query(FundingOpportunity).filter(
        (FundingOpportunity.title.ilike(search_filter)) |
        (FundingOpportunity.description.ilike(search_filter))
    ).limit(limit).all()
    
    return opportunities
