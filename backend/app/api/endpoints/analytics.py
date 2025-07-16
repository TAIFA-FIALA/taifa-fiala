from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime

from app.core.database import get_db
from app.models import RFP, Organization

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get analytics summary for dashboard"""
    
    # 1. Number of active RFPs accepting applications
    active_rfps_count = db.query(RFP).filter(
        RFP.status == "open",
        RFP.deadline > datetime.now()
    ).count()

    # 2. Total number of unique funders accepting proposals
    unique_funders_count = db.query(distinct(RFP.organization_id)).filter(
        RFP.status == "open",
        RFP.deadline > datetime.now()
    ).count()

    # 3. Total value of all those applications if they are fully disbursed
    total_funding_value = db.query(func.sum(RFP.amount_usd)).filter(
        RFP.status == "open",
        RFP.deadline > datetime.now()
    ).scalar()

    return {
        "active_rfps_count": active_rfps_count,
        "unique_funders_count": unique_funders_count,
        "total_funding_value": total_funding_value if total_funding_value is not None else 0.0,
    }

@router.get("/trends")
async def get_funding_trends():
    """Get funding trends over time"""
    return {"message": "Funding trends - coming soon"}

# These endpoints have been moved to equity_analyses.py
# No need for redirects since we're not in production yet