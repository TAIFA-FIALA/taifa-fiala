"""
Performance Tracker Module

Monitors and evaluates the performance of data sources during pilot periods
and ongoing operation. Tracks metrics like opportunity discovery rate,
quality scores, duplicate rates, and technical reliability.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from app.core.database import get_database


class PerformanceStatus(Enum):
    """Source performance status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILING = "failing"


@dataclass
class SourceMetrics:
    """Performance metrics for a source"""
    source_id: int
    source_name: str
    evaluation_period: int  # days
    
    # Volume metrics
    opportunities_discovered: int
    ai_relevant_count: int
    africa_relevant_count: int
    funding_relevant_count: int
    
    # Quality metrics
    community_approval_rate: float
    duplicate_rate: float
    data_completeness_score: float
    
    # Technical metrics
    monitoring_reliability: float
    processing_error_rate: float
    average_response_time: float
    
    # Value metrics
    unique_opportunities_added: int
    high_value_opportunities: int
    successful_applications: int
    
    # Derived scores
    overall_score: float
    performance_status: PerformanceStatus
    
    # Timestamps
    calculated_at: datetime
    next_evaluation: datetime


@dataclass
class PerformanceThresholds:
    """Thresholds for performance evaluation"""
    # Minimum requirements for approval
    min_ai_relevance: float = 0.30
    min_africa_relevance: float = 0.50
    min_community_approval: float = 0.70
    max_duplicate_rate: float = 0.20
    min_monitoring_reliability: float = 0.95
    
    # Preferred performance levels
    preferred_unique_opportunities: int = 5  # per month
    preferred_high_value_count: int = 1     # per month
    preferred_completeness: float = 0.80
    
    # Failing thresholds
    failing_approval_rate: float = 0.50
    failing_reliability: float = 0.80
    failing_duplicate_rate: float = 0.40


class PerformanceTracker:
    """Tracks and evaluates source performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.thresholds = PerformanceThresholds()
    
    async def evaluate_source_performance(self, source_id: int, evaluation_days: int = 30) -> SourceMetrics:
        """
        Evaluate comprehensive performance metrics for a source
        
        Args:
            source_id: ID of the source to evaluate
            evaluation_days: Number of days to look back for evaluation
            
        Returns:
            SourceMetrics with comprehensive performance data
        """
        self.logger.info(f"Evaluating performance for source {source_id} over {evaluation_days} days")
        
        try:
            db = await get_database()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=evaluation_days)
            
            # Get source information
            source_info = await db.fetch_one(
                "SELECT name FROM data_sources WHERE id = $1",
                source_id
            )
            
            if not source_info:
                raise ValueError(f"Source {source_id} not found")
            
            # Calculate metrics concurrently
            volume_metrics, quality_metrics, technical_metrics, value_metrics = await asyncio.gather(
                self._calculate_volume_metrics(source_id, start_date, end_date),
                self._calculate_quality_metrics(source_id, start_date, end_date),
                self._calculate_technical_metrics(source_id, start_date, end_date),
                self._calculate_value_metrics(source_id, start_date, end_date)
            )
            
            # Calculate overall score and status
            overall_score = self._calculate_overall_score(
                volume_metrics, quality_metrics, technical_metrics, value_metrics
            )
            
            performance_status = self._determine_performance_status(
                overall_score, quality_metrics, technical_metrics
            )
            
            # Create metrics object
            metrics = SourceMetrics(
                source_id=source_id,
                source_name=source_info["name"],
                evaluation_period=evaluation_days,
                
                # Volume metrics
                opportunities_discovered=volume_metrics["total_opportunities"],
                ai_relevant_count=volume_metrics["ai_relevant"],
                africa_relevant_count=volume_metrics["africa_relevant"],
                funding_relevant_count=volume_metrics["funding_relevant"],
                
                # Quality metrics  
                community_approval_rate=quality_metrics["approval_rate"],
                duplicate_rate=quality_metrics["duplicate_rate"],
                data_completeness_score=quality_metrics["completeness_score"],
                
                # Technical metrics
                monitoring_reliability=technical_metrics["reliability"],
                processing_error_rate=technical_metrics["error_rate"],
                average_response_time=technical_metrics["avg_response_time"],
                
                # Value metrics
                unique_opportunities_added=value_metrics["unique_added"],
                high_value_opportunities=value_metrics["high_value_count"],
                successful_applications=value_metrics["successful_applications"],
                
                # Derived scores
                overall_score=overall_score,
                performance_status=performance_status,
                
                # Timestamps
                calculated_at=datetime.now(),
                next_evaluation=datetime.now() + timedelta(days=evaluation_days)
            )
            
            # Store metrics in database
            await self._store_performance_metrics(metrics)
            
            self.logger.info(f"Performance evaluation complete: {performance_status.value} (score: {overall_score:.2f})")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating source performance: {e}")
            raise
    
    async def _calculate_volume_metrics(self, source_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate volume-related metrics"""
        db = await get_database()
        
        # Get all opportunities from this source in the period
        opportunities = await db.fetch_all(
            """
            SELECT agent_scores, processing_metadata
            FROM funding_opportunities 
            WHERE source_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            source_id, start_date, end_date
        )
        
        total_opportunities = len(opportunities)
        
        if total_opportunities == 0:
            return {
                "total_opportunities": 0,
                "ai_relevant": 0,
                "africa_relevant": 0,
                "funding_relevant": 0,
                "ai_relevance_rate": 0,
                "africa_relevance_rate": 0,
                "funding_relevance_rate": 0
            }
        
        # Count relevant opportunities based on agent scores
        ai_relevant = 0
        africa_relevant = 0
        funding_relevant = 0
        
        for opp in opportunities:
            scores = opp.get("agent_scores", {})
            if isinstance(scores, dict):
                if scores.get("ai_relevance_score", 0) >= 0.7:
                    ai_relevant += 1
                if scores.get("africa_relevance_score", 0) >= 0.7:
                    africa_relevant += 1
                if scores.get("funding_relevance_score", 0) >= 0.7:
                    funding_relevant += 1
        
        return {
            "total_opportunities": total_opportunities,
            "ai_relevant": ai_relevant,
            "africa_relevant": africa_relevant,
            "funding_relevant": funding_relevant,
            "ai_relevance_rate": ai_relevant / total_opportunities,
            "africa_relevance_rate": africa_relevant / total_opportunities,
            "funding_relevance_rate": funding_relevant / total_opportunities
        }
    
    async def _calculate_quality_metrics(self, source_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate quality-related metrics"""
        db = await get_database()
        
        # Get community validation results
        validations = await db.fetch_all(
            """
            SELECT fo.id, fo.review_status, fo.confidence_score
            FROM funding_opportunities fo
            WHERE fo.source_id = $1 
            AND fo.created_at BETWEEN $2 AND $3
            AND fo.review_status IS NOT NULL
            """,
            source_id, start_date, end_date
        )
        
        if not validations:
            return {
                "approval_rate": 0,
                "duplicate_rate": 0,
                "completeness_score": 0,
                "avg_confidence": 0
            }
        
        # Calculate approval rate
        approved = sum(1 for v in validations if v["review_status"] in ["approved", "published"])
        approval_rate = approved / len(validations)
        
        # Get duplicate detection results
        duplicates = await db.fetch_all(
            """
            SELECT COUNT(*) as duplicate_count
            FROM deduplication_logs dl
            JOIN funding_opportunities fo ON dl.opportunity_id = fo.id
            WHERE fo.source_id = $1
            AND dl.checked_at BETWEEN $2 AND $3  
            AND dl.is_duplicate = true
            """,
            source_id, start_date, end_date
        )
        
        duplicate_count = duplicates[0]["duplicate_count"] if duplicates else 0
        total_processed = len(validations) + duplicate_count
        duplicate_rate = duplicate_count / total_processed if total_processed > 0 else 0
        
        # Calculate data completeness
        complete_records = await db.fetch_all(
            """
            SELECT fo.id
            FROM funding_opportunities fo
            WHERE fo.source_id = $1
            AND fo.created_at BETWEEN $2 AND $3
            AND fo.title IS NOT NULL 
            AND fo.description IS NOT NULL
            AND fo.organization_name IS NOT NULL
            AND fo.amount IS NOT NULL
            AND fo.deadline IS NOT NULL
            """,
            source_id, start_date, end_date
        )
        
        total_records = await db.fetch_one(
            """
            SELECT COUNT(*) as total
            FROM funding_opportunities 
            WHERE source_id = $1 AND created_at BETWEEN $2 AND $3
            """,
            source_id, start_date, end_date
        )
        
        total_count = total_records["total"] if total_records else 0
        completeness_score = len(complete_records) / total_count if total_count > 0 else 0
        
        # Calculate average confidence
        avg_confidence = sum(v["confidence_score"] or 0 for v in validations) / len(validations)
        
        return {
            "approval_rate": approval_rate,
            "duplicate_rate": duplicate_rate,
            "completeness_score": completeness_score,
            "avg_confidence": avg_confidence,
            "total_validated": len(validations),
            "total_approved": approved
        }
    
    async def _calculate_technical_metrics(self, source_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate technical performance metrics"""
        db = await get_database()
        
        # Get monitoring logs for this source
        monitoring_logs = await db.fetch_all(
            """
            SELECT success, error_message, response_time_ms, checked_at
            FROM source_monitoring_logs 
            WHERE source_id = $1 AND checked_at BETWEEN $2 AND $3
            ORDER BY checked_at
            """,
            source_id, start_date, end_date
        )
        
        if not monitoring_logs:
            return {
                "reliability": 0,
                "error_rate": 1,
                "avg_response_time": 0,
                "total_checks": 0,
                "successful_checks": 0
            }
        
        total_checks = len(monitoring_logs)
        successful_checks = sum(1 for log in monitoring_logs if log["success"])
        reliability = successful_checks / total_checks
        error_rate = 1 - reliability
        
        # Calculate average response time (only for successful requests)
        successful_times = [
            log["response_time_ms"] for log in monitoring_logs 
            if log["success"] and log["response_time_ms"]
        ]
        avg_response_time = sum(successful_times) / len(successful_times) if successful_times else 0
        
        return {
            "reliability": reliability,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "total_checks": total_checks,
            "successful_checks": successful_checks
        }
    
    async def _calculate_value_metrics(self, source_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate value-related metrics"""
        db = await get_database()
        
        # Get unique opportunities (not duplicates)
        unique_opportunities = await db.fetch_all(
            """
            SELECT fo.id, fo.amount
            FROM funding_opportunities fo
            LEFT JOIN deduplication_logs dl ON fo.id = dl.opportunity_id
            WHERE fo.source_id = $1 
            AND fo.created_at BETWEEN $2 AND $3
            AND fo.review_status = 'approved'
            AND (dl.is_duplicate = false OR dl.is_duplicate IS NULL)
            """,
            source_id, start_date, end_date
        )
        
        unique_added = len(unique_opportunities)
        
        # Count high-value opportunities (>$10K USD equivalent)
        high_value_count = sum(
            1 for opp in unique_opportunities 
            if opp["amount"] and opp["amount"] >= 10000
        )
        
        # Get successful applications (if tracked)
        successful_applications = await db.fetch_one(
            """
            SELECT COUNT(*) as count
            FROM application_outcomes ao
            JOIN funding_opportunities fo ON ao.opportunity_id = fo.id
            WHERE fo.source_id = $1
            AND ao.outcome = 'successful'
            AND ao.created_at BETWEEN $2 AND $3
            """,
            source_id, start_date, end_date
        )
        
        return {
            "unique_added": unique_added,
            "high_value_count": high_value_count,
            "successful_applications": successful_applications["count"] if successful_applications else 0,
            "total_value": sum(opp["amount"] or 0 for opp in unique_opportunities)
        }
    
    def _calculate_overall_score(self, volume_metrics: Dict, quality_metrics: Dict, 
                                technical_metrics: Dict, value_metrics: Dict) -> float:
        """Calculate overall performance score"""
        # Weights for different metric categories
        weights = {
            "volume": 0.25,
            "quality": 0.35,
            "technical": 0.25,
            "value": 0.15
        }
        
        # Volume score (based on relevance rates)
        volume_score = (
            volume_metrics["ai_relevance_rate"] * 0.4 +
            volume_metrics["africa_relevance_rate"] * 0.4 +
            volume_metrics["funding_relevance_rate"] * 0.2
        )
        
        # Quality score  
        quality_score = (
            quality_metrics["approval_rate"] * 0.5 +
            (1 - quality_metrics["duplicate_rate"]) * 0.3 +
            quality_metrics["completeness_score"] * 0.2
        )
        
        # Technical score
        technical_score = (
            technical_metrics["reliability"] * 0.7 +
            (1 - technical_metrics["error_rate"]) * 0.3
        )
        
        # Value score (normalized)
        monthly_unique = value_metrics["unique_added"] * (30 / 30)  # Normalize to monthly
        monthly_high_value = value_metrics["high_value_count"] * (30 / 30)
        
        value_score = min(
            (monthly_unique / max(self.thresholds.preferred_unique_opportunities, 1)) * 0.7 +
            (monthly_high_value / max(self.thresholds.preferred_high_value_count, 1)) * 0.3,
            1.0  # Cap at 1.0
        )
        
        # Calculate weighted overall score
        overall_score = (
            volume_score * weights["volume"] +
            quality_score * weights["quality"] +
            technical_score * weights["technical"] +
            value_score * weights["value"]
        )
        
        return min(max(overall_score, 0.0), 1.0)  # Ensure score is between 0 and 1
    
    def _determine_performance_status(self, overall_score: float, quality_metrics: Dict, 
                                    technical_metrics: Dict) -> PerformanceStatus:
        """Determine performance status based on score and critical metrics"""
        # Check for failing conditions first
        if (quality_metrics["approval_rate"] < self.thresholds.failing_approval_rate or
            technical_metrics["reliability"] < self.thresholds.failing_reliability or
            quality_metrics["duplicate_rate"] > self.thresholds.failing_duplicate_rate):
            return PerformanceStatus.FAILING
        
        # Check minimum requirements
        if (quality_metrics["approval_rate"] < self.thresholds.min_community_approval or
            technical_metrics["reliability"] < self.thresholds.min_monitoring_reliability or
            quality_metrics["duplicate_rate"] > self.thresholds.max_duplicate_rate):
            return PerformanceStatus.POOR
        
        # Determine status based on overall score
        if overall_score >= 0.9:
            return PerformanceStatus.EXCELLENT
        elif overall_score >= 0.75:
            return PerformanceStatus.GOOD
        elif overall_score >= 0.6:
            return PerformanceStatus.ACCEPTABLE
        else:
            return PerformanceStatus.POOR
    
    async def _store_performance_metrics(self, metrics: SourceMetrics) -> None:
        """Store performance metrics in database"""
        try:
            db = await get_database()
            
            await db.execute(
                """
                INSERT INTO source_performance_metrics (
                    source_id, evaluation_period_days, calculated_at,
                    opportunities_discovered, ai_relevant_count, africa_relevant_count,
                    community_approval_rate, duplicate_rate, data_completeness_score,
                    monitoring_reliability, processing_error_rate, average_response_time,
                    unique_opportunities_added, high_value_opportunities,
                    overall_score, performance_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                metrics.source_id, metrics.evaluation_period, metrics.calculated_at,
                metrics.opportunities_discovered, metrics.ai_relevant_count, metrics.africa_relevant_count,
                metrics.community_approval_rate, metrics.duplicate_rate, metrics.data_completeness_score,
                metrics.monitoring_reliability, metrics.processing_error_rate, metrics.average_response_time,
                metrics.unique_opportunities_added, metrics.high_value_opportunities,
                metrics.overall_score, metrics.performance_status.value
            )
            
        except Exception as e:
            self.logger.error(f"Error storing performance metrics: {e}")
    
    async def get_source_performance_history(self, source_id: int, limit: int = 10) -> List[SourceMetrics]:
        """Get historical performance metrics for a source"""
        try:
            db = await get_database()
            
            history = await db.fetch_all(
                """
                SELECT * FROM source_performance_metrics 
                WHERE source_id = $1 
                ORDER BY calculated_at DESC 
                LIMIT $2
                """,
                source_id, limit
            )
            
            metrics_list = []
            for record in history:
                metrics = SourceMetrics(
                    source_id=record["source_id"],
                    source_name="",  # Will be filled separately if needed
                    evaluation_period=record["evaluation_period_days"],
                    opportunities_discovered=record["opportunities_discovered"],
                    ai_relevant_count=record["ai_relevant_count"],
                    africa_relevant_count=record["africa_relevant_count"],
                    funding_relevant_count=0,  # Not stored in old records
                    community_approval_rate=record["community_approval_rate"],
                    duplicate_rate=record["duplicate_rate"],
                    data_completeness_score=record["data_completeness_score"],
                    monitoring_reliability=record["monitoring_reliability"],
                    processing_error_rate=record["processing_error_rate"],
                    average_response_time=record["average_response_time"],
                    unique_opportunities_added=record["unique_opportunities_added"],
                    high_value_opportunities=record["high_value_opportunities"],
                    successful_applications=0,  # Not stored in old records
                    overall_score=record["overall_score"],
                    performance_status=PerformanceStatus(record["performance_status"]),
                    calculated_at=record["calculated_at"],
                    next_evaluation=record["calculated_at"] + timedelta(days=30)
                )
                metrics_list.append(metrics)
            
            return metrics_list
            
        except Exception as e:
            self.logger.error(f"Error getting performance history: {e}")
            return []
    
    async def get_all_sources_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all sources"""
        try:
            db = await get_database()
            
            # Get latest performance metrics for all sources
            summary = await db.fetch_all(
                """
                WITH latest_metrics AS (
                    SELECT DISTINCT ON (source_id) 
                        source_id, performance_status, overall_score, calculated_at
                    FROM source_performance_metrics 
                    ORDER BY source_id, calculated_at DESC
                )
                SELECT 
                    ds.name as source_name,
                    ds.url as source_url,
                    ds.source_type,
                    lm.performance_status,
                    lm.overall_score,
                    lm.calculated_at as last_evaluation
                FROM data_sources ds
                LEFT JOIN latest_metrics lm ON ds.id = lm.source_id
                WHERE ds.status = 'active'
                ORDER BY lm.overall_score DESC NULLS LAST
                """)
            
            # Count by status
            status_counts = {}
            for status in PerformanceStatus:
                status_counts[status.value] = 0
            
            for source in summary:
                if source["performance_status"]:
                    status_counts[source["performance_status"]] += 1
                else:
                    status_counts["not_evaluated"] = status_counts.get("not_evaluated", 0) + 1
            
            return {
                "total_sources": len(summary),
                "status_breakdown": status_counts,
                "average_score": sum(s["overall_score"] or 0 for s in summary) / len(summary) if summary else 0,
                "sources_needing_evaluation": sum(1 for s in summary if not s["performance_status"]),
                "top_performing_sources": [
                    {
                        "name": s["source_name"],
                        "score": s["overall_score"],
                        "status": s["performance_status"]
                    }
                    for s in summary[:5] if s["overall_score"]
                ],
                "sources_detail": summary
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    async def identify_sources_for_review(self) -> List[Dict[str, Any]]:
        """Identify sources that need performance review"""
        try:
            db = await get_database()
            
            # Find sources that haven't been evaluated recently
            sources_for_review = await db.fetch_all(
                """
                WITH latest_evaluations AS (
                    SELECT DISTINCT ON (source_id) 
                        source_id, calculated_at, performance_status
                    FROM source_performance_metrics 
                    ORDER BY source_id, calculated_at DESC
                )
                SELECT 
                    ds.id, ds.name, ds.url, ds.created_at,
                    le.calculated_at as last_evaluation,
                    le.performance_status
                FROM data_sources ds
                LEFT JOIN latest_evaluations le ON ds.id = le.source_id
                WHERE ds.status = 'active'
                AND (
                    le.calculated_at IS NULL OR 
                    le.calculated_at < NOW() - INTERVAL '30 days' OR
                    le.performance_status IN ('poor', 'failing')
                )
                ORDER BY 
                    CASE 
                        WHEN le.performance_status = 'failing' THEN 1
                        WHEN le.performance_status = 'poor' THEN 2
                        WHEN le.calculated_at IS NULL THEN 3
                        ELSE 4
                    END,
                    le.calculated_at ASC NULLS FIRST
                """)
            
            review_list = []
            for source in sources_for_review:
                days_since_eval = None
                if source["last_evaluation"]:
                    days_since_eval = (datetime.now() - source["last_evaluation"]).days
                
                priority = "high" if source["performance_status"] in ["poor", "failing"] else "medium"
                if not source["last_evaluation"]:
                    priority = "high"
                elif days_since_eval > 60:
                    priority = "high"
                
                review_list.append({
                    "source_id": source["id"],
                    "source_name": source["name"],
                    "source_url": source["url"],
                    "last_evaluation": source["last_evaluation"],
                    "days_since_evaluation": days_since_eval,
                    "current_status": source["performance_status"],
                    "review_priority": priority,
                    "reason": self._get_review_reason(source, days_since_eval)
                })
            
            return review_list
            
        except Exception as e:
            self.logger.error(f"Error identifying sources for review: {e}")
            return []
    
    def _get_review_reason(self, source: Dict, days_since_eval: Optional[int]) -> str:
        """Determine reason for performance review"""
        if not source["last_evaluation"]:
            return "Never evaluated"
        elif source["performance_status"] == "failing":
            return "Failing performance status"
        elif source["performance_status"] == "poor":
            return "Poor performance status"
        elif days_since_eval and days_since_eval > 60:
            return f"Overdue evaluation ({days_since_eval} days)"
        elif days_since_eval and days_since_eval > 30:
            return f"Scheduled evaluation ({days_since_eval} days)"
        else:
            return "Regular review"
    
    async def generate_performance_report(self, source_id: int) -> Dict[str, Any]:
        """Generate comprehensive performance report for a source"""
        try:
            # Get current metrics
            current_metrics = await self.evaluate_source_performance(source_id)
            
            # Get historical performance
            history = await self.get_source_performance_history(source_id, limit=6)
            
            # Calculate trends
            trends = self._calculate_performance_trends(history)
            
            # Get recommendations
            recommendations = self._generate_performance_recommendations(current_metrics, trends)
            
            return {
                "source_id": source_id,
                "source_name": current_metrics.source_name,
                "current_performance": {
                    "overall_score": current_metrics.overall_score,
                    "status": current_metrics.performance_status.value,
                    "key_metrics": {
                        "opportunities_discovered": current_metrics.opportunities_discovered,
                        "approval_rate": current_metrics.community_approval_rate,
                        "duplicate_rate": current_metrics.duplicate_rate,
                        "reliability": current_metrics.monitoring_reliability
                    }
                },
                "historical_performance": history,
                "trends": trends,
                "recommendations": recommendations,
                "meets_thresholds": self._check_threshold_compliance(current_metrics),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_trends(self, history: List[SourceMetrics]) -> Dict[str, Any]:
        """Calculate performance trends from historical data"""
        if len(history) < 2:
            return {"insufficient_data": True}
        
        # Sort by date (oldest first for trend calculation)
        sorted_history = sorted(history, key=lambda x: x.calculated_at)
        
        # Calculate trends for key metrics
        scores = [m.overall_score for m in sorted_history]
        approval_rates = [m.community_approval_rate for m in sorted_history]
        reliability_scores = [m.monitoring_reliability for m in sorted_history]
        
        def calculate_trend(values):
            if len(values) < 2:
                return "stable"
            
            # Simple trend calculation
            recent_avg = sum(values[-2:]) / 2
            older_avg = sum(values[:-2]) / max(len(values) - 2, 1)
            
            if recent_avg > older_avg * 1.1:
                return "improving"
            elif recent_avg < older_avg * 0.9:
                return "declining"
            else:
                return "stable"
        
        return {
            "overall_score_trend": calculate_trend(scores),
            "approval_rate_trend": calculate_trend(approval_rates),
            "reliability_trend": calculate_trend(reliability_scores),
            "evaluation_count": len(history),
            "evaluation_period": f"{sorted_history[0].calculated_at.date()} to {sorted_history[-1].calculated_at.date()}"
        }
    
    def _generate_performance_recommendations(self, metrics: SourceMetrics, trends: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Approval rate recommendations
        if metrics.community_approval_rate < self.thresholds.min_community_approval:
            recommendations.append(
                f"Improve content relevance - approval rate is {metrics.community_approval_rate:.1%}, "
                f"target is {self.thresholds.min_community_approval:.1%}"
            )
        
        # Duplicate rate recommendations  
        if metrics.duplicate_rate > self.thresholds.max_duplicate_rate:
            recommendations.append(
                f"Reduce duplicate content - duplicate rate is {metrics.duplicate_rate:.1%}, "
                f"target is below {self.thresholds.max_duplicate_rate:.1%}"
            )
        
        # Reliability recommendations
        if metrics.monitoring_reliability < self.thresholds.min_monitoring_reliability:
            recommendations.append(
                f"Improve technical reliability - current reliability is {metrics.monitoring_reliability:.1%}, "
                f"target is {self.thresholds.min_monitoring_reliability:.1%}"
            )
        
        # Volume recommendations
        if metrics.unique_opportunities_added < self.thresholds.preferred_unique_opportunities:
            recommendations.append(
                f"Increase unique opportunity discovery - current rate is {metrics.unique_opportunities_added} "
                f"per month, target is {self.thresholds.preferred_unique_opportunities}"
            )
        
        # Trend-based recommendations
        if trends.get("overall_score_trend") == "declining":
            recommendations.append("Overall performance is declining - investigate recent changes")
        
        if trends.get("reliability_trend") == "declining":
            recommendations.append("Technical reliability is declining - check monitoring configuration")
        
        # Data completeness recommendations
        if metrics.data_completeness_score < self.thresholds.preferred_completeness:
            recommendations.append(
                f"Improve data extraction completeness - current score is {metrics.data_completeness_score:.1%}, "
                f"target is {self.thresholds.preferred_completeness:.1%}"
            )
        
        if not recommendations:
            recommendations.append("Performance is meeting all targets - continue current approach")
        
        return recommendations
    
    def _check_threshold_compliance(self, metrics: SourceMetrics) -> Dict[str, bool]:
        """Check if metrics meet minimum thresholds"""
        return {
            "min_community_approval": metrics.community_approval_rate >= self.thresholds.min_community_approval,
            "max_duplicate_rate": metrics.duplicate_rate <= self.thresholds.max_duplicate_rate,
            "min_monitoring_reliability": metrics.monitoring_reliability >= self.thresholds.min_monitoring_reliability,
            "preferred_unique_opportunities": metrics.unique_opportunities_added >= self.thresholds.preferred_unique_opportunities,
            "preferred_completeness": metrics.data_completeness_score >= self.thresholds.preferred_completeness,
            "overall_passing": (
                metrics.community_approval_rate >= self.thresholds.min_community_approval and
                metrics.duplicate_rate <= self.thresholds.max_duplicate_rate and
                metrics.monitoring_reliability >= self.thresholds.min_monitoring_reliability
            )
        }


async def test_performance_tracker():
    """Test function for performance tracker"""
    tracker = PerformanceTracker()
    
    # Test with a sample source ID (would need to exist in database)
    test_source_id = 1
    
    try:
        print("Testing performance evaluation...")
        metrics = await tracker.evaluate_source_performance(test_source_id, evaluation_days=30)
        
        print(f"\nPerformance Results for Source {test_source_id}:")
        print(f"Overall Score: {metrics.overall_score:.2f}")
        print(f"Status: {metrics.performance_status.value}")
        print(f"Opportunities Discovered: {metrics.opportunities_discovered}")
        print(f"Community Approval Rate: {metrics.community_approval_rate:.1%}")
        print(f"Duplicate Rate: {metrics.duplicate_rate:.1%}")
        print(f"Monitoring Reliability: {metrics.monitoring_reliability:.1%}")
        
        # Test performance summary
        print("\nTesting performance summary...")
        summary = await tracker.get_all_sources_performance_summary()
        print(f"Total Sources: {summary['total_sources']}")
        print(f"Average Score: {summary['average_score']:.2f}")
        
        # Test sources needing review
        print("\nTesting sources for review identification...")
        review_list = await tracker.identify_sources_for_review()
        print(f"Sources needing review: {len(review_list)}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_performance_tracker())
