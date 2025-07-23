from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging
from supabase import Client

from app.core.database import get_db
from app.models import AfricaIntelligenceItem, Organization, AIDomain, FundingType, GeographicScope
from app.schemas.funding import (
    AfricaIntelligenceItemResponse, AfricaIntelligenceItemCreate, AfricaIntelligenceItemUpdate,
    GrantFundingSpecific, InvestmentFundingSpecific, FundingOpportunityCardResponse
)
from app.services.funding_intelligence.vector_intelligence import FundingIntelligenceVectorDB

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize vector database for Pinecone integration
try:
    vector_db = FundingIntelligenceVectorDB()
    logger.info("✅ Pinecone vector database initialized for funding announcements API")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize Pinecone vector database: {e}")
    vector_db = None

#
# Core Intelligence Item Endpoints (from funding.py)
#

@router.get("/", response_model=List[FundingOpportunityCardResponse])
async def get_africa_intelligence_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    currency: Optional[str] = "USD",
    deadline_after: Optional[datetime] = Query(None),
    deadline_before: Optional[datetime] = Query(None),
    organization_id: Optional[int] = Query(None),
    ai_domain: Optional[str] = Query(None),
    funding_type: Optional[str] = Query(None, description="Filter by funding type category: 'grant', 'investment', 'prize', or 'other'"),
    requires_equity: Optional[bool] = Query(None, description="Filter for announcements requiring equity"),
    db = Depends(get_db)
):
    """Get intelligence feed with optional filtering, formatted for FundingAnnouncementCard"""
    # Check if db is a Supabase client or SQLAlchemy session
    query = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*), organizations!africa_intelligence_feed_organization_id_fkey(*), ai_domains!intelligence_item_ai_domains(*)')

    # Apply filters
    if status:
        query = query.filter('status', 'eq', status)
    if min_amount:
        query = query.or_(f'amount_exact.gte.{min_amount},amount_min.gte.{min_amount},total_funding_pool.gte.{min_amount}')
    if max_amount:
        query = query.or_(f'amount_exact.lte.{max_amount},amount_max.lte.{max_amount},total_funding_pool.lte.{max_amount}')
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
    if ai_domain:
        query = query.filter('ai_domains.name', 'ilike', f'%{ai_domain}%')

    # Execute query with pagination
    response = query.range(skip, skip + limit - 1).execute()
    announcements = response.data
    
    # Prepare responses with type-specific data
    results = []
    for announcement in announcements:
        # Handle organization info
        organization_data = announcement.get('organizations', {})
        organization_name = organization_data.get('name') if organization_data else announcement.get('organization_name', 'Unknown')
        
        # Handle AI domains
        ai_domains = announcement.get('ai_domains', [])
        ai_domain_names = [domain.get('name') for domain in ai_domains if domain.get('name')]
        
        # Handle funding type data
        funding_type_data = announcement.get('funding_types', {})
        funding_category = funding_type_data.get('category', 'other')
        
        # Base announcement data
        base_data = {
            "id": announcement.get('id'),
            "title": announcement.get('title'),
            "description": announcement.get('description'),
            "amount_exact": announcement.get('amount_exact'),
            "amount_min": announcement.get('amount_min'),
            "amount_max": announcement.get('amount_max'),
            "currency": announcement.get('currency', 'USD'),
            "deadline": announcement.get('deadline'),
            "status": announcement.get('status'),
            "provider_organization": {
                "id": announcement.get('organization_id'),
                "name": organization_name,
                "type": organization_data.get('type') if organization_data else None,
                "country": organization_data.get('country') if organization_data else None,
                "is_granting_agency": organization_data.get('is_granting_agency', False) if organization_data else False,
                "is_venture_capital": organization_data.get('is_venture_capital', False) if organization_data else False,
            },
            "funding_type": {
                "id": announcement.get('funding_type_id'),
                "name": funding_type_data.get('name') if funding_type_data else None,
                "category": funding_category,
                "requires_equity": funding_type_data.get('requires_equity', False) if funding_type_data else False,
                "requires_repayment": funding_type_data.get('requires_repayment', False) if funding_type_data else False,
            },
            "ai_domains": ai_domain_names,
            "equity_score": announcement.get('equity_score'),
            "underserved_focus": announcement.get('underserved_focus', False),
            "women_focus": announcement.get('women_focus', False),
            "youth_focus": announcement.get('youth_focus', False),
            "rural_focus": announcement.get('rural_focus', False),
            "created_at": announcement.get('created_at'),
            "last_checked": announcement.get('last_checked')
        }
        
        # Add type-specific data based on funding category
        if funding_category == 'grant':
            base_data.update({
                "grant_specific": {
                    "renewable": announcement.get('renewable', False),
                    "project_based": announcement.get('project_based', False),
                    "duration_months": announcement.get('duration_months'),
                    "reporting_requirements": announcement.get('reporting_requirements'),
                    "matching_funds_required": announcement.get('matching_funds_required', False)
                }
            })
        elif funding_category == 'investment':
            base_data.update({
                "investment_specific": {
                    "equity_percentage": announcement.get('equity_percentage'),
                    "valuation_cap": announcement.get('valuation_cap'),
                    "convertible_note": announcement.get('convertible_note', False),
                    "board_seat": announcement.get('board_seat', False),
                    "follow_on_potential": announcement.get('follow_on_potential', False)
                }
            })
        
        results.append(base_data)
    
    return results


@router.get("/{announcement_id}", response_model=AfricaIntelligenceItemResponse)
async def get_intelligence_item(
    announcement_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific intelligence item by ID"""
    # Check if db is a Supabase client or SQLAlchemy session
    if hasattr(db, 'table'):
        # Supabase client
        response = db.table('africa_intelligence_feed').select('*, funding_types!fk_africa_intelligence_feed_funding_type_id(*), organizations!africa_intelligence_feed_organization_id_fkey(*), ai_domains!intelligence_item_ai_domains(*)').eq('id', announcement_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Funding announcement not found")
        
        announcement = response.data[0]
        
        # Handle organization info
        organization_data = announcement.get('organizations', {})
        
        # Handle AI domains
        ai_domains = announcement.get('ai_domains', [])
        ai_domain_names = [domain.get('name') for domain in ai_domains if domain.get('name')]
        
        # Handle funding type data
        funding_type_data = announcement.get('funding_types', {})
        
        return {
            "id": announcement.get('id'),
            "title": announcement.get('title'),
            "description": announcement.get('description'),
            "amount_exact": announcement.get('amount_exact'),
            "amount_min": announcement.get('amount_min'),
            "amount_max": announcement.get('amount_max'),
            "currency": announcement.get('currency', 'USD'),
            "deadline": announcement.get('deadline'),
            "status": announcement.get('status'),
            "organization_id": announcement.get('organization_id'),
            "organization_name": organization_data.get('name') if organization_data else announcement.get('organization_name'),
            "funding_type_id": announcement.get('funding_type_id'),
            "funding_type_name": funding_type_data.get('name') if funding_type_data else None,
            "ai_domains": ai_domain_names,
            "equity_score": announcement.get('equity_score'),
            "underserved_focus": announcement.get('underserved_focus', False),
            "women_focus": announcement.get('women_focus', False),
            "youth_focus": announcement.get('youth_focus', False),
            "rural_focus": announcement.get('rural_focus', False),
            "created_at": announcement.get('created_at'),
            "last_checked": announcement.get('last_checked')
        }
    else:
        # SQLAlchemy session
        announcement = db.query(AfricaIntelligenceItem).filter(AfricaIntelligenceItem.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="Funding announcement not found")
        
        return announcement