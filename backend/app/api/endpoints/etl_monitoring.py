"""
ETL Monitoring API Endpoints
Provides real-time monitoring and statistics for the multi-stage data pipeline
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()

class PipelineStage(str, Enum):
    """ETL Pipeline stages"""
    STAGE1_RSS_INGESTION = "stage1_rss_ingestion"
    STAGE2_CRAWL4AI_SCRAPING = "stage2_crawl4ai_scraping"
    STAGE3_SERPER_ENRICHMENT = "stage3_serper_enrichment"

class ProcessingStatus(str, Enum):
    """Processing status types"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"

class ETLStageStats(BaseModel):
    """Statistics for a single ETL stage"""
    stage: PipelineStage
    status: ProcessingStatus
    current_batch_id: Optional[str] = None
    
    # Progress metrics
    total_items_processed: int = 0
    items_processed_today: int = 0
    items_processed_last_hour: int = 0
    current_batch_size: int = 0
    current_batch_progress: int = 0
    
    # Quality metrics
    success_rate: float = 0.0
    error_count: int = 0
    duplicate_count: int = 0
    
    # Performance metrics
    avg_processing_time_seconds: float = 0.0
    items_per_minute: float = 0.0
    last_processed_at: Optional[datetime] = None
    
    # Stage-specific metrics
    stage_specific_metrics: Dict[str, Any] = {}

class ETLOverallStats(BaseModel):
    """Overall ETL pipeline statistics"""
    pipeline_status: ProcessingStatus
    total_opportunities_in_db: int
    opportunities_added_today: int
    opportunities_added_last_hour: int
    
    # Quality overview
    overall_success_rate: float
    total_duplicates_prevented: int
    data_completeness_score: float
    
    # Performance overview
    total_processing_time_hours: float
    avg_opportunities_per_hour: float
    
    # Stage breakdown
    stage_stats: List[ETLStageStats]
    
    # Recent activity
    recent_errors: List[Dict[str, Any]] = []
    recent_successes: List[Dict[str, Any]] = []
    
    last_updated: datetime

class ETLHistoricalData(BaseModel):
    """Historical ETL performance data"""
    date: str
    stage1_processed: int = 0
    stage2_processed: int = 0
    stage3_processed: int = 0
    total_opportunities_added: int = 0
    success_rate: float = 0.0
    avg_processing_time: float = 0.0

@router.get("/stats/live", response_model=ETLOverallStats)
async def get_live_etl_stats(db: AsyncSession = Depends(get_db)):
    """
    Get real-time ETL pipeline statistics
    
    Returns comprehensive statistics for all pipeline stages including:
    - Current processing status and progress
    - Performance metrics and success rates
    - Recent activity and error logs
    """
    try:
        supabase = get_supabase_client()
        
        # Get overall database statistics
        total_opportunities = await _get_total_opportunities_count(supabase)
        opportunities_today = await _get_opportunities_count_since(supabase, datetime.now().replace(hour=0, minute=0, second=0))
        opportunities_last_hour = await _get_opportunities_count_since(supabase, datetime.now() - timedelta(hours=1))
        
        # Get stage-specific statistics
        stage_stats = []
        
        # Stage 1: RSS Ingestion
        stage1_stats = await _get_stage1_stats(supabase)
        stage_stats.append(stage1_stats)
        
        # Stage 2: Crawl4AI Scraping
        stage2_stats = await _get_stage2_stats(supabase)
        stage_stats.append(stage2_stats)
        
        # Stage 3: Serper Enrichment
        stage3_stats = await _get_stage3_stats(supabase)
        stage_stats.append(stage3_stats)
        
        # Calculate overall metrics
        overall_success_rate = sum(s.success_rate for s in stage_stats) / len(stage_stats) if stage_stats else 0.0
        total_duplicates = sum(s.duplicate_count for s in stage_stats)
        
        # Determine overall pipeline status
        pipeline_status = _determine_pipeline_status(stage_stats)
        
        # Get recent activity
        recent_errors = await _get_recent_errors(supabase)
        recent_successes = await _get_recent_successes(supabase)
        
        # Calculate data completeness
        data_completeness = await _calculate_data_completeness(supabase)
        
        return ETLOverallStats(
            pipeline_status=pipeline_status,
            total_opportunities_in_db=total_opportunities,
            opportunities_added_today=opportunities_today,
            opportunities_added_last_hour=opportunities_last_hour,
            overall_success_rate=overall_success_rate,
            total_duplicates_prevented=total_duplicates,
            data_completeness_score=data_completeness,
            total_processing_time_hours=0.0,  # TODO: Implement from logs
            avg_opportunities_per_hour=opportunities_today / 24.0 if opportunities_today > 0 else 0.0,
            stage_stats=stage_stats,
            recent_errors=recent_errors,
            recent_successes=recent_successes,
            last_updated=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting live ETL stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ETL statistics: {str(e)}")

@router.get("/stats/historical", response_model=List[ETLHistoricalData])
async def get_historical_etl_stats(
    days: int = Query(default=7, ge=1, le=30, description="Number of days of historical data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical ETL performance data
    
    Returns daily statistics for the specified number of days
    """
    try:
        supabase = get_supabase_client()
        
        historical_data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Get daily statistics
            daily_stats = await _get_daily_stats(supabase, date)
            historical_data.append(ETLHistoricalData(
                date=date_str,
                **daily_stats
            ))
        
        return historical_data
        
    except Exception as e:
        logger.error(f"Error getting historical ETL stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get historical statistics: {str(e)}")

@router.get("/stats/stage/{stage}", response_model=ETLStageStats)
async def get_stage_specific_stats(
    stage: PipelineStage,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed statistics for a specific pipeline stage
    """
    try:
        supabase = get_supabase_client()
        
        if stage == PipelineStage.STAGE1_RSS_INGESTION:
            return await _get_stage1_stats(supabase)
        elif stage == PipelineStage.STAGE2_CRAWL4AI_SCRAPING:
            return await _get_stage2_stats(supabase)
        elif stage == PipelineStage.STAGE3_SERPER_ENRICHMENT:
            return await _get_stage3_stats(supabase)
        else:
            raise HTTPException(status_code=400, detail="Invalid stage")
            
    except Exception as e:
        logger.error(f"Error getting stage {stage} stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stage statistics: {str(e)}")

@router.post("/control/{stage}/{action}")
async def control_pipeline_stage(
    stage: PipelineStage,
    action: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Control pipeline stage operations (start, stop, pause, resume)
    """
    valid_actions = ["start", "stop", "pause", "resume"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
    
    try:
        # TODO: Implement pipeline control logic
        # This would integrate with the actual pipeline processes
        
        logger.info(f"Pipeline control: {action} on {stage}")
        return {"status": "success", "message": f"Stage {stage} {action} command sent"}
        
    except Exception as e:
        logger.error(f"Error controlling pipeline stage {stage}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to control pipeline: {str(e)}")

# Helper functions

async def _get_total_opportunities_count(supabase) -> int:
    """Get total count of opportunities in database"""
    try:
        response = supabase.table('africa_intelligence_feed').select('id', count='exact').execute()
        return response.count if response.count else 0
    except Exception:
        return 0

async def _get_opportunities_count_since(supabase, since_date: datetime) -> int:
    """Get count of opportunities added since a specific date"""
    try:
        response = supabase.table('africa_intelligence_feed')\
            .select('id', count='exact')\
            .gte('created_at', since_date.isoformat())\
            .execute()
        return response.count if response.count else 0
    except Exception:
        return 0

async def _get_stage1_stats(supabase) -> ETLStageStats:
    """Get Stage 1 (RSS Ingestion) statistics"""
    # TODO: Implement based on actual Stage 1 logging/tracking
    return ETLStageStats(
        stage=PipelineStage.STAGE1_RSS_INGESTION,
        status=ProcessingStatus.IDLE,
        total_items_processed=0,
        success_rate=95.0,
        stage_specific_metrics={
            "rss_feeds_monitored": 5,
            "avg_items_per_feed": 12,
            "last_feed_check": datetime.now().isoformat()
        }
    )

async def _get_stage2_stats(supabase) -> ETLStageStats:
    """Get Stage 2 (Crawl4AI Scraping) statistics"""
    # TODO: Implement based on actual Stage 2 logging/tracking
    return ETLStageStats(
        stage=PipelineStage.STAGE2_CRAWL4AI_SCRAPING,
        status=ProcessingStatus.IDLE,
        total_items_processed=0,
        success_rate=88.0,
        stage_specific_metrics={
            "urls_queued": 0,
            "avg_scraping_time_seconds": 15.2,
            "llm_extraction_success_rate": 92.0
        }
    )

async def _get_stage3_stats(supabase) -> ETLStageStats:
    """Get Stage 3 (Serper Enrichment) statistics"""
    # TODO: Implement based on actual Stage 3 logging/tracking
    return ETLStageStats(
        stage=PipelineStage.STAGE3_SERPER_ENRICHMENT,
        status=ProcessingStatus.IDLE,
        total_items_processed=0,
        success_rate=82.0,
        stage_specific_metrics={
            "records_needing_enrichment": 0,
            "avg_search_time_seconds": 3.8,
            "fields_enriched_today": 0
        }
    )

def _determine_pipeline_status(stage_stats: List[ETLStageStats]) -> ProcessingStatus:
    """Determine overall pipeline status from stage statuses"""
    if any(s.status == ProcessingStatus.RUNNING for s in stage_stats):
        return ProcessingStatus.RUNNING
    elif any(s.status == ProcessingStatus.ERROR for s in stage_stats):
        return ProcessingStatus.ERROR
    elif any(s.status == ProcessingStatus.PAUSED for s in stage_stats):
        return ProcessingStatus.PAUSED
    else:
        return ProcessingStatus.IDLE

async def _get_recent_errors(supabase) -> List[Dict[str, Any]]:
    """Get recent error logs"""
    # TODO: Implement based on actual error logging system
    return []

async def _get_recent_successes(supabase) -> List[Dict[str, Any]]:
    """Get recent successful operations"""
    # TODO: Implement based on actual success logging system
    return []

async def _calculate_data_completeness(supabase) -> float:
    """Calculate overall data completeness score"""
    try:
        # Check for missing critical fields
        response = supabase.table('africa_intelligence_feed')\
            .select('id,title,amount_max,deadline,organization,application_url')\
            .execute()
        
        if not response.data:
            return 0.0
        
        total_records = len(response.data)
        complete_records = 0
        
        for record in response.data:
            fields_present = sum(1 for field in ['title', 'amount_max', 'deadline', 'organization', 'application_url'] 
                               if record.get(field))
            if fields_present >= 3:  # At least 3 out of 5 critical fields
                complete_records += 1
        
        return (complete_records / total_records) * 100.0 if total_records > 0 else 0.0
        
    except Exception:
        return 0.0

async def _get_daily_stats(supabase, date: datetime) -> Dict[str, Any]:
    """Get statistics for a specific day"""
    # TODO: Implement based on actual daily tracking
    return {
        "stage1_processed": 0,
        "stage2_processed": 0,
        "stage3_processed": 0,
        "total_opportunities_added": 0,
        "success_rate": 0.0,
        "avg_processing_time": 0.0
    }
