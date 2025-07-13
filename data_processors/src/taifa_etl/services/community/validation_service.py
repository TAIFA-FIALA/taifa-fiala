"""
TAIFA Community Validation Service
24-Hour Review Window with Automated Publication
"""

import json
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database imports (adapt to your actual setup)
from app.models.funding import FundingOpportunity
from app.core.database import get_db

class ValidationAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    FLAG_ISSUE = "flag_issue"
    SUGGEST_EDIT = "suggest_edit"
    REQUEST_INFO = "request_info"

class ReviewStatus(Enum):
    PENDING_COMMUNITY = "pending_community"
    COMMUNITY_APPROVED = "community_approved"
    COMMUNITY_FLAGGED = "community_flagged"
    AUTO_PUBLISHED = "auto_published"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"

@dataclass
class CommunityValidator:
    """Community validator profile"""
    id: str
    email: str
    name: str
    expertise_areas: List[str]
    countries_of_focus: List[str]
    languages: List[str]
    validation_count: int = 0
    accuracy_score: float = 0.0
    last_active: datetime = None
    is_active: bool = True

@dataclass
class ValidationFeedback:
    """Community validation feedback"""
    opportunity_id: int
    validator_id: str
    action: ValidationAction
    confidence: str  # high, medium, low
    reasoning: str
    suggested_changes: Optional[Dict[str, str]] = None
    relevance_score: Optional[int] = None  # 1-5
    accuracy_score: Optional[int] = None   # 1-5
    completeness_score: Optional[int] = None  # 1-5
    submitted_at: datetime = None
    
    def __post_init__(self):
        if self.submitted_at is None:
            self.submitted_at = datetime.utcnow()

@dataclass
class NewsletterBatch:
    """Batch of opportunities for newsletter"""
    batch_id: str
    opportunities: List[Dict[str, Any]]
    created_at: datetime
    review_deadline: datetime
    sent_at: Optional[datetime] = None
    auto_publish_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, reviewing, completed

class CommunityValidationService:
    """Main service for community validation"""
    
    def __init__(self):
        self.validators: Dict[str, CommunityValidator] = {}
        self.pending_validations: Dict[int, List[ValidationFeedback]] = {}
        self.newsletter_batches: Dict[str, NewsletterBatch] = {}
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"  # Configure as needed
        self.smtp_port = 587
        self.email_user = "noreply@taifa-africa.com"  # Configure as needed
        self.email_password = "your_email_password"  # Load from environment
        
        # Review window configuration
        self.review_window_hours = 24
        self.minimum_validations_for_auto_approve = 3
        self.consensus_threshold = 0.8  # 80% agreement for auto-approval
    
    async def load_validators(self):
        """Load community validators from database"""
        try:
            # This would load from your user/validator database
            # For now, using mock data
            self.validators = {
                "validator_1": CommunityValidator(
                    id="validator_1",
                    email="validator1@example.com",
                    name="Dr. Amina Hassan",
                    expertise_areas=["ai", "healthcare", "grants"],
                    countries_of_focus=["nigeria", "ghana", "kenya"],
                    languages=["en", "fr"],
                    validation_count=45,
                    accuracy_score=0.92
                ),
                "validator_2": CommunityValidator(
                    id="validator_2", 
                    email="validator2@example.com",
                    name="Prof. Jean Kouame",
                    expertise_areas=["ai", "agriculture", "funding"],
                    countries_of_focus=["senegal", "ivory_coast", "burkina_faso"],
                    languages=["fr", "en"],
                    validation_count=38,
                    accuracy_score=0.89
                )
            }
        except Exception as e:
            logging.error(f"Failed to load validators: {e}")
    
    async def prepare_daily_newsletter(self) -> Optional[str]:
        """Prepare daily newsletter with new opportunities"""
        
        # Get opportunities processed in last 24 hours
        new_opportunities = await self._get_pending_opportunities()
        
        if not new_opportunities:
            logging.info("No new opportunities for newsletter")
            return None
        
        # Create newsletter batch
        batch_id = self._generate_batch_id()
        review_deadline = datetime.utcnow() + timedelta(hours=self.review_window_hours)
        auto_publish_at = review_deadline + timedelta(minutes=30)  # 30 min buffer
        
        batch = NewsletterBatch(
            batch_id=batch_id,
            opportunities=new_opportunities,
            created_at=datetime.utcnow(),
            review_deadline=review_deadline,
            auto_publish_at=auto_publish_at
        )
        
        self.newsletter_batches[batch_id] = batch
        
        # Generate newsletter content
        newsletter_content = await self._generate_newsletter_content(batch)
        
        # Send newsletter to validators
        await self._send_newsletter(newsletter_content, batch)
        
        # Schedule automated publication
        await self._schedule_auto_publication(batch)
        
        # Update opportunity statuses
        await self._update_opportunity_statuses(new_opportunities, batch_id, review_deadline)
        
        return batch_id
    
    async def _get_pending_opportunities(self) -> List[Dict[str, Any]]:
        """Get opportunities needing community review"""
        try:
            # This would query your database for opportunities with review_status = 'community_review_queue'
            # For now, return mock data
            return [
                {
                    "id": 1,
                    "title": "AI for Health Innovation Grant - Gates Foundation",
                    "description": "Supporting AI applications in healthcare across Sub-Saharan Africa...",
                    "amount": 500000,
                    "currency": "USD",
                    "deadline": "2025-09-15T23:59:59Z",
                    "organization_name": "Gates Foundation",
                    "source_url": "https://www.gatesfoundation.org/grants",
                    "ai_relevance_score": 0.95,
                    "africa_relevance_score": 0.88,
                    "overall_confidence": 0.87,
                    "geographic_scope": ["Sub-Saharan Africa"],
                    "ai_domains": ["healthcare", "machine learning"],
                    "processing_metadata": {
                        "processed_at": "2025-07-11T10:30:00Z",
                        "agent_scores": {"parser": 0.9, "relevancy": 0.85, "extractor": 0.88}
                    }
                },
                {
                    "id": 2,
                    "title": "Rwanda AI Innovation Challenge",
                    "description": "National competition for AI solutions addressing local challenges...",
                    "amount": 50000,
                    "currency": "USD", 
                    "deadline": "2025-08-30T23:59:59Z",
                    "organization_name": "Government of Rwanda",
                    "source_url": "https://gov.rw/innovation-challenge",
                    "ai_relevance_score": 0.92,
                    "africa_relevance_score": 0.98,
                    "overall_confidence": 0.91,
                    "geographic_scope": ["Rwanda"],
                    "ai_domains": ["general ai", "innovation"],
                    "processing_metadata": {
                        "processed_at": "2025-07-11T11:15:00Z",
                        "agent_scores": {"parser": 0.88, "relevancy": 0.94, "extractor": 0.92}
                    }
                }
            ]
        except Exception as e:
            logging.error(f"Failed to get pending opportunities: {e}")
            return []
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"newsletter_{timestamp}"
    
    async def _generate_newsletter_content(self, batch: NewsletterBatch) -> str:
        """Generate HTML newsletter content"""
        
        # Newsletter template
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TAIFA-FIALA Community Review Newsletter</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .opportunity { border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 5px; }
        .meta { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; }
        .scores { display: flex; gap: 15px; margin: 10px 0; }
        .score { padding: 5px 10px; border-radius: 3px; color: white; }
        .score.high { background: #22c55e; }
        .score.medium { background: #f59e0b; }
        .score.low { background: #ef4444; }
        .actions { margin: 20px 0; padding: 15px; background: #f0f9ff; border-radius: 5px; }
        .action-button { display: inline-block; padding: 8px 16px; margin: 5px; text-decoration: none; 
                        border-radius: 3px; color: white; font-weight: bold; }
        .approve { background: #22c55e; }
        .reject { background: #ef4444; }
        .flag { background: #f59e0b; }
        .footer { margin-top: 40px; padding: 20px; background: #f8f9fa; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 TAIFA-FIALA Community Review</h1>
        <p>{{ batch.opportunities|length }} new AI funding opportunities need your review</p>
        <p><strong>Review Deadline:</strong> {{ batch.review_deadline.strftime('%B %d, %Y at %H:%M UTC') }}</p>
    </div>
    
    <div style="padding: 20px;">
        <h2>📋 Summary</h2>
        <ul>
            <li><strong>Total Opportunities:</strong> {{ batch.opportunities|length }}</li>
            <li><strong>Total Funding Value:</strong> ${{ total_funding_value:,.2f }}</li>
            <li><strong>Geographic Scope:</strong> {{ geographic_summary }}</li>
            <li><strong>Review Window:</strong> {{ review_window_hours }} hours</li>
        </ul>
        
        <p><strong>🎯 Your Mission:</strong> Help ensure only high-quality, relevant AI funding opportunities 
        reach the African AI community. Review each opportunity and provide feedback within {{ review_window_hours }} hours.</p>
        
        {% for opp in batch.opportunities %}
        <div class="opportunity">
            <h3>{{ opp.title }}</h3>
            
            <div class="meta">
                <strong>Organization:</strong> {{ opp.organization_name }}<br>
                <strong>Amount:</strong> {{ opp.currency }} {{ "{:,.0f}".format(opp.amount) }}<br>
                <strong>Deadline:</strong> {{ opp.deadline }}<br>
                <strong>Geographic Scope:</strong> {{ opp.geographic_scope|join(', ') }}<br>
                <strong>AI Domains:</strong> {{ opp.ai_domains|join(', ') }}
            </div>
            
            <p>{{ opp.description[:300] }}{% if opp.description|length > 300 %}...{% endif %}</p>
            
            <div class="scores">
                <div class="score {{ 'high' if opp.ai_relevance_score >= 0.8 else 'medium' if opp.ai_relevance_score >= 0.6 else 'low' }}">
                    AI Relevance: {{ "%.0f"|format(opp.ai_relevance_score * 100) }}%
                </div>
                <div class="score {{ 'high' if opp.africa_relevance_score >= 0.8 else 'medium' if opp.africa_relevance_score >= 0.6 else 'low' }}">
                    Africa Relevance: {{ "%.0f"|format(opp.africa_relevance_score * 100) }}%
                </div>
                <div class="score {{ 'high' if opp.overall_confidence >= 0.8 else 'medium' if opp.overall_confidence >= 0.6 else 'low' }}">
                    Confidence: {{ "%.0f"|format(opp.overall_confidence * 100) }}%
                </div>
            </div>
            
            <div class="actions">
                <p><strong>Quick Actions (click to validate):</strong></p>
                <a href="{{ validation_base_url }}/validate/{{ batch.batch_id }}/{{ opp.id }}/approve" class="action-button approve">✅ Approve</a>
                <a href="{{ validation_base_url }}/validate/{{ batch.batch_id }}/{{ opp.id }}/reject" class="action-button reject">❌ Reject</a>
                <a href="{{ validation_base_url }}/validate/{{ batch.batch_id }}/{{ opp.id }}/flag" class="action-button flag">🚩 Flag for Review</a>
                <a href="{{ validation_base_url }}/review/{{ batch.batch_id }}/{{ opp.id }}" class="action-button" style="background: #6366f1;">📝 Detailed Review</a>
            </div>
            
            <p><small><strong>Source:</strong> <a href="{{ opp.source_url }}" target="_blank">{{ opp.source_url }}</a></small></p>
        </div>
        {% endfor %}
        
        <div class="footer">
            <h3>⏰ Important Reminders</h3>
            <ul style="text-align: left; display: inline-block;">
                <li>If no objections are received within {{ review_window_hours }} hours, opportunities will be auto-published</li>
                <li>Your feedback helps improve our AI agents and benefits the entire African AI community</li>
                <li>For detailed reviews, use the "Detailed Review" link to provide specific feedback</li>
                <li>Questions? Reply to this email or contact community@taifa-africa.com</li>
            </ul>
            
            <p><strong>Thank you for your dedication to the African AI community! 🙏</strong></p>
            
            <hr>
            <p><small>
                You're receiving this because you're a valued TAIFA-FIALA community validator.<br>
                To update your preferences or unsubscribe, <a href="{{ unsubscribe_url }}">click here</a>.
            </small></p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        # Calculate summary statistics
        total_funding_value = sum(opp.get('amount', 0) for opp in batch.opportunities)
        
        geographic_areas = set()
        for opp in batch.opportunities:
            geographic_areas.update(opp.get('geographic_scope', []))
        geographic_summary = ', '.join(list(geographic_areas)[:5])  # Show first 5
        
        # Render template
        content = template.render(
            batch=batch,
            total_funding_value=total_funding_value,
            geographic_summary=geographic_summary,
            review_window_hours=self.review_window_hours,
            validation_base_url="https://taifa-africa.com",  # Configure as needed
            unsubscribe_url="https://taifa-africa.com/unsubscribe"  # Configure as needed
        )
        
        return content
    
    async def _send_newsletter(self, content: str, batch: NewsletterBatch):
        """Send newsletter to community validators"""
        
        try:
            # Prepare email
            subject = f"🌍 TAIFA Community Review: {len(batch.opportunities)} New AI Funding Opportunities"
            
            # Get active validators
            active_validators = [v for v in self.validators.values() if v.is_active]
            
            # Send to each validator
            for validator in active_validators:
                await self._send_email(
                    to_email=validator.email,
                    to_name=validator.name,
                    subject=subject,
                    html_content=content
                )
            
            # Update batch status
            batch.sent_at = datetime.utcnow()
            batch.status = "sent"
            
            logging.info(f"Newsletter sent to {len(active_validators)} validators for batch {batch.batch_id}")
            
        except Exception as e:
            logging.error(f"Failed to send newsletter: {e}")
            batch.status = "failed"
    
    async def _send_email(self, to_email: str, to_name: str, subject: str, html_content: str):
        """Send individual email"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"TAIFA Community <{self.email_user}>"
            msg['To'] = f"{to_name} <{to_email}>"
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logging.info(f"Email sent to {to_email}")
            
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
    
    async def _schedule_auto_publication(self, batch: NewsletterBatch):
        """Schedule automated publication if no objections"""
        
        # This would typically use a task scheduler like Celery or APScheduler
        # For now, we'll store the schedule and check it in a background process
        
        auto_publish_task = {
            "batch_id": batch.batch_id,
            "scheduled_at": batch.auto_publish_at,
            "action": "auto_publish_if_no_objections"
        }
        
        # Store in database or task queue
        await self._store_scheduled_task(auto_publish_task)
        
        logging.info(f"Auto-publication scheduled for {batch.auto_publish_at} for batch {batch.batch_id}")
    
    async def _store_scheduled_task(self, task: Dict[str, Any]):
        """Store scheduled task (implement with your task queue)"""
        # This would integrate with your task scheduling system
        pass
    
    async def _update_opportunity_statuses(self, opportunities: List[Dict], batch_id: str, review_deadline: datetime):
        """Update opportunity statuses to reflect community review"""
        
        for opp in opportunities:
            try:
                # Update database record
                # This would update the funding_opportunities table
                update_data = {
                    "review_status": ReviewStatus.PENDING_COMMUNITY.value,
                    "processing_batch_id": batch_id,
                    "community_review_deadline": review_deadline,
                    "auto_publish_at": review_deadline + timedelta(minutes=30)
                }
                
                # In production, this would be a database update
                logging.info(f"Updated opportunity {opp['id']} status for community review")
                
            except Exception as e:
                logging.error(f"Failed to update opportunity {opp['id']} status: {e}")
    
    async def handle_community_validation(self, batch_id: str, opportunity_id: int, 
                                        validator_id: str, feedback: ValidationFeedback) -> Dict[str, Any]:
        """Handle community validation feedback"""
        
        try:
            # Store feedback
            if opportunity_id not in self.pending_validations:
                self.pending_validations[opportunity_id] = []
            
            self.pending_validations[opportunity_id].append(feedback)
            
            # Store in database
            await self._store_validation_feedback(feedback)
            
            # Check if we have enough feedback to make a decision
            decision = await self._evaluate_community_consensus(opportunity_id)
            
            if decision:
                await self._apply_community_decision(opportunity_id, decision)
            
            # Update validator statistics
            await self._update_validator_stats(validator_id, feedback)
            
            return {
                "status": "success",
                "message": "Validation received",
                "consensus_reached": decision is not None,
                "decision": decision
            }
            
        except Exception as e:
            logging.error(f"Failed to handle validation: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _store_validation_feedback(self, feedback: ValidationFeedback):
        """Store validation feedback in database"""
        try:
            # This would insert into community_validations table
            validation_data = {
                "opportunity_id": feedback.opportunity_id,
                "validator_user_id": feedback.validator_id,
                "validation_type": feedback.action.value,
                "validation_reason": feedback.reasoning,
                "suggested_changes": feedback.suggested_changes,
                "confidence_in_validation": feedback.confidence,
                "relevance_feedback": self._score_to_feedback(feedback.relevance_score),
                "accuracy_feedback": self._score_to_feedback(feedback.accuracy_score),
                "completeness_feedback": self._score_to_feedback(feedback.completeness_score),
                "created_at": feedback.submitted_at
            }
            
            logging.info(f"Stored validation feedback for opportunity {feedback.opportunity_id}")
            
        except Exception as e:
            logging.error(f"Failed to store validation feedback: {e}")
    
    def _score_to_feedback(self, score: Optional[int]) -> Optional[str]:
        """Convert numeric score to feedback category"""
        if score is None:
            return None
        
        if score >= 4:
            return "excellent"
        elif score >= 3:
            return "good"
        elif score >= 2:
            return "fair"
        else:
            return "poor"
    
    async def _evaluate_community_consensus(self, opportunity_id: int) -> Optional[str]:
        """Evaluate if community has reached consensus"""
        
        validations = self.pending_validations.get(opportunity_id, [])
        
        if len(validations) < self.minimum_validations_for_auto_approve:
            return None
        
        # Count actions
        action_counts = {}
        for validation in validations:
            action = validation.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
        
        total_validations = len(validations)
        
        # Check for consensus
        for action, count in action_counts.items():
            if count / total_validations >= self.consensus_threshold:
                return action
        
        # Check for strong rejection signals
        reject_count = action_counts.get(ValidationAction.REJECT.value, 0)
        flag_count = action_counts.get(ValidationAction.FLAG_ISSUE.value, 0)
        
        if (reject_count + flag_count) / total_validations >= 0.5:
            return "community_flagged"
        
        return None
    
    async def _apply_community_decision(self, opportunity_id: int, decision: str):
        """Apply community decision to opportunity"""
        
        try:
            # Update opportunity status based on decision
            if decision == ValidationAction.APPROVE.value:
                new_status = ReviewStatus.COMMUNITY_APPROVED.value
                await self._schedule_immediate_publication(opportunity_id)
            
            elif decision == ValidationAction.REJECT.value:
                new_status = ReviewStatus.COMMUNITY_FLAGGED.value
                await self._move_to_rejection_database(opportunity_id)
            
            elif decision == "community_flagged":
                new_status = ReviewStatus.MANUAL_REVIEW_REQUIRED.value
                await self._flag_for_human_review(opportunity_id)
            
            else:
                new_status = ReviewStatus.MANUAL_REVIEW_REQUIRED.value
            
            # Update database
            await self._update_opportunity_status(opportunity_id, new_status)
            
            # Notify moderators if needed
            if new_status == ReviewStatus.MANUAL_REVIEW_REQUIRED.value:
                await self._notify_moderators(opportunity_id, decision)
            
            logging.info(f"Applied community decision '{decision}' to opportunity {opportunity_id}")
            
        except Exception as e:
            logging.error(f"Failed to apply community decision: {e}")
    
    async def _schedule_immediate_publication(self, opportunity_id: int):
        """Schedule opportunity for immediate publication"""
        # This would trigger immediate publication workflow
        pass
    
    async def _move_to_rejection_database(self, opportunity_id: int):
        """Move opportunity to rejection database"""
        # This would move the opportunity to rejected_opportunities table
        pass
    
    async def _flag_for_human_review(self, opportunity_id: int):
        """Flag opportunity for human moderator review"""
        # This would add to human review queue
        pass
    
    async def _update_opportunity_status(self, opportunity_id: int, status: str):
        """Update opportunity review status"""
        # This would update the funding_opportunities table
        pass
    
    async def _notify_moderators(self, opportunity_id: int, decision: str):
        """Notify human moderators of community decision"""
        # This would send notifications to moderators
        pass
    
    async def _update_validator_stats(self, validator_id: str, feedback: ValidationFeedback):
        """Update validator performance statistics"""
        
        if validator_id in self.validators:
            validator = self.validators[validator_id]
            validator.validation_count += 1
            validator.last_active = datetime.utcnow()
            
            # Store in database
            await self._store_validator_stats_update(validator_id, feedback)
    
    async def _store_validator_stats_update(self, validator_id: str, feedback: ValidationFeedback):
        """Store validator statistics update"""
        # This would update validator performance metrics
        pass
    
    async def handle_auto_publication_check(self, batch_id: str) -> Dict[str, Any]:
        """Check and execute auto-publication for batch"""
        
        try:
            batch = self.newsletter_batches.get(batch_id)
            if not batch:
                return {"status": "error", "message": "Batch not found"}
            
            if datetime.utcnow() < batch.auto_publish_at:
                return {"status": "not_ready", "message": "Auto-publication time not reached"}
            
            # Check each opportunity for objections
            results = []
            for opp in batch.opportunities:
                opp_id = opp["id"]
                validations = self.pending_validations.get(opp_id, [])
                
                # Check for blocking validations
                blocking_actions = [ValidationAction.REJECT, ValidationAction.FLAG_ISSUE]
                has_objections = any(v.action in blocking_actions for v in validations)
                
                if has_objections:
                    await self._flag_for_human_review(opp_id)
                    results.append({"id": opp_id, "action": "flagged_for_review"})
                else:
                    await self._schedule_immediate_publication(opp_id)
                    results.append({"id": opp_id, "action": "auto_published"})
            
            # Update batch status
            batch.status = "completed"
            
            return {
                "status": "completed",
                "batch_id": batch_id,
                "results": results
            }
            
        except Exception as e:
            logging.error(f"Auto-publication check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get community validation statistics"""
        
        total_validators = len(self.validators)
        active_validators = len([v for v in self.validators.values() if v.is_active])
        
        # Calculate average validation metrics
        total_validations = sum(v.validation_count for v in self.validators.values())
        avg_accuracy = sum(v.accuracy_score for v in self.validators.values()) / total_validators if total_validators > 0 else 0
        
        # Pending validations by opportunity
        pending_count = len(self.pending_validations)
        
        return {
            "validators": {
                "total": total_validators,
                "active": active_validators,
                "avg_accuracy_score": round(avg_accuracy, 3)
            },
            "validations": {
                "total_completed": total_validations,
                "pending_opportunities": pending_count,
                "avg_validations_per_opportunity": round(total_validations / max(pending_count, 1), 2)
            },
            "batches": {
                "total_batches": len(self.newsletter_batches),
                "pending_batches": len([b for b in self.newsletter_batches.values() if b.status == "sent"]),
                "completed_batches": len([b for b in self.newsletter_batches.values() if b.status == "completed"])
            }
        }

# API endpoints and usage functions

async def create_validation_service() -> CommunityValidationService:
    """Create and configure validation service"""
    service = CommunityValidationService()
    await service.load_validators()
    return service

async def daily_newsletter_job():
    """Daily job to prepare and send newsletter"""
    service = await create_validation_service()
    batch_id = await service.prepare_daily_newsletter()
    
    if batch_id:
        logging.info(f"Daily newsletter sent: {batch_id}")
        return {"status": "sent", "batch_id": batch_id}
    else:
        logging.info("No newsletter sent - no new opportunities")
        return {"status": "no_content"}

async def handle_validation_webhook(batch_id: str, opportunity_id: int, 
                                  validator_id: str, action: str, 
                                  feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """Webhook endpoint for handling validation feedback"""
    
    service = await create_validation_service()
    
    # Create feedback object
    feedback = ValidationFeedback(
        opportunity_id=opportunity_id,
        validator_id=validator_id,
        action=ValidationAction(action),
        confidence=feedback_data.get("confidence", "medium"),
        reasoning=feedback_data.get("reasoning", ""),
        suggested_changes=feedback_data.get("suggested_changes"),
        relevance_score=feedback_data.get("relevance_score"),
        accuracy_score=feedback_data.get("accuracy_score"),
        completeness_score=feedback_data.get("completeness_score")
    )
    
    result = await service.handle_community_validation(batch_id, opportunity_id, validator_id, feedback)
    return result

async def auto_publication_check_job():
    """Background job to check for auto-publication"""
    service = await create_validation_service()
    
    # Check all active batches
    results = []
    for batch_id, batch in service.newsletter_batches.items():
        if batch.status == "sent" and datetime.utcnow() >= batch.auto_publish_at:
            result = await service.handle_auto_publication_check(batch_id)
            results.append(result)
    
    return results

# Example usage
if __name__ == "__main__":
    async def main():
        # Test newsletter generation
        service = await create_validation_service()
        batch_id = await service.prepare_daily_newsletter()
        
        if batch_id:
            print(f"Newsletter prepared: {batch_id}")
            
            # Simulate validation feedback
            feedback = ValidationFeedback(
                opportunity_id=1,
                validator_id="validator_1",
                action=ValidationAction.APPROVE,
                confidence="high",
                reasoning="This looks like a legitimate and relevant funding opportunity",
                relevance_score=5,
                accuracy_score=4,
                completeness_score=4
            )
            
            result = await service.handle_community_validation(batch_id, 1, "validator_1", feedback)
            print("Validation result:", result)
            
            # Get statistics
            stats = service.get_validation_statistics()
            print("Statistics:", json.dumps(stats, indent=2))
    
    asyncio.run(main())
