"""
User Submissions API Endpoints
Handles Method 1: User submissions from Next.js frontend
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import logging

from app.services.unified_scraper import UnifiedScraperModule, InputSource
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class UserSubmissionCreate(BaseModel):
    """Schema for user submission creation"""
    title: str
    organization: str
    description: str
    url: str
    amount: Optional[float] = None
    currency: str = "USD"
    deadline: Optional[str] = None
    contact_email: Optional[str] = None
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('organization')
    def organization_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Organization cannot be empty')
        return v.strip()
    
    @validator('url')
    def url_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        # Basic URL validation
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()
    
    @validator('currency')
    def currency_must_be_valid(cls, v):
        valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'ZAR', 'NGN', 'KES', 'GHS']
        if v not in valid_currencies:
            raise ValueError(f'Currency must be one of: {", ".join(valid_currencies)}')
        return v

class UserSubmissionResponse(BaseModel):
    """Response schema for user submission"""
    status: str
    opportunity_id: Optional[int] = None
    validation_score: Optional[float] = None
    requires_review: bool = False
    message: str
    submission_id: str

@router.post("/create", response_model=UserSubmissionResponse)
async def create_user_submission(
    submission: UserSubmissionCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Create a new funding opportunity submission from a user
    
    This endpoint handles Method 1 of the data importation system:
    - Validates user input
    - Processes through unified scraper
    - Returns immediate response
    - Queues for validation review if needed
    """
    logger.info(f"📝 Received user submission: {submission.title}")
    
    try:
        # Initialize unified scraper
        scraper = UnifiedScraperModule()
        
        # Prepare input data for unified scraper
        input_data = {
            "source": InputSource.USER_SUBMISSION.value,
            "data": submission.dict(),
            "priority": "high",  # User submissions get high priority
            "validation_required": True
        }
        
        # Process through unified scraper
        result = await scraper.process_input(input_data)
        
        if result["status"] == "success":
            submission_id = f"user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{result['opportunity_id']}"
            
            # If requires review, add to background task
            if result.get("requires_review", False):
                background_tasks.add_task(
                    _queue_for_community_review,
                    result["opportunity_id"],
                    submission.dict(),
                    result["validation_score"]
                )
            
            return UserSubmissionResponse(
                status="success",
                opportunity_id=result["opportunity_id"],
                validation_score=result.get("validation_score"),
                requires_review=result.get("requires_review", False),
                message="Submission received and processed successfully!",
                submission_id=submission_id
            )
        
        elif result["status"] == "validation_error":
            raise HTTPException(
                status_code=400,
                detail=f"Validation error: {result['error']}"
            )
        
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Processing error: {result.get('error', 'Unknown error')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing user submission: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing submission"
        )

@router.get("/status/{submission_id}")
async def get_submission_status(submission_id: str, db = Depends(get_db)):
    """
    Get the status of a user submission
    
    Allows users to track their submission through the review process
    """
    logger.info(f"📊 Status check for submission: {submission_id}")
    
    try:
        # Extract opportunity ID from submission ID
        if not submission_id.startswith("user_"):
            raise HTTPException(status_code=400, detail="Invalid submission ID format")
        
        parts = submission_id.split("_")
        if len(parts) < 3:
            raise HTTPException(status_code=400, detail="Invalid submission ID format")
        
        opportunity_id = parts[-1]
        
        # Query database for opportunity status
        # This would query your actual database
        # For now, return a mock response
        
        return {
            "submission_id": submission_id,
            "status": "under_review",
            "submitted_at": "2024-01-01T12:00:00Z",
            "validation_score": 0.85,
            "review_status": "pending_community_review",
            "estimated_review_time": "24-48 hours",
            "notes": "Your submission is in the community review queue"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting submission status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving submission status")

@router.get("/submissions/recent")
async def get_recent_submissions(
    limit: int = 10,
    skip: int = 0,
    db = Depends(get_db)
):
    """
    Get recent user submissions (for admin/community review)
    
    Returns recent submissions that may need review
    """
    logger.info(f"📋 Fetching recent submissions (limit: {limit}, skip: {skip})")
    
    try:
        # This would query your actual database
        # For now, return mock data
        mock_submissions = [
            {
                "id": 1,
                "title": "AI for Healthcare Innovation Grant",
                "organization": "Gates Foundation",
                "submitted_at": "2024-01-01T10:00:00Z",
                "validation_score": 0.92,
                "status": "approved",
                "submitted_by": "user123"
            },
            {
                "id": 2,
                "title": "Digital Agriculture Development Fund",
                "organization": "World Bank",
                "submitted_at": "2024-01-01T09:00:00Z",
                "validation_score": 0.78,
                "status": "under_review",
                "submitted_by": "user456"
            }
        ]
        
        return {
            "submissions": mock_submissions[skip:skip+limit],
            "total": len(mock_submissions),
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching recent submissions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching submissions")

async def _queue_for_community_review(opportunity_id: int, submission_data: dict, validation_score: float):
    """
    Background task to queue submission for community review
    
    This would integrate with your community review system
    """
    logger.info(f"📬 Queuing opportunity {opportunity_id} for community review (score: {validation_score})")
    
    try:
        # Add to community review queue
        # This would integrate with your notification system
        # For now, just log the action
        
        review_data = {
            "opportunity_id": opportunity_id,
            "submission_data": submission_data,
            "validation_score": validation_score,
            "queued_at": datetime.utcnow().isoformat(),
            "review_deadline": "24_hours"
        }
        
        logger.info(f"✅ Successfully queued {opportunity_id} for review")
        
        # Future: Send notification emails, add to review dashboard, etc.
        
    except Exception as e:
        logger.error(f"❌ Error queuing submission for review: {e}")

# Health check endpoint
@router.get("/health")
async def submissions_health_check():
    """Health check for user submissions service"""
    return {
        "status": "healthy",
        "service": "user_submissions",
        "timestamp": datetime.utcnow().isoformat(),
        "methods_supported": ["create", "status_check", "recent_list"]
    }
