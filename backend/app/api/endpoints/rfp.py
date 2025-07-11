from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models import RFP, Organization # Import Organization model
from app.schemas.rfp import RFPCreate, RFPResponse

router = APIRouter()

@router.post("/", response_model=RFPResponse, status_code=201)
async def create_rfp(
    rfp: RFPCreate,
    db: Session = Depends(get_db)
):
    """Create a new Request for Proposal (RFP)"""
    db_rfp = RFP(**rfp.model_dump())
    db.add(db_rfp)
    db.commit()
    db.refresh(db_rfp)
    return db_rfp

@router.get("/", response_model=Dict[str, Any]) # Changed response_model
async def get_rfps(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="Search keyword for title and description"),
    min_amount_usd: Optional[float] = Query(None, ge=0, description="Minimum funding amount in USD"),
    max_amount_usd: Optional[float] = Query(None, ge=0, description="Maximum funding amount in USD"),
    start_deadline: Optional[datetime] = Query(None, description="RFPs with deadline after this date"),
    end_deadline: Optional[datetime] = Query(None, description="RFPs with deadline before this date"),
    status: Optional[str] = Query(None, description="Filter by RFP status (e.g., open, closed, awarded)"),
    category: Optional[str] = Query(None, description="Filter by category (comma-separated for multiple)"),
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    country: Optional[str] = Query(None, description="Filter by the country of the issuing organization"),
    db: Session = Depends(get_db)
):
    """Get a list of RFPs with comprehensive filtering options"""
    query = db.query(RFP)

    if keyword:
        query = query.filter(
            (RFP.title.ilike(f"%{keyword}%")) |
            (RFP.description.ilike(f"%{keyword}%"))
        )
    if min_amount_usd:
        query = query.filter(RFP.amount_usd >= min_amount_usd)
    if max_amount_usd:
        query = query.filter(RFP.amount_usd <= max_amount_usd)
    if start_deadline:
        query = query.filter(RFP.deadline >= start_deadline)
    if end_deadline:
        query = query.filter(RFP.deadline <= end_deadline)
    if status:
        query = query.filter(RFP.status == status)
    if category:
        category_list = [c.strip() for c in category.split(',')]
        category_filters = [RFP.categories.ilike(f"%{c}%") for c in category_list]
        query = query.filter(or_(*category_filters))
    if organization_id:
        query = query.filter(RFP.organization_id == organization_id)
    if country:
        query = query.join(Organization).filter(Organization.country.ilike(f"%{country}%"))

    total_count = query.count()
    rfps = query.offset(skip).limit(limit).all()
    
    return {"rfps": rfps, "total_count": total_count}

@router.get("/{rfp_id}", response_model=RFPResponse)
async def get_rfp(
    rfp_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific RFP by ID"""
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return rfp