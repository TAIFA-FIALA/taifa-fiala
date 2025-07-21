from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging
from ...core.config import settings
from ...services.data_ingestion.master_pipeline import MasterDataIngestionPipeline, create_default_config
from ...db.supabase import get_supabase_client
from supabase import Client as SupabaseClient

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class EnrichmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class FundingOpportunityBase(BaseModel):
    id: int
    title: str
    source: Optional[str] = None
    published_date: Optional[datetime] = None
    url: Optional[str] = None
    content: Optional[str] = None
    enrichment_status: Optional[EnrichmentStatus] = EnrichmentStatus.NOT_STARTED
    missing_fields: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class FundingOpportunityListResponse(BaseModel):
    items: List[FundingOpportunityBase]
    total: int
    limit: int
    offset: int

class EnrichmentResponse(BaseModel):
    success: bool
    message: str
    job_id: Optional[str] = None

# Helper functions
def get_missing_fields(record: Dict[str, Any]) -> List[str]:
    """Determine which required fields are missing from a record."""
    required_fields = [
        'funding_amount',
        'application_deadline',
        'eligibility_criteria',
        'contact_email',
        'application_url'
    ]
    return [field for field in required_fields if not record.get(field)]

async def get_enrichment_status(record_id: int, supabase: SupabaseClient) -> EnrichmentStatus:
    """Get the current enrichment status of a record."""
    try:
        result = supabase.table('africa_intelligence_feed')\
            .select('enrichment_status,enrichment_attempted,enrichment_success')\
            .eq('id', record_id)\
            .single().execute()
        
        data = result.data
        if not data:
            return EnrichmentStatus.NOT_STARTED
            
        if data.get('enrichment_attempted'):
            if data.get('enrichment_success'):
                return EnrichmentStatus.COMPLETED
            return EnrichmentStatus.FAILED
        return EnrichmentStatus.IN_PROGRESS if data.get('enrichment_status') == 'in_progress' else EnrichmentStatus.NOT_STARTED
    except Exception as e:
        logger.error(f"Error getting enrichment status for record {record_id}: {str(e)}")
        return EnrichmentStatus.NOT_STARTED

# API Endpoints
@router.get("/", response_model=FundingOpportunityListResponse)
async def list_funding_opportunities(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    enrichment_status: Optional[EnrichmentStatus] = None,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    List funding opportunities with optional filtering by enrichment status.
    """
    try:
        query = supabase.table('africa_intelligence_feed')\
            .select('*', count='exact')\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)
        
        if enrichment_status:
            if enrichment_status == EnrichmentStatus.COMPLETED:
                query = query.eq('enrichment_success', True)
            elif enrichment_status == EnrichmentStatus.FAILED:
                query = query.eq('enrichment_attempted', True).eq('enrichment_success', False)
            elif enrichment_status == EnrichmentStatus.IN_PROGRESS:
                query = query.eq('enrichment_status', 'in_progress')
            else:  # NOT_STARTED
                query = query.is_('enrichment_attempted', 'FALSE')
        
        result = query.execute()
        
        items = []
        for item in result.data:
            missing_fields = get_missing_fields(item)
            items.append({
                **item,
                "enrichment_status": await get_enrichment_status(item['id'], supabase),
                "missing_fields": missing_fields
            })
        
        return {
            "items": items,
            "total": result.count or 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error listing funding opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching funding opportunities")

@router.get("/{record_id}", response_model=Dict[str, Any])
async def get_funding_opportunity(
    record_id: int,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get details of a specific funding opportunity.
    """
    try:
        result = supabase.table('africa_intelligence_feed')\
            .select('*')\
            .eq('id', record_id)\
            .single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Funding opportunity not found")
        
        record = dict(result.data)
        record['missing_fields'] = get_missing_fields(record)
        record['enrichment_status'] = await get_enrichment_status(record_id, supabase)
        
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching funding opportunity {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching funding opportunity")

@router.post("/{record_id}/enrich", response_model=EnrichmentResponse)
async def trigger_enrichment(
    record_id: int,
    background_tasks: BackgroundTasks,
    force: bool = False,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Trigger enrichment for a specific funding opportunity.
    """
    try:
        # Check if record exists
        result = supabase.table('africa_intelligence_feed')\
            .select('id,enrichment_status')\
            .eq('id', record_id)\
            .single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Funding opportunity not found")
        
        # Check current status if not forcing
        if not force and result.data.get('enrichment_status') == 'in_progress':
            return EnrichmentResponse(
                success=False,
                message="Enrichment already in progress"
            )
        
        # Update status to in_progress
        supabase.table('africa_intelligence_feed')\
            .update({
                'enrichment_status': 'in_progress',
                'enrichment_attempted': False,
                'enrichment_success': False,
                'updated_at': datetime.utcnow().isoformat()
            })\
            .eq('id', record_id)\
            .execute()
        
        # In a real implementation, you would start the enrichment process here
        # For now, we'll just simulate it with a background task
        background_tasks.add_task(
            process_enrichment,
            record_id=record_id,
            supabase=supabase
        )
        
        return EnrichmentResponse(
            success=True,
            message="Enrichment started",
            job_id=f"enrich_{record_id}_{int(datetime.utcnow().timestamp())}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering enrichment for record {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error triggering enrichment")

async def process_enrichment(record_id: int, supabase: SupabaseClient):
    """
    Background task to process enrichment for a record.
    In a real implementation, this would call your enrichment pipeline.
    """
    try:
        # Simulate processing time
        import time
        time.sleep(5)
        
        # Update status to completed
        supabase.table('africa_intelligence_feed')\
            .update({
                'enrichment_status': 'completed',
                'enrichment_attempted': True,
                'enrichment_success': True,
                'updated_at': datetime.utcnow().isoformat(),
                # In a real implementation, you would update with actual enriched data
                'funding_amount': "$50,000",  # Example
                'application_deadline': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'eligibility_criteria': 'Open to African startups in the AI/ML space',
                'contact_email': 'grants@example.org',
                'application_url': 'https://example.org/apply'
            })\
            .eq('id', record_id)\
            .execute()
    except Exception as e:
        logger.error(f"Error processing enrichment for record {record_id}: {str(e)}")
        # Update status to failed
        supabase.table('africa_intelligence_feed')\
            .update({
                'enrichment_status': 'failed',
                'enrichment_attempted': True,
                'enrichment_success': False,
                'updated_at': datetime.utcnow().isoformat()
            })\
            .eq('id', record_id)\
            .execute()

@router.get("/{record_id}/enrichment-status", response_model=Dict[str, Any])
async def get_enrichment_status_endpoint(
    record_id: int,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get the enrichment status for a specific funding opportunity.
    """
    try:
        result = supabase.table('africa_intelligence_feed')\
            .select('id,enrichment_status,enrichment_attempted,enrichment_success')\
            .eq('id', record_id)\
            .single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Funding opportunity not found")
        
        return {
            "record_id": record_id,
            "status": await get_enrichment_status(record_id, supabase),
            "last_updated": result.data.get('updated_at')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enrichment status for record {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting enrichment status")

@router.get("/{record_id}/missing-fields", response_model=Dict[str, Any])
async def get_missing_fields_endpoint(
    record_id: int,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Get the list of missing required fields for a funding opportunity.
    """
    try:
        result = supabase.table('africa_intelligence_feed')\
            .select('*')\
            .eq('id', record_id)\
            .single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Funding opportunity not found")
        
        missing_fields = get_missing_fields(result.data)
        
        return {
            "record_id": record_id,
            "missing_fields": missing_fields,
            "all_required_fields": [
                'funding_amount',
                'application_deadline',
                'eligibility_criteria',
                'contact_email',
                'application_url'
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting missing fields for record {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting missing fields")
