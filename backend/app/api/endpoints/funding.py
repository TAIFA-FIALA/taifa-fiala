from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import AfricaIntelligenceItem
from app.schemas.funding import AfricaIntelligenceItemResponse, AfricaIntelligenceItemCreate

router = APIRouter()

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
    db: Session = Depends(get_db)
):
    """Get intelligence feed with optional filtering"""
    query = db.query(AfricaIntelligenceItem)
    
    # Apply filters
    if status:
        query = query.filter(AfricaIntelligenceItem.status == status)
    if min_amount:
        query = query.filter(AfricaIntelligenceItem.amount_usd >= min_amount)
    if max_amount:
        query = query.filter(AfricaIntelligenceItem.amount_usd <= max_amount)
    if deadline_after:
        query = query.filter(AfricaIntelligenceItem.deadline >= deadline_after)
    if deadline_before:
        query = query.filter(AfricaIntelligenceItem.deadline <= deadline_before)
    if organization_id:
        query = query.filter(AfricaIntelligenceItem.source_organization_id == organization_id)
    
    # Execute query with pagination
    opportunities = query.offset(skip).limit(limit).all()
    return opportunities

@router.get("/{opportunity_id}", response_model=AfricaIntelligenceItemResponse)
async def get_intelligence_item(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific intelligence item by ID"""
    opportunity = db.query(AfricaIntelligenceItem).filter(
        AfricaIntelligenceItem.id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    
    return opportunity

@router.post("/", response_model=AfricaIntelligenceItemResponse)
async def create_intelligence_item(
    opportunity: AfricaIntelligenceItemCreate,
    db: Session = Depends(get_db)
):
    """Create a new intelligence item"""
    db_opportunity = AfricaIntelligenceItem(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@router.get("/search/", response_model=List[AfricaIntelligenceItemResponse])
async def search_africa_intelligence_feed(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search intelligence feed by title or description"""
    search_filter = f"%{q}%"
    opportunities = db.query(AfricaIntelligenceItem).filter(
        (AfricaIntelligenceItem.title.ilike(search_filter)) |
        (AfricaIntelligenceItem.description.ilike(search_filter))
    ).limit(limit).all()
    
    return opportunities
