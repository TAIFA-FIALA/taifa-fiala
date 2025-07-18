from fastapi import APIRouter, Depends
from app.core.data_access import get_data_access, DataAccess

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(data_access: DataAccess = Depends(get_data_access)):
    """Get analytics summary for dashboard"""
    
    # Use the hybrid data access layer that handles RLS policies properly
    return await data_access.get_analytics_summary()

@router.get("/trends")
async def get_funding_trends():
    """Get funding trends over time"""
    return {"message": "Funding trends - coming soon"}

# These endpoints have been moved to equity_analyses.py
# No need for redirects since we're not in production yet