"""
FastAPI Webhook Endpoints for n8n Pipeline Integration
Handles incoming funding opportunities from n8n workflows
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
from datetime import datetime

from ..database.sqlite_manager import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

class FundingOpportunityWebhook(BaseModel):
    """Schema for incoming funding opportunities from n8n"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    organization: str = Field(..., min_length=1, max_length=200)
    
    # Financial details
    amount_exact: Optional[float] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    currency: str = Field(default="USD", max_length=10)
    
    # Dates (ISO format strings)
    deadline: Optional[str] = None
    announcement_date: Optional[str] = None
    funding_start_date: Optional[str] = None
    
    # Location and targeting
    location: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=100)
    stage: Optional[str] = Field(None, max_length=100)
    
    # Requirements
    eligibility: Optional[str] = Field(None, max_length=2000)
    application_url: Optional[str] = Field(None, max_length=500)
    application_process: Optional[str] = Field(None, max_length=2000)
    selection_criteria: Optional[str] = Field(None, max_length=2000)
    
    # Metadata
    source_url: Optional[str] = Field(None, max_length=500)
    source_type: str = Field(default="n8n", max_length=50)
    validation_status: str = Field(default="pending", max_length=20)
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Additional fields
    tags: Optional[List[str]] = None
    project_duration: Optional[str] = Field(None, max_length=100)
    reporting_requirements: Optional[str] = Field(None, max_length=1000)
    target_audience: Optional[str] = Field(None, max_length=500)
    ai_subsectors: Optional[str] = Field(None, max_length=500)
    development_stage: Optional[str] = Field(None, max_length=200)
    
    # Flags
    is_active: bool = True
    is_open: bool = True
    requires_registration: bool = False
    collaboration_required: bool = False
    gender_focused: bool = False
    youth_focused: bool = False

class PipelineLogWebhook(BaseModel):
    """Schema for pipeline execution logging"""
    source_name: str
    execution_id: str
    status: str = Field(..., regex="^(success|error|warning)$")
    records_processed: int = Field(default=0, ge=0)
    records_inserted: int = Field(default=0, ge=0)
    records_updated: int = Field(default=0, ge=0)
    error_message: Optional[str] = None
    execution_time: float = Field(default=0.0, ge=0.0)

class BulkFundingOpportunities(BaseModel):
    """Schema for bulk funding opportunity insertion"""
    opportunities: List[FundingOpportunityWebhook]
    source_name: str
    execution_id: str

@router.post("/funding-opportunity")
async def create_funding_opportunity(
    opportunity: FundingOpportunityWebhook,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Create a single funding opportunity from n8n pipeline
    """
    try:
        start_time = time.time()
        
        # Convert Pydantic model to dict
        opportunity_data = opportunity.dict()
        
        # Insert into database
        opportunity_id = db_manager.insert_funding_opportunity(opportunity_data)
        
        execution_time = time.time() - start_time
        
        # Log successful execution in background
        background_tasks.add_task(
            db_manager.log_pipeline_execution,
            source_name=opportunity_data.get('source_type', 'n8n'),
            execution_id=f"single_{int(time.time())}",
            status="success",
            records_processed=1,
            records_inserted=1,
            execution_time=execution_time
        )
        
        logger.info(f"Created funding opportunity: {opportunity.title} (ID: {opportunity_id})")
        
        return {
            "status": "success",
            "opportunity_id": opportunity_id,
            "message": f"Funding opportunity '{opportunity.title}' created successfully",
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Error creating funding opportunity: {str(e)}")
        
        # Log failed execution
        background_tasks.add_task(
            db_manager.log_pipeline_execution,
            source_name=opportunity_data.get('source_type', 'n8n'),
            execution_id=f"single_error_{int(time.time())}",
            status="error",
            records_processed=1,
            records_inserted=0,
            error_message=str(e),
            execution_time=time.time() - start_time
        )
        
        raise HTTPException(status_code=500, detail=f"Failed to create funding opportunity: {str(e)}")

@router.post("/funding-opportunities/bulk")
async def create_bulk_funding_opportunities(
    bulk_data: BulkFundingOpportunities,
    background_tasks: BackgroundTasks
):
    """
    Create multiple funding opportunities from n8n pipeline
    """
    try:
        start_time = time.time()
        
        inserted_ids = []
        errors = []
        
        for opportunity in bulk_data.opportunities:
            try:
                opportunity_data = opportunity.dict()
                opportunity_id = db_manager.insert_funding_opportunity(opportunity_data)
                inserted_ids.append(opportunity_id)
            except Exception as e:
                errors.append(f"Error inserting '{opportunity.title}': {str(e)}")
                logger.error(f"Error inserting opportunity '{opportunity.title}': {str(e)}")
        
        execution_time = time.time() - start_time
        
        # Log execution
        status = "success" if not errors else ("warning" if inserted_ids else "error")
        error_message = "; ".join(errors) if errors else None
        
        background_tasks.add_task(
            db_manager.log_pipeline_execution,
            source_name=bulk_data.source_name,
            execution_id=bulk_data.execution_id,
            status=status,
            records_processed=len(bulk_data.opportunities),
            records_inserted=len(inserted_ids),
            error_message=error_message,
            execution_time=execution_time
        )
        
        logger.info(f"Bulk insert completed: {len(inserted_ids)} inserted, {len(errors)} errors")
        
        return {
            "status": status,
            "inserted_count": len(inserted_ids),
            "error_count": len(errors),
            "inserted_ids": inserted_ids,
            "errors": errors,
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Error in bulk funding opportunity creation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")

@router.post("/pipeline-log")
async def log_pipeline_execution(log_data: PipelineLogWebhook):
    """
    Log n8n pipeline execution for monitoring
    """
    try:
        log_id = db_manager.log_pipeline_execution(
            source_name=log_data.source_name,
            execution_id=log_data.execution_id,
            status=log_data.status,
            records_processed=log_data.records_processed,
            records_inserted=log_data.records_inserted,
            records_updated=log_data.records_updated,
            error_message=log_data.error_message,
            execution_time=log_data.execution_time
        )
        
        return {
            "status": "success",
            "log_id": log_id,
            "message": "Pipeline execution logged successfully"
        }
        
    except Exception as e:
        logger.error(f"Error logging pipeline execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to log execution: {str(e)}")

@router.post("/refresh-cache")
async def refresh_cache(background_tasks: BackgroundTasks):
    """
    Refresh application caches after new data insertion
    """
    try:
        # Add background tasks for cache refresh
        background_tasks.add_task(refresh_search_cache)
        background_tasks.add_task(refresh_analytics_cache)
        
        logger.info("Cache refresh initiated")
        
        return {
            "status": "success",
            "message": "Cache refresh initiated in background"
        }
        
    except Exception as e:
        logger.error(f"Error initiating cache refresh: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cache refresh failed: {str(e)}")

@router.get("/pipeline-stats")
async def get_pipeline_stats():
    """
    Get pipeline execution statistics for monitoring
    """
    try:
        stats = db_manager.get_pipeline_stats()
        
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting pipeline stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/health")
async def webhook_health_check():
    """
    Health check endpoint for n8n monitoring
    """
    try:
        # Test database connection
        stats = db_manager.get_pipeline_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_opportunities": stats.get("total_opportunities", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Background task functions
async def refresh_search_cache():
    """Background task to refresh search cache"""
    try:
        # Implement search cache refresh logic here
        logger.info("Search cache refreshed")
    except Exception as e:
        logger.error(f"Error refreshing search cache: {str(e)}")

async def refresh_analytics_cache():
    """Background task to refresh analytics cache"""
    try:
        # Implement analytics cache refresh logic here
        logger.info("Analytics cache refreshed")
    except Exception as e:
        logger.error(f"Error refreshing analytics cache: {str(e)}")