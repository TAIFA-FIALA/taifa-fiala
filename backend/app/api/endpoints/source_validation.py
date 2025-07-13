"""
Source Validation API Endpoints

FastAPI routes for the source validation workflow including source submission,
validation status, manual review, pilot monitoring, and performance analytics.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, HttpUrl, validator

from app.services.source_validation.orchestrator import (
    SourceValidationOrchestrator, 
    SourceSubmission,
    SourceStatus
)
from app.core.database import get_database


# API Router
router = APIRouter(prefix="/source-validation", tags=["source-validation"])


# Pydantic models for API requests/responses
class SourceSubmissionRequest(BaseModel):
    """Request model for source submission"""
    name: str
    url: HttpUrl
    contact_person: str
    contact_email: str
    source_type: str
    update_frequency: str
    geographic_focus: List[str]
    expected_volume: str
    sample_urls: List[HttpUrl]
    ai_relevance_estimate: int
    africa_relevance_estimate: int
    language: str
    submitter_role: str
    has_permission: bool
    preferred_contact: str
    
    @validator('ai_relevance_estimate', 'africa_relevance_estimate')
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Must be between 0 and 100')
        return v
    
    @validator('source_type')
    def validate_source_type(cls, v):
        valid_types = ['rss_feed', 'newsletter', 'webpage', 'api', 'other']
        if v not in valid_types:
            raise ValueError(f'Must be one of: {valid_types}')
        return v
    
    @validator('update_frequency')
    def validate_frequency(cls, v):
        valid_frequencies = ['daily', 'weekly', 'monthly', 'ad_hoc']
        if v not in valid_frequencies:
            raise ValueError(f'Must be one of: {valid_frequencies}')
        return v
    
    @validator('expected_volume')
    def validate_volume(cls, v):
        valid_volumes = ['1-5', '5-20', '20+']
        if v not in valid_volumes:
            raise ValueError(f'Must be one of: {valid_volumes}')
        return v


class SourceSubmissionResponse(BaseModel):
    """Response model for source submission"""
    submission_id: int
    status: str
    validation_score: Optional[float]
    classification_type: Optional[str]
    pilot_id: Optional[int]
    issues: List[str]
    recommendations: List[str]
    next_steps: List[str]
    estimated_production_date: Optional[datetime]


class ManualReviewDecisionRequest(BaseModel):
    """Request model for manual review decision"""
    decision: str
    reviewer_notes: str
    
    @validator('decision')
    def validate_decision(cls, v):
        if v not in ['approve', 'reject']:
            raise ValueError('Decision must be approve or reject')
        return v


class OpportunityDeduplicationRequest(BaseModel):
    """Request model for opportunity deduplication check"""
    url: HttpUrl
    title: str
    description: str
    organization: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    deadline: Optional[datetime] = None


# API Endpoints

@router.post("/submit", response_model=SourceSubmissionResponse)
async def submit_source(
    submission_request: SourceSubmissionRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a new funding source for validation and potential integration
    """
    try:
        # Convert request to SourceSubmission
        submission = SourceSubmission(
            name=submission_request.name,
            url=str(submission_request.url),
            contact_person=submission_request.contact_person,
            contact_email=submission_request.contact_email,
            source_type=submission_request.source_type,
            update_frequency=submission_request.update_frequency,
            geographic_focus=submission_request.geographic_focus,
            expected_volume=submission_request.expected_volume,
            sample_urls=[str(url) for url in submission_request.sample_urls],
            ai_relevance_estimate=submission_request.ai_relevance_estimate,
            africa_relevance_estimate=submission_request.africa_relevance_estimate,
            language=submission_request.language,
            submitter_role=submission_request.submitter_role,
            has_permission=submission_request.has_permission,
            preferred_contact=submission_request.preferred_contact,
            submitted_at=datetime.now()
        )
        
        # Process submission
        async with SourceValidationOrchestrator() as orchestrator:
            result = await orchestrator.submit_source(submission)
        
        return SourceSubmissionResponse(
            submission_id=result.submission_id,
            status=result.status.value,
            validation_score=result.validation_result.validation_score,
            classification_type=result.classification.source_type.value if result.classification else None,
            pilot_id=result.pilot_id,
            issues=result.issues,
            recommendations=result.recommendations,
            next_steps=result.next_steps,
            estimated_production_date=result.estimated_production_date
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing submission: {str(e)}")


@router.get("/submissions/{submission_id}")
async def get_submission_status(submission_id: int):
    """
    Get the current status of a source submission
    """
    try:
        async with SourceValidationOrchestrator() as orchestrator:
            status = await orchestrator.get_submission_status(submission_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving submission status: {str(e)}")


@router.get("/submissions")
async def list_submissions(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List source submissions with optional status filtering
    """
    try:
        db = await get_database()
        
        # Build query with optional status filter
        where_clause = "WHERE 1=1"
        params = []
        
        if status:
            where_clause += " AND status = $1"
            params.append(status)
            params.append(limit)
            params.append(offset)
        else:
            params = [limit, offset]
        
        query = f"""
            SELECT id, name, url, status, submitted_at, validation_score,
                   contact_person, geographic_focus, pilot_id
            FROM source_submissions 
            {where_clause}
            ORDER BY submitted_at DESC 
            LIMIT ${len(params)-1} OFFSET ${len(params)}
        """
        
        submissions = await db.fetch_all(query, *params)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM source_submissions {where_clause}"
        total = await db.fetch_val(count_query, *params[:-2] if status else [])
        
        return {
            "submissions": [dict(row) for row in submissions],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing submissions: {str(e)}")


@router.get("/manual-review/queue")
async def get_manual_review_queue():
    """
    Get submissions pending manual review
    """
    try:
        async with SourceValidationOrchestrator() as orchestrator:
            queue = await orchestrator.get_manual_review_queue()
        
        return {"review_queue": queue}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting review queue: {str(e)}")


@router.post("/manual-review/{review_id}/decision")
async def process_manual_review_decision(
    review_id: int,
    decision_request: ManualReviewDecisionRequest
):
    """
    Process a manual review decision
    """
    try:
        async with SourceValidationOrchestrator() as orchestrator:
            result = await orchestrator.process_manual_review_decision(
                review_id=review_id,
                decision=decision_request.decision,
                reviewer_notes=decision_request.reviewer_notes
            )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing review decision: {str(e)}")


@router.get("/pilots/dashboard")
async def get_pilot_dashboard():
    """
    Get pilot monitoring dashboard data
    """
    try:
        async with SourceValidationOrchestrator() as orchestrator:
            dashboard = await orchestrator.get_pilot_monitoring_dashboard()
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pilot dashboard: {str(e)}")


@router.post("/pilots/{pilot_id}/evaluate")
async def evaluate_pilot_performance(
    pilot_id: int,
    background_tasks: BackgroundTasks
):
    """
    Trigger pilot performance evaluation
    """
    try:
        async with SourceValidationOrchestrator() as orchestrator:
            result = await orchestrator.evaluate_pilot_performance(pilot_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating pilot: {str(e)}")


@router.post("/deduplication/check")
async def check_opportunity_duplicates(
    opportunity: OpportunityDeduplicationRequest
):
    """
    Check if an opportunity is a duplicate before adding to community validation
    """
    try:
        from app.services.source_validation.deduplication import OpportunityContent
        
        # Convert request to OpportunityContent
        opp_content = OpportunityContent(
            url=str(opportunity.url),
            title=opportunity.title,
            description=opportunity.description,
            organization=opportunity.organization,
            amount=opportunity.amount,
            currency=opportunity.currency,
            deadline=opportunity.deadline
        )
        
        async with SourceValidationOrchestrator() as orchestrator:
            result = await orchestrator.check_for_duplicates_before_validation(opp_content)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking duplicates: {str(e)}")


@router.get("/analytics")
async def get_validation_analytics(days: int = 30):
    """
    Get source validation analytics and statistics
    """
    try:
        async with SourceValidationOrchestrator() as orchestrator:
            analytics = await orchestrator.get_source_validation_analytics(days)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")


@router.get("/performance/sources")
async def get_sources_performance_summary():
    """
    Get performance summary for all sources
    """
    try:
        from app.services.source_validation.performance_tracker import PerformanceTracker
        
        tracker = PerformanceTracker()
        summary = await tracker.get_all_sources_performance_summary()
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance summary: {str(e)}")


@router.get("/performance/sources/{source_id}/report")
async def get_source_performance_report(source_id: int):
    """
    Get detailed performance report for a specific source
    """
    try:
        from app.services.source_validation.performance_tracker import PerformanceTracker
        
        tracker = PerformanceTracker()
        report = await tracker.generate_performance_report(source_id)
        
        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance report: {str(e)}")


@router.get("/performance/sources/review-needed")
async def get_sources_needing_review():
    """
    Get sources that need performance review
    """
    try:
        from app.services.source_validation.performance_tracker import PerformanceTracker
        
        tracker = PerformanceTracker()
        sources = await tracker.identify_sources_for_review()
        
        return {"sources_for_review": sources}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying sources for review: {str(e)}")


# Health check endpoint
@router.get("/health")
async def source_validation_health():
    """
    Health check for source validation module
    """
    try:
        # Quick database connectivity check
        db = await get_database()
        result = await db.fetch_val("SELECT COUNT(*) FROM source_submissions")
        
        return {
            "status": "healthy",
            "module": "source_validation",
            "total_submissions": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Source validation module unhealthy: {str(e)}")


# Public endpoint for source submission form (no auth required)
@router.get("/submit-form")
async def get_submission_form_config():
    """
    Get configuration for the public source submission form
    """
    return {
        "source_types": [
            {"value": "rss_feed", "label": "RSS Feed"},
            {"value": "newsletter", "label": "Email Newsletter"},
            {"value": "webpage", "label": "Web Page"},
            {"value": "api", "label": "API"},
            {"value": "other", "label": "Other"}
        ],
        "update_frequencies": [
            {"value": "daily", "label": "Daily"},
            {"value": "weekly", "label": "Weekly"},
            {"value": "monthly", "label": "Monthly"},
            {"value": "ad_hoc", "label": "As Needed"}
        ],
        "expected_volumes": [
            {"value": "1-5", "label": "1-5 per month"},
            {"value": "5-20", "label": "5-20 per month"},
            {"value": "20+", "label": "20+ per month"}
        ],
        "languages": [
            {"value": "English", "label": "English"},
            {"value": "French", "label": "French"},
            {"value": "Arabic", "label": "Arabic"},
            {"value": "Portuguese", "label": "Portuguese"},
            {"value": "Other", "label": "Other"}
        ],
        "contact_preferences": [
            {"value": "email", "label": "Email"},
            {"value": "phone", "label": "Phone"},
            {"value": "slack", "label": "Slack"}
        ],
        "african_countries": [
            "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
            "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros",
            "Congo", "Democratic Republic of Congo", "Djibouti", "Egypt", 
            "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
            "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya",
            "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali",
            "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia",
            "Niger", "Nigeria", "Rwanda", "São Tomé and Príncipe", "Senegal",
            "Seychelles", "Sierra Leone", "Somalia", "South Africa", "South Sudan",
            "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
        ],
        "african_regions": [
            "West Africa", "East Africa", "Central Africa", "Southern Africa", "North Africa"
        ]
    }
