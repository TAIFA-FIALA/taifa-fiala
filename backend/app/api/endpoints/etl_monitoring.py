"""
ETL Monitoring API Endpoints
Provides real-time monitoring and statistics for the multi-stage data pipeline
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta, date
from enum import Enum
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_admin_db
from app.core.supabase_client import get_supabase_client
from app.core.config import settings
from app.services.data_ingestion.master_pipeline import MasterDataIngestionPipeline, PipelineStatus as MasterPipelineStatus, create_default_config
from app.core.llm_provider import get_smart_llm_provider
from app.core.notification_system import get_notification_system, AlertCategory, AlertLevel

logger = logging.getLogger(__name__)

# Create router without the version prefix (it will be added in __init__.py)
router = APIRouter(prefix="/etl-monitoring", tags=["etl-monitoring"])

# Global pipeline instance (singleton pattern)
_pipeline_instance: Optional[MasterDataIngestionPipeline] = None

def get_pipeline_instance() -> Optional[MasterDataIngestionPipeline]:
    """Get or create the master pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        try:
            config = create_default_config()
            _pipeline_instance = MasterDataIngestionPipeline(config, settings)
            logger.info("Master pipeline instance created for monitoring")
        except Exception as e:
            logger.error(f"Failed to create pipeline instance: {e}")
            return None
    return _pipeline_instance

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
    total_items_processed: int = 0
    items_processed_today: int = 0
    items_processed_last_hour: int = 0
    current_batch_size: int = 0
    current_batch_progress: int = 0
    success_rate: float = 0.0
    error_count: int = 0
    duplicate_count: int = 0
    avg_processing_time_seconds: float = 0.0
    items_per_minute: float = 0.0
    last_processed_at: Optional[datetime] = None
    stage_specific_metrics: Dict[str, Any] = {}
    # Smart prioritization metrics (Stage 1 RSS only)
    smart_prioritization: Optional[Dict[str, Any]] = None

class ETLOverallStats(BaseModel):
    """Overall ETL pipeline statistics"""
    pipeline_status: ProcessingStatus
    total_opportunities_in_db: int
    opportunities_added_today: int
    opportunities_added_last_hour: int
    overall_success_rate: float
    total_duplicates_prevented: int
    data_completeness_score: float
    total_processing_time_hours: float
    avg_opportunities_per_hour: float
    stage_stats: List[ETLStageStats]
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

class DailyNewRecords(BaseModel):
    """Daily new records statistics"""
    date: datetime
    stage: str
    new_records_count: int
    source: Optional[str] = None

class DailyDuplicatesRemoved(BaseModel):
    """Daily duplicates removed statistics"""
    date: datetime
    stage: str
    duplicates_removed: int
    total_processed: int
    duplicate_rate: float

class LLMUsageStats(BaseModel):
    """LLM provider usage statistics"""
    provider: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens_input: int
    total_tokens_output: int
    estimated_cost_usd: float
    avg_response_time_ms: float
    last_used: Optional[datetime]
    success_rate: float

class LLMProviderSummary(BaseModel):
    """Summary of all LLM provider usage"""
    total_requests: int
    total_cost_usd: float
    cost_savings_vs_openai_only: float
    primary_provider: str
    fallback_count: int
    providers: List[LLMUsageStats]

class BalanceSummary(BaseModel):
    """Account balance summary for dashboard"""
    total_providers: int
    active_providers: int
    warning_providers: int
    critical_providers: int
    total_balance_usd: float
    balances: List[Dict[str, Any]]
    last_updated: Optional[datetime]

class NotificationSummary(BaseModel):
    """Notification system summary for dashboard"""
    active_alerts: int
    critical_alerts: int
    warning_alerts: int
    monitoring_active: bool
    enabled_channels: int
    recent_alerts: List[Dict[str, Any]]

class ETLDashboard(BaseModel):
    """Complete ETL dashboard data"""
    pipeline_status: ETLOverallStats
    real_time_metrics: Dict[str, Any]
    llm_usage: Optional[LLMProviderSummary]
    account_balances: BalanceSummary
    notifications: NotificationSummary
    alerts: List[Dict[str, Any]]
    system_health: Dict[str, Any]
    last_updated: datetime

@router.get("/stats/live", response_model=ETLOverallStats)
async def get_live_etl_stats(db = Depends(get_admin_db)):
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get ETL statistics: {str(e)}")

@router.get("/stats/historical", response_model=List[ETLHistoricalData])
async def get_historical_etl_stats(
    days: int = Query(default=7, ge=1, le=30, description="Number of days of historical data"),
    db = Depends(get_admin_db)
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get historical statistics: {str(e)}")

@router.get("/stats/stage/{stage}", response_model=ETLStageStats)
async def get_stage_specific_stats(
    stage: PipelineStage,
    db = Depends(get_admin_db)
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage")
            
    except Exception as e:
        logger.error(f"Error getting stage {stage} stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get stage statistics: {str(e)}")

@router.post("/control/{stage}/{action}")
async def control_pipeline_stage(
    stage: PipelineStage,
    action: str,
    db = Depends(get_admin_db)
):
    """
    Control pipeline stage operations (start, stop, pause, resume)
    """
    valid_actions = ["start", "stop", "pause", "resume"]
    if action not in valid_actions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid action. Must be one of: {valid_actions}")
    
    try:
        # TODO: Implement pipeline control logic
        # This would integrate with the actual pipeline processes
        
        logger.info(f"Pipeline control: {action} on {stage}")
        return {"status": "success", "message": f"Stage {stage} {action} command sent"}
        
    except Exception as e:
        logger.error(f"Error controlling pipeline stage {stage}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to control pipeline: {str(e)}")

@router.get("/daily-new-records")
async def get_daily_new_records(
    days: int = Query(default=7, ge=1, le=30, description="Number of days of data to return"),
    stage: Optional[PipelineStage] = Query(None, description="Filter by pipeline stage")
):
    """
    Get the number of new records added per day, with optional filtering by pipeline stage.
    
    This endpoint provides visibility into the volume of new data being ingested
    through different stages of the ETL pipeline.
    """
    try:
        db = get_supabase_client()
        if not db:
            logger.error("Supabase client not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
            
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logger.debug(f"Querying daily new records from {start_date} to {end_date}")
        
        try:
            # First, verify the table exists
            test_query = db.table('etl_processing_logs').select('*', count='exact').limit(1).execute()
            if hasattr(test_query, 'error') and test_query.error:
                logger.error(f"Error accessing etl_processing_logs table: {test_query.error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error accessing processing logs: {str(test_query.error)}"
                )
            
            # Build the main query
            query = db.table('etl_processing_logs') \
                .select('date(created_at) as date, pipeline_stage as stage, count(*) as new_records_count, source') \
                .gte('created_at', start_date.isoformat()) \
                .order('date', desc=True) \
                .eq('operation_type', 'insert')
                
            if stage:
                query = query.eq('pipeline_stage', stage.value)
                
            result = query.execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Error querying daily new records: {result.error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error retrieving daily new records: {str(result.error)}"
                )
                
            logger.debug(f"Successfully retrieved {len(result.data) if result.data else 0} records")
            
            return [
                DailyNewRecords(
                    date=datetime.strptime(row['date'], '%Y-%m-%d').date() if isinstance(row['date'], str) else row['date'],
                    stage=row['stage'],
                    new_records_count=row['new_records_count'],
                    source=row.get('source')
                )
                for row in (result.data or [])
            ]
            
        except Exception as query_error:
            logger.exception(f"Error in daily new records query: {str(query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query error: {str(query_error)}"
            )
            
    except HTTPException as http_error:
        # Re-raise HTTP exceptions as-is
        raise http_error
    except Exception as e:
        logger.exception("Unexpected error in get_daily_new_records")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/duplicates-removed", response_model=List[DailyDuplicatesRemoved])
async def get_daily_duplicates_removed(
    days: int = Query(default=7, ge=1, le=30, description="Number of days of data to return"),
    stage: Optional[PipelineStage] = Query(None, description="Filter by pipeline stage")
):
    """
    Get the number of duplicate records removed per day, with optional filtering by pipeline stage.
    
    This endpoint helps track data quality by showing how many duplicate records
    were detected and removed during the ETL process.
    """
    try:
        db = get_supabase_client()
        if not db:
            logger.error("Supabase client not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
            
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logger.debug(f"Querying daily duplicates removed from {start_date} to {end_date}")
        
        try:
            # First, verify the table exists
            test_query = db.table('etl_duplicate_logs').select('*', count='exact').limit(1).execute()
            if hasattr(test_query, 'error') and test_query.error:
                logger.error(f"Error accessing etl_duplicate_logs table: {test_query.error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error accessing duplicate logs: {str(test_query.error)}"
                )
            
            # Check available columns for debugging
            test_columns_query = db.table('etl_duplicate_logs').select('*').limit(1).execute()
            if hasattr(test_columns_query, 'data') and test_columns_query.data:
                logger.debug(f"Available columns in etl_duplicate_logs: {list(test_columns_query.data[0].keys())}")
                timestamp_column = 'created_at' if 'created_at' in test_columns_query.data[0] else 'detected_at'
            else:
                timestamp_column = 'created_at' # Default fallback

            # Fetch all relevant records
            query = db.table('etl_duplicate_logs') \
                .select('*') \
                .gte(timestamp_column, start_date.isoformat())
                
            if stage:
                query = query.eq('pipeline_stage', stage.value)
                
            result = query.execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Error querying duplicates removed: {result.error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error retrieving duplicates removed data: {str(result.error)}"
                )
            
            # Process and aggregate the data in Python
            from collections import defaultdict
            
            # Group by date and pipeline stage
            daily_data = defaultdict(lambda: {
                'date': None,
                'stage': None,
                'duplicates_removed': 0,
                'batch_ids': set()
            })
            
            for row in (result.data or []):
                if not row.get(timestamp_column):
                    continue
                    
                # Convert to date string for grouping
                date_str = row[timestamp_column].split('T')[0]
                stage_name = row.get('pipeline_stage', 'unknown')
                key = (date_str, stage_name)
                
                if key not in daily_data:
                    daily_data[key] = {
                        'date': date_str,
                        'stage': stage_name,
                        'duplicates_removed': 0,
                        'batch_ids': set()
                    }
                
                daily_data[key]['duplicates_removed'] += 1
                if row.get('batch_id'):
                    daily_data[key]['batch_ids'].add(row['batch_id'])
            
            # Convert to response format
            response = []
            for key, data in daily_data.items():
                total_batches = len(data['batch_ids']) if data['batch_ids'] else 1
                total_processed = total_batches * 100  # Assuming 100 items per batch
                response.append(DailyDuplicatesRemoved(
                    date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                    stage=data['stage'],
                    duplicates_removed=data['duplicates_removed'],
                    total_processed=total_processed,
                    duplicate_rate=min(100.0, (data['duplicates_removed'] / total_processed) * 100) if total_processed > 0 else 0.0
                ))
            
            # Sort by date descending
            response.sort(key=lambda x: x.date, reverse=True)
            
            logger.debug(f"Successfully processed {len(response)} date/stage groups")
            return response
            
        except Exception as query_error:
            logger.exception(f"Error in duplicates removed query: {str(query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Query error: {str(query_error)}"
            )
            
    except HTTPException as http_error:
        # Re-raise HTTP exceptions as-is
        raise http_error
    except Exception as e:
        logger.exception("Unexpected error in get_daily_duplicates_removed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def _get_total_opportunities_count(db) -> int:
    """Get total count of opportunities in database"""
    try:
        response = db.table('africa_intelligence_feed').select('id', count='exact').execute()
        return response.count if response.count else 0
    except Exception:
        return 0

async def _get_opportunities_count_since(db, since_date: datetime) -> int:
    """Get count of opportunities added since a specific date"""
    try:
        response = db.table('africa_intelligence_feed')\
            .select('id', count='exact')\
            .gte('created_at', since_date.isoformat())\
            .execute()
        return response.count if response.count else 0
    except Exception:
        return 0

async def _get_stage1_stats(db) -> ETLStageStats:
    """Get Stage 1 (RSS Ingestion) statistics from real pipeline"""
    pipeline = get_pipeline_instance()
    if not pipeline:
        # Fallback to basic stats if pipeline unavailable
        return ETLStageStats(
            stage=PipelineStage.STAGE1_RSS_INGESTION,
            status=ProcessingStatus.IDLE,
            total_items_processed=0,
            success_rate=0.0,
            stage_specific_metrics={"error": "Pipeline instance unavailable"}
        )
    
    try:
        pipeline_status = pipeline.get_status()
        component_stats = pipeline_status.get('component_stats', {})
        rss_stats = component_stats.get('rss_pipeline', {})
        
        # Map pipeline status to our enum
        status_mapping = {
            MasterPipelineStatus.RUNNING.value: ProcessingStatus.RUNNING,
            MasterPipelineStatus.STOPPED.value: ProcessingStatus.IDLE,
            MasterPipelineStatus.PAUSED.value: ProcessingStatus.PAUSED,
            MasterPipelineStatus.ERROR.value: ProcessingStatus.ERROR,
            MasterPipelineStatus.STARTING.value: ProcessingStatus.RUNNING,
            MasterPipelineStatus.STOPPING.value: ProcessingStatus.IDLE
        }
        
        current_status = status_mapping.get(
            pipeline_status.get('status', 'stopped'), 
            ProcessingStatus.IDLE
        )
        
        return ETLStageStats(
            stage=PipelineStage.STAGE1_RSS_INGESTION,
            status=current_status,
            total_items_processed=rss_stats.get('total_items_processed', 0),
            items_processed_today=rss_stats.get('items_processed_today', 0),
            success_rate=rss_stats.get('success_rate', 0.0),
            error_count=rss_stats.get('total_errors', 0),
            avg_processing_time_seconds=rss_stats.get('avg_processing_time_seconds', 0.0),
            stage_specific_metrics={
                "rss_feeds_monitored": rss_stats.get('feeds_monitored', 0),
                "avg_items_per_feed": rss_stats.get('avg_items_per_feed', 0),
                "last_feed_check": rss_stats.get('last_check', datetime.now().isoformat()),
                "pipeline_uptime_seconds": pipeline_status.get('uptime_seconds', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting Stage 1 stats: {e}")
        return ETLStageStats(
            stage=PipelineStage.STAGE1_RSS_INGESTION,
            status=ProcessingStatus.ERROR,
            total_items_processed=0,
            success_rate=0.0,
            stage_specific_metrics={"error": str(e)}
        )

async def _get_stage2_stats(db) -> ETLStageStats:
    """Get Stage 2 (Crawl4AI Scraping) statistics from real pipeline"""
    pipeline = get_pipeline_instance()
    if not pipeline:
        return ETLStageStats(
            stage=PipelineStage.STAGE2_CRAWL4AI_SCRAPING,
            status=ProcessingStatus.IDLE,
            total_items_processed=0,
            success_rate=0.0,
            stage_specific_metrics={"error": "Pipeline instance unavailable"}
        )
    
    try:
        pipeline_status = pipeline.get_status()
        component_stats = pipeline_status.get('component_stats', {})
        web_scraper_stats = component_stats.get('web_scraper', {})
        
        # Map pipeline status
        status_mapping = {
            MasterPipelineStatus.RUNNING.value: ProcessingStatus.RUNNING,
            MasterPipelineStatus.STOPPED.value: ProcessingStatus.IDLE,
            MasterPipelineStatus.PAUSED.value: ProcessingStatus.PAUSED,
            MasterPipelineStatus.ERROR.value: ProcessingStatus.ERROR,
            MasterPipelineStatus.STARTING.value: ProcessingStatus.RUNNING,
            MasterPipelineStatus.STOPPING.value: ProcessingStatus.IDLE
        }
        
        current_status = status_mapping.get(
            pipeline_status.get('status', 'stopped'), 
            ProcessingStatus.IDLE
        )
        
        return ETLStageStats(
            stage=PipelineStage.STAGE2_CRAWL4AI_SCRAPING,
            status=current_status,
            total_items_processed=web_scraper_stats.get('content_extracted', 0),
            items_processed_today=web_scraper_stats.get('content_extracted_today', 0),
            success_rate=web_scraper_stats.get('success_rate', 0.0),
            error_count=web_scraper_stats.get('total_errors', 0),
            avg_processing_time_seconds=web_scraper_stats.get('avg_scraping_time_seconds', 0.0),
            stage_specific_metrics={
                "urls_queued": web_scraper_stats.get('urls_queued', 0),
                "avg_scraping_time_seconds": web_scraper_stats.get('avg_scraping_time_seconds', 0.0),
                "llm_extraction_success_rate": web_scraper_stats.get('llm_extraction_success_rate', 0.0),
                "active_crawlers": web_scraper_stats.get('active_crawlers', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting Stage 2 stats: {e}")
        return ETLStageStats(
            stage=PipelineStage.STAGE2_CRAWL4AI_SCRAPING,
            status=ProcessingStatus.ERROR,
            total_items_processed=0,
            success_rate=0.0,
            stage_specific_metrics={"error": str(e)}
        )

async def _get_stage3_stats(db) -> ETLStageStats:
    """Get Stage 3 (Serper Enrichment) statistics from real pipeline"""
    pipeline = get_pipeline_instance()
    if not pipeline:
        return ETLStageStats(
            stage=PipelineStage.STAGE3_SERPER_ENRICHMENT,
            status=ProcessingStatus.IDLE,
            total_items_processed=0,
            success_rate=0.0,
            stage_specific_metrics={"error": "Pipeline instance unavailable"}
        )
    
    try:
        pipeline_status = pipeline.get_status()
        component_stats = pipeline_status.get('component_stats', {})
        news_collector_stats = component_stats.get('news_collector', {})
        
        # Map pipeline status
        status_mapping = {
            MasterPipelineStatus.RUNNING.value: ProcessingStatus.RUNNING,
            MasterPipelineStatus.STOPPED.value: ProcessingStatus.IDLE,
            MasterPipelineStatus.PAUSED.value: ProcessingStatus.PAUSED,
            MasterPipelineStatus.ERROR.value: ProcessingStatus.ERROR,
            MasterPipelineStatus.STARTING.value: ProcessingStatus.RUNNING,
            MasterPipelineStatus.STOPPING.value: ProcessingStatus.IDLE
        }
        
        current_status = status_mapping.get(
            pipeline_status.get('status', 'stopped'), 
            ProcessingStatus.IDLE
        )
        
        return ETLStageStats(
            stage=PipelineStage.STAGE3_SERPER_ENRICHMENT,
            status=current_status,
            total_items_processed=news_collector_stats.get('articles_collected', 0),
            items_processed_today=news_collector_stats.get('articles_collected_today', 0),
            success_rate=news_collector_stats.get('success_rate', 0.0),
            error_count=news_collector_stats.get('total_errors', 0),
            avg_processing_time_seconds=news_collector_stats.get('avg_search_time_seconds', 0.0),
            stage_specific_metrics={
                "records_needing_enrichment": news_collector_stats.get('records_needing_enrichment', 0),
                "avg_search_time_seconds": news_collector_stats.get('avg_search_time_seconds', 0.0),
                "fields_enriched_today": news_collector_stats.get('fields_enriched_today', 0),
                "api_quota_remaining": news_collector_stats.get('api_quota_remaining', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting Stage 3 stats: {e}")
        return ETLStageStats(
            stage=PipelineStage.STAGE3_SERPER_ENRICHMENT,
            status=ProcessingStatus.ERROR,
            total_items_processed=0,
            success_rate=0.0,
            stage_specific_metrics={"error": str(e)}
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

async def _get_recent_errors(db) -> List[Dict[str, Any]]:
    """Get recent error logs"""
    # TODO: Implement based on actual error logging system
    return []

async def _get_recent_successes(db) -> List[Dict[str, Any]]:
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

# =============================================================================
# LLM Usage Monitoring Endpoints
# =============================================================================

@router.get("/llm-usage", response_model=LLMProviderSummary)
async def get_llm_usage_stats():
    """Get comprehensive LLM provider usage statistics"""
    try:
        smart_provider = get_smart_llm_provider()
        usage_stats = smart_provider.get_usage_stats()
        
        # Calculate totals and savings
        total_requests = sum(stats.total_requests for stats in usage_stats.values())
        total_cost = sum(stats.estimated_cost_usd for stats in usage_stats.values())
        
        # Estimate cost if using only OpenAI (for savings calculation)
        deepseek_stats = usage_stats.get('deepseek')
        openai_cost_per_1k_input = 0.01  # GPT-4o-mini pricing
        openai_cost_per_1k_output = 0.03
        
        estimated_openai_only_cost = total_cost
        if deepseek_stats:
            estimated_openai_only_cost += (
                (deepseek_stats.total_tokens_input / 1000 * openai_cost_per_1k_input) +
                (deepseek_stats.total_tokens_output / 1000 * openai_cost_per_1k_output) -
                deepseek_stats.estimated_cost_usd
            )
        
        cost_savings = max(0, estimated_openai_only_cost - total_cost)
        
        # Determine primary provider and fallback count
        primary_provider = "deepseek" if deepseek_stats and deepseek_stats.total_requests > 0 else "openai"
        fallback_count = smart_provider.get_fallback_count()
        
        # Convert to response format
        provider_list = []
        for provider_name, stats in usage_stats.items():
            provider_list.append(LLMUsageStats(
                provider=provider_name,
                total_requests=stats.total_requests,
                successful_requests=stats.successful_requests,
                failed_requests=stats.failed_requests,
                total_tokens_input=stats.total_tokens_input,
                total_tokens_output=stats.total_tokens_output,
                estimated_cost_usd=stats.estimated_cost_usd,
                avg_response_time_ms=stats.avg_response_time_ms,
                last_used=stats.last_used,
                success_rate=stats.success_rate
            ))
        
        return LLMProviderSummary(
            total_requests=total_requests,
            total_cost_usd=total_cost,
            cost_savings_vs_openai_only=cost_savings,
            primary_provider=primary_provider,
            fallback_count=fallback_count,
            providers=provider_list
        )
        
    except Exception as e:
        logger.error(f"Failed to get LLM usage stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve LLM usage statistics: {str(e)}")

@router.get("/llm-usage/{provider}")
async def get_provider_usage_stats(provider: str):
    """Get detailed usage statistics for a specific LLM provider"""
    try:
        smart_provider = get_smart_llm_provider()
        usage_stats = smart_provider.get_usage_stats()
        
        if provider not in usage_stats:
            raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
        
        stats = usage_stats[provider]
        
        return {
            "provider": provider,
            "statistics": {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": stats.success_rate,
                "total_tokens_input": stats.total_tokens_input,
                "total_tokens_output": stats.total_tokens_output,
                "estimated_cost_usd": stats.estimated_cost_usd,
                "avg_response_time_ms": stats.avg_response_time_ms,
                "last_used": stats.last_used
            },
            "recent_tasks": smart_provider.get_recent_tasks(provider, limit=10)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider usage stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve provider statistics: {str(e)}")

@router.post("/llm-usage/reset")
async def reset_llm_usage_stats():
    """Reset LLM usage statistics (admin function)"""
    try:
        smart_provider = get_smart_llm_provider()
        smart_provider.reset_usage_stats()
        
        return {"message": "LLM usage statistics reset successfully"}
        
    except Exception as e:
        logger.error(f"Failed to reset LLM usage stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset usage statistics: {str(e)}")

@router.get("/smart-prioritization", response_model=Dict[str, Any])
async def get_smart_prioritization_metrics(db = Depends(get_admin_db)):
    """
    Get detailed smart RSS feed prioritization metrics
    
    Returns comprehensive metrics about adaptive feed scheduling including:
    - Performance tier distribution (high/medium/low performers)
    - Top performing sources with priority scores
    - Adaptive interval statistics
    - Source-level success rates and productivity metrics
    """
    try:
        pipeline = get_pipeline_instance()
        if not pipeline:
            raise HTTPException(status_code=503, detail="Pipeline not available")
        
        # Get high-volume pipeline for smart prioritization stats
        high_volume_pipeline = getattr(pipeline, 'high_volume_pipeline', None)
        if not high_volume_pipeline:
            return {
                "error": "Smart prioritization not available",
                "reason": "High-volume pipeline not initialized",
                "available_features": ["basic_etl_stats", "llm_usage", "balance_monitoring"]
            }
        
        # Get comprehensive smart prioritization statistics
        smart_stats = high_volume_pipeline.get_smart_prioritization_stats()
        
        # Add additional real-time metrics
        current_time = datetime.utcnow()
        smart_stats.update({
            "timestamp": current_time.isoformat(),
            "total_sources": len(high_volume_pipeline.sources),
            "active_sources": len([s for s in high_volume_pipeline.sources if s.enabled]),
            "sources_due_for_check": len([s for s in high_volume_pipeline.sources if s.should_check_now()]),
            "queue_status": {
                "source_queue_size": high_volume_pipeline.source_queue.qsize(),
                "processing_queue_size": high_volume_pipeline.processing_queue.qsize()
            },
            "monitoring_active": high_volume_pipeline.is_running
        })
        
        return smart_stats
        
    except Exception as e:
        logger.error(f"Failed to get smart prioritization metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/dashboard", response_model=ETLDashboard)
async def get_etl_dashboard(db = Depends(get_admin_db)):
    """Get comprehensive ETL dashboard with pipeline stats, LLM usage, notifications, and smart prioritization"""
    try:
        # Get existing ETL stats
        pipeline_stats = await get_live_etl_stats(db)
        
        # Get LLM usage stats
        llm_stats = await get_llm_usage_stats()
        
        # Get account balance information
        from app.services.balance_monitoring import get_balance_monitor
        balance_monitor = get_balance_monitor()
        
        # Get cached balances or refresh if needed
        cached_balances = balance_monitor.get_cached_balances()
        if not cached_balances or not balance_monitor.last_check or \
           (datetime.utcnow() - balance_monitor.last_check).total_seconds() > 3600:
            try:
                async with balance_monitor:
                    cached_balances = await balance_monitor.check_all_balances()
            except Exception as e:
                logger.warning(f"Failed to refresh balance data: {e}")
        
        # Process balance data for dashboard
        total_balance = 0.0
        warning_count = 0
        critical_count = 0
        balance_list = []
        
        for provider_type, balance in cached_balances.items():
            balance_data = {
                "provider": provider_type.value,
                "balance_usd": balance.balance_usd,
                "status": balance.status,
                "usage_current_month_usd": balance.usage_current_month_usd,
                "days_remaining": balance.days_remaining,
                "last_updated": balance.last_updated.isoformat()
            }
            balance_list.append(balance_data)
            
            total_balance += balance.balance_usd
            if balance.status == "warning":
                warning_count += 1
            elif balance.status == "critical":
                critical_count += 1
        
        balance_summary = BalanceSummary(
            total_providers=len(cached_balances),
            active_providers=len(cached_balances) - warning_count - critical_count,
            warning_providers=warning_count,
            critical_providers=critical_count,
            total_balance_usd=total_balance,
            balances=balance_list,
            last_updated=balance_monitor.last_check
        )
        
        # Get notification system status
        notification_system = get_notification_system()
        active_alerts = notification_system.get_active_alerts()
        
        # Count alerts by level
        critical_alerts = len([a for a in active_alerts if a.level == AlertLevel.CRITICAL])
        warning_alerts = len([a for a in active_alerts if a.level == AlertLevel.WARNING])
        
        # Get recent alerts (last 5)
        recent_alerts = [{
            "id": alert.id,
            "category": alert.category.value,
            "level": alert.level.value,
            "title": alert.title,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        } for alert in active_alerts[:5]]
        
        notifications_summary = NotificationSummary(
            active_alerts=len(active_alerts),
            critical_alerts=critical_alerts,
            warning_alerts=warning_alerts,
            monitoring_active=notification_system.monitoring_active,
            enabled_channels=len([c for c in notification_system.channels.values() if c.enabled]),
            recent_alerts=recent_alerts
        )
        
        # Get smart prioritization metrics if available
        smart_prioritization_summary = None
        try:
            smart_metrics = await get_smart_prioritization_metrics(db)
            if "error" not in smart_metrics:
                smart_prioritization_summary = {
                    "high_performers": smart_metrics.get("performance_tiers", {}).get("high_performers", 0),
                    "medium_performers": smart_metrics.get("performance_tiers", {}).get("medium_performers", 0),
                    "low_performers": smart_metrics.get("performance_tiers", {}).get("low_performers", 0),
                    "avg_success_rate": smart_metrics.get("average_metrics", {}).get("success_rate", 0),
                    "fastest_interval": smart_metrics.get("adaptive_intervals", {}).get("fastest_interval", 60),
                    "slowest_interval": smart_metrics.get("adaptive_intervals", {}).get("slowest_interval", 60),
                    "sources_due_for_check": smart_metrics.get("sources_due_for_check", 0)
                }
        except Exception as e:
            logger.debug(f"Smart prioritization metrics not available: {e}")
        
        # Generate real-time metrics
        real_time_metrics = {
            "current_time": datetime.utcnow().isoformat(),
            "system_health": "critical" if critical_alerts > 0 else "warning" if warning_alerts > 0 else "operational",
            "active_processes": sum(1 for stage in pipeline_stats.stage_stats if stage.status == ProcessingStatus.RUNNING),
            "total_opportunities_processed": pipeline_stats.total_opportunities_in_db,
            "pipeline_uptime_hours": pipeline_stats.total_processing_time_hours,
            "smart_prioritization": smart_prioritization_summary
        }
        
        # Generate system health summary
        system_health = {
            "overall_status": real_time_metrics["system_health"],
            "pipeline_operational": pipeline_stats.pipeline_status != ProcessingStatus.ERROR,
            "llm_providers_healthy": all(provider.success_rate > 0.8 for provider in llm_stats.providers),
            "notifications_active": notification_system.monitoring_active,
            "data_quality_score": pipeline_stats.data_completeness_score,
            "cost_efficiency": {
                "total_llm_cost": llm_stats.total_cost_usd,
                "cost_savings": llm_stats.cost_savings_vs_openai_only,
                "primary_provider": llm_stats.primary_provider
            }
        }
        
        # Enhanced dashboard with comprehensive monitoring
        dashboard = ETLDashboard(
            pipeline_status=pipeline_stats,
            real_time_metrics=real_time_metrics,
            llm_usage=llm_stats,
            account_balances=balance_summary,
            notifications=notifications_summary,
            alerts=await _generate_dashboard_alerts(pipeline_stats, llm_stats),
            system_health=system_health,
            last_updated=datetime.utcnow()
        )
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Failed to generate ETL dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

async def _generate_dashboard_alerts(pipeline_stats: ETLOverallStats, llm_stats: LLMProviderSummary) -> List[Dict[str, Any]]:
    """Generate alerts for dashboard based on pipeline and LLM metrics"""
    alerts = []
    
    # Pipeline alerts
    if pipeline_stats.stage_stats:
        for stage in pipeline_stats.stage_stats:
            if stage.error_count > 10:
                alerts.append({
                    "type": "warning",
                    "category": "pipeline",
                    "message": f"High error count in {stage.stage.value}: {stage.error_count} errors",
                    "timestamp": datetime.utcnow()
                })
    
    # LLM usage alerts
    for provider in llm_stats.providers:
        # High failure rate alert
        if provider.success_rate < 0.9 and provider.total_requests > 10:
            alerts.append({
                "type": "error",
                "category": "llm",
                "message": f"{provider.provider} has low success rate: {provider.success_rate:.1%}",
                "timestamp": datetime.utcnow()
            })
        
        # High cost alert (over $10/day estimated)
        daily_cost_estimate = provider.estimated_cost_usd * 24  # Rough daily estimate
        if daily_cost_estimate > 10:
            alerts.append({
                "type": "warning",
                "category": "cost",
                "message": f"{provider.provider} estimated daily cost: ${daily_cost_estimate:.2f}",
                "timestamp": datetime.utcnow()
            })
    
    # Cost savings celebration
    if llm_stats.cost_savings_vs_openai_only > 5:
        alerts.append({
            "type": "info",
            "category": "savings",
            "message": f"DeepSeek integration saving ${llm_stats.cost_savings_vs_openai_only:.2f} vs OpenAI-only",
            "timestamp": datetime.utcnow()
        })
    
    return alerts
