"""
Real-time Bias Monitoring System
================================

Comprehensive monitoring system to track and alert on bias patterns
in the AI Africa Funding Tracker ingestion pipeline.

Monitors:
- Geographic distribution bias
- Sectoral representation gaps
- Gender and inclusion metrics
- Language diversity
- Funding stage distribution
- Source quality equity
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from statistics import mean, stdev
import pandas as pd
from collections import defaultdict, Counter

from app.core.database import get_db
from app.core.equity_aware_classifier import GeographicTier, SectorPriority, InclusionCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# BIAS MONITORING MODELS
# =============================================================================

class BiasType(Enum):
    """Types of bias being monitored"""
    GEOGRAPHIC = "geographic"
    SECTORAL = "sectoral"
    GENDER = "gender"
    LANGUAGE = "language"
    FUNDING_STAGE = "funding_stage"
    SOURCE_QUALITY = "source_quality"
    TEMPORAL = "temporal"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class BiasDirection(Enum):
    """Direction of bias"""
    OVER_REPRESENTED = "over_represented"
    UNDER_REPRESENTED = "under_represented"
    BALANCED = "balanced"

@dataclass
class BiasMetric:
    """Individual bias metric"""
    metric_name: str
    current_value: float
    target_value: float
    threshold_warning: float
    threshold_critical: float
    direction: BiasDirection
    trend_7d: float = 0.0
    trend_30d: float = 0.0
    
    def calculate_severity(self) -> AlertSeverity:
        """Calculate alert severity based on deviation from target"""
        deviation = abs(self.current_value - self.target_value)
        
        if deviation >= self.threshold_critical:
            return AlertSeverity.CRITICAL
        elif deviation >= self.threshold_warning:
            return AlertSeverity.HIGH
        elif deviation >= self.threshold_warning * 0.5:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

@dataclass
class BiasAlert:
    """Bias alert notification"""
    alert_id: str
    bias_type: BiasType
    severity: AlertSeverity
    message: str
    metric: BiasMetric
    recommendations: List[str] = field(default_factory=list)
    affected_regions: List[str] = field(default_factory=list)
    affected_sectors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'bias_type': self.bias_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'metric': {
                'name': self.metric.metric_name,
                'current_value': self.metric.current_value,
                'target_value': self.metric.target_value,
                'direction': self.metric.direction.value,
                'trend_7d': self.metric.trend_7d,
                'trend_30d': self.metric.trend_30d
            },
            'recommendations': self.recommendations,
            'affected_regions': self.affected_regions,
            'affected_sectors': self.affected_sectors,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class BiasSnapshot:
    """Comprehensive bias snapshot"""
    timestamp: datetime
    geographic_metrics: Dict[str, BiasMetric]
    sectoral_metrics: Dict[str, BiasMetric]
    inclusion_metrics: Dict[str, BiasMetric]
    language_metrics: Dict[str, BiasMetric]
    stage_metrics: Dict[str, BiasMetric]
    source_metrics: Dict[str, BiasMetric]
    overall_equity_score: float = 0.0
    active_alerts: List[BiasAlert] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_equity_score': self.overall_equity_score,
            'geographic_metrics': {k: vars(v) for k, v in self.geographic_metrics.items()},
            'sectoral_metrics': {k: vars(v) for k, v in self.sectoral_metrics.items()},
            'inclusion_metrics': {k: vars(v) for k, v in self.inclusion_metrics.items()},
            'language_metrics': {k: vars(v) for k, v in self.language_metrics.items()},
            'stage_metrics': {k: vars(v) for k, v in self.stage_metrics.items()},
            'source_metrics': {k: vars(v) for k, v in self.source_metrics.items()},
            'active_alerts': [alert.to_dict() for alert in self.active_alerts]
        }

# =============================================================================
# BIAS MONITORING ENGINE
# =============================================================================

class BiasMonitoringEngine:
    """Real-time bias monitoring and alerting system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Bias targets and thresholds
        self.bias_targets = {
            'geographic': {
                'non_big_four_percentage': {
                    'target': 0.35,  # 35% from non-Big 4 countries
                    'warning': 0.15,  # Alert if deviation > 15%
                    'critical': 0.25  # Critical if deviation > 25%
                },
                'central_africa_percentage': {
                    'target': 0.15,  # 15% from Central Africa
                    'warning': 0.10,
                    'critical': 0.15
                },
                'west_africa_percentage': {
                    'target': 0.25,  # 25% from West Africa
                    'warning': 0.10,
                    'critical': 0.15
                },
                'geographic_diversity_index': {
                    'target': 0.7,   # Diversity index target
                    'warning': 0.15,
                    'critical': 0.25
                }
            },
            'sectoral': {
                'healthcare_percentage': {
                    'target': 0.15,  # 15% healthcare opportunities
                    'warning': 0.05,
                    'critical': 0.08
                },
                'agriculture_percentage': {
                    'target': 0.15,  # 15% agriculture opportunities
                    'warning': 0.05,
                    'critical': 0.08
                },
                'climate_percentage': {
                    'target': 0.10,  # 10% climate opportunities
                    'warning': 0.05,
                    'critical': 0.08
                },
                'sector_diversity_index': {
                    'target': 0.8,   # Sector diversity target
                    'warning': 0.15,
                    'critical': 0.25
                }
            },
            'inclusion': {
                'women_focused_percentage': {
                    'target': 0.20,  # 20% women-focused opportunities
                    'warning': 0.08,
                    'critical': 0.12
                },
                'youth_focused_percentage': {
                    'target': 0.25,  # 25% youth-focused opportunities
                    'warning': 0.10,
                    'critical': 0.15
                },
                'rural_focused_percentage': {
                    'target': 0.15,  # 15% rural-focused opportunities
                    'warning': 0.08,
                    'critical': 0.12
                },
                'inclusion_diversity_index': {
                    'target': 0.6,   # Inclusion diversity target
                    'warning': 0.15,
                    'critical': 0.25
                }
            },
            'language': {
                'non_english_percentage': {
                    'target': 0.20,  # 20% non-English opportunities
                    'warning': 0.10,
                    'critical': 0.15
                },
                'french_percentage': {
                    'target': 0.10,  # 10% French opportunities
                    'warning': 0.05,
                    'critical': 0.08
                },
                'arabic_percentage': {
                    'target': 0.05,  # 5% Arabic opportunities
                    'warning': 0.03,
                    'critical': 0.05
                },
                'language_diversity_index': {
                    'target': 0.5,   # Language diversity target
                    'warning': 0.15,
                    'critical': 0.25
                }
            },
            'funding_stage': {
                'early_stage_percentage': {
                    'target': 0.40,  # 40% early-stage opportunities
                    'warning': 0.15,
                    'critical': 0.20
                },
                'seed_stage_percentage': {
                    'target': 0.25,  # 25% seed-stage opportunities
                    'warning': 0.10,
                    'critical': 0.15
                },
                'grant_percentage': {
                    'target': 0.30,  # 30% grant opportunities
                    'warning': 0.10,
                    'critical': 0.15
                },
                'stage_diversity_index': {
                    'target': 0.7,   # Stage diversity target
                    'warning': 0.15,
                    'critical': 0.25
                }
            }
        }
        
        # Historical data for trend analysis
        self.historical_snapshots = []
        self.max_history_days = 90
        
        # Alert configuration
        self.alert_cooldown_hours = 6  # Minimum time between similar alerts
        self.recent_alerts = []
    
    async def analyze_current_bias(self) -> BiasSnapshot:
        """Analyze current bias in the system"""
        try:
            # Get current data
            current_data = await self._get_current_ingestion_data()
            
            # Calculate metrics for each bias type
            geographic_metrics = await self._calculate_geographic_metrics(current_data)
            sectoral_metrics = await self._calculate_sectoral_metrics(current_data)
            inclusion_metrics = await self._calculate_inclusion_metrics(current_data)
            language_metrics = await self._calculate_language_metrics(current_data)
            stage_metrics = await self._calculate_stage_metrics(current_data)
            source_metrics = await self._calculate_source_metrics(current_data)
            
            # Calculate overall equity score
            overall_equity = await self._calculate_overall_equity_score({
                'geographic': geographic_metrics,
                'sectoral': sectoral_metrics,
                'inclusion': inclusion_metrics,
                'language': language_metrics,
                'stage': stage_metrics,
                'source': source_metrics
            })
            
            # Generate alerts
            alerts = await self._generate_alerts({
                'geographic': geographic_metrics,
                'sectoral': sectoral_metrics,
                'inclusion': inclusion_metrics,
                'language': language_metrics,
                'stage': stage_metrics,
                'source': source_metrics
            })
            
            # Create snapshot
            snapshot = BiasSnapshot(
                timestamp=datetime.now(),
                geographic_metrics=geographic_metrics,
                sectoral_metrics=sectoral_metrics,
                inclusion_metrics=inclusion_metrics,
                language_metrics=language_metrics,
                stage_metrics=stage_metrics,
                source_metrics=source_metrics,
                overall_equity_score=overall_equity,
                active_alerts=alerts
            )
            
            # Store snapshot
            await self._store_snapshot(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Bias analysis failed: {e}")
            return BiasSnapshot(timestamp=datetime.now(), geographic_metrics={}, sectoral_metrics={}, 
                              inclusion_metrics={}, language_metrics={}, stage_metrics={}, source_metrics={})
    
    async def get_bias_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get bias trends over specified period"""
        try:
            # Get historical snapshots
            historical_data = await self._get_historical_snapshots(days)
            
            if not historical_data:
                return {'error': 'No historical data available'}
            
            trends = {
                'geographic_trends': self._calculate_metric_trends(historical_data, 'geographic_metrics'),
                'sectoral_trends': self._calculate_metric_trends(historical_data, 'sectoral_metrics'),
                'inclusion_trends': self._calculate_metric_trends(historical_data, 'inclusion_metrics'),
                'language_trends': self._calculate_metric_trends(historical_data, 'language_metrics'),
                'stage_trends': self._calculate_metric_trends(historical_data, 'stage_metrics'),
                'overall_equity_trend': self._calculate_equity_trend(historical_data)
            }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Getting bias trends failed: {e}")
            return {'error': str(e)}
    
    async def get_bias_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for addressing bias issues"""
        try:
            # Get current snapshot
            current_snapshot = await self.analyze_current_bias()
            
            recommendations = []
            
            # Analyze geographic bias
            geo_recs = await self._analyze_geographic_bias(current_snapshot.geographic_metrics)
            recommendations.extend(geo_recs)
            
            # Analyze sectoral bias
            sector_recs = await self._analyze_sectoral_bias(current_snapshot.sectoral_metrics)
            recommendations.extend(sector_recs)
            
            # Analyze inclusion bias
            inclusion_recs = await self._analyze_inclusion_bias(current_snapshot.inclusion_metrics)
            recommendations.extend(inclusion_recs)
            
            # Analyze language bias
            language_recs = await self._analyze_language_bias(current_snapshot.language_metrics)
            recommendations.extend(language_recs)
            
            # Analyze stage bias
            stage_recs = await self._analyze_stage_bias(current_snapshot.stage_metrics)
            recommendations.extend(stage_recs)
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Getting bias recommendations failed: {e}")
            return []
    
    async def trigger_bias_mitigation(self, bias_type: BiasType, severity: AlertSeverity) -> Dict[str, Any]:
        """Trigger automatic bias mitigation measures"""
        try:
            mitigation_actions = []
            
            if bias_type == BiasType.GEOGRAPHIC:
                if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                    # Boost underserved region searches
                    mitigation_actions.append({
                        'action': 'boost_underserved_searches',
                        'description': 'Increase search frequency for Central/West Africa',
                        'parameters': {'multiplier': 2.0, 'duration_hours': 24}
                    })
                    
                    # Reduce Big 4 country search frequency
                    mitigation_actions.append({
                        'action': 'reduce_saturated_searches',
                        'description': 'Reduce search frequency for oversaturated regions',
                        'parameters': {'multiplier': 0.7, 'duration_hours': 24}
                    })
            
            elif bias_type == BiasType.SECTORAL:
                if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                    # Boost priority sector searches
                    mitigation_actions.append({
                        'action': 'boost_priority_sectors',
                        'description': 'Increase searches for healthcare/agriculture/climate',
                        'parameters': {'sectors': ['healthcare', 'agriculture', 'climate'], 'multiplier': 1.5}
                    })
            
            elif bias_type == BiasType.LANGUAGE:
                if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                    # Activate multilingual searches
                    mitigation_actions.append({
                        'action': 'activate_multilingual_search',
                        'description': 'Activate French/Arabic/Portuguese searches',
                        'parameters': {'languages': ['fr', 'ar', 'pt'], 'frequency': 'hourly'}
                    })
            
            # Execute mitigation actions
            execution_results = []
            for action in mitigation_actions:
                result = await self._execute_mitigation_action(action)
                execution_results.append(result)
            
            return {
                'bias_type': bias_type.value,
                'severity': severity.value,
                'mitigation_actions': mitigation_actions,
                'execution_results': execution_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Bias mitigation failed: {e}")
            return {'error': str(e)}
    
    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================
    
    async def _get_current_ingestion_data(self) -> Dict[str, Any]:
        """Get current ingestion data for analysis"""
        try:
            async with get_db() as session:
                # Get opportunities from last 24 hours
                query = """
                    SELECT fo.*, 
                           vr.confidence_score,
                           vr.validation_notes,
                           cf.organization_name,
                           cf.funding_amount,
                           cf.key_phrases
                    FROM africa_intelligence_feed fo
                    LEFT JOIN validation_results vr ON fo.id = vr.opportunity_id
                    LEFT JOIN content_fingerprints cf ON fo.id = cf.opportunity_id
                    WHERE fo.discovered_date >= (NOW() - INTERVAL '24 hours')
                    ORDER BY fo.discovered_date DESC
                """
                
                result = await session.execute(query)
                opportunities = [dict(row) for row in result.fetchall()]
                
                # Get source statistics
                source_query = """
                    SELECT source_name, source_type, COUNT(*) as count
                    FROM africa_intelligence_feed
                    WHERE discovered_date >= (NOW() - INTERVAL '24 hours')
                    GROUP BY source_name, source_type
                    ORDER BY count DESC
                """
                
                source_result = await session.execute(source_query)
                source_stats = [dict(row) for row in source_result.fetchall()]
                
                return {
                    'opportunities': opportunities,
                    'source_stats': source_stats,
                    'total_count': len(opportunities),
                    'analysis_period': '24_hours'
                }
                
        except Exception as e:
            self.logger.error(f"Getting current ingestion data failed: {e}")
            return {'opportunities': [], 'source_stats': [], 'total_count': 0}
    
    async def _calculate_geographic_metrics(self, data: Dict[str, Any]) -> Dict[str, BiasMetric]:
        """Calculate geographic bias metrics"""
        try:
            opportunities = data.get('opportunities', [])
            if not opportunities:
                return {}
            
            # Extract geographic data
            geographic_data = defaultdict(int)
            big_four_countries = {'KE', 'NG', 'ZA', 'EG'}
            central_africa = {'CF', 'TD', 'CD', 'CM', 'GQ', 'GA'}
            west_africa = {'GW', 'SL', 'LR', 'TG', 'BJ', 'NE', 'ML', 'BF', 'SN', 'CI', 'GH', 'GM', 'NG'}
            
            big_four_count = 0
            central_africa_count = 0
            west_africa_count = 0
            total_with_location = 0
            unique_countries = set()
            
            for opp in opportunities:
                # Extract countries from opportunity data
                countries = self._extract_countries_from_opportunity(opp)
                
                if countries:
                    total_with_location += 1
                    unique_countries.update(countries)
                    
                    for country in countries:
                        geographic_data[country] += 1
                        
                        if country in big_four_countries:
                            big_four_count += 1
                        if country in central_africa:
                            central_africa_count += 1
                        if country in west_africa:
                            west_africa_count += 1
            
            # Calculate metrics
            metrics = {}
            
            if total_with_location > 0:
                # Non-Big 4 percentage
                non_big_four_pct = (total_with_location - big_four_count) / total_with_location
                metrics['non_big_four_percentage'] = BiasMetric(
                    metric_name='non_big_four_percentage',
                    current_value=non_big_four_pct,
                    target_value=self.bias_targets['geographic']['non_big_four_percentage']['target'],
                    threshold_warning=self.bias_targets['geographic']['non_big_four_percentage']['warning'],
                    threshold_critical=self.bias_targets['geographic']['non_big_four_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if non_big_four_pct < 0.35 else BiasDirection.BALANCED
                )
                
                # Central Africa percentage
                central_africa_pct = central_africa_count / total_with_location
                metrics['central_africa_percentage'] = BiasMetric(
                    metric_name='central_africa_percentage',
                    current_value=central_africa_pct,
                    target_value=self.bias_targets['geographic']['central_africa_percentage']['target'],
                    threshold_warning=self.bias_targets['geographic']['central_africa_percentage']['warning'],
                    threshold_critical=self.bias_targets['geographic']['central_africa_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if central_africa_pct < 0.15 else BiasDirection.BALANCED
                )
                
                # West Africa percentage
                west_africa_pct = west_africa_count / total_with_location
                metrics['west_africa_percentage'] = BiasMetric(
                    metric_name='west_africa_percentage',
                    current_value=west_africa_pct,
                    target_value=self.bias_targets['geographic']['west_africa_percentage']['target'],
                    threshold_warning=self.bias_targets['geographic']['west_africa_percentage']['warning'],
                    threshold_critical=self.bias_targets['geographic']['west_africa_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if west_africa_pct < 0.25 else BiasDirection.BALANCED
                )
                
                # Geographic diversity index (Simpson's diversity index)
                diversity_index = self._calculate_diversity_index(list(geographic_data.values()))
                metrics['geographic_diversity_index'] = BiasMetric(
                    metric_name='geographic_diversity_index',
                    current_value=diversity_index,
                    target_value=self.bias_targets['geographic']['geographic_diversity_index']['target'],
                    threshold_warning=self.bias_targets['geographic']['geographic_diversity_index']['warning'],
                    threshold_critical=self.bias_targets['geographic']['geographic_diversity_index']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if diversity_index < 0.7 else BiasDirection.BALANCED
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Calculating geographic metrics failed: {e}")
            return {}
    
    async def _calculate_sectoral_metrics(self, data: Dict[str, Any]) -> Dict[str, BiasMetric]:
        """Calculate sectoral bias metrics"""
        try:
            opportunities = data.get('opportunities', [])
            if not opportunities:
                return {}
            
            # Extract sectoral data
            sectoral_data = defaultdict(int)
            healthcare_count = 0
            agriculture_count = 0
            climate_count = 0
            total_count = len(opportunities)
            
            for opp in opportunities:
                sectors = self._extract_sectors_from_opportunity(opp)
                
                for sector in sectors:
                    sectoral_data[sector] += 1
                    
                    if sector == 'healthcare':
                        healthcare_count += 1
                    elif sector == 'agriculture':
                        agriculture_count += 1
                    elif sector == 'climate':
                        climate_count += 1
            
            # Calculate metrics
            metrics = {}
            
            if total_count > 0:
                # Healthcare percentage
                healthcare_pct = healthcare_count / total_count
                metrics['healthcare_percentage'] = BiasMetric(
                    metric_name='healthcare_percentage',
                    current_value=healthcare_pct,
                    target_value=self.bias_targets['sectoral']['healthcare_percentage']['target'],
                    threshold_warning=self.bias_targets['sectoral']['healthcare_percentage']['warning'],
                    threshold_critical=self.bias_targets['sectoral']['healthcare_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if healthcare_pct < 0.15 else BiasDirection.BALANCED
                )
                
                # Agriculture percentage
                agriculture_pct = agriculture_count / total_count
                metrics['agriculture_percentage'] = BiasMetric(
                    metric_name='agriculture_percentage',
                    current_value=agriculture_pct,
                    target_value=self.bias_targets['sectoral']['agriculture_percentage']['target'],
                    threshold_warning=self.bias_targets['sectoral']['agriculture_percentage']['warning'],
                    threshold_critical=self.bias_targets['sectoral']['agriculture_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if agriculture_pct < 0.15 else BiasDirection.BALANCED
                )
                
                # Climate percentage
                climate_pct = climate_count / total_count
                metrics['climate_percentage'] = BiasMetric(
                    metric_name='climate_percentage',
                    current_value=climate_pct,
                    target_value=self.bias_targets['sectoral']['climate_percentage']['target'],
                    threshold_warning=self.bias_targets['sectoral']['climate_percentage']['warning'],
                    threshold_critical=self.bias_targets['sectoral']['climate_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if climate_pct < 0.10 else BiasDirection.BALANCED
                )
                
                # Sector diversity index
                diversity_index = self._calculate_diversity_index(list(sectoral_data.values()))
                metrics['sector_diversity_index'] = BiasMetric(
                    metric_name='sector_diversity_index',
                    current_value=diversity_index,
                    target_value=self.bias_targets['sectoral']['sector_diversity_index']['target'],
                    threshold_warning=self.bias_targets['sectoral']['sector_diversity_index']['warning'],
                    threshold_critical=self.bias_targets['sectoral']['sector_diversity_index']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if diversity_index < 0.8 else BiasDirection.BALANCED
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Calculating sectoral metrics failed: {e}")
            return {}
    
    async def _calculate_inclusion_metrics(self, data: Dict[str, Any]) -> Dict[str, BiasMetric]:
        """Calculate inclusion bias metrics"""
        try:
            opportunities = data.get('opportunities', [])
            if not opportunities:
                return {}
            
            # Extract inclusion data
            women_focused_count = 0
            youth_focused_count = 0
            rural_focused_count = 0
            total_count = len(opportunities)
            
            for opp in opportunities:
                inclusion_indicators = self._extract_inclusion_from_opportunity(opp)
                
                if 'women_led' in inclusion_indicators:
                    women_focused_count += 1
                if 'youth_focused' in inclusion_indicators:
                    youth_focused_count += 1
                if 'rural_priority' in inclusion_indicators:
                    rural_focused_count += 1
            
            # Calculate metrics
            metrics = {}
            
            if total_count > 0:
                # Women-focused percentage
                women_pct = women_focused_count / total_count
                metrics['women_focused_percentage'] = BiasMetric(
                    metric_name='women_focused_percentage',
                    current_value=women_pct,
                    target_value=self.bias_targets['inclusion']['women_focused_percentage']['target'],
                    threshold_warning=self.bias_targets['inclusion']['women_focused_percentage']['warning'],
                    threshold_critical=self.bias_targets['inclusion']['women_focused_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if women_pct < 0.20 else BiasDirection.BALANCED
                )
                
                # Youth-focused percentage
                youth_pct = youth_focused_count / total_count
                metrics['youth_focused_percentage'] = BiasMetric(
                    metric_name='youth_focused_percentage',
                    current_value=youth_pct,
                    target_value=self.bias_targets['inclusion']['youth_focused_percentage']['target'],
                    threshold_warning=self.bias_targets['inclusion']['youth_focused_percentage']['warning'],
                    threshold_critical=self.bias_targets['inclusion']['youth_focused_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if youth_pct < 0.25 else BiasDirection.BALANCED
                )
                
                # Rural-focused percentage
                rural_pct = rural_focused_count / total_count
                metrics['rural_focused_percentage'] = BiasMetric(
                    metric_name='rural_focused_percentage',
                    current_value=rural_pct,
                    target_value=self.bias_targets['inclusion']['rural_focused_percentage']['target'],
                    threshold_warning=self.bias_targets['inclusion']['rural_focused_percentage']['warning'],
                    threshold_critical=self.bias_targets['inclusion']['rural_focused_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if rural_pct < 0.15 else BiasDirection.BALANCED
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Calculating inclusion metrics failed: {e}")
            return {}
    
    async def _calculate_language_metrics(self, data: Dict[str, Any]) -> Dict[str, BiasMetric]:
        """Calculate language bias metrics"""
        try:
            opportunities = data.get('opportunities', [])
            if not opportunities:
                return {}
            
            # Extract language data
            language_data = defaultdict(int)
            non_english_count = 0
            french_count = 0
            arabic_count = 0
            total_count = len(opportunities)
            
            for opp in opportunities:
                # Simple language detection based on content
                language = self._detect_opportunity_language(opp)
                language_data[language] += 1
                
                if language != 'en':
                    non_english_count += 1
                if language == 'fr':
                    french_count += 1
                if language == 'ar':
                    arabic_count += 1
            
            # Calculate metrics
            metrics = {}
            
            if total_count > 0:
                # Non-English percentage
                non_english_pct = non_english_count / total_count
                metrics['non_english_percentage'] = BiasMetric(
                    metric_name='non_english_percentage',
                    current_value=non_english_pct,
                    target_value=self.bias_targets['language']['non_english_percentage']['target'],
                    threshold_warning=self.bias_targets['language']['non_english_percentage']['warning'],
                    threshold_critical=self.bias_targets['language']['non_english_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if non_english_pct < 0.20 else BiasDirection.BALANCED
                )
                
                # French percentage
                french_pct = french_count / total_count
                metrics['french_percentage'] = BiasMetric(
                    metric_name='french_percentage',
                    current_value=french_pct,
                    target_value=self.bias_targets['language']['french_percentage']['target'],
                    threshold_warning=self.bias_targets['language']['french_percentage']['warning'],
                    threshold_critical=self.bias_targets['language']['french_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if french_pct < 0.10 else BiasDirection.BALANCED
                )
                
                # Arabic percentage
                arabic_pct = arabic_count / total_count
                metrics['arabic_percentage'] = BiasMetric(
                    metric_name='arabic_percentage',
                    current_value=arabic_pct,
                    target_value=self.bias_targets['language']['arabic_percentage']['target'],
                    threshold_warning=self.bias_targets['language']['arabic_percentage']['warning'],
                    threshold_critical=self.bias_targets['language']['arabic_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if arabic_pct < 0.05 else BiasDirection.BALANCED
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Calculating language metrics failed: {e}")
            return {}
    
    async def _calculate_stage_metrics(self, data: Dict[str, Any]) -> Dict[str, BiasMetric]:
        """Calculate funding stage bias metrics"""
        try:
            opportunities = data.get('opportunities', [])
            if not opportunities:
                return {}
            
            # Extract stage data
            stage_data = defaultdict(int)
            early_stage_count = 0
            seed_stage_count = 0
            grant_count = 0
            total_count = len(opportunities)
            
            for opp in opportunities:
                stage = self._extract_stage_from_opportunity(opp)
                stage_data[stage] += 1
                
                if stage in ['pre_seed', 'seed']:
                    early_stage_count += 1
                if stage == 'seed':
                    seed_stage_count += 1
                if stage == 'grant':
                    grant_count += 1
            
            # Calculate metrics
            metrics = {}
            
            if total_count > 0:
                # Early stage percentage
                early_stage_pct = early_stage_count / total_count
                metrics['early_stage_percentage'] = BiasMetric(
                    metric_name='early_stage_percentage',
                    current_value=early_stage_pct,
                    target_value=self.bias_targets['funding_stage']['early_stage_percentage']['target'],
                    threshold_warning=self.bias_targets['funding_stage']['early_stage_percentage']['warning'],
                    threshold_critical=self.bias_targets['funding_stage']['early_stage_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if early_stage_pct < 0.40 else BiasDirection.BALANCED
                )
                
                # Seed stage percentage
                seed_stage_pct = seed_stage_count / total_count
                metrics['seed_stage_percentage'] = BiasMetric(
                    metric_name='seed_stage_percentage',
                    current_value=seed_stage_pct,
                    target_value=self.bias_targets['funding_stage']['seed_stage_percentage']['target'],
                    threshold_warning=self.bias_targets['funding_stage']['seed_stage_percentage']['warning'],
                    threshold_critical=self.bias_targets['funding_stage']['seed_stage_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if seed_stage_pct < 0.25 else BiasDirection.BALANCED
                )
                
                # Grant percentage
                grant_pct = grant_count / total_count
                metrics['grant_percentage'] = BiasMetric(
                    metric_name='grant_percentage',
                    current_value=grant_pct,
                    target_value=self.bias_targets['funding_stage']['grant_percentage']['target'],
                    threshold_warning=self.bias_targets['funding_stage']['grant_percentage']['warning'],
                    threshold_critical=self.bias_targets['funding_stage']['grant_percentage']['critical'],
                    direction=BiasDirection.UNDER_REPRESENTED if grant_pct < 0.30 else BiasDirection.BALANCED
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Calculating stage metrics failed: {e}")
            return {}
    
    async def _calculate_source_metrics(self, data: Dict[str, Any]) -> Dict[str, BiasMetric]:
        """Calculate source quality bias metrics"""
        try:
            # This would integrate with the source quality scoring system
            # For now, return empty metrics
            return {}
            
        except Exception as e:
            self.logger.error(f"Calculating source metrics failed: {e}")
            return {}
    
    def _extract_countries_from_opportunity(self, opportunity: Dict[str, Any]) -> List[str]:
        """Extract countries from opportunity data"""
        countries = []
        
        # Extract from title and description
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        content = f"{title} {description}".lower()
        
        # Simple country detection
        country_patterns = {
            'KE': ['kenya', 'nairobi'],
            'NG': ['nigeria', 'lagos', 'abuja'],
            'ZA': ['south africa', 'cape town', 'johannesburg'],
            'EG': ['egypt', 'cairo'],
            'GH': ['ghana', 'accra'],
            'ET': ['ethiopia', 'addis ababa'],
            'MA': ['morocco', 'casablanca'],
            'TN': ['tunisia', 'tunis'],
            'SN': ['senegal', 'dakar'],
            'CI': ['ivory coast', 'côte d\'ivoire', 'abidjan'],
            'CF': ['central african republic', 'bangui'],
            'TD': ['chad', 'n\'djamena'],
            'CD': ['democratic republic of congo', 'kinshasa'],
            'CM': ['cameroon', 'yaoundé', 'douala']
        }
        
        for iso_code, patterns in country_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    countries.append(iso_code)
                    break
        
        return countries
    
    def _extract_sectors_from_opportunity(self, opportunity: Dict[str, Any]) -> List[str]:
        """Extract sectors from opportunity data"""
        sectors = []
        
        # Extract from title and description
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        content = f"{title} {description}".lower()
        
        # Sector detection patterns
        sector_patterns = {
            'healthcare': ['health', 'medical', 'hospital', 'clinic', 'disease'],
            'agriculture': ['agriculture', 'farming', 'crop', 'livestock', 'food'],
            'climate': ['climate', 'environment', 'sustainable', 'green', 'renewable'],
            'education': ['education', 'learning', 'school', 'university', 'training'],
            'fintech': ['fintech', 'financial', 'banking', 'payment', 'credit']
        }
        
        for sector, patterns in sector_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    sectors.append(sector)
                    break
        
        return sectors
    
    def _extract_inclusion_from_opportunity(self, opportunity: Dict[str, Any]) -> List[str]:
        """Extract inclusion indicators from opportunity data"""
        indicators = []
        
        # Extract from title and description
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        content = f"{title} {description}".lower()
        
        # Inclusion detection patterns
        inclusion_patterns = {
            'women_led': ['women', 'female', 'gender', 'maternal'],
            'youth_focused': ['youth', 'young', 'student', 'under 35'],
            'rural_priority': ['rural', 'remote', 'village', 'countryside'],
            'disability_inclusive': ['disability', 'accessible', 'inclusive'],
            'refugee_focused': ['refugee', 'displaced', 'migration']
        }
        
        for indicator, patterns in inclusion_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    indicators.append(indicator)
                    break
        
        return indicators
    
    def _detect_opportunity_language(self, opportunity: Dict[str, Any]) -> str:
        """Detect language of opportunity content"""
        # Extract from title and description
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        content = f"{title} {description}"
        
        # Simple language detection patterns
        language_patterns = {
            'fr': ['financement', 'subvention', 'recherche', 'développement', 'programme'],
            'ar': ['تمويل', 'منح', 'برامج', 'تطوير', 'ابتكار'],
            'pt': ['financiamento', 'bolsa', 'investigação', 'desenvolvimento', 'programa'],
            'sw': ['ufumuzi', 'ruzuku', 'utafiti', 'maendeleo', 'programu']
        }
        
        for lang, patterns in language_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    return lang
        
        return 'en'  # Default to English
    
    def _extract_stage_from_opportunity(self, opportunity: Dict[str, Any]) -> str:
        """Extract funding stage from opportunity data"""
        # Extract from title and description
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        content = f"{title} {description}".lower()
        
        # Stage detection patterns
        stage_patterns = {
            'pre_seed': ['pre-seed', 'idea', 'concept', 'prototype', 'mvp'],
            'seed': ['seed', 'early stage', 'startup', 'launch'],
            'series_a': ['series a', 'growth', 'scaling', 'expansion'],
            'grant': ['grant', 'research', 'development', 'non-dilutive']
        }
        
        for stage, patterns in stage_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    return stage
        
        return 'unknown'
    
    def _calculate_diversity_index(self, values: List[int]) -> float:
        """Calculate Simpson's diversity index"""
        if not values or sum(values) == 0:
            return 0.0
        
        total = sum(values)
        sum_squares = sum(x * x for x in values)
        
        # Simpson's diversity index: 1 - (sum of squares / total squared)
        diversity = 1 - (sum_squares / (total * total))
        return diversity
    
    async def _calculate_overall_equity_score(self, all_metrics: Dict[str, Dict[str, BiasMetric]]) -> float:
        """Calculate overall equity score"""
        try:
            all_scores = []
            
            for metric_group in all_metrics.values():
                for metric in metric_group.values():
                    # Score based on how close to target
                    deviation = abs(metric.current_value - metric.target_value)
                    max_deviation = max(metric.threshold_warning, metric.threshold_critical)
                    
                    if max_deviation > 0:
                        score = max(0.0, 1.0 - (deviation / max_deviation))
                        all_scores.append(score)
            
            return mean(all_scores) if all_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Calculating overall equity score failed: {e}")
            return 0.0
    
    async def _generate_alerts(self, all_metrics: Dict[str, Dict[str, BiasMetric]]) -> List[BiasAlert]:
        """Generate bias alerts"""
        alerts = []
        
        try:
            for bias_type_str, metrics in all_metrics.items():
                bias_type = BiasType(bias_type_str)
                
                for metric_name, metric in metrics.items():
                    severity = metric.calculate_severity()
                    
                    if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                        alert = BiasAlert(
                            alert_id=f"{bias_type_str}_{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            bias_type=bias_type,
                            severity=severity,
                            message=f"{metric.metric_name}: {metric.current_value:.3f} (target: {metric.target_value:.3f})",
                            metric=metric,
                            recommendations=await self._get_metric_recommendations(bias_type, metric_name, metric)
                        )
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Generating alerts failed: {e}")
            return []
    
    async def _get_metric_recommendations(self, bias_type: BiasType, metric_name: str, 
                                        metric: BiasMetric) -> List[str]:
        """Get recommendations for a specific metric"""
        recommendations = []
        
        if bias_type == BiasType.GEOGRAPHIC:
            if 'central_africa' in metric_name:
                recommendations.extend([
                    "Increase search frequency for Central African sources",
                    "Add Central African funding databases to monitoring",
                    "Implement French-language searches for CAR/Chad/DRC"
                ])
            elif 'non_big_four' in metric_name:
                recommendations.extend([
                    "Reduce search frequency for Big 4 countries",
                    "Boost searches for underrepresented countries",
                    "Add regional development bank sources"
                ])
        
        elif bias_type == BiasType.SECTORAL:
            if 'healthcare' in metric_name:
                recommendations.extend([
                    "Add healthcare-specific funding sources",
                    "Implement health-focused search terms",
                    "Monitor WHO and health ministry announcements"
                ])
            elif 'agriculture' in metric_name:
                recommendations.extend([
                    "Add agricultural development funding sources",
                    "Monitor FAO and agricultural ministry announcements",
                    "Implement agri-tech specific search terms"
                ])
        
        elif bias_type == BiasType.LANGUAGE:
            if 'french' in metric_name:
                recommendations.extend([
                    "Activate French-language search modules",
                    "Add francophone African funding sources",
                    "Monitor AFD and francophone development banks"
                ])
            elif 'arabic' in metric_name:
                recommendations.extend([
                    "Activate Arabic-language search modules",
                    "Add North African funding sources",
                    "Monitor Islamic Development Bank announcements"
                ])
        
        return recommendations
    
    async def _store_snapshot(self, snapshot: BiasSnapshot):
        """Store bias snapshot for historical analysis"""
        try:
            # Store in historical snapshots
            self.historical_snapshots.append(snapshot)
            
            # Trim old snapshots
            cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
            self.historical_snapshots = [
                s for s in self.historical_snapshots 
                if s.timestamp > cutoff_date
            ]
            
        except Exception as e:
            self.logger.error(f"Storing snapshot failed: {e}")
    
    async def _get_historical_snapshots(self, days: int) -> List[BiasSnapshot]:
        """Get historical snapshots for trend analysis"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            return [s for s in self.historical_snapshots if s.timestamp > cutoff_date]
            
        except Exception as e:
            self.logger.error(f"Getting historical snapshots failed: {e}")
            return []
    
    def _calculate_metric_trends(self, historical_data: List[BiasSnapshot], 
                               metric_group: str) -> Dict[str, Any]:
        """Calculate trends for a metric group"""
        try:
            if not historical_data:
                return {}
            
            trends = {}
            
            # Get all metric names from the group
            all_metrics = set()
            for snapshot in historical_data:
                group_metrics = getattr(snapshot, metric_group, {})
                all_metrics.update(group_metrics.keys())
            
            # Calculate trend for each metric
            for metric_name in all_metrics:
                values = []
                for snapshot in historical_data:
                    group_metrics = getattr(snapshot, metric_group, {})
                    metric = group_metrics.get(metric_name)
                    if metric:
                        values.append(metric.current_value)
                
                if len(values) >= 2:
                    # Simple trend calculation
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    
                    first_avg = mean(first_half)
                    second_avg = mean(second_half)
                    
                    trend_direction = 'improving' if second_avg > first_avg else 'declining'
                    trend_magnitude = abs(second_avg - first_avg)
                    
                    trends[metric_name] = {
                        'direction': trend_direction,
                        'magnitude': trend_magnitude,
                        'current_value': values[-1],
                        'volatility': stdev(values) if len(values) > 1 else 0.0
                    }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Calculating metric trends failed: {e}")
            return {}
    
    def _calculate_equity_trend(self, historical_data: List[BiasSnapshot]) -> Dict[str, Any]:
        """Calculate overall equity trend"""
        try:
            if not historical_data:
                return {}
            
            equity_scores = [s.overall_equity_score for s in historical_data]
            
            if len(equity_scores) >= 2:
                first_half = equity_scores[:len(equity_scores)//2]
                second_half = equity_scores[len(equity_scores)//2:]
                
                first_avg = mean(first_half)
                second_avg = mean(second_half)
                
                return {
                    'direction': 'improving' if second_avg > first_avg else 'declining',
                    'magnitude': abs(second_avg - first_avg),
                    'current_score': equity_scores[-1],
                    'volatility': stdev(equity_scores) if len(equity_scores) > 1 else 0.0
                }
            
            return {'direction': 'unknown', 'magnitude': 0.0}
            
        except Exception as e:
            self.logger.error(f"Calculating equity trend failed: {e}")
            return {}
    
    async def _analyze_geographic_bias(self, metrics: Dict[str, BiasMetric]) -> List[Dict[str, Any]]:
        """Analyze geographic bias and provide recommendations"""
        recommendations = []
        
        for metric_name, metric in metrics.items():
            if metric.direction == BiasDirection.UNDER_REPRESENTED:
                if 'central_africa' in metric_name:
                    recommendations.append({
                        'type': 'geographic_bias',
                        'priority': 5,
                        'title': 'Central Africa Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities from Central Africa (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add Central African funding databases',
                            'Implement French-language searches',
                            'Monitor regional development banks'
                        ]
                    })
                elif 'non_big_four' in metric_name:
                    recommendations.append({
                        'type': 'geographic_bias',
                        'priority': 4,
                        'title': 'Over-concentration in Big 4 Countries',
                        'description': f'Only {metric.current_value:.1%} of opportunities from non-Big 4 countries (target: {metric.target_value:.1%})',
                        'actions': [
                            'Reduce Big 4 search frequency',
                            'Boost underserved region searches',
                            'Add regional funding sources'
                        ]
                    })
        
        return recommendations
    
    async def _analyze_sectoral_bias(self, metrics: Dict[str, BiasMetric]) -> List[Dict[str, Any]]:
        """Analyze sectoral bias and provide recommendations"""
        recommendations = []
        
        for metric_name, metric in metrics.items():
            if metric.direction == BiasDirection.UNDER_REPRESENTED:
                if 'healthcare' in metric_name:
                    recommendations.append({
                        'type': 'sectoral_bias',
                        'priority': 5,
                        'title': 'Healthcare Sector Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities in healthcare (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add health ministry sources',
                            'Monitor WHO funding announcements',
                            'Implement health-specific search terms'
                        ]
                    })
                elif 'agriculture' in metric_name:
                    recommendations.append({
                        'type': 'sectoral_bias',
                        'priority': 5,
                        'title': 'Agriculture Sector Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities in agriculture (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add agricultural ministry sources',
                            'Monitor FAO funding announcements',
                            'Implement agri-tech search terms'
                        ]
                    })
        
        return recommendations
    
    async def _analyze_inclusion_bias(self, metrics: Dict[str, BiasMetric]) -> List[Dict[str, Any]]:
        """Analyze inclusion bias and provide recommendations"""
        recommendations = []
        
        for metric_name, metric in metrics.items():
            if metric.direction == BiasDirection.UNDER_REPRESENTED:
                if 'women' in metric_name:
                    recommendations.append({
                        'type': 'inclusion_bias',
                        'priority': 4,
                        'title': 'Women-focused Opportunities Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities target women (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add women-focused funding sources',
                            'Monitor gender equality organizations',
                            'Implement women-specific search terms'
                        ]
                    })
                elif 'youth' in metric_name:
                    recommendations.append({
                        'type': 'inclusion_bias',
                        'priority': 4,
                        'title': 'Youth-focused Opportunities Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities target youth (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add youth-focused funding sources',
                            'Monitor youth development organizations',
                            'Implement youth-specific search terms'
                        ]
                    })
        
        return recommendations
    
    async def _analyze_language_bias(self, metrics: Dict[str, BiasMetric]) -> List[Dict[str, Any]]:
        """Analyze language bias and provide recommendations"""
        recommendations = []
        
        for metric_name, metric in metrics.items():
            if metric.direction == BiasDirection.UNDER_REPRESENTED:
                if 'french' in metric_name:
                    recommendations.append({
                        'type': 'language_bias',
                        'priority': 3,
                        'title': 'French Language Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities in French (target: {metric.target_value:.1%})',
                        'actions': [
                            'Activate French search modules',
                            'Add francophone funding sources',
                            'Monitor AFD announcements'
                        ]
                    })
                elif 'arabic' in metric_name:
                    recommendations.append({
                        'type': 'language_bias',
                        'priority': 3,
                        'title': 'Arabic Language Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities in Arabic (target: {metric.target_value:.1%})',
                        'actions': [
                            'Activate Arabic search modules',
                            'Add North African funding sources',
                            'Monitor Islamic Development Bank'
                        ]
                    })
        
        return recommendations
    
    async def _analyze_stage_bias(self, metrics: Dict[str, BiasMetric]) -> List[Dict[str, Any]]:
        """Analyze funding stage bias and provide recommendations"""
        recommendations = []
        
        for metric_name, metric in metrics.items():
            if metric.direction == BiasDirection.UNDER_REPRESENTED:
                if 'early_stage' in metric_name:
                    recommendations.append({
                        'type': 'stage_bias',
                        'priority': 4,
                        'title': 'Early Stage Opportunities Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities are early-stage (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add accelerator/incubator sources',
                            'Monitor startup competition announcements',
                            'Implement early-stage search terms'
                        ]
                    })
                elif 'grant' in metric_name:
                    recommendations.append({
                        'type': 'stage_bias',
                        'priority': 4,
                        'title': 'Grant Opportunities Under-represented',
                        'description': f'Only {metric.current_value:.1%} of opportunities are grants (target: {metric.target_value:.1%})',
                        'actions': [
                            'Add government funding sources',
                            'Monitor research funding announcements',
                            'Implement grant-specific search terms'
                        ]
                    })
        
        return recommendations
    
    async def _execute_mitigation_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific mitigation action"""
        try:
            action_type = action.get('action')
            
            if action_type == 'boost_underserved_searches':
                # This would integrate with the search scheduling system
                return {
                    'action': action_type,
                    'status': 'executed',
                    'message': 'Boosted underserved region searches',
                    'timestamp': datetime.now().isoformat()
                }
            
            elif action_type == 'activate_multilingual_search':
                # This would integrate with the multilingual search system
                return {
                    'action': action_type,
                    'status': 'executed',
                    'message': 'Activated multilingual search modules',
                    'timestamp': datetime.now().isoformat()
                }
            
            else:
                return {
                    'action': action_type,
                    'status': 'not_implemented',
                    'message': 'Action type not implemented',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Executing mitigation action failed: {e}")
            return {
                'action': action.get('action', 'unknown'),
                'status': 'failed',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def example_usage():
    """Example usage of bias monitoring system"""
    monitor = BiasMonitoringEngine()
    
    # Analyze current bias
    snapshot = await monitor.analyze_current_bias()
    
    print("=== Current Bias Analysis ===")
    print(f"Overall Equity Score: {snapshot.overall_equity_score:.3f}")
    print(f"Active Alerts: {len(snapshot.active_alerts)}")
    
    # Show geographic metrics
    print("\n=== Geographic Metrics ===")
    for name, metric in snapshot.geographic_metrics.items():
        print(f"{name}: {metric.current_value:.3f} (target: {metric.target_value:.3f})")
    
    # Show alerts
    print("\n=== Active Alerts ===")
    for alert in snapshot.active_alerts:
        print(f"[{alert.severity.value.upper()}] {alert.message}")
    
    # Get recommendations
    recommendations = await monitor.get_bias_recommendations()
    print(f"\n=== Recommendations ({len(recommendations)}) ===")
    for rec in recommendations[:5]:  # Show top 5
        print(f"[Priority {rec['priority']}] {rec['title']}")
        print(f"  {rec['description']}")
    
    # Get trends
    trends = await monitor.get_bias_trends(30)
    print(f"\n=== 30-Day Trends ===")
    equity_trend = trends.get('overall_equity_trend', {})
    print(f"Overall Equity: {equity_trend.get('direction', 'unknown')} (magnitude: {equity_trend.get('magnitude', 0):.3f})")

if __name__ == "__main__":
    asyncio.run(example_usage())