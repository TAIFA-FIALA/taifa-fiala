"""
Source Quality Scoring System
============================

Comprehensive system for tracking and scoring the quality of different
data sources in the AI Africa Funding Tracker pipeline.

This system helps identify the most reliable sources and automatically
adjust processing priorities based on historical performance.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from statistics import mean, median, stdev

from app.models.validation import SourceQuality, ValidationResult
from app.models.funding import AfricaIntelligenceItem
from app.core.database import get_db_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# QUALITY SCORING MODELS
# =============================================================================

class QualityGrade(Enum):
    """Quality grades for sources"""
    A = "A"  # Excellent (≥90%)
    B = "B"  # Good (≥80%)
    C = "C"  # Average (≥70%)
    D = "D"  # Below Average (≥60%)
    F = "F"  # Poor (<60%)

class SourceType(Enum):
    """Types of sources"""
    RSS_FEED = "rss_feed"
    WEBSITE = "website"
    API = "api"
    USER_SUBMISSION = "user_submission"
    SOCIAL_MEDIA = "social_media"
    NEWS_OUTLET = "news_outlet"
    OFFICIAL_ANNOUNCEMENT = "official_announcement"

@dataclass
class QualityMetrics:
    """Quality metrics for a source"""
    accuracy_score: float = 0.0
    duplicate_rate: float = 0.0
    processing_success_rate: float = 0.0
    content_relevance_score: float = 0.0
    timeliness_score: float = 0.0
    completeness_score: float = 0.0
    
    def calculate_overall_score(self) -> float:
        """Calculate overall quality score"""
        weights = {
            'accuracy': 0.25,
            'duplicate_rate': 0.20,  # Lower is better
            'processing_success': 0.20,
            'content_relevance': 0.15,
            'timeliness': 0.10,
            'completeness': 0.10
        }
        
        score = (
            self.accuracy_score * weights['accuracy'] +
            (1 - self.duplicate_rate) * weights['duplicate_rate'] +
            self.processing_success_rate * weights['processing_success'] +
            self.content_relevance_score * weights['content_relevance'] +
            self.timeliness_score * weights['timeliness'] +
            self.completeness_score * weights['completeness']
        )
        
        return min(1.0, max(0.0, score))

@dataclass
class SourcePerformanceSnapshot:
    """Performance snapshot for a source"""
    source_name: str
    source_type: SourceType
    timestamp: datetime
    metrics: QualityMetrics
    item_counts: Dict[str, int] = field(default_factory=dict)
    recent_issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'source_name': self.source_name,
            'source_type': self.source_type.value,
            'timestamp': self.timestamp.isoformat(),
            'metrics': {
                'accuracy_score': self.metrics.accuracy_score,
                'duplicate_rate': self.metrics.duplicate_rate,
                'processing_success_rate': self.metrics.processing_success_rate,
                'content_relevance_score': self.metrics.content_relevance_score,
                'timeliness_score': self.metrics.timeliness_score,
                'completeness_score': self.metrics.completeness_score,
                'overall_score': self.metrics.calculate_overall_score()
            },
            'item_counts': self.item_counts,
            'recent_issues': self.recent_issues
        }

# =============================================================================
# SOURCE QUALITY SCORING ENGINE
# =============================================================================

class SourceQualityScorer:
    """Engine for scoring source quality with equity awareness"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Scoring thresholds
        self.accuracy_threshold = 0.8
        self.duplicate_rate_threshold = 0.15
        self.relevance_threshold = 0.7
        self.timeliness_threshold = 0.8
        
        # Time windows for analysis
        self.analysis_window_days = 30
        self.recent_issues_window_days = 7
        
        # Quality patterns
        self.quality_patterns = {
            'high_duplicate_sources': set(),
            'low_accuracy_sources': set(),
            'slow_processing_sources': set(),
            'unreliable_sources': set()
        }
        
        # Equity-aware scoring weights
        self.equity_weights = {
            'geographic_diversity': 0.25,
            'sector_diversity': 0.20,
            'inclusion_focus': 0.15,
            'transparency_level': 0.15,
            'underserved_coverage': 0.25
        }
    
    async def score_source(self, source_name: str, source_type: SourceType) -> SourcePerformanceSnapshot:
        """Score a specific source with equity awareness"""
        try:
            # Get recent data for the source
            recent_data = await self._get_recent_source_data(source_name, source_type)
            
            # Calculate quality metrics
            metrics = await self._calculate_quality_metrics(recent_data)
            
            # Calculate equity score
            equity_score = await self._calculate_equity_score(recent_data)
            
            # Adjust quality score based on equity
            metrics = await self._adjust_metrics_for_equity(metrics, equity_score)
            
            # Get item counts
            item_counts = await self._get_item_counts(source_name)
            
            # Identify recent issues
            recent_issues = await self._identify_recent_issues(source_name, recent_data)
            
            snapshot = SourcePerformanceSnapshot(
                source_name=source_name,
                source_type=source_type,
                timestamp=datetime.now(),
                metrics=metrics,
                item_counts=item_counts,
                recent_issues=recent_issues
            )
            
            # Update database
            await self._update_source_quality_db(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Source scoring failed for {source_name}: {e}")
            return SourcePerformanceSnapshot(
                source_name=source_name,
                source_type=source_type,
                timestamp=datetime.now(),
                metrics=QualityMetrics()
            )
    
    async def score_all_sources(self) -> List[SourcePerformanceSnapshot]:
        """Score all sources in the system"""
        snapshots = []
        
        try:
            # Get all unique sources
            sources = await self._get_all_sources()
            
            for source_name, source_type in sources:
                snapshot = await self.score_source(source_name, source_type)
                snapshots.append(snapshot)
            
            # Generate quality patterns
            await self._update_quality_patterns(snapshots)
            
            return snapshots
            
        except Exception as e:
            self.logger.error(f"Scoring all sources failed: {e}")
            return []
    
    async def get_source_recommendations(self, source_name: str) -> Dict[str, Any]:
        """Get recommendations for improving source quality"""
        try:
            source_data = await self._get_recent_source_data(source_name, None)
            
            if not source_data:
                return {'recommendations': ['No data available for analysis']}
            
            recommendations = []
            
            # Analyze quality issues
            metrics = await self._calculate_quality_metrics(source_data)
            
            if metrics.accuracy_score < self.accuracy_threshold:
                recommendations.append({
                    'issue': 'Low accuracy score',
                    'current_score': metrics.accuracy_score,
                    'recommendations': [
                        'Review content validation rules',
                        'Improve content extraction patterns',
                        'Consider adding human review for this source'
                    ]
                })
            
            if metrics.duplicate_rate > self.duplicate_rate_threshold:
                recommendations.append({
                    'issue': 'High duplicate rate',
                    'current_rate': metrics.duplicate_rate,
                    'recommendations': [
                        'Implement more aggressive duplicate detection',
                        'Check for RSS feed issues',
                        'Review content fingerprinting'
                    ]
                })
            
            if metrics.processing_success_rate < 0.8:
                recommendations.append({
                    'issue': 'Low processing success rate',
                    'current_rate': metrics.processing_success_rate,
                    'recommendations': [
                        'Check parsing rules for this source',
                        'Update content extraction patterns',
                        'Review error logs for common failures'
                    ]
                })
            
            if metrics.content_relevance_score < self.relevance_threshold:
                recommendations.append({
                    'issue': 'Low content relevance',
                    'current_score': metrics.content_relevance_score,
                    'recommendations': [
                        'Review content filtering rules',
                        'Improve keyword matching',
                        'Consider removing irrelevant content sources'
                    ]
                })
            
            return {
                'source_name': source_name,
                'overall_score': metrics.calculate_overall_score(),
                'recommendations': recommendations,
                'next_review_date': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Getting recommendations failed for {source_name}: {e}")
            return {'recommendations': ['Error analyzing source']}
    
    async def get_quality_trends(self, source_name: str, days: int = 30) -> Dict[str, Any]:
        """Get quality trends for a source over time"""
        try:
            # Get historical data
            historical_data = await self._get_historical_source_data(source_name, days)
            
            if not historical_data:
                return {'trends': 'No historical data available'}
            
            # Calculate trends
            trends = {
                'accuracy_trend': self._calculate_trend([d['accuracy_score'] for d in historical_data]),
                'duplicate_rate_trend': self._calculate_trend([d['duplicate_rate'] for d in historical_data]),
                'processing_success_trend': self._calculate_trend([d['processing_success_rate'] for d in historical_data]),
                'relevance_trend': self._calculate_trend([d['content_relevance_score'] for d in historical_data])
            }
            
            # Overall trend
            overall_scores = [d['overall_score'] for d in historical_data]
            overall_trend = self._calculate_trend(overall_scores)
            
            return {
                'source_name': source_name,
                'analysis_period_days': days,
                'overall_trend': overall_trend,
                'metric_trends': trends,
                'current_score': overall_scores[-1] if overall_scores else 0.0,
                'best_score': max(overall_scores) if overall_scores else 0.0,
                'worst_score': min(overall_scores) if overall_scores else 0.0,
                'average_score': mean(overall_scores) if overall_scores else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Getting quality trends failed for {source_name}: {e}")
            return {'trends': 'Error calculating trends'}
    
    async def get_source_ranking(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get ranking of sources by quality"""
        try:
            async with get_db_session() as session:
                # Get all sources with their quality scores
                sources = await session.execute(
                    """
                    SELECT source_name, source_type, accuracy_score, duplicate_rate,
                           processing_success_rate, content_relevance_score, quality_grade,
                           total_items_processed, successful_items, last_processed
                    FROM source_quality
                    WHERE is_active = true
                    ORDER BY (accuracy_score * 0.25 + 
                             (1 - duplicate_rate) * 0.20 + 
                             processing_success_rate * 0.20 + 
                             content_relevance_score * 0.15) DESC
                    LIMIT :limit
                    """,
                    {'limit': limit}
                )
                
                ranking = []
                for i, source in enumerate(sources.fetchall(), 1):
                    overall_score = (
                        source.accuracy_score * 0.25 +
                        (1 - source.duplicate_rate) * 0.20 +
                        source.processing_success_rate * 0.20 +
                        source.content_relevance_score * 0.15
                    )
                    
                    ranking.append({
                        'rank': i,
                        'source_name': source.source_name,
                        'source_type': source.source_type,
                        'overall_score': overall_score,
                        'quality_grade': source.quality_grade,
                        'accuracy_score': source.accuracy_score,
                        'duplicate_rate': source.duplicate_rate,
                        'processing_success_rate': source.processing_success_rate,
                        'content_relevance_score': source.content_relevance_score,
                        'total_items_processed': source.total_items_processed,
                        'successful_items': source.successful_items,
                        'last_processed': source.last_processed.isoformat() if source.last_processed else None
                    })
                
                return ranking
                
        except Exception as e:
            self.logger.error(f"Getting source ranking failed: {e}")
            return []
    
    async def identify_problem_sources(self) -> Dict[str, List[str]]:
        """Identify sources with quality problems including equity issues"""
        try:
            async with get_db_session() as session:
                # Get sources with various quality issues
                problem_sources = {
                    'high_duplicate_rate': [],
                    'low_accuracy': [],
                    'poor_processing_success': [],
                    'low_relevance': [],
                    'inactive_sources': [],
                    'low_equity_coverage': [],
                    'geographic_bias': [],
                    'sector_bias': []
                }
                
                # High duplicate rate sources
                high_duplicate = await session.execute(
                    """
                    SELECT source_name, duplicate_rate
                    FROM source_quality
                    WHERE duplicate_rate > 0.15 AND is_active = true
                    ORDER BY duplicate_rate DESC
                    """
                )
                
                for source in high_duplicate.fetchall():
                    problem_sources['high_duplicate_rate'].append({
                        'source_name': source.source_name,
                        'duplicate_rate': source.duplicate_rate
                    })
                
                # Low accuracy sources
                low_accuracy = await session.execute(
                    """
                    SELECT source_name, accuracy_score
                    FROM source_quality
                    WHERE accuracy_score < 0.7 AND is_active = true
                    ORDER BY accuracy_score ASC
                    """
                )
                
                for source in low_accuracy.fetchall():
                    problem_sources['low_accuracy'].append({
                        'source_name': source.source_name,
                        'accuracy_score': source.accuracy_score
                    })
                
                # Poor processing success
                poor_processing = await session.execute(
                    """
                    SELECT source_name, processing_success_rate
                    FROM source_quality
                    WHERE processing_success_rate < 0.8 AND is_active = true
                    ORDER BY processing_success_rate ASC
                    """
                )
                
                for source in poor_processing.fetchall():
                    problem_sources['poor_processing_success'].append({
                        'source_name': source.source_name,
                        'processing_success_rate': source.processing_success_rate
                    })
                
                # Low relevance sources
                low_relevance = await session.execute(
                    """
                    SELECT source_name, content_relevance_score
                    FROM source_quality
                    WHERE content_relevance_score < 0.6 AND is_active = true
                    ORDER BY content_relevance_score ASC
                    """
                )
                
                for source in low_relevance.fetchall():
                    problem_sources['low_relevance'].append({
                        'source_name': source.source_name,
                        'content_relevance_score': source.content_relevance_score
                    })
                
                # Inactive sources
                inactive = await session.execute(
                    """
                    SELECT source_name, last_processed
                    FROM source_quality
                    WHERE last_processed < (NOW() - INTERVAL '7 days') AND is_active = true
                    ORDER BY last_processed ASC
                    """
                )
                
                for source in inactive.fetchall():
                    problem_sources['inactive_sources'].append({
                        'source_name': source.source_name,
                        'last_processed': source.last_processed.isoformat() if source.last_processed else None
                    })
                
                # Sources with low equity coverage (need to implement equity tracking)
                # This would require additional database fields to track equity metrics
                # For now, we'll identify sources that primarily serve Big 4 countries
                
                return problem_sources
                
        except Exception as e:
            self.logger.error(f"Identifying problem sources failed: {e}")
            return {}
    
    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================
    
    async def _get_recent_source_data(self, source_name: str, source_type: Optional[SourceType]) -> List[Dict[str, Any]]:
        """Get recent data for a source"""
        try:
            async with get_db_session() as session:
                # Get recent opportunities from this source
                query = """
                    SELECT fo.*, vr.status as validation_status, vr.confidence_score,
                           vr.completeness_score, vr.relevance_score, vr.legitimacy_score
                    FROM africa_intelligence_feed fo
                    LEFT JOIN validation_results vr ON fo.id = vr.opportunity_id
                    WHERE fo.source_url LIKE :source_pattern
                    AND fo.discovered_date >= (NOW() - INTERVAL ':days days')
                    ORDER BY fo.discovered_date DESC
                """
                
                result = await session.execute(
                    query,
                    {
                        'source_pattern': f'%{source_name}%',
                        'days': self.analysis_window_days
                    }
                )
                
                return [dict(row) for row in result.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Getting recent source data failed: {e}")
            return []
    
    async def _calculate_quality_metrics(self, source_data: List[Dict[str, Any]]) -> QualityMetrics:
        """Calculate quality metrics from source data"""
        try:
            if not source_data:
                return QualityMetrics()
            
            total_items = len(source_data)
            
            # Accuracy score (based on validation results)
            validation_scores = [
                item.get('confidence_score', 0.0) 
                for item in source_data 
                if item.get('confidence_score') is not None
            ]
            accuracy_score = mean(validation_scores) if validation_scores else 0.0
            
            # Duplicate rate (percentage of items marked as duplicates)
            duplicate_count = sum(1 for item in source_data if item.get('validation_status') == 'duplicate')
            duplicate_rate = duplicate_count / total_items if total_items > 0 else 0.0
            
            # Processing success rate
            successful_items = sum(1 for item in source_data if item.get('validation_status') in ['approved', 'auto_approved'])
            processing_success_rate = successful_items / total_items if total_items > 0 else 0.0
            
            # Content relevance score
            relevance_scores = [
                item.get('relevance_score', 0.0) 
                for item in source_data 
                if item.get('relevance_score') is not None
            ]
            content_relevance_score = mean(relevance_scores) if relevance_scores else 0.0
            
            # Timeliness score (based on how fresh the content is)
            timeliness_scores = []
            for item in source_data:
                discovered_date = item.get('discovered_date')
                if discovered_date:
                    age_hours = (datetime.now() - discovered_date).total_seconds() / 3600
                    timeliness_score = max(0.0, 1.0 - (age_hours / (24 * 7)))  # Decay over a week
                    timeliness_scores.append(timeliness_score)
            
            timeliness_score = mean(timeliness_scores) if timeliness_scores else 0.0
            
            # Completeness score
            completeness_scores = [
                item.get('completeness_score', 0.0) 
                for item in source_data 
                if item.get('completeness_score') is not None
            ]
            completeness_score = mean(completeness_scores) if completeness_scores else 0.0
            
            return QualityMetrics(
                accuracy_score=accuracy_score,
                duplicate_rate=duplicate_rate,
                processing_success_rate=processing_success_rate,
                content_relevance_score=content_relevance_score,
                timeliness_score=timeliness_score,
                completeness_score=completeness_score
            )
            
        except Exception as e:
            self.logger.error(f"Calculating quality metrics failed: {e}")
            return QualityMetrics()
    
    async def _get_item_counts(self, source_name: str) -> Dict[str, int]:
        """Get item counts for a source"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    """
                    SELECT 
                        COUNT(*) as total_items,
                        SUM(CASE WHEN validation_status = 'approved' THEN 1 ELSE 0 END) as approved_items,
                        SUM(CASE WHEN validation_status = 'rejected' THEN 1 ELSE 0 END) as rejected_items,
                        SUM(CASE WHEN validation_status = 'duplicate' THEN 1 ELSE 0 END) as duplicate_items,
                        SUM(CASE WHEN validation_status = 'pending' THEN 1 ELSE 0 END) as pending_items
                    FROM africa_intelligence_feed
                    WHERE source_url LIKE :source_pattern
                    AND discovered_date >= (NOW() - INTERVAL ':days days')
                    """,
                    {
                        'source_pattern': f'%{source_name}%',
                        'days': self.analysis_window_days
                    }
                )
                
                row = result.fetchone()
                return {
                    'total_items': row.total_items or 0,
                    'approved_items': row.approved_items or 0,
                    'rejected_items': row.rejected_items or 0,
                    'duplicate_items': row.duplicate_items or 0,
                    'pending_items': row.pending_items or 0
                }
                
        except Exception as e:
            self.logger.error(f"Getting item counts failed: {e}")
            return {}
    
    async def _identify_recent_issues(self, source_name: str, source_data: List[Dict[str, Any]]) -> List[str]:
        """Identify recent issues with a source"""
        issues = []
        
        try:
            if not source_data:
                issues.append("No recent data available")
                return issues
            
            # Check for high duplicate rate
            recent_duplicates = sum(1 for item in source_data if item.get('validation_status') == 'duplicate')
            if recent_duplicates > len(source_data) * 0.2:
                issues.append(f"High duplicate rate: {recent_duplicates}/{len(source_data)} items")
            
            # Check for low accuracy
            low_accuracy_items = sum(1 for item in source_data if item.get('confidence_score', 0) < 0.5)
            if low_accuracy_items > len(source_data) * 0.3:
                issues.append(f"Low accuracy: {low_accuracy_items}/{len(source_data)} items with confidence < 0.5")
            
            # Check for processing failures
            failed_items = sum(1 for item in source_data if item.get('validation_status') == 'failed')
            if failed_items > len(source_data) * 0.1:
                issues.append(f"Processing failures: {failed_items}/{len(source_data)} items failed")
            
            # Check for content relevance issues
            irrelevant_items = sum(1 for item in source_data if item.get('relevance_score', 0) < 0.4)
            if irrelevant_items > len(source_data) * 0.4:
                issues.append(f"Low relevance: {irrelevant_items}/{len(source_data)} items with relevance < 0.4")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Identifying recent issues failed: {e}")
            return ["Error analyzing recent issues"]
    
    async def _update_source_quality_db(self, snapshot: SourcePerformanceSnapshot):
        """Update source quality in database"""
        try:
            async with get_db_session() as session:
                # Update or create source quality record
                existing = await session.execute(
                    "SELECT id FROM source_quality WHERE source_name = :name",
                    {'name': snapshot.source_name}
                )
                
                if existing.fetchone():
                    # Update existing record
                    await session.execute(
                        """
                        UPDATE source_quality SET
                            accuracy_score = :accuracy,
                            duplicate_rate = :duplicate_rate,
                            processing_success_rate = :processing_success,
                            content_relevance_score = :content_relevance,
                            total_items_processed = :total_items,
                            successful_items = :successful_items,
                            duplicate_items = :duplicate_items,
                            last_processed = NOW(),
                            updated_at = NOW()
                        WHERE source_name = :name
                        """,
                        {
                            'name': snapshot.source_name,
                            'accuracy': snapshot.metrics.accuracy_score,
                            'duplicate_rate': snapshot.metrics.duplicate_rate,
                            'processing_success': snapshot.metrics.processing_success_rate,
                            'content_relevance': snapshot.metrics.content_relevance_score,
                            'total_items': snapshot.item_counts.get('total_items', 0),
                            'successful_items': snapshot.item_counts.get('approved_items', 0),
                            'duplicate_items': snapshot.item_counts.get('duplicate_items', 0)
                        }
                    )
                else:
                    # Create new record
                    await session.execute(
                        """
                        INSERT INTO source_quality (
                            source_name, source_type, accuracy_score, duplicate_rate,
                            processing_success_rate, content_relevance_score,
                            total_items_processed, successful_items, duplicate_items,
                            last_processed, created_at, updated_at
                        ) VALUES (
                            :name, :type, :accuracy, :duplicate_rate,
                            :processing_success, :content_relevance,
                            :total_items, :successful_items, :duplicate_items,
                            NOW(), NOW(), NOW()
                        )
                        """,
                        {
                            'name': snapshot.source_name,
                            'type': snapshot.source_type.value,
                            'accuracy': snapshot.metrics.accuracy_score,
                            'duplicate_rate': snapshot.metrics.duplicate_rate,
                            'processing_success': snapshot.metrics.processing_success_rate,
                            'content_relevance': snapshot.metrics.content_relevance_score,
                            'total_items': snapshot.item_counts.get('total_items', 0),
                            'successful_items': snapshot.item_counts.get('approved_items', 0),
                            'duplicate_items': snapshot.item_counts.get('duplicate_items', 0)
                        }
                    )
                
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Updating source quality DB failed: {e}")
    
    async def _get_all_sources(self) -> List[Tuple[str, SourceType]]:
        """Get all unique sources"""
        try:
            async with get_db_session() as session:
                # Extract unique source names from intelligence feed
                result = await session.execute(
                    """
                    SELECT DISTINCT 
                        COALESCE(source_name, 'unknown') as source_name,
                        COALESCE(source_type, 'website') as source_type
                    FROM africa_intelligence_feed
                    WHERE discovered_date >= (NOW() - INTERVAL '30 days')
                    """
                )
                
                sources = []
                for row in result.fetchall():
                    try:
                        source_type = SourceType(row.source_type)
                    except ValueError:
                        source_type = SourceType.WEBSITE
                    
                    sources.append((row.source_name, source_type))
                
                return sources
                
        except Exception as e:
            self.logger.error(f"Getting all sources failed: {e}")
            return []
    
    async def _update_quality_patterns(self, snapshots: List[SourcePerformanceSnapshot]):
        """Update quality patterns based on snapshots"""
        try:
            self.quality_patterns = {
                'high_duplicate_sources': set(),
                'low_accuracy_sources': set(),
                'slow_processing_sources': set(),
                'unreliable_sources': set()
            }
            
            for snapshot in snapshots:
                if snapshot.metrics.duplicate_rate > self.duplicate_rate_threshold:
                    self.quality_patterns['high_duplicate_sources'].add(snapshot.source_name)
                
                if snapshot.metrics.accuracy_score < self.accuracy_threshold:
                    self.quality_patterns['low_accuracy_sources'].add(snapshot.source_name)
                
                if snapshot.metrics.processing_success_rate < 0.8:
                    self.quality_patterns['slow_processing_sources'].add(snapshot.source_name)
                
                if snapshot.metrics.calculate_overall_score() < 0.5:
                    self.quality_patterns['unreliable_sources'].add(snapshot.source_name)
            
        except Exception as e:
            self.logger.error(f"Updating quality patterns failed: {e}")
    
    async def _get_historical_source_data(self, source_name: str, days: int) -> List[Dict[str, Any]]:
        """Get historical source data for trend analysis"""
        try:
            # This would typically query a historical metrics table
            # For now, we'll simulate historical data
            return []
            
        except Exception as e:
            self.logger.error(f"Getting historical source data failed: {e}")
            return []
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend for a list of values"""
        try:
            if len(values) < 2:
                return {'trend': 'insufficient_data', 'change': 0.0}
            
            # Simple trend calculation
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = mean(first_half)
            second_avg = mean(second_half)
            
            change = second_avg - first_avg
            
            if abs(change) < 0.05:
                trend = 'stable'
            elif change > 0:
                trend = 'improving'
            else:
                trend = 'declining'
            
            return {
                'trend': trend,
                'change': change,
                'first_period_avg': first_avg,
                'second_period_avg': second_avg,
                'volatility': stdev(values) if len(values) > 1 else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Calculating trend failed: {e}")
            return {'trend': 'error', 'change': 0.0}
    
    async def _calculate_equity_score(self, source_data: List[Dict[str, Any]]) -> float:
        """Calculate equity score based on source's contribution to funding equity"""
        try:
            if not source_data:
                return 0.5
            
            # Country diversity (non-Big 4 percentage)
            countries = set()
            big_four_countries = {'KE', 'NG', 'ZA', 'EG'}
            non_big_four_count = 0
            
            for item in source_data:
                detected_countries = item.get('detected_countries', [])
                countries.update(detected_countries)
                if any(country not in big_four_countries for country in detected_countries):
                    non_big_four_count += 1
            
            geographic_diversity = non_big_four_count / len(source_data) if source_data else 0.0
            
            # Sector diversity (priority sectors percentage)
            priority_sectors = {'healthcare', 'agriculture', 'climate'}
            priority_sector_count = 0
            
            for item in source_data:
                detected_sectors = item.get('detected_sectors', [])
                if any(sector in priority_sectors for sector in detected_sectors):
                    priority_sector_count += 1
            
            sector_diversity = priority_sector_count / len(source_data) if source_data else 0.0
            
            # Inclusion focus (opportunities with inclusion criteria)
            inclusion_count = 0
            for item in source_data:
                inclusion_indicators = item.get('inclusion_indicators', [])
                if inclusion_indicators:
                    inclusion_count += 1
            
            inclusion_focus = inclusion_count / len(source_data) if source_data else 0.0
            
            # Transparency level (clear criteria percentage)
            clear_criteria_count = 0
            for item in source_data:
                transparency_issues = item.get('transparency_issues', [])
                if not transparency_issues or len(transparency_issues) < 2:
                    clear_criteria_count += 1
            
            transparency_level = clear_criteria_count / len(source_data) if source_data else 0.0
            
            # Underserved coverage (Central/West Africa focus)
            underserved_countries = {'CF', 'TD', 'CD', 'CM', 'GQ', 'GA', 'GW', 'SL', 'LR', 'TG', 'BJ'}
            underserved_count = 0
            
            for item in source_data:
                detected_countries = item.get('detected_countries', [])
                if any(country in underserved_countries for country in detected_countries):
                    underserved_count += 1
            
            underserved_coverage = underserved_count / len(source_data) if source_data else 0.0
            
            # Calculate weighted equity score
            equity_score = (
                geographic_diversity * self.equity_weights['geographic_diversity'] +
                sector_diversity * self.equity_weights['sector_diversity'] +
                inclusion_focus * self.equity_weights['inclusion_focus'] +
                transparency_level * self.equity_weights['transparency_level'] +
                underserved_coverage * self.equity_weights['underserved_coverage']
            )
            
            return min(1.0, max(0.0, equity_score))
            
        except Exception as e:
            self.logger.error(f"Calculating equity score failed: {e}")
            return 0.5
    
    async def _adjust_metrics_for_equity(self, metrics: QualityMetrics, equity_score: float) -> QualityMetrics:
        """Adjust quality metrics based on equity contribution"""
        try:
            # Boost overall score for sources that serve equity
            if equity_score > 0.7:
                # High equity sources get quality boost
                metrics.accuracy_score = min(1.0, metrics.accuracy_score * 1.1)
                metrics.content_relevance_score = min(1.0, metrics.content_relevance_score * 1.1)
            elif equity_score > 0.5:
                # Medium equity sources get modest boost
                metrics.accuracy_score = min(1.0, metrics.accuracy_score * 1.05)
                metrics.content_relevance_score = min(1.0, metrics.content_relevance_score * 1.05)
            elif equity_score < 0.3:
                # Low equity sources get slight penalty
                metrics.accuracy_score = max(0.0, metrics.accuracy_score * 0.95)
                metrics.content_relevance_score = max(0.0, metrics.content_relevance_score * 0.95)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Adjusting metrics for equity failed: {e}")
            return metrics

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of source quality scorer"""
    scorer = SourceQualityScorer()
    
    # Score a specific source
    snapshot = await scorer.score_source("techcrunch.com", SourceType.NEWS_OUTLET)
    print(f"Source: {snapshot.source_name}")
    print(f"Overall Score: {snapshot.metrics.calculate_overall_score():.3f}")
    print(f"Recent Issues: {snapshot.recent_issues}")
    
    # Get source ranking
    ranking = await scorer.get_source_ranking(10)
    print("\nTop 10 Sources:")
    for source in ranking:
        print(f"{source['rank']}. {source['source_name']} - {source['overall_score']:.3f}")
    
    # Identify problem sources
    problems = await scorer.identify_problem_sources()
    print(f"\nProblem Sources: {problems}")

if __name__ == "__main__":
    asyncio.run(example_usage())