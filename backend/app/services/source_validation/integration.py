"""
Integration Helpers for Source Validation

Helper functions and classes to integrate source validation with existing
TAIFA systems including CrewAI ETL, community validation, and translation pipeline.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .orchestrator import SourceValidationOrchestrator, SourceSubmission
from .deduplication import DeduplicationPipeline, OpportunityContent
from .config import get_config
from app.core.database import get_database


logger = logging.getLogger(__name__)


class CrewAIIntegration:
    """Integration helpers for CrewAI ETL pipeline"""
    
    def __init__(self):
        self.deduplication = DeduplicationPipeline()
        self.config = get_config()
    
    async def preprocess_opportunity(self, raw_opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess opportunity before CrewAI agent processing
        
        Args:
            raw_opportunity: Raw opportunity data from source
            
        Returns:
            Dict with preprocessing results and recommendations
        """
        try:
            # Convert to OpportunityContent for deduplication
            opp_content = OpportunityContent(
                url=raw_opportunity.get('url', ''),
                title=raw_opportunity.get('title', ''),
                description=raw_opportunity.get('description', ''),
                organization=raw_opportunity.get('organization', ''),
                amount=raw_opportunity.get('amount'),
                currency=raw_opportunity.get('currency'),
                deadline=raw_opportunity.get('deadline')
            )
            
            # Check for duplicates
            dedup_result = await self.deduplication.check_for_duplicates(opp_content)
            
            # Determine processing recommendation
            if dedup_result['is_duplicate']:
                return {
                    'action': 'skip_processing',
                    'reason': 'duplicate_detected',
                    'duplicate_info': dedup_result,
                    'existing_opportunity_id': dedup_result.get('existing_opportunity_id'),
                    'confidence': 1.0
                }
            
            # Check content quality indicators
            quality_score = self._assess_content_quality(raw_opportunity)
            
            # Determine processing priority
            priority = self._determine_processing_priority(raw_opportunity, quality_score)
            
            return {
                'action': 'process_with_crewai',
                'reason': 'unique_opportunity',
                'quality_score': quality_score,
                'processing_priority': priority,
                'deduplication_result': dedup_result,
                'confidence': quality_score
            }
            
        except Exception as e:
            logger.error(f"Error preprocessing opportunity: {e}")
            return {
                'action': 'process_with_crewai',  # Fail open
                'reason': 'preprocessing_error',
                'error': str(e),
                'confidence': 0.5
            }
    
    def _assess_content_quality(self, opportunity: Dict[str, Any]) -> float:
        """Assess content quality for processing prioritization"""
        score = 0.0
        max_score = 0.0
        
        # Check for required fields
        required_fields = ['title', 'description', 'organization', 'url']
        for field in required_fields:
            max_score += 1
            if opportunity.get(field):
                score += 1
        
        # Check for additional valuable fields
        valuable_fields = ['amount', 'deadline', 'contact_email', 'application_url']
        for field in valuable_fields:
            max_score += 0.5
            if opportunity.get(field):
                score += 0.5
        
        # Check content length and quality
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        
        if title and len(title) > 10:
            max_score += 0.5
            score += 0.5
        
        if description and len(description) > 50:
            max_score += 0.5
            score += 0.5
        
        return score / max_score if max_score > 0 else 0.0
    
    def _determine_processing_priority(self, opportunity: Dict[str, Any], quality_score: float) -> str:
        """Determine processing priority based on opportunity characteristics"""
        # High priority indicators
        high_priority_keywords = [
            'urgent', 'deadline', 'closing soon', 'final call',
            'ai', 'artificial intelligence', 'machine learning'
        ]
        
        # Check for high priority indicators
        content = f"{opportunity.get('title', '')} {opportunity.get('description', '')}".lower()
        has_high_priority_keywords = any(keyword in content for keyword in high_priority_keywords)
        
        # Check deadline urgency
        deadline = opportunity.get('deadline')
        urgent_deadline = False
        if deadline:
            try:
                if isinstance(deadline, str):
                    from dateutil.parser import parse
                    deadline_date = parse(deadline)
                else:
                    deadline_date = deadline
                
                days_until_deadline = (deadline_date - datetime.now()).days
                urgent_deadline = days_until_deadline <= 7
            except:
                pass
        
        # Check amount significance
        high_value = False
        amount = opportunity.get('amount')
        if amount and isinstance(amount, (int, float)) and amount >= 10000:
            high_value = True
        
        # Determine priority
        if urgent_deadline or (has_high_priority_keywords and high_value):
            return 'high'
        elif quality_score >= 0.8 or has_high_priority_keywords or high_value:
            return 'medium'
        else:
            return 'low'
    
    async def postprocess_opportunity(self, processed_opportunity: Dict[str, Any], 
                                    agent_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Postprocess opportunity after CrewAI agent processing
        
        Args:
            processed_opportunity: Opportunity processed by CrewAI agents
            agent_scores: Scores from relevancy assessor agent
            
        Returns:
            Dict with postprocessing results and routing decisions
        """
        try:
            # Determine confidence level
            overall_confidence = agent_scores.get('overall_relevance', 0.0)
            
            # Determine routing based on confidence and configuration
            config = get_config()
            
            if overall_confidence >= config.validation_thresholds.auto_approve_threshold:
                routing_decision = 'auto_approve'
            elif overall_confidence >= config.validation_thresholds.manual_review_threshold:
                routing_decision = 'community_validation'
            else:
                routing_decision = 'human_review'
            
            # Store processing metadata
            processing_metadata = {
                'processed_at': datetime.now().isoformat(),
                'agent_scores': agent_scores,
                'routing_decision': routing_decision,
                'confidence_level': overall_confidence
            }
            
            return {
                'routing_decision': routing_decision,
                'confidence_level': overall_confidence,
                'processing_metadata': processing_metadata,
                'ready_for_publication': routing_decision == 'auto_approve'
            }
            
        except Exception as e:
            logger.error(f"Error postprocessing opportunity: {e}")
            return {
                'routing_decision': 'human_review',  # Safe default
                'confidence_level': 0.0,
                'processing_metadata': {'error': str(e)},
                'ready_for_publication': False
            }


class CommunityValidationIntegration:
    """Integration helpers for community validation workflow"""
    
    def __init__(self):
        self.config = get_config()
    
    async def prepare_for_community_validation(self, opportunity_id: int) -> Dict[str, Any]:
        """
        Prepare opportunity for community validation
        
        Args:
            opportunity_id: ID of the opportunity to prepare
            
        Returns:
            Dict with preparation results
        """
        try:
            db = await get_database()
            
            # Get opportunity details
            opportunity = await db.fetch_one(
                """
                SELECT id, title, description, organization_name, amount, 
                       deadline, url, agent_scores, confidence_score
                FROM funding_opportunities 
                WHERE id = $1
                """,
                opportunity_id
            )
            
            if not opportunity:
                return {'error': 'Opportunity not found'}
            
            # Create community validation package
            validation_package = {
                'opportunity_id': opportunity_id,
                'title': opportunity['title'],
                'description': opportunity['description'],
                'organization': opportunity['organization_name'],
                'amount': opportunity['amount'],
                'deadline': opportunity['deadline'],
                'url': opportunity['url'],
                'ai_relevance_score': opportunity.get('agent_scores', {}).get('ai_relevance_score'),
                'africa_relevance_score': opportunity.get('agent_scores', {}).get('africa_relevance_score'),
                'confidence_score': opportunity['confidence_score'],
                'validation_instructions': self._generate_validation_instructions(opportunity),
                'required_validators': self._determine_required_validators(opportunity)
            }
            
            # Update opportunity status
            await db.execute(
                "UPDATE funding_opportunities SET review_status = 'pending_community_validation' WHERE id = $1",
                opportunity_id
            )
            
            return validation_package
            
        except Exception as e:
            logger.error(f"Error preparing opportunity for community validation: {e}")
            return {'error': str(e)}
    
    def _generate_validation_instructions(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate specific validation instructions for community"""
        instructions = [
            "Please verify that this opportunity is relevant to AI research or implementation in Africa",
            "Check that the organization and funding details appear legitimate",
            "Verify that the deadline has not passed"
        ]
        
        # Add specific instructions based on opportunity characteristics
        if opportunity.get('amount'):
            instructions.append(f"Verify that the funding amount ({opportunity['amount']}) is accurate")
        
        if opportunity.get('agent_scores', {}).get('ai_relevance_score', 0) < 0.8:
            instructions.append("This opportunity has a lower AI relevance score - please verify AI connection")
        
        if opportunity.get('agent_scores', {}).get('africa_relevance_score', 0) < 0.8:
            instructions.append("This opportunity has a lower Africa relevance score - please verify geographic eligibility")
        
        return instructions
    
    def _determine_required_validators(self, opportunity: Dict[str, Any]) -> int:
        """Determine number of validators required based on opportunity characteristics"""
        base_validators = 2
        
        # Require more validators for high-value opportunities
        amount = opportunity.get('amount', 0)
        if amount and amount >= 100000:  # $100K+
            base_validators += 1
        
        # Require more validators for uncertain opportunities
        confidence = opportunity.get('confidence_score', 1.0)
        if confidence < 0.7:
            base_validators += 1
        
        return min(base_validators, 5)  # Cap at 5 validators
    
    async def process_community_feedback(self, opportunity_id: int, 
                                       validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process community validation results and determine final outcome
        
        Args:
            opportunity_id: ID of the opportunity
            validation_results: List of validation results from community
            
        Returns:
            Dict with processing results and final decision
        """
        try:
            if not validation_results:
                return {'decision': 'insufficient_feedback', 'reason': 'No validation results received'}
            
            # Calculate approval metrics
            total_validators = len(validation_results)
            approvals = sum(1 for result in validation_results if result.get('approved', False))
            approval_rate = approvals / total_validators
            
            # Collect feedback and issues
            all_feedback = []
            issues_raised = []
            
            for result in validation_results:
                if result.get('feedback'):
                    all_feedback.append(result['feedback'])
                if result.get('issues'):
                    issues_raised.extend(result['issues'])
            
            # Determine final decision
            config = get_config()
            required_approval_rate = config.validation_thresholds.min_community_approval
            
            if approval_rate >= required_approval_rate:
                decision = 'approved'
                final_status = 'approved'
            elif approval_rate >= 0.5:  # Marginal case
                decision = 'requires_expert_review'
                final_status = 'pending_expert_review'
            else:
                decision = 'rejected'
                final_status = 'rejected'
            
            # Update opportunity in database
            db = await get_database()
            await db.execute(
                """
                UPDATE funding_opportunities SET
                    review_status = $1,
                    community_approval_rate = $2,
                    community_feedback = $3,
                    community_validation_completed_at = CURRENT_TIMESTAMP
                WHERE id = $4
                """,
                final_status, approval_rate, all_feedback, opportunity_id
            )
            
            return {
                'decision': decision,
                'approval_rate': approval_rate,
                'total_validators': total_validators,
                'approvals': approvals,
                'feedback': all_feedback,
                'issues_raised': issues_raised,
                'final_status': final_status
            }
            
        except Exception as e:
            logger.error(f"Error processing community feedback: {e}")
            return {'decision': 'processing_error', 'error': str(e)}


class TranslationIntegration:
    """Integration helpers for translation pipeline"""
    
    def __init__(self):
        self.config = get_config()
    
    async def queue_for_translation(self, opportunity_id: int, 
                                  source_language: str = 'en',
                                  target_languages: List[str] = None) -> Dict[str, Any]:
        """
        Queue opportunity for translation
        
        Args:
            opportunity_id: ID of the opportunity
            source_language: Source language code
            target_languages: List of target language codes
            
        Returns:
            Dict with queuing results
        """
        if target_languages is None:
            target_languages = ['fr']  # Default to French
        
        try:
            db = await get_database()
            
            # Get opportunity content
            opportunity = await db.fetch_one(
                """
                SELECT title, description, organization_name, 
                       amount, deadline, confidence_score
                FROM funding_opportunities 
                WHERE id = $1
                """,
                opportunity_id
            )
            
            if not opportunity:
                return {'error': 'Opportunity not found'}
            
            # Determine translation priority
            priority = self._determine_translation_priority(opportunity)
            
            # Queue translations for each target language
            translation_jobs = []
            for target_lang in target_languages:
                job_id = await self._create_translation_job(
                    opportunity_id, source_language, target_lang, priority
                )
                translation_jobs.append({
                    'job_id': job_id,
                    'target_language': target_lang,
                    'priority': priority
                })
            
            return {
                'queued': True,
                'translation_jobs': translation_jobs,
                'priority': priority,
                'estimated_completion': self._estimate_completion_time(priority, len(target_languages))
            }
            
        except Exception as e:
            logger.error(f"Error queuing opportunity for translation: {e}")
            return {'error': str(e)}
    
    def _determine_translation_priority(self, opportunity: Dict[str, Any]) -> str:
        """Determine translation priority based on opportunity characteristics"""
        # High priority for urgent deadlines
        deadline = opportunity.get('deadline')
        if deadline:
            try:
                if isinstance(deadline, str):
                    from dateutil.parser import parse
                    deadline_date = parse(deadline)
                else:
                    deadline_date = deadline
                
                days_until_deadline = (deadline_date - datetime.now()).days
                if days_until_deadline <= 14:  # Two weeks or less
                    return 'high'
            except:
                pass
        
        # High priority for high-value opportunities
        amount = opportunity.get('amount', 0)
        if amount and amount >= 50000:  # $50K+
            return 'high'
        
        # Medium priority for confident opportunities
        confidence = opportunity.get('confidence_score', 0)
        if confidence >= 0.8:
            return 'medium'
        
        return 'low'
    
    async def _create_translation_job(self, opportunity_id: int, source_lang: str,
                                    target_lang: str, priority: str) -> int:
        """Create translation job in queue"""
        db = await get_database()
        
        job_id = await db.fetch_val(
            """
            INSERT INTO translation_queue (
                content_type, content_id, source_language, target_language,
                priority, status, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP)
            RETURNING id
            """,
            'funding_opportunity', opportunity_id, source_lang, target_lang,
            priority, 'pending'
        )
        
        return job_id
    
    def _estimate_completion_time(self, priority: str, num_languages: int) -> str:
        """Estimate translation completion time"""
        base_times = {
            'high': 2,    # 2 hours
            'medium': 8,  # 8 hours
            'low': 24     # 24 hours
        }
        
        base_time = base_times.get(priority, 24)
        total_time = base_time * num_languages
        
        if total_time < 24:
            return f"{total_time} hours"
        else:
            days = total_time // 24
            return f"{days} day{'s' if days > 1 else ''}"


class SourceManagementHelpers:
    """Helper functions for source management operations"""
    
    @staticmethod
    async def create_source_from_submission(submission_id: int) -> Optional[int]:
        """Create data source from approved submission"""
        try:
            db = await get_database()
            
            # Get submission details
            submission = await db.fetch_one(
                "SELECT * FROM source_submissions WHERE id = $1",
                submission_id
            )
            
            if not submission or submission['status'] != 'approved_for_pilot':
                return None
            
            # Create data source entry
            source_id = await db.fetch_val(
                """
                INSERT INTO data_sources (
                    name, url, source_type, status, pilot_mode,
                    created_at, submission_id
                ) VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, $6)
                RETURNING id
                """,
                submission['name'], submission['url'], submission['source_type'],
                'pilot', True, submission_id
            )
            
            return source_id
            
        except Exception as e:
            logger.error(f"Error creating source from submission: {e}")
            return None
    
    @staticmethod
    async def get_source_performance_summary(source_id: int, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for a source"""
        try:
            from .performance_tracker import PerformanceTracker
            
            tracker = PerformanceTracker()
            metrics = await tracker.evaluate_source_performance(source_id, days)
            
            return {
                'source_id': source_id,
                'overall_score': metrics.overall_score,
                'status': metrics.performance_status.value,
                'opportunities_discovered': metrics.opportunities_discovered,
                'approval_rate': metrics.community_approval_rate,
                'duplicate_rate': metrics.duplicate_rate,
                'reliability': metrics.monitoring_reliability,
                'evaluation_period': days
            }
            
        except Exception as e:
            logger.error(f"Error getting source performance summary: {e}")
            return {'error': str(e)}


# Convenience functions for common operations
async def quick_duplicate_check(url: str, title: str, organization: str) -> bool:
    """Quick duplicate check for an opportunity"""
    try:
        content = OpportunityContent(
            url=url,
            title=title,
            description="",  # Can be empty for quick check
            organization=organization
        )
        
        pipeline = DeduplicationPipeline()
        result = await pipeline.check_for_duplicates(content)
        
        return result['is_duplicate']
        
    except Exception as e:
        logger.error(f"Error in quick duplicate check: {e}")
        return False  # Assume not duplicate on error


async def submit_source_from_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit source from web form data"""
    try:
        # Convert form data to SourceSubmission
        submission = SourceSubmission(
            name=form_data['name'],
            url=form_data['url'],
            contact_person=form_data['contact_person'],
            contact_email=form_data['contact_email'],
            source_type=form_data['source_type'],
            update_frequency=form_data['update_frequency'],
            geographic_focus=form_data['geographic_focus'],
            expected_volume=form_data['expected_volume'],
            sample_urls=form_data['sample_urls'],
            ai_relevance_estimate=form_data['ai_relevance_estimate'],
            africa_relevance_estimate=form_data['africa_relevance_estimate'],
            language=form_data['language'],
            submitter_role=form_data['submitter_role'],
            has_permission=form_data['has_permission'],
            preferred_contact=form_data['preferred_contact'],
            submitted_at=datetime.now()
        )
        
        # Process submission
        async with SourceValidationOrchestrator() as orchestrator:
            result = await orchestrator.submit_source(submission)
        
        return {
            'success': True,
            'submission_id': result.submission_id,
            'status': result.status.value,
            'next_steps': result.next_steps
        }
        
    except Exception as e:
        logger.error(f"Error submitting source from form: {e}")
        return {'success': False, 'error': str(e)}


# Export helper instances for easy import
crewai_integration = CrewAIIntegration()
community_validation_integration = CommunityValidationIntegration()
translation_integration = TranslationIntegration()
