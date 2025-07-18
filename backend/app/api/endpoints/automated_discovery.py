"""
Automated Discovery API Endpoints  
Handles Method 3: Automated discovery through Serper searches and scheduled monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid

from app.services.unified_scraper import UnifiedScraperModule, InputSource, ProcessingPriority
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class SearchType(str, Enum):
    """Types of automated searches"""
    GENERAL = "general"
    TARGETED = "targeted"
    GEOGRAPHIC = "geographic"
    SECTOR_SPECIFIC = "sector_specific"

class DiscoveryJobCreate(BaseModel):
    """Schema for creating automated discovery job"""
    search_terms: Optional[List[str]] = None
    search_type: SearchType = SearchType.GENERAL
    priority: ProcessingPriority = ProcessingPriority.MEDIUM
    max_results: int = 50
    geographic_focus: Optional[List[str]] = None  # African countries to focus on
    ai_domains: Optional[List[str]] = None  # AI domains to focus on
    
    @validator('max_results')
    def max_results_validation(cls, v):
        if v < 1 or v > 200:
            raise ValueError('max_results must be between 1 and 200')
        return v
    
    @validator('search_terms')
    def search_terms_validation(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 search terms allowed')
        return v

class DiscoveryJobResponse(BaseModel):
    """Response schema for discovery job creation"""
    job_id: str
    status: str
    search_type: str
    created_at: str
    estimated_completion: str

class DiscoveryJobStatus(BaseModel):
    """Schema for discovery job status"""
    job_id: str
    status: str
    search_type: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    search_results_found: int = 0
    opportunities_discovered: int = 0
    opportunities_saved: int = 0
    duplicates: int = 0
    average_relevance_score: Optional[float] = None
    error_message: Optional[str] = None
    processing_log: List[str] = []

class ScheduledDiscoveryCreate(BaseModel):
    """Schema for creating scheduled discovery tasks"""
    name: str
    search_terms: List[str]
    schedule_type: str  # "daily", "weekly", "monthly"
    search_type: SearchType = SearchType.GENERAL
    priority: ProcessingPriority = ProcessingPriority.LOW
    is_active: bool = True
    
    @validator('schedule_type')
    def schedule_type_validation(cls, v):
        valid_schedules = ["daily", "weekly", "monthly"]
        if v not in valid_schedules:
            raise ValueError(f'schedule_type must be one of: {", ".join(valid_schedules)}')
        return v

# In-memory storage for discovery jobs and schedules
discovery_jobs: Dict[str, Dict[str, Any]] = {}
scheduled_discoveries: Dict[str, Dict[str, Any]] = {}

@router.post("/start-discovery", response_model=DiscoveryJobResponse)
async def start_discovery(
    discovery_request: DiscoveryJobCreate,
    background_tasks: BackgroundTasks
):
    """
    Start an automated discovery job
    
    This endpoint handles Method 3 of the data importation system:
    - Initiates Serper searches with specified parameters
    - Discovers new intelligence feed automatically
    - Returns job ID for status tracking
    - Processes in background
    """
    logger.info(f"🤖 Starting automated discovery job: {discovery_request.search_type}")
    
    try:
        # Generate unique job ID
        job_id = f"discovery_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create job record
        job_data = {
            "job_id": job_id,
            "search_type": discovery_request.search_type.value,
            "search_terms": discovery_request.search_terms,
            "priority": discovery_request.priority.value,
            "max_results": discovery_request.max_results,
            "geographic_focus": discovery_request.geographic_focus,
            "ai_domains": discovery_request.ai_domains,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "processing_log": [f"Discovery job created at {datetime.utcnow().isoformat()}"]
        }
        
        # Store job in discovery jobs
        discovery_jobs[job_id] = job_data
        
        # Queue background processing
        background_tasks.add_task(
            _process_discovery_job,
            job_id,
            discovery_request.dict()
        )
        
        # Estimate completion time based on search complexity
        completion_estimates = {
            SearchType.GENERAL: "3-8 minutes",
            SearchType.TARGETED: "5-12 minutes",
            SearchType.GEOGRAPHIC: "4-10 minutes", 
            SearchType.SECTOR_SPECIFIC: "6-15 minutes"
        }
        
        return DiscoveryJobResponse(
            job_id=job_id,
            status="queued",
            search_type=discovery_request.search_type.value,
            created_at=job_data["created_at"],
            estimated_completion=completion_estimates[discovery_request.search_type]
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating discovery job: {e}")
        raise HTTPException(status_code=500, detail="Error creating discovery job")

@router.get("/jobs/{job_id}", response_model=DiscoveryJobStatus)
async def get_discovery_job_status(job_id: str):
    """
    Get the status of a specific discovery job
    
    Allows tracking progress of automated discovery
    """
    logger.info(f"📊 Status check for discovery job: {job_id}")
    
    if job_id not in discovery_jobs:
        raise HTTPException(status_code=404, detail="Discovery job not found")
    
    job_data = discovery_jobs[job_id]
    
    return DiscoveryJobStatus(
        job_id=job_data["job_id"],
        status=job_data["status"],
        search_type=job_data["search_type"],
        created_at=job_data["created_at"],
        started_at=job_data.get("started_at"),
        completed_at=job_data.get("completed_at"),
        search_results_found=job_data.get("search_results_found", 0),
        opportunities_discovered=job_data.get("opportunities_discovered", 0),
        opportunities_saved=job_data.get("opportunities_saved", 0),
        duplicates=job_data.get("duplicates", 0),
        average_relevance_score=job_data.get("average_relevance_score"),
        error_message=job_data.get("error_message"),
        processing_log=job_data.get("processing_log", [])
    )

@router.get("/jobs")
async def list_discovery_jobs(
    status: Optional[str] = None,
    search_type: Optional[SearchType] = None,
    limit: int = 20,
    skip: int = 0
):
    """
    List discovery jobs with optional filtering
    
    Provides overview of all automated discovery activities
    """
    logger.info(f"📋 Listing discovery jobs (status: {status}, type: {search_type})")
    
    try:
        jobs = list(discovery_jobs.values())
        
        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job["status"] == status]
        
        # Filter by search type if provided
        if search_type:
            jobs = [job for job in jobs if job["search_type"] == search_type.value]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_jobs = jobs[skip:skip+limit]
        
        return {
            "jobs": paginated_jobs,
            "total": len(jobs),
            "limit": limit,
            "skip": skip,
            "available_statuses": ["queued", "processing", "completed", "failed"],
            "available_search_types": [t.value for t in SearchType]
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing discovery jobs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving discovery jobs")

@router.post("/schedule")
async def create_scheduled_discovery(schedule: ScheduledDiscoveryCreate):
    """
    Create a scheduled discovery task
    
    Allows setting up recurring automated discovery jobs
    """
    logger.info(f"⏰ Creating scheduled discovery: {schedule.name}")
    
    try:
        # Generate unique schedule ID
        schedule_id = f"schedule_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Calculate next run time
        now = datetime.utcnow()
        if schedule.schedule_type == "daily":
            next_run = now + timedelta(days=1)
        elif schedule.schedule_type == "weekly":
            next_run = now + timedelta(weeks=1)
        else:  # monthly
            next_run = now + timedelta(days=30)
        
        # Create schedule record
        schedule_data = {
            "schedule_id": schedule_id,
            "name": schedule.name,
            "search_terms": schedule.search_terms,
            "schedule_type": schedule.schedule_type,
            "search_type": schedule.search_type.value,
            "priority": schedule.priority.value,
            "is_active": schedule.is_active,
            "created_at": now.isoformat(),
            "next_run": next_run.isoformat(),
            "last_run": None,
            "total_runs": 0,
            "total_opportunities_found": 0
        }
        
        # Store schedule
        scheduled_discoveries[schedule_id] = schedule_data
        
        return {
            "schedule_id": schedule_id,
            "name": schedule.name,
            "status": "active" if schedule.is_active else "inactive",
            "next_run": next_run.isoformat(),
            "message": "Scheduled discovery created successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating scheduled discovery: {e}")
        raise HTTPException(status_code=500, detail="Error creating scheduled discovery")

@router.get("/schedules")
async def list_scheduled_discoveries():
    """
    List all scheduled discovery tasks
    
    Shows recurring discovery jobs and their schedules
    """
    logger.info("📅 Listing scheduled discoveries")
    
    try:
        schedules = list(scheduled_discoveries.values())
        
        # Sort by next run time
        schedules.sort(key=lambda x: x["next_run"])
        
        return {
            "schedules": schedules,
            "total": len(schedules),
            "active": len([s for s in schedules if s["is_active"]]),
            "inactive": len([s for s in schedules if not s["is_active"]])
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing scheduled discoveries: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving scheduled discoveries")

@router.patch("/schedules/{schedule_id}")
async def update_scheduled_discovery(
    schedule_id: str,
    is_active: Optional[bool] = None,
    search_terms: Optional[List[str]] = None
):
    """
    Update a scheduled discovery task
    
    Allows enabling/disabling schedules or updating search terms
    """
    logger.info(f"✏️ Updating scheduled discovery: {schedule_id}")
    
    if schedule_id not in scheduled_discoveries:
        raise HTTPException(status_code=404, detail="Scheduled discovery not found")
    
    try:
        schedule_data = scheduled_discoveries[schedule_id]
        
        # Update fields if provided
        if is_active is not None:
            schedule_data["is_active"] = is_active
        
        if search_terms is not None:
            schedule_data["search_terms"] = search_terms
        
        schedule_data["updated_at"] = datetime.utcnow().isoformat()
        
        return {
            "schedule_id": schedule_id,
            "message": "Scheduled discovery updated successfully",
            "is_active": schedule_data["is_active"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error updating scheduled discovery: {e}")
        raise HTTPException(status_code=500, detail="Error updating scheduled discovery")

@router.get("/analytics/summary")
async def get_discovery_analytics():
    """
    Get analytics summary for automated discovery
    
    Provides insights into discovery performance and results
    """
    logger.info("📊 Getting discovery analytics")
    
    try:
        # Calculate analytics from discovery jobs
        completed_jobs = [job for job in discovery_jobs.values() if job["status"] == "completed"]
        
        total_opportunities = sum(job.get("opportunities_discovered", 0) for job in completed_jobs)
        total_saved = sum(job.get("opportunities_saved", 0) for job in completed_jobs)
        
        # Calculate averages
        avg_relevance = None
        if completed_jobs:
            relevance_scores = [job.get("average_relevance_score", 0) for job in completed_jobs if job.get("average_relevance_score")]
            if relevance_scores:
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_jobs = [
            job for job in discovery_jobs.values() 
            if datetime.fromisoformat(job["created_at"]) > week_ago
        ]
        
        return {
            "summary": {
                "total_discovery_jobs": len(discovery_jobs),
                "completed_jobs": len(completed_jobs),
                "total_opportunities_discovered": total_opportunities,
                "total_opportunities_saved": total_saved,
                "average_relevance_score": round(avg_relevance, 3) if avg_relevance else None,
                "save_rate": round(total_saved / total_opportunities * 100, 1) if total_opportunities > 0 else 0
            },
            "recent_activity": {
                "jobs_last_7_days": len(recent_jobs),
                "opportunities_last_7_days": sum(job.get("opportunities_discovered", 0) for job in recent_jobs)
            },
            "scheduled_discoveries": {
                "total_schedules": len(scheduled_discoveries),
                "active_schedules": len([s for s in scheduled_discoveries.values() if s["is_active"]])
            },
            "search_type_breakdown": self._get_search_type_breakdown()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting discovery analytics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")

def _get_search_type_breakdown():
    """Get breakdown of discovery jobs by search type"""
    breakdown = {}
    for job in discovery_jobs.values():
        search_type = job["search_type"]
        if search_type not in breakdown:
            breakdown[search_type] = {"count": 0, "opportunities": 0}
        
        breakdown[search_type]["count"] += 1
        breakdown[search_type]["opportunities"] += job.get("opportunities_discovered", 0)
    
    return breakdown

async def _process_discovery_job(job_id: str, discovery_request: dict):
    """
    Background task to process automated discovery job
    
    This handles the actual discovery work in the background
    """
    logger.info(f"🔄 Processing discovery job: {job_id}")
    
    try:
        # Update job status
        job_data = discovery_jobs[job_id]
        job_data["status"] = "processing"
        job_data["started_at"] = datetime.utcnow().isoformat()
        job_data["processing_log"].append(f"Processing started at {datetime.utcnow().isoformat()}")
        
        # Initialize unified scraper
        scraper = UnifiedScraperModule()
        
        # Prepare input data for unified scraper
        input_data = {
            "source": InputSource.AUTOMATED_DISCOVERY.value,
            "data": {
                "search_terms": discovery_request.get("search_terms"),
                "search_type": discovery_request["search_type"],
                "max_results": discovery_request["max_results"],
                "geographic_focus": discovery_request.get("geographic_focus"),
                "ai_domains": discovery_request.get("ai_domains")
            },
            "priority": discovery_request["priority"]
        }
        
        # Process through unified scraper
        result = await scraper.process_input(input_data)
        
        # Update job with results
        if result["status"] == "success":
            job_data["status"] = "completed"
            job_data["opportunities_discovered"] = result.get("opportunities_found", 0)
            job_data["opportunities_saved"] = result.get("opportunities_saved", 0)
            job_data["duplicates"] = result.get("duplicates", 0)
            job_data["processing_log"].append(f"Discovery completed successfully at {datetime.utcnow().isoformat()}")
            job_data["processing_log"].append(f"Discovered {result.get('opportunities_found', 0)} opportunities")
            
            # Calculate average relevance score if available
            # This would come from the validation scores in the actual implementation
            job_data["average_relevance_score"] = 0.78  # Mock value for now
            
        else:
            job_data["status"] = "failed"
            job_data["error_message"] = result.get("error", "Unknown error")
            job_data["processing_log"].append(f"Discovery failed at {datetime.utcnow().isoformat()}: {result.get('error')}")
        
        job_data["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Completed discovery job {job_id} with status: {job_data['status']}")
        
        # Clean up scraper
        await scraper.close()
        
    except Exception as e:
        logger.error(f"❌ Error processing discovery job {job_id}: {e}")
        
        # Update job with error
        job_data = discovery_jobs[job_id]
        job_data["status"] = "failed"
        job_data["error_message"] = str(e)
        job_data["completed_at"] = datetime.utcnow().isoformat()
        job_data["processing_log"].append(f"Discovery failed with error at {datetime.utcnow().isoformat()}: {str(e)}")

# Health check endpoint
@router.get("/health")
async def discovery_health_check():
    """Health check for automated discovery service"""
    active_jobs_count = len([job for job in discovery_jobs.values() if job["status"] in ["queued", "processing"]])
    active_schedules_count = len([s for s in scheduled_discoveries.values() if s["is_active"]])
    
    return {
        "status": "healthy",
        "service": "automated_discovery",
        "timestamp": datetime.utcnow().isoformat(),
        "active_discovery_jobs": active_jobs_count,
        "total_discovery_jobs": len(discovery_jobs),
        "active_schedules": active_schedules_count,
        "total_schedules": len(scheduled_discoveries),
        "methods_supported": ["start_discovery", "schedule_discovery", "job_status", "analytics"]
    }
