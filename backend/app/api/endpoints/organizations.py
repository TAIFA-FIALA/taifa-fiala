from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional

from app.core.database import get_db
from app.models import Organization
from app.schemas.organization import OrganizationResponse

router = APIRouter()

@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get organizations with optional filtering"""
    query = db.query(Organization)
    
    if type:
        query = query.filter(Organization.type == type)
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

@router.get("/countries", response_model=List[str])
async def get_unique_countries(db: Session = Depends(get_db)):
    """Get a list of unique countries from organizations"""
    countries = db.query(distinct(Organization.country)).filter(
        Organization.country != None
    ).order_by(Organization.country).all()
    return [country[0] for country in countries]