"""
Organization Completeness Scorer

Calculates completeness scores for organization profiles with emphasis on 
cultural context and respectful representation metrics.
"""
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.core.logging import logger


class OrganizationCompletenessScorer:
    """
    Calculates completeness scores for organization profiles with weighted 
    scoring based on importance for respectful representation.
    """
    
    def __init__(self):
        self.field_weights = self._define_field_weights()
        self.scoring_criteria = self._define_scoring_criteria()
    
    def _define_field_weights(self) -> Dict[str, float]:
        """Define weighted importance of different fields"""
        return {
            # Core identity fields (high importance)
            'name': 1.0,
            'type': 1.0,
            'description': 1.0,
            'mission_statement': 1.0,
            'vision_statement': 0.8,
            'country': 1.0,
            'region': 0.8,
            'website': 0.9,
            
            # Cultural and heritage context (critical for respectful representation)
            'founding_story': 1.2,
            'cultural_significance': 1.2,
            'local_partnerships': 1.1,
            'community_impact': 1.1,
            'languages_supported': 0.9,
            
            # Leadership and governance (important for credibility)
            'leadership_team': 1.0,
            'established_year': 0.7,
            'contact_person': 0.6,
            'contact_email': 0.6,
            
            # Impact and achievements (showcase value)
            'notable_achievements': 1.0,
            'awards_recognition': 0.9,
            'success_stories': 1.0,
            'beneficiaries_count': 0.8,
            'total_funding_distributed': 0.8,
            
            # Online presence and accessibility
            'logo_url': 0.7,
            'linkedin_url': 0.6,
            'twitter_handle': 0.5,
            'facebook_url': 0.4,
            'instagram_url': 0.3,
            
            # Operational context
            'annual_budget_range': 0.6,
            'staff_size_range': 0.5,
            'focus_areas': 0.8,
            'funding_capacity': 0.7,
            
            # Metrics and performance
            'ai_relevance_score': 0.8,
            'africa_relevance_score': 0.8,
            'community_rating': 0.6,
            'data_completeness_score': 0.4,
            
            # Enrichment tracking
            'enrichment_sources': 0.3,
            'last_enrichment_attempt': 0.2
        }
    
    def _define_scoring_criteria(self) -> Dict[str, Dict]:
        """Define scoring criteria for different field types"""
        return {
            'text_fields': {
                'excellent': lambda x: len(x) >= 200,
                'good': lambda x: len(x) >= 100,
                'fair': lambda x: len(x) >= 50,
                'poor': lambda x: len(x) >= 10,
                'missing': lambda x: len(x) == 0
            },
            'json_fields': {
                'excellent': lambda x: len(x) >= 5,
                'good': lambda x: len(x) >= 3,
                'fair': lambda x: len(x) >= 2,
                'poor': lambda x: len(x) >= 1,
                'missing': lambda x: len(x) == 0
            },
            'numeric_fields': {
                'excellent': lambda x: x is not None and x > 0,
                'missing': lambda x: x is None or x == 0
            },
            'url_fields': {
                'excellent': lambda x: x is not None and x.startswith('http') and len(x) > 10,
                'missing': lambda x: x is None or x == ''
            },
            'score_fields': {
                'excellent': lambda x: x >= 80,
                'good': lambda x: x >= 60,
                'fair': lambda x: x >= 40,
                'poor': lambda x: x >= 20,
                'missing': lambda x: x < 20
            }
        }
    
    def calculate_completeness_score(self, organization: Organization) -> Dict:
        """
        Calculate comprehensive completeness score for an organization.
        
        Args:
            organization: Organization instance
            
        Returns:
            Dictionary with detailed scoring breakdown
        """
        try:
            field_scores = {}
            category_scores = {}
            total_weighted_score = 0
            total_weight = 0
            
            # Score each field
            for field_name, weight in self.field_weights.items():
                field_score = self._score_field(organization, field_name)
                field_scores[field_name] = {
                    'score': field_score,
                    'weight': weight,
                    'weighted_score': field_score * weight
                }
                total_weighted_score += field_score * weight
                total_weight += weight
            
            # Calculate category scores
            category_scores = self._calculate_category_scores(field_scores)
            
            # Calculate overall score
            overall_score = round((total_weighted_score / total_weight) * 100) if total_weight > 0 else 0
            
            # Determine quality grade
            quality_grade = self._get_quality_grade(overall_score)
            
            # Calculate cultural representation score
            cultural_score = self._calculate_cultural_representation_score(organization)
            
            # Calculate showcase readiness score
            showcase_score = self._calculate_showcase_readiness_score(organization)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(field_scores, organization)
            
            result = {
                'organization_id': organization.id,
                'organization_name': organization.name,
                'overall_score': overall_score,
                'quality_grade': quality_grade,
                'cultural_representation_score': cultural_score,
                'showcase_readiness_score': showcase_score,
                'category_scores': category_scores,
                'field_scores': field_scores,
                'recommendations': recommendations,
                'calculated_at': datetime.utcnow().isoformat(),
                'scoring_version': '1.0'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating completeness score for organization {organization.id}: {str(e)}")
            return {
                'organization_id': organization.id,
                'error': str(e),
                'calculated_at': datetime.utcnow().isoformat()
            }
    
    def _score_field(self, organization: Organization, field_name: str) -> float:
        """Score a single field based on its content and type"""
        try:
            value = getattr(organization, field_name, None)
            
            if value is None:
                return 0.0
            
            # Handle different field types
            if field_name in ['name', 'type', 'country', 'region', 'website', 'email']:
                return self._score_basic_field(value)
            
            elif field_name in ['description', 'mission_statement', 'vision_statement', 
                               'founding_story', 'cultural_significance', 'community_impact']:
                return self._score_text_field(value)
            
            elif field_name in ['leadership_team', 'local_partnerships', 'notable_achievements',
                               'awards_recognition', 'success_stories', 'languages_supported',
                               'focus_areas', 'enrichment_sources']:
                return self._score_json_field(value)
            
            elif field_name in ['established_year', 'beneficiaries_count', 'ai_relevance_score',
                               'africa_relevance_score', 'data_completeness_score']:
                return self._score_numeric_field(value)
            
            elif field_name in ['logo_url', 'linkedin_url', 'twitter_handle', 'facebook_url',
                               'instagram_url']:
                return self._score_url_field(value)
            
            elif field_name in ['annual_budget_range', 'staff_size_range', 'funding_capacity']:
                return self._score_range_field(value)
            
            elif field_name in ['community_rating', 'total_funding_distributed']:
                return self._score_rating_field(value)
            
            elif field_name in ['last_enrichment_attempt']:
                return self._score_datetime_field(value)
            
            else:
                return 0.5 if value else 0.0
                
        except Exception as e:
            logger.error(f"Error scoring field {field_name}: {str(e)}")
            return 0.0
    
    def _score_basic_field(self, value: str) -> float:
        """Score basic string fields"""
        if not value or value.strip() == '':
            return 0.0
        elif len(value.strip()) >= 3:
            return 1.0
        else:
            return 0.5
    
    def _score_text_field(self, value: str) -> float:
        """Score text fields based on length and quality"""
        if not value or value.strip() == '':
            return 0.0
        
        length = len(value.strip())
        
        if length >= 200:
            return 1.0
        elif length >= 100:
            return 0.8
        elif length >= 50:
            return 0.6
        elif length >= 10:
            return 0.4
        else:
            return 0.2
    
    def _score_json_field(self, value: str) -> float:
        """Score JSON array fields"""
        if not value or value.strip() == '':
            return 0.0
        
        try:
            if value == '[]':
                return 0.0
            
            data = json.loads(value) if isinstance(value, str) else value
            
            if not isinstance(data, list):
                return 0.3
            
            count = len(data)
            
            if count >= 5:
                return 1.0
            elif count >= 3:
                return 0.8
            elif count >= 2:
                return 0.6
            elif count >= 1:
                return 0.4
            else:
                return 0.0
                
        except (json.JSONDecodeError, TypeError):
            return 0.0
    
    def _score_numeric_field(self, value) -> float:
        """Score numeric fields"""
        if value is None:
            return 0.0
        elif isinstance(value, (int, float)) and value > 0:
            return 1.0
        else:
            return 0.0
    
    def _score_url_field(self, value: str) -> float:
        """Score URL fields"""
        if not value or value.strip() == '':
            return 0.0
        elif value.startswith('http') and len(value) > 10:
            return 1.0
        else:
            return 0.3
    
    def _score_range_field(self, value: str) -> float:
        """Score range fields (budget, staff size, etc.)"""
        if not value or value.strip() == '':
            return 0.0
        elif '-' in value and len(value) > 3:
            return 1.0
        else:
            return 0.5
    
    def _score_rating_field(self, value) -> float:
        """Score rating/financial fields"""
        if value is None:
            return 0.0
        elif isinstance(value, (int, float)) and value > 0:
            return 1.0
        else:
            return 0.0
    
    def _score_datetime_field(self, value) -> float:
        """Score datetime fields"""
        if value is None:
            return 0.0
        elif isinstance(value, datetime):
            return 1.0
        else:
            return 0.0
    
    def _calculate_category_scores(self, field_scores: Dict) -> Dict:
        """Calculate scores for different categories"""
        categories = {
            'core_identity': [
                'name', 'type', 'description', 'mission_statement', 'vision_statement',
                'country', 'region', 'website', 'established_year'
            ],
            'cultural_context': [
                'founding_story', 'cultural_significance', 'local_partnerships',
                'community_impact', 'languages_supported'
            ],
            'leadership_governance': [
                'leadership_team', 'contact_person', 'contact_email'
            ],
            'impact_achievements': [
                'notable_achievements', 'awards_recognition', 'success_stories',
                'beneficiaries_count', 'total_funding_distributed'
            ],
            'online_presence': [
                'logo_url', 'linkedin_url', 'twitter_handle', 'facebook_url',
                'instagram_url'
            ],
            'operational_context': [
                'annual_budget_range', 'staff_size_range', 'focus_areas',
                'funding_capacity'
            ],
            'performance_metrics': [
                'ai_relevance_score', 'africa_relevance_score', 'community_rating',
                'data_completeness_score'
            ]
        }
        
        category_scores = {}
        
        for category, fields in categories.items():
            total_score = 0
            total_weight = 0
            field_count = 0
            
            for field in fields:
                if field in field_scores:
                    score_data = field_scores[field]
                    total_score += score_data['weighted_score']
                    total_weight += score_data['weight']
                    field_count += 1
            
            if total_weight > 0:
                category_scores[category] = {
                    'score': round((total_score / total_weight) * 100),
                    'fields_evaluated': field_count,
                    'weight': total_weight
                }
            else:
                category_scores[category] = {
                    'score': 0,
                    'fields_evaluated': 0,
                    'weight': 0
                }
        
        return category_scores
    
    def _calculate_cultural_representation_score(self, organization: Organization) -> int:
        """Calculate cultural representation score"""
        cultural_fields = [
            'founding_story', 'cultural_significance', 'local_partnerships',
            'community_impact', 'languages_supported'
        ]
        
        total_score = 0
        field_count = 0
        
        for field in cultural_fields:
            score = self._score_field(organization, field)
            total_score += score
            field_count += 1
        
        return round((total_score / field_count) * 100) if field_count > 0 else 0
    
    def _calculate_showcase_readiness_score(self, organization: Organization) -> int:
        """Calculate readiness for respectful showcase"""
        showcase_fields = [
            'name', 'description', 'mission_statement', 'founding_story',
            'cultural_significance', 'notable_achievements', 'success_stories',
            'logo_url', 'website', 'leadership_team'
        ]
        
        total_score = 0
        field_count = 0
        
        for field in showcase_fields:
            score = self._score_field(organization, field)
            total_score += score
            field_count += 1
        
        return round((total_score / field_count) * 100) if field_count > 0 else 0
    
    def _get_quality_grade(self, score: int) -> str:
        """Convert score to quality grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, field_scores: Dict, organization: Organization) -> List[Dict]:
        """Generate recommendations for improving completeness"""
        recommendations = []
        
        # Identify missing high-priority fields
        high_priority_fields = [
            'mission_statement', 'founding_story', 'cultural_significance',
            'leadership_team', 'notable_achievements', 'success_stories'
        ]
        
        for field in high_priority_fields:
            if field in field_scores and field_scores[field]['score'] < 0.5:
                recommendations.append({
                    'type': 'missing_field',
                    'priority': 'high',
                    'field': field,
                    'description': f"Add {field.replace('_', ' ')} to improve cultural representation",
                    'impact': 'high'
                })
        
        # Check for missing contact information
        if field_scores.get('contact_person', {}).get('score', 0) < 0.5:
            recommendations.append({
                'type': 'missing_contact',
                'priority': 'medium',
                'field': 'contact_person',
                'description': "Add contact person for better accessibility",
                'impact': 'medium'
            })
        
        # Check for missing online presence
        online_fields = ['logo_url', 'linkedin_url', 'website']
        missing_online = [f for f in online_fields if field_scores.get(f, {}).get('score', 0) < 0.5]
        
        if len(missing_online) > 1:
            recommendations.append({
                'type': 'missing_online_presence',
                'priority': 'medium',
                'fields': missing_online,
                'description': "Improve online presence for better discoverability",
                'impact': 'medium'
            })
        
        # Check for missing impact metrics
        impact_fields = ['beneficiaries_count', 'total_funding_distributed']
        missing_impact = [f for f in impact_fields if field_scores.get(f, {}).get('score', 0) < 0.5]
        
        if missing_impact:
            recommendations.append({
                'type': 'missing_impact_metrics',
                'priority': 'medium',
                'fields': missing_impact,
                'description': "Add impact metrics to showcase effectiveness",
                'impact': 'medium'
            })
        
        return recommendations
    
    def batch_calculate_scores(self, db: Session, organization_ids: List[int] = None) -> List[Dict]:
        """Calculate completeness scores for multiple organizations"""
        if organization_ids:
            organizations = db.query(Organization).filter(
                Organization.id.in_(organization_ids)
            ).all()
        else:
            organizations = db.query(Organization).all()
        
        results = []
        
        for org in organizations:
            try:
                score_result = self.calculate_completeness_score(org)
                results.append(score_result)
                
                # Update organization completeness score
                if 'overall_score' in score_result:
                    org.enrichment_completeness = score_result['overall_score']
                    db.commit()
                    
            except Exception as e:
                logger.error(f"Error calculating score for organization {org.id}: {str(e)}")
                results.append({
                    'organization_id': org.id,
                    'error': str(e),
                    'calculated_at': datetime.utcnow().isoformat()
                })
        
        return results
    
    def get_organizations_by_completeness(self, db: Session, grade: str = None, 
                                        min_score: int = None, max_score: int = None) -> List[Organization]:
        """Get organizations filtered by completeness criteria"""
        query = db.query(Organization)
        
        if grade:
            score_ranges = {
                'A': (90, 100),
                'B': (80, 89),
                'C': (70, 79),
                'D': (60, 69),
                'F': (0, 59)
            }
            
            if grade in score_ranges:
                min_range, max_range = score_ranges[grade]
                query = query.filter(
                    Organization.enrichment_completeness >= min_range,
                    Organization.enrichment_completeness <= max_range
                )
        
        if min_score:
            query = query.filter(Organization.enrichment_completeness >= min_score)
        
        if max_score:
            query = query.filter(Organization.enrichment_completeness <= max_score)
        
        return query.all()
    
    def generate_completeness_report(self, db: Session) -> Dict:
        """Generate comprehensive completeness report"""
        organizations = db.query(Organization).all()
        
        if not organizations:
            return {'error': 'No organizations found'}
        
        scores = []
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for org in organizations:
            score_result = self.calculate_completeness_score(org)
            if 'overall_score' in score_result:
                scores.append(score_result['overall_score'])
                grade = score_result['quality_grade']
                grade_distribution[grade] += 1
        
        if not scores:
            return {'error': 'No valid scores calculated'}
        
        return {
            'total_organizations': len(organizations),
            'average_score': round(sum(scores) / len(scores), 1),
            'median_score': sorted(scores)[len(scores) // 2],
            'grade_distribution': grade_distribution,
            'organizations_needing_attention': len([s for s in scores if s < 70]),
            'showcase_ready_organizations': len([s for s in scores if s >= 80]),
            'generated_at': datetime.utcnow().isoformat()
        }