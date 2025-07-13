"""
Source Validation Orchestrator

Main orchestrator class that coordinates the entire source submission,
validation, pilot monitoring, and integration process.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .source_validator import SourceValidator, SourceSubmission, ValidationResult
from .source_classifier import SourceClassifier, SourceClassification
from .deduplication import DeduplicationPipeline, OpportunityContent
from .performance_tracker import PerformanceTracker, SourceMetrics, PerformanceStatus

from app.core.database import get_database
from app.core.config import settings


class SourceStatus(Enum):
    """Source lifecycle status"""
    SUBMITTED = "submitted"
    VALIDATING = "validating"
    APPROVED_FOR_PILOT = "approved_for_pilot"
    PILOT_ACTIVE = "pilot_active"
    PILOT_EVALUATION = "pilot_evaluation"
    APPROVED_FOR_PRODUCTION = "approved_for_production"
    PRODUCTION_ACTIVE = "production_active"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"


@dataclass
class SourceSubmissionResult:
    """Result of complete source submission process"""
    submission_id: int
    status: SourceStatus
    validation_result: ValidationResult
    classification: Optional[SourceClassification]
    pilot_id: Optional[int]
    issues: List[str]
    recommendations: List[str]
    next_steps: List[str]
    estimated_production_date: Optional[datetime]


class SourceValidationOrchestrator:
    """Main orchestrator for source validation workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = None
        self.classifier = None
        self.deduplication = DeduplicationPipeline()
        self.performance_tracker = PerformanceTracker()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.validator = SourceValidator()
        self.classifier = SourceClassifier()
        await self.validator.__aenter__()
        await self.classifier.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.validator:
            await self.validator.__aexit__(exc_type, exc_val, exc_tb)
        if self.classifier:
            await self.classifier.__aexit__(exc_type, exc_val, exc_tb)
    
    async def submit_source(self, submission: SourceSubmission) -> SourceSubmissionResult:
        """
        Process complete source submission workflow
        
        Args:
            submission: SourceSubmission with all source details
            
        Returns:
            SourceSubmissionResult with complete processing outcome
        """
        self.logger.info(f"Processing source submission: {submission.name}")
        
        try:
            # Step 1: Store initial submission
            submission_id = await self._store_submission(submission)
            
            # Step 2: Initial validation
            validation_result = await self.validator.validate_submission(submission)
            
            # Update submission with validation results
            await self._update_submission_validation(submission_id, validation_result)
            
            # Step 3: Process based on validation outcome
            if validation_result.recommendation == "reject":
                return await self._handle_rejection(submission_id, validation_result)
            
            elif validation_result.recommendation == "needs_review":
                return await self._handle_manual_review(submission_id, validation_result)
            
            elif validation_result.recommendation == "accept":
                return await self._handle_acceptance(submission_id, submission, validation_result)
            
        except Exception as e:
            self.logger.error(f"Error processing source submission: {e}")
            return SourceSubmissionResult(
                submission_id=submission_id if 'submission_id' in locals() else 0,
                status=SourceStatus.REJECTED,
                validation_result=ValidationResult(0.0, "error", {}, [str(e)], []),
                classification=None,
                pilot_id=None,
                issues=[f"Processing error: {str(e)}"],
                recommendations=["Please contact support"],
                next_steps=["Review error and resubmit"],
                estimated_production_date=None
            )
    
    async def _store_submission(self, submission: SourceSubmission) -> int:
        """Store initial source submission"""
        db = await get_database()
        
        submission_id = await db.fetch_val(
            """
            INSERT INTO source_submissions (
                name, url, contact_person, contact_email, source_type,
                update_frequency, geographic_focus, expected_volume,
                sample_urls, ai_relevance_estimate, africa_relevance_estimate,
                language, submitter_role, has_permission, preferred_contact,
                submitted_at, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            RETURNING id
            """,
            submission.name, submission.url, submission.contact_person, submission.contact_email,
            submission.source_type, submission.update_frequency, submission.geographic_focus,
            submission.expected_volume, submission.sample_urls, submission.ai_relevance_estimate,
            submission.africa_relevance_estimate, submission.language, submission.submitter_role,
            submission.has_permission, submission.preferred_contact, submission.submitted_at,
            SourceStatus.SUBMITTED.value
        )
        
        return submission_id
    
    async def _update_submission_validation(self, submission_id: int, validation: ValidationResult) -> None:
        """Update submission with validation results"""
        db = await get_database()
        
        await db.execute(
            """
            UPDATE source_submissions SET
                validation_score = $1,
                validation_recommendation = $2,
                validation_checks = $3,
                validation_issues = $4,
                validation_suggestions = $5,
                validated_at = $6
            WHERE id = $7
            """,
            validation.validation_score, validation.recommendation, validation.checks,
            validation.issues, validation.suggestions, datetime.now(), submission_id
        )
    
    async def _handle_rejection(self, submission_id: int, validation: ValidationResult) -> SourceSubmissionResult:
        """Handle rejected submission"""
        db = await get_database()
        
        await db.execute(
            """
            UPDATE source_submissions SET
                status = $1,
                rejected_at = $2,
                rejection_reason = $3
            WHERE id = $4
            """,
            SourceStatus.REJECTED.value, datetime.now(),
            "; ".join(validation.issues), submission_id
        )
        
        # Send rejection notification
        await self._send_rejection_notification(submission_id, validation)
        
        return SourceSubmissionResult(
            submission_id=submission_id,
            status=SourceStatus.REJECTED,
            validation_result=validation,
            classification=None,
            pilot_id=None,
            issues=validation.issues,
            recommendations=validation.suggestions,
            next_steps=["Address validation issues and resubmit"],
            estimated_production_date=None
        )
    
    async def _handle_manual_review(self, submission_id: int, validation: ValidationResult) -> SourceSubmissionResult:
        """Handle submission requiring manual review"""
        db = await get_database()
        
        await db.execute(
            """
            UPDATE source_submissions SET
                status = $1,
                requires_manual_review = true,
                manual_review_queued_at = $2
            WHERE id = $3
            """,
            SourceStatus.VALIDATING.value, datetime.now(), submission_id
        )
        
        # Add to manual review queue
        await self._queue_for_manual_review(submission_id, validation)
        
        return SourceSubmissionResult(
            submission_id=submission_id,
            status=SourceStatus.VALIDATING,
            validation_result=validation,
            classification=None,
            pilot_id=None,
            issues=validation.issues,
            recommendations=validation.suggestions,
            next_steps=["Awaiting manual review by TAIFA team"],
            estimated_production_date=datetime.now() + timedelta(days=7)
        )
    
    async def _handle_acceptance(self, submission_id: int, submission: SourceSubmission, 
                               validation: ValidationResult) -> SourceSubmissionResult:
        """Handle accepted submission - proceed to classification and pilot setup"""
        
        # Step 1: Classify the source
        classification = await self.classifier.classify_source(
            submission.url, 
            additional_info={
                "source_type": submission.source_type,
                "update_frequency": submission.update_frequency,
                "preferred_contact": submission.preferred_contact
            }
        )
        
        # Step 2: Set up pilot monitoring
        pilot_id = await self._setup_pilot_monitoring(submission_id, submission, classification)
        
        # Step 3: Update submission status
        db = await get_database()
        await db.execute(
            """
            UPDATE source_submissions SET
                status = $1,
                approved_for_pilot_at = $2,
                source_classification = $3,
                pilot_id = $4
            WHERE id = $5
            """,
            SourceStatus.APPROVED_FOR_PILOT.value, datetime.now(),
            classification.__dict__, pilot_id, submission_id
        )
        
        # Step 4: Send approval notification
        await self._send_approval_notification(submission_id, submission, classification)
        
        return SourceSubmissionResult(
            submission_id=submission_id,
            status=SourceStatus.APPROVED_FOR_PILOT,
            validation_result=validation,
            classification=classification,
            pilot_id=pilot_id,
            issues=[],
            recommendations=["Monitor pilot performance over next 30 days"],
            next_steps=[
                "Pilot monitoring started",
                "Performance evaluation in 30 days",
                "Production integration upon successful pilot"
            ],
            estimated_production_date=datetime.now() + timedelta(days=35)
        )
    
    async def _setup_pilot_monitoring(self, submission_id: int, submission: SourceSubmission, 
                                    classification: SourceClassification) -> int:
        """Set up pilot monitoring for approved source"""
        db = await get_database()
        
        # Create pilot monitoring entry
        pilot_id = await db.fetch_val(
            """
            INSERT INTO pilot_monitoring (
                submission_id, source_name, source_url, source_type,
                monitoring_config, pilot_start_date, pilot_end_date,
                status, classification_data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
            """,
            submission_id, submission.name, submission.url, classification.source_type.value,
            classification.monitoring_config, datetime.now(), 
            datetime.now() + timedelta(days=30), "active", classification.__dict__
        )
        
        # Create data source entry (in limited/pilot mode)
        source_id = await db.fetch_val(
            """
            INSERT INTO data_sources (
                name, url, source_type, status, reliability_score,
                last_checked, pilot_mode, pilot_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
            """,
            submission.name, submission.url, classification.source_type.value,
            "pilot", 0.0, None, True, pilot_id, datetime.now()
        )
        
        # Update pilot with source_id
        await db.execute(
            "UPDATE pilot_monitoring SET source_id = $1 WHERE id = $2",
            source_id, pilot_id
        )
        
        # Schedule initial monitoring check
        await self._schedule_pilot_monitoring(pilot_id, classification)
        
        return pilot_id
    
    async def _schedule_pilot_monitoring(self, pilot_id: int, classification: SourceClassification) -> None:
        """Schedule pilot monitoring tasks"""
        # This would integrate with your task scheduler (Celery, etc.)
        # For now, just log the scheduling
        self.logger.info(f"Scheduled pilot monitoring for pilot {pilot_id} with strategy: {classification.monitoring_strategy}")
        
        # TODO: Integrate with actual task scheduler
        # schedule_task("pilot_monitoring", {
        #     "pilot_id": pilot_id,
        #     "strategy": classification.monitoring_strategy,
        #     "frequency": classification.monitoring_config["check_frequency"]
        # })
    
    async def evaluate_pilot_performance(self, pilot_id: int) -> Dict[str, Any]:
        """Evaluate pilot performance after 30-day period"""
        db = await get_database()
        
        # Get pilot information
        pilot_info = await db.fetch_one(
            "SELECT * FROM pilot_monitoring WHERE id = $1",
            pilot_id
        )
        
        if not pilot_info:
            raise ValueError(f"Pilot {pilot_id} not found")
        
        # Evaluate performance using performance tracker
        source_id = pilot_info["source_id"]
        performance_metrics = await self.performance_tracker.evaluate_source_performance(
            source_id, evaluation_days=30
        )
        
        # Determine pilot outcome
        pilot_outcome = self._determine_pilot_outcome(performance_metrics)
        
        # Update pilot status
        await db.execute(
            """
            UPDATE pilot_monitoring SET
                performance_metrics = $1,
                pilot_outcome = $2,
                evaluation_completed_at = $3,
                status = $4
            WHERE id = $5
            """,
            performance_metrics.__dict__, pilot_outcome["decision"],
            datetime.now(), "completed", pilot_id
        )
        
        # Handle outcome
        if pilot_outcome["decision"] == "approve_for_production":
            await self._promote_to_production(pilot_id, source_id)
        else:
            await self._handle_pilot_failure(pilot_id, source_id, pilot_outcome)
        
        return {
            "pilot_id": pilot_id,
            "performance_metrics": performance_metrics,
            "outcome": pilot_outcome,
            "next_steps": pilot_outcome["next_steps"]
        }
    
    def _determine_pilot_outcome(self, metrics: SourceMetrics) -> Dict[str, Any]:
        """Determine outcome based on pilot performance metrics"""
        # Check minimum thresholds
        meets_minimums = (
            metrics.community_approval_rate >= 0.70 and
            metrics.duplicate_rate <= 0.20 and
            metrics.monitoring_reliability >= 0.95 and
            metrics.performance_status not in [PerformanceStatus.FAILING, PerformanceStatus.POOR]
        )
        
        if meets_minimums and metrics.overall_score >= 0.6:
            return {
                "decision": "approve_for_production",
                "reason": f"Pilot successful with score {metrics.overall_score:.2f}",
                "next_steps": ["Promote to production monitoring", "Add to known sources", "Notify contributor"]
            }
        elif metrics.overall_score >= 0.4:
            return {
                "decision": "extend_pilot",
                "reason": f"Performance marginal (score: {metrics.overall_score:.2f}), extending pilot",
                "next_steps": ["Extend pilot by 30 days", "Provide improvement recommendations", "Re-evaluate"]
            }
        else:
            return {
                "decision": "reject",
                "reason": f"Performance below threshold (score: {metrics.overall_score:.2f})",
                "next_steps": ["Deprecate source", "Notify contributor with feedback", "Archive pilot data"]
            }
    
    async def _promote_to_production(self, pilot_id: int, source_id: int) -> None:
        """Promote successful pilot to production"""
        db = await get_database()
        
        # Update source status to production
        await db.execute(
            """
            UPDATE data_sources SET
                status = 'active',
                pilot_mode = false,
                promoted_to_production_at = $1
            WHERE id = $2
            """,
            datetime.now(), source_id
        )
        
        # Update submission status
        await db.execute(
            """
            UPDATE source_submissions SET
                status = $1,
                production_active_at = $2
            WHERE pilot_id = $3
            """,
            SourceStatus.PRODUCTION_ACTIVE.value, datetime.now(), pilot_id
        )
        
        # Add to known sources for agent training
        await self._add_to_known_sources(source_id)
        
        # Send success notification
        await self._send_production_notification(pilot_id, "success")
        
        self.logger.info(f"Source {source_id} promoted to production from pilot {pilot_id}")
    
    async def _handle_pilot_failure(self, pilot_id: int, source_id: int, outcome: Dict[str, Any]) -> None:
        """Handle failed or extended pilot"""
        db = await get_database()
        
        if outcome["decision"] == "extend_pilot":
            # Extend pilot period
            await db.execute(
                """
                UPDATE pilot_monitoring SET
                    pilot_end_date = pilot_end_date + INTERVAL '30 days',
                    status = 'extended',
                    extension_reason = $1
                WHERE id = $2
                """,
                outcome["reason"], pilot_id
            )
            
        else:  # reject
            # Deprecate the source
            await db.execute(
                """
                UPDATE data_sources SET
                    status = 'deprecated',
                    deprecated_at = $1,
                    deprecation_reason = $2
                WHERE id = $3
                """,
                datetime.now(), outcome["reason"], source_id
            )
            
            # Update submission status
            await db.execute(
                """
                UPDATE source_submissions SET
                    status = $1,
                    rejected_at = $2,
                    rejection_reason = $3
                WHERE pilot_id = $4
                """,
                SourceStatus.REJECTED.value, datetime.now(), 
                outcome["reason"], pilot_id
            )
        
        # Send notification
        await self._send_production_notification(pilot_id, outcome["decision"])
    
    async def _add_to_known_sources(self, source_id: int) -> None:
        """Add successful source to known sources for agent training"""
        # This would update the agent prompts with the new source information
        # For now, just log it
        self.logger.info(f"Added source {source_id} to known sources for agent training")
        
        # TODO: Implement agent prompt updating
    
    async def check_for_duplicates_before_validation(self, opportunity: OpportunityContent) -> Dict[str, Any]:
        """Check for duplicates before community validation"""
        return await self.deduplication.check_for_duplicates(opportunity)
    
    async def get_submission_status(self, submission_id: int) -> Dict[str, Any]:
        """Get current status of a source submission"""
        db = await get_database()
        
        submission = await db.fetch_one(
            """
            SELECT ss.*, pm.performance_metrics, pm.pilot_outcome 
            FROM source_submissions ss
            LEFT JOIN pilot_monitoring pm ON ss.pilot_id = pm.id
            WHERE ss.id = $1
            """,
            submission_id
        )
        
        if not submission:
            return {"error": "Submission not found"}
        
        return {
            "submission_id": submission_id,
            "status": submission["status"],
            "name": submission["name"],
            "url": submission["url"],
            "submitted_at": submission["submitted_at"],
            "validation_score": submission["validation_score"],
            "validation_recommendation": submission["validation_recommendation"],
            "pilot_id": submission["pilot_id"],
            "performance_metrics": submission.get("performance_metrics"),
            "pilot_outcome": submission.get("pilot_outcome")
        }
    
    # Notification methods
    async def _send_rejection_notification(self, submission_id: int, validation: ValidationResult) -> None:
        """Send rejection notification to submitter"""
        self.logger.info(f"Sending rejection notification for submission {submission_id}")
        # TODO: Implement email notification
        pass
    
    async def _send_approval_notification(self, submission_id: int, submission: SourceSubmission, 
                                        classification: SourceClassification) -> None:
        """Send approval notification to submitter"""
        self.logger.info(f"Sending approval notification for submission {submission_id}")
        # TODO: Implement email notification
        pass
    
    async def _send_production_notification(self, pilot_id: int, outcome: str) -> None:
        """Send production outcome notification"""
        self.logger.info(f"Sending production notification for pilot {pilot_id}: {outcome}")
        # TODO: Implement email notification
        pass
    
    async def _queue_for_manual_review(self, submission_id: int, validation: ValidationResult) -> None:
        """Add submission to manual review queue"""
        db = await get_database()
        
        await db.execute(
            """
            INSERT INTO manual_review_queue (
                submission_id, validation_score, issues, suggestions,
                priority, queued_at, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            submission_id, validation.validation_score, validation.issues,
            validation.suggestions, "medium", datetime.now(), "pending"
        )
    
    async def get_manual_review_queue(self) -> List[Dict[str, Any]]:
        """Get submissions pending manual review"""
        db = await get_database()
        
        queue = await db.fetch_all(
            """
            SELECT mrq.*, ss.name, ss.url, ss.contact_person, ss.contact_email
            FROM manual_review_queue mrq
            JOIN source_submissions ss ON mrq.submission_id = ss.id
            WHERE mrq.status = 'pending'
            ORDER BY 
                CASE mrq.priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    WHEN 'low' THEN 3 
                END,
                mrq.queued_at ASC
            """
        )
        
        return [dict(row) for row in queue]
    
    async def process_manual_review_decision(self, review_id: int, decision: str, 
                                           reviewer_notes: str) -> Dict[str, Any]:
        """Process manual review decision"""
        db = await get_database()
        
        # Get review info
        review = await db.fetch_one(
            "SELECT * FROM manual_review_queue WHERE id = $1",
            review_id
        )
        
        if not review:
            return {"error": "Review not found"}
        
        # Update review status
        await db.execute(
            """
            UPDATE manual_review_queue SET
                status = 'completed',
                decision = $1,
                reviewer_notes = $2,
                reviewed_at = $3
            WHERE id = $4
            """,
            decision, reviewer_notes, datetime.now(), review_id
        )
        
        submission_id = review["submission_id"]
        
        if decision == "approve":
            # Get original submission
            submission_data = await db.fetch_one(
                "SELECT * FROM source_submissions WHERE id = $1",
                submission_id
            )
            
            # Convert to SourceSubmission object and process
            submission = SourceSubmission(
                name=submission_data["name"],
                url=submission_data["url"],
                contact_person=submission_data["contact_person"],
                contact_email=submission_data["contact_email"],
                source_type=submission_data["source_type"],
                update_frequency=submission_data["update_frequency"],
                geographic_focus=submission_data["geographic_focus"],
                expected_volume=submission_data["expected_volume"],
                sample_urls=submission_data["sample_urls"],
                ai_relevance_estimate=submission_data["ai_relevance_estimate"],
                africa_relevance_estimate=submission_data["africa_relevance_estimate"],
                language=submission_data["language"],
                submitter_role=submission_data["submitter_role"],
                has_permission=submission_data["has_permission"],
                preferred_contact=submission_data["preferred_contact"],
                submitted_at=submission_data["submitted_at"]
            )
            
            # Create mock validation result for manual approval
            validation_result = ValidationResult(
                validation_score=0.8,
                recommendation="accept",
                checks={},
                issues=[],
                suggestions=[]
            )
            
            # Process acceptance
            result = await self._handle_acceptance(submission_id, submission, validation_result)
            return {"decision": "approved", "result": result}
            
        else:  # reject
            await db.execute(
                """
                UPDATE source_submissions SET
                    status = $1,
                    rejected_at = $2,
                    rejection_reason = $3
                WHERE id = $4
                """,
                SourceStatus.REJECTED.value, datetime.now(),
                f"Manual review rejection: {reviewer_notes}", submission_id
            )
            
            return {"decision": "rejected", "reason": reviewer_notes}
    
    async def get_pilot_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for pilot monitoring"""
        db = await get_database()
        
        # Get active pilots
        active_pilots = await db.fetch_all(
            """
            SELECT pm.*, ss.name, ss.contact_person
            FROM pilot_monitoring pm
            JOIN source_submissions ss ON pm.submission_id = ss.id
            WHERE pm.status = 'active'
            ORDER BY pm.pilot_start_date DESC
            """
        )
        
        # Get pilots ready for evaluation
        ready_for_evaluation = await db.fetch_all(
            """
            SELECT pm.*, ss.name
            FROM pilot_monitoring pm
            JOIN source_submissions ss ON pm.submission_id = ss.id
            WHERE pm.status = 'active' 
            AND pm.pilot_end_date <= NOW()
            ORDER BY pm.pilot_end_date ASC
            """
        )
        
        # Get performance summary
        performance_summary = await self.performance_tracker.get_all_sources_performance_summary()
        
        return {
            "active_pilots": [dict(row) for row in active_pilots],
            "pilots_ready_for_evaluation": [dict(row) for row in ready_for_evaluation],
            "total_active_pilots": len(active_pilots),
            "pilots_pending_evaluation": len(ready_for_evaluation),
            "performance_summary": performance_summary,
            "generated_at": datetime.now().isoformat()
        }
    
    async def get_source_validation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics for source validation process"""
        db = await get_database()
        start_date = datetime.now() - timedelta(days=days)
        
        # Submission statistics
        submission_stats = await db.fetch_one(
            """
            SELECT 
                COUNT(*) as total_submissions,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN status = 'production_active' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status LIKE 'pilot%' THEN 1 ELSE 0 END) as in_pilot,
                AVG(validation_score) as avg_validation_score
            FROM source_submissions 
            WHERE submitted_at >= $1
            """,
            start_date
        )
        
        # Validation distribution
        validation_distribution = await db.fetch_all(
            """
            SELECT 
                validation_recommendation,
                COUNT(*) as count
            FROM source_submissions 
            WHERE submitted_at >= $1
            AND validation_recommendation IS NOT NULL
            GROUP BY validation_recommendation
            """,
            start_date
        )
        
        # Source type distribution
        source_type_distribution = await db.fetch_all(
            """
            SELECT 
                source_type,
                COUNT(*) as count
            FROM source_submissions 
            WHERE submitted_at >= $1
            GROUP BY source_type
            ORDER BY count DESC
            """,
            start_date
        )
        
        # Geographic distribution
        geographic_distribution = await db.fetch_all(
            """
            SELECT 
                UNNEST(geographic_focus) as region,
                COUNT(*) as count
            FROM source_submissions 
            WHERE submitted_at >= $1
            GROUP BY region
            ORDER BY count DESC
            """,
            start_date
        )
        
        # Deduplication statistics
        dedup_stats = await self.deduplication.get_deduplication_stats(days)
        
        return {
            "period_days": days,
            "submission_statistics": dict(submission_stats) if submission_stats else {},
            "validation_distribution": [dict(row) for row in validation_distribution],
            "source_type_distribution": [dict(row) for row in source_type_distribution],
            "geographic_distribution": [dict(row) for row in geographic_distribution],
            "deduplication_statistics": dedup_stats,
            "generated_at": datetime.now().isoformat()
        }


async def test_orchestrator():
    """Test function for the orchestrator"""
    from datetime import datetime
    
    # Create test submission
    test_submission = SourceSubmission(
        name="Test University Research Office",
        url="https://test-university.edu/research/funding",
        contact_person="Dr. Test Person",
        contact_email="test@test-university.edu",
        source_type="webpage",
        update_frequency="monthly",
        geographic_focus=["Kenya", "East Africa"],
        expected_volume="5-20",
        sample_urls=[
            "https://test-university.edu/research/funding/ai-grant-2025"
        ],
        ai_relevance_estimate=80,
        africa_relevance_estimate=90,
        language="English",
        submitter_role="Research Funding Manager",
        has_permission=True,
        preferred_contact="email",
        submitted_at=datetime.now()
    )
    
    # Test orchestrator
    async with SourceValidationOrchestrator() as orchestrator:
        print("Testing source submission workflow...")
        
        try:
            result = await orchestrator.submit_source(test_submission)
            
            print(f"Submission ID: {result.submission_id}")
            print(f"Status: {result.status.value}")
            print(f"Validation Score: {result.validation_result.validation_score:.2f}")
            print(f"Classification: {result.classification.source_type.value if result.classification else 'None'}")
            print(f"Issues: {result.issues}")
            print(f"Next Steps: {result.next_steps}")
            
        except Exception as e:
            print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
