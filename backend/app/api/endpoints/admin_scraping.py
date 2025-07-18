"""
Admin Portal Scraping API Endpoints
Handles Method 2: Admin-initiated URL scraping through Streamlit portal
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import logging
import uuid

from app.services.unified_scraper import UnifiedScraperModule, InputSource, ProcessingPriority
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class SourceType(str, Enum):
    """Types of funding sources"""
    FOUNDATION = "foundation"
    GOVERNMENT = "government"
    CORPORATE = "corporate"
    ACADEMIC = "academic"
    MULTILATERAL = "multilateral"
    NGO = "ngo"
    UNKNOWN = "unknown"

class ScrapingJobCreate(BaseModel):
    """Schema for creating a new scraping job"""
    url: str
    source_type: SourceType = SourceType.UNKNOWN
    priority: ProcessingPriority = ProcessingPriority.MEDIUM
    description: Optional[str] = None
    admin_notes: Optional[str] = None
    
    @validator('url')
    def url_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        # Basic URL validation
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()

class ScrapingJobResponse(BaseModel):
    """Response schema for scraping job creation"""
    job_id: str
    status: str
    url: str
    created_at: str
    estimated_completion: str

class ScrapingJobStatus(BaseModel):
    """Schema for scraping job status"""
    job_id: str
    status: str
    url: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    opportunities_found: int = 0
    opportunities_saved: int = 0
    duplicates: int = 0
    error_message: Optional[str] = None
    processing_log: List[str] = []

# In-memory job storage (in production, use Redis or database)
active_jobs: Dict[str, Dict[str, Any]] = {}

@router.post("/process-url", response_model=ScrapingJobResponse)
async def process_url(
    job_request: ScrapingJobCreate,
    background_tasks: BackgroundTasks,
    admin_id: Optional[str] = None
):
    """
    Process a URL through the admin portal scraping system
    
    This endpoint handles Method 2 of the data importation system:
    - Accepts URL from Streamlit admin portal
    - Initiates Crawl4AI processing
    - Returns job ID for status tracking
    - Processes in background
    """
    logger.info(f"🛠️ Admin portal URL processing request: {job_request.url}")
    
    try:
        # Generate unique job ID
        job_id = f"admin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create job record
        job_data = {
            "job_id": job_id,
            "url": job_request.url,
            "source_type": job_request.source_type.value,
            "priority": job_request.priority.value,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "admin_id": admin_id,
            "description": job_request.description,
            "admin_notes": job_request.admin_notes,
            "processing_log": [f"Job created at {datetime.utcnow().isoformat()}"]
        }
        
        # Store job in active jobs
        active_jobs[job_id] = job_data
        
        # Queue background processing
        background_tasks.add_task(
            _process_admin_url_job,
            job_id,
            job_request.dict()
        )
        
        # Estimate completion time based on priority
        completion_estimates = {
            ProcessingPriority.HIGH: "2-5 minutes",
            ProcessingPriority.MEDIUM: "5-10 minutes", 
            ProcessingPriority.LOW: "10-20 minutes"
        }
        
        return ScrapingJobResponse(
            job_id=job_id,
            status="queued",
            url=job_request.url,
            created_at=job_data["created_at"],
            estimated_completion=completion_estimates[job_request.priority]
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating scraping job: {e}")
        raise HTTPException(status_code=500, detail="Error creating scraping job")

@router.get("/jobs/{job_id}", response_model=ScrapingJobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a specific scraping job
    
    Allows admin to track progress of URL processing
    """
    logger.info(f"📊 Status check for job: {job_id}")
    
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = active_jobs[job_id]
    
    return ScrapingJobStatus(
        job_id=job_data["job_id"],
        status=job_data["status"],
        url=job_data["url"],
        created_at=job_data["created_at"],
        started_at=job_data.get("started_at"),
        completed_at=job_data.get("completed_at"),
        opportunities_found=job_data.get("opportunities_found", 0),
        opportunities_saved=job_data.get("opportunities_saved", 0),
        duplicates=job_data.get("duplicates", 0),
        error_message=job_data.get("error_message"),
        processing_log=job_data.get("processing_log", [])
    )

@router.get("/jobs")
async def list_active_jobs(
    status: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """
    List active scraping jobs with optional filtering
    
    Provides admin dashboard view of all scraping activities
    """
    logger.info(f"📋 Listing active jobs (status: {status}, limit: {limit})")
    
    try:
        jobs = list(active_jobs.values())
        
        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job["status"] == status]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_jobs = jobs[skip:skip+limit]
        
        return {
            "jobs": paginated_jobs,
            "total": len(jobs),
            "limit": limit,
            "skip": skip,
            "available_statuses": ["queued", "processing", "completed", "failed"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving jobs")

@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a queued or processing job
    
    Allows admin to stop jobs that are taking too long or are incorrect
    """
    logger.info(f"⏹️ Canceling job: {job_id}")
    
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = active_jobs[job_id]
    
    if job_data["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed job")
    
    # Mark job as cancelled
    job_data["status"] = "cancelled"
    job_data["completed_at"] = datetime.utcnow().isoformat()
    job_data["processing_log"].append(f"Job cancelled at {datetime.utcnow().isoformat()}")
    
    return {"message": "Job cancelled successfully", "job_id": job_id}

@router.post("/bulk-process")
async def bulk_process_urls(
    urls: List[str],
    background_tasks: BackgroundTasks,
    source_type: SourceType = SourceType.UNKNOWN,
    priority: ProcessingPriority = ProcessingPriority.LOW,
):
    """
    Process multiple URLs in bulk
    
    Useful for processing a list of known funding source URLs
    """
    logger.info(f"📦 Bulk processing {len(urls)} URLs")
    
    if len(urls) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 URLs per bulk request")
    
    job_ids = []
    
    for url in urls:
        try:
            # Create individual job for each URL
            job_request = ScrapingJobCreate(
                url=url,
                source_type=source_type,
                priority=priority,
                description=f"Bulk processing batch"
            )
            
            # Generate job ID
            job_id = f"bulk_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            # Create job record
            job_data = {
                "job_id": job_id,
                "url": url,
                "source_type": source_type.value,
                "priority": priority.value,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat(),
                "processing_log": [f"Bulk job created at {datetime.utcnow().isoformat()}"]
            }
            
            active_jobs[job_id] = job_data
            job_ids.append(job_id)
            
            # Queue processing with slight delay to avoid overwhelming
            background_tasks.add_task(
                _process_admin_url_job,
                job_id,
                job_request.dict(),
                delay_seconds=len(job_ids) * 2  # Stagger processing
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating bulk job for {url}: {e}")
    
    return {
        "message": f"Created {len(job_ids)} bulk processing jobs",
        "job_ids": job_ids,
        "total_urls": len(urls),
        "estimated_completion": f"{len(urls) * 2} minutes"
    }

async def _process_admin_url_job(job_id: str, job_request: dict, delay_seconds: int = 0):
    """
    Background task to process admin URL scraping job
    
    This handles the actual scraping work in the background
    """
    import asyncio
    
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
    
    logger.info(f"🔄 Processing admin URL job: {job_id}")
    
    try:
        # Update job status
        job_data = active_jobs[job_id]
        job_data["status"] = "processing"
        job_data["started_at"] = datetime.utcnow().isoformat()
        job_data["processing_log"].append(f"Processing started at {datetime.utcnow().isoformat()}")
        
        # Initialize unified scraper
        scraper = UnifiedScraperModule()
        
        # Prepare input data for unified scraper
        input_data = {
            "source": InputSource.ADMIN_PORTAL.value,
            "data": {
                "url": job_request["url"],
                "source_type": job_request["source_type"]
            },
            "priority": job_request["priority"]
        }
        
        # Process through unified scraper
        result = await scraper.process_input(input_data)
        
        # Update job with results
        if result["status"] == "success":
            job_data["status"] = "completed"
            job_data["opportunities_found"] = result.get("opportunities_found", 0)
            job_data["opportunities_saved"] = result.get("opportunities_saved", 0)
            job_data["duplicates"] = result.get("duplicates", 0)
            job_data["processing_log"].append(f"Processing completed successfully at {datetime.utcnow().isoformat()}")
            job_data["processing_log"].append(f"Found {result.get('opportunities_found', 0)} opportunities")
            
        else:
            job_data["status"] = "failed"
            job_data["error_message"] = result.get("error", "Unknown error")
            job_data["processing_log"].append(f"Processing failed at {datetime.utcnow().isoformat()}: {result.get('error')}")
        
        job_data["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Completed processing job {job_id} with status: {job_data['status']}")
        
        # Clean up scraper
        await scraper.close()
        
    except Exception as e:
        logger.error(f"❌ Error processing job {job_id}: {e}")
        
        # Update job with error
        job_data = active_jobs[job_id]
        job_data["status"] = "failed"
        job_data["error_message"] = str(e)
        job_data["completed_at"] = datetime.utcnow().isoformat()
        job_data["processing_log"].append(f"Processing failed with error at {datetime.utcnow().isoformat()}: {str(e)}")

# Health check endpoint
@router.get("/health")
async def admin_scraping_health_check():
    """Health check for admin scraping service"""
    active_count = len([job for job in active_jobs.values() if job["status"] in ["queued", "processing"]])
    
    return {
        "status": "healthy",
        "service": "admin_scraping",
        "timestamp": datetime.utcnow().isoformat(),
        "active_jobs": active_count,
        "total_jobs": len(active_jobs),
        "methods_supported": ["process_url", "bulk_process", "job_status", "list_jobs"]
    }
