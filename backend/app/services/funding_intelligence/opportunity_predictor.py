"""
Opportunity Prediction Engine for Funding Intelligence
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class OpportunityType(Enum):
    FUNDING_PROGRAM = "funding_program"
    INNOVATION_CHALLENGE = "innovation_challenge"
    ACCELERATOR_PROGRAM = "accelerator_program"
    RESEARCH_GRANT = "research_grant"
    PARTNERSHIP_OPPORTUNITY = "partnership_opportunity"
    INVESTMENT_ROUND = "investment_round"
    PILOT_PROGRAM = "pilot_program"
    SCALE_UP_FUNDING = "scale_up_funding"
    CONFERENCE_SPONSORSHIP = "conference_sponsorship"
    CAPACITY_BUILDING = "capacity_building"


@dataclass
class OpportunityPrediction:
    """Represents a predicted funding opportunity"""
    opportunity_type: OpportunityType
    title: str
    description: str
    predicted_funder: str
    estimated_amount: str
    confidence: float
    expected_timeline: str  # "immediate", "short_term", "long_term"
    expected_date: Optional[datetime] = None
    rationale: str = ""
    supporting_evidence: List[str] = field(default_factory=list)
    target_sectors: List[str] = field(default_factory=list)
    target_regions: List[str] = field(default_factory=list)
    application_process: str = ""
    key_requirements: List[str] = field(default_factory=list)
    decision_makers: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.opportunity_type, str):
            self.opportunity_type = OpportunityType(self.opportunity_type)


class OpportunityPredictor:
    """
    Predict future funding opportunities from current events
    """
    
    def __init__(self):
        self.prediction_rules = self._build_prediction_rules()
        self.pattern_library = self._build_pattern_library()
        self.funder_profiles = self._build_funder_profiles()
    
    def _build_prediction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Build rules for predicting opportunities from events"""
        return {
            'strategy_launch': {
                'trigger_patterns': ['AI strategy', 'national plan', 'digital transformation', 'policy framework'],
                'typical_outcomes': [
                    {
                        'opportunity_type': OpportunityType.FUNDING_PROGRAM,
                        'probability': 0.8,
                        'timeline_days': 180,
                        'estimated_amounts': ['$1M-10M', '$10M-50M', '$50M+'],
                        'rationale': 'National AI strategies typically result in funding programs within 6 months'
                    },
                    {
                        'opportunity_type': OpportunityType.RESEARCH_GRANT,
                        'probability': 0.7,
                        'timeline_days': 120,
                        'estimated_amounts': ['$100K-1M', '$1M-5M'],
                        'rationale': 'Government strategies often include research funding components'
                    }
                ]
            },
            'corporate_partnership': {
                'trigger_patterns': ['partnership', 'alliance', 'collaboration', 'MOU'],
                'typical_outcomes': [
                    {
                        'opportunity_type': OpportunityType.INNOVATION_CHALLENGE,
                        'probability': 0.65,
                        'timeline_days': 90,
                        'estimated_amounts': ['$50K-500K', '$500K-2M'],
                        'rationale': 'Corporate partnerships typically include innovation challenges'
                    },
                    {
                        'opportunity_type': OpportunityType.ACCELERATOR_PROGRAM,
                        'probability': 0.6,
                        'timeline_days': 120,
                        'estimated_amounts': ['$25K-100K', '$100K-500K'],
                        'rationale': 'Partnerships often lead to accelerator programs'
                    }
                ]
            },
            'pilot_success': {
                'trigger_patterns': ['pilot successful', 'proof of concept', 'trial completed', 'initial results'],
                'typical_outcomes': [
                    {
                        'opportunity_type': OpportunityType.SCALE_UP_FUNDING,
                        'probability': 0.7,
                        'timeline_days': 60,
                        'estimated_amounts': ['$500K-5M', '$5M-20M'],
                        'rationale': 'Successful pilots typically receive scale-up funding'
                    },
                    {
                        'opportunity_type': OpportunityType.PARTNERSHIP_OPPORTUNITY,
                        'probability': 0.6,
                        'timeline_days': 90,
                        'estimated_amounts': ['$100K-1M', '$1M-5M'],
                        'rationale': 'Pilot success often leads to strategic partnerships'
                    }
                ]
            },
            'investment_round': {
                'trigger_patterns': ['raises', 'funding round', 'Series A', 'Series B', 'investment'],
                'typical_outcomes': [
                    {
                        'opportunity_type': OpportunityType.INVESTMENT_ROUND,
                        'probability': 0.9,
                        'timeline_days': 30,
                        'estimated_amounts': ['$1M-10M', '$10M-50M', '$50M+'],
                        'rationale': 'Direct investment opportunity'
                    }
                ]
            },
            'conference_announcement': {
                'trigger_patterns': ['conference', 'summit', 'symposium', 'workshop'],
                'typical_outcomes': [
                    {
                        'opportunity_type': OpportunityType.CONFERENCE_SPONSORSHIP,
                        'probability': 0.5,
                        'timeline_days': 30,
                        'estimated_amounts': ['$10K-100K', '$100K-500K'],
                        'rationale': 'Conferences often seek sponsors and may announce funding'
                    },
                    {
                        'opportunity_type': OpportunityType.INNOVATION_CHALLENGE,
                        'probability': 0.4,
                        'timeline_days': 60,
                        'estimated_amounts': ['$25K-250K', '$250K-1M'],
                        'rationale': 'Conferences often host innovation challenges'
                    }
                ]
            }
        }
    
    def _build_pattern_library(self) -> Dict[str, Dict[str, Any]]:
        """Build library of historical patterns"""
        return {
            'google_africa_pattern': {
                'description': 'Google typically announces funding programs 2-3 months after partnership announcements',
                'historical_accuracy': 0.8,
                'typical_amounts': ['$1M-5M', '$5M-20M'],
                'typical_timeline': 90,
                'focus_areas': ['AI', 'digital skills', 'startup acceleration']
            },
            'world_bank_pattern': {
                'description': 'World Bank funding follows government strategy launches by 4-6 months',
                'historical_accuracy': 0.85,
                'typical_amounts': ['$10M-50M', '$50M-200M'],
                'typical_timeline': 150,
                'focus_areas': ['digital transformation', 'infrastructure', 'capacity building']
            },
            'microsoft_pattern': {
                'description': 'Microsoft AI for Good initiatives typically launch 2-4 months after announcements',
                'historical_accuracy': 0.75,
                'typical_amounts': ['$500K-3M', '$3M-10M'],
                'typical_timeline': 75,
                'focus_areas': ['AI for Good', 'skills development', 'digital inclusion']
            }
        }
    
    def _build_funder_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Build profiles of known funders"""
        return {
            'Google': {
                'funding_capacity': 5000000000,
                'focus_areas': ['AI', 'digital skills', 'startup acceleration', 'women in tech'],
                'typical_amounts': ['$50K-500K', '$500K-2M', '$2M-10M'],
                'preferred_regions': ['Africa', 'Global'],
                'funding_cycle': 'quarterly',
                'decision_timeline': '60-90 days',
                'key_decision_makers': ['Head of AI', 'Country Director', 'Program Manager']
            },
            'Microsoft': {
                'funding_capacity': 3000000000,
                'focus_areas': ['AI for Good', 'digital transformation', 'skills development'],
                'typical_amounts': ['$100K-1M', '$1M-5M', '$5M-20M'],
                'preferred_regions': ['Africa', 'Global'],
                'funding_cycle': 'bi-annual',
                'decision_timeline': '45-75 days',
                'key_decision_makers': ['AI for Good Director', 'Regional Lead']
            },
            'World Bank': {
                'funding_capacity': 50000000000,
                'focus_areas': ['digital development', 'infrastructure', 'capacity building'],
                'typical_amounts': ['$1M-10M', '$10M-50M', '$50M+'],
                'preferred_regions': ['Africa', 'Developing Countries'],
                'funding_cycle': 'annual',
                'decision_timeline': '120-180 days',
                'key_decision_makers': ['Country Director', 'Sector Manager', 'Program Leader']
            }
        }
    
    async def predict_opportunities(self, recent_events: List[Dict[str, Any]]) -> List[OpportunityPrediction]:
        """
        Predict future funding opportunities from current events
        """
        predictions = []
        
        for event in recent_events:
            event_predictions = await self._analyze_event_for_opportunities(event)
            predictions.extend(event_predictions)
        
        # Cross-reference with patterns
        pattern_predictions = await self._apply_pattern_matching(recent_events)
        predictions.extend(pattern_predictions)
        
        # Remove duplicates and rank by confidence
        unique_predictions = self._deduplicate_predictions(predictions)
        ranked_predictions = sorted(unique_predictions, key=lambda x: x.confidence, reverse=True)
        
        return ranked_predictions
    
    async def _analyze_event_for_opportunities(self, event: Dict[str, Any]) -> List[OpportunityPrediction]:
        """
        Analyze a single event for funding opportunities
        """
        predictions = []
        event_type = event.get('signal_type', 'unknown')
        event_content = event.get('content', '')
        
        # Check if event matches any prediction rules
        for rule_name, rule_config in self.prediction_rules.items():
            if self._event_matches_rule(event_content, rule_config):
                for outcome in rule_config['typical_outcomes']:
                    prediction = await self._create_prediction_from_rule(
                        event, rule_name, outcome
                    )
                    predictions.append(prediction)
        
        return predictions
    
    def _event_matches_rule(self, content: str, rule_config: Dict[str, Any]) -> bool:
        """Check if event content matches a prediction rule"""
        content_lower = content.lower()
        patterns = rule_config.get('trigger_patterns', [])
        
        return any(pattern.lower() in content_lower for pattern in patterns)
    
    async def _create_prediction_from_rule(self, event: Dict[str, Any], 
                                         rule_name: str, 
                                         outcome: Dict[str, Any]) -> OpportunityPrediction:
        """Create a prediction based on a rule and outcome"""
        
        # Determine timeline
        timeline_days = outcome.get('timeline_days', 90)
        expected_date = datetime.now() + timedelta(days=timeline_days)
        
        if timeline_days <= 30:
            timeline = "immediate"
        elif timeline_days <= 90:
            timeline = "short_term"
        else:
            timeline = "long_term"
        
        # Extract entities from event
        entities = event.get('extracted_entities', {})
        funders = entities.get('funders', ['Unknown Funder'])
        predicted_funder = funders[0] if funders else 'Unknown Funder'
        
        # Estimate amount
        amounts = outcome.get('estimated_amounts', ['$100K-1M'])
        estimated_amount = amounts[0] if amounts else '$100K-1M'
        
        # Build prediction
        prediction = OpportunityPrediction(
            opportunity_type=outcome['opportunity_type'],
            title=f"{predicted_funder} {outcome['opportunity_type'].value.replace('_', ' ').title()}",
            description=f"Predicted {outcome['opportunity_type'].value} based on {rule_name}",
            predicted_funder=predicted_funder,
            estimated_amount=estimated_amount,
            confidence=outcome.get('probability', 0.5),
            expected_timeline=timeline,
            expected_date=expected_date,
            rationale=outcome.get('rationale', 'Based on historical patterns'),
            supporting_evidence=[event.get('title', 'Event analysis')],
            target_sectors=['AI', 'Technology', 'Innovation'],
            target_regions=['Africa']
        )
        
        # Enhance with funder profile if available
        if predicted_funder in self.funder_profiles:
            profile = self.funder_profiles[predicted_funder]
            prediction.key_requirements = profile.get('focus_areas', [])
            prediction.decision_makers = profile.get('key_decision_makers', [])
            prediction.application_process = f"Typical timeline: {profile.get('decision_timeline', 'Unknown')}"
        
        return prediction
    
    async def _apply_pattern_matching(self, events: List[Dict[str, Any]]) -> List[OpportunityPrediction]:
        """Apply historical pattern matching"""
        predictions = []
        
        # Group events by organization
        org_events = defaultdict(list)
        for event in events:
            entities = event.get('extracted_entities', {})
            for funder in entities.get('funders', []):
                org_events[funder].append(event)
        
        # Check each organization against patterns
        for org, org_event_list in org_events.items():
            org_lower = org.lower()
            
            # Check Google pattern
            if 'google' in org_lower:
                pattern_pred = await self._apply_google_pattern(org_event_list)
                if pattern_pred:
                    predictions.append(pattern_pred)
            
            # Check Microsoft pattern
            elif 'microsoft' in org_lower:
                pattern_pred = await self._apply_microsoft_pattern(org_event_list)
                if pattern_pred:
                    predictions.append(pattern_pred)
            
            # Check World Bank pattern
            elif 'world bank' in org_lower:
                pattern_pred = await self._apply_world_bank_pattern(org_event_list)
                if pattern_pred:
                    predictions.append(pattern_pred)
        
        return predictions
    
    async def _apply_google_pattern(self, events: List[Dict[str, Any]]) -> Optional[OpportunityPrediction]:
        """Apply Google-specific patterns"""
        if not events:
            return None
        
        pattern = self.pattern_library['google_africa_pattern']
        latest_event = max(events, key=lambda x: x.get('created_at', datetime.min))
        
        # Check if this matches the pattern
        if 'partnership' in latest_event.get('content', '').lower():
            return OpportunityPrediction(
                opportunity_type=OpportunityType.INNOVATION_CHALLENGE,
                title="Google AI for Africa Innovation Challenge",
                description="Predicted funding program based on Google's partnership announcement pattern",
                predicted_funder="Google",
                estimated_amount=pattern['typical_amounts'][0],
                confidence=pattern['historical_accuracy'],
                expected_timeline="short_term",
                expected_date=datetime.now() + timedelta(days=pattern['typical_timeline']),
                rationale=pattern['description'],
                supporting_evidence=[latest_event.get('title', 'Partnership announcement')],
                target_sectors=pattern['focus_areas'],
                target_regions=['Africa'],
                key_requirements=['AI focus', 'African presence', 'scalable solution'],
                decision_makers=['Head of AI', 'Country Director Africa'],
                success_factors=['Strong technical team', 'Clear social impact', 'Scalability plan']
            )
        
        return None
    
    async def _apply_microsoft_pattern(self, events: List[Dict[str, Any]]) -> Optional[OpportunityPrediction]:
        """Apply Microsoft-specific patterns"""
        if not events:
            return None
        
        pattern = self.pattern_library['microsoft_pattern']
        latest_event = max(events, key=lambda x: x.get('created_at', datetime.min))
        
        return OpportunityPrediction(
            opportunity_type=OpportunityType.FUNDING_PROGRAM,
            title="Microsoft AI for Good Africa Program",
            description="Predicted based on Microsoft's historical funding patterns",
            predicted_funder="Microsoft",
            estimated_amount=pattern['typical_amounts'][0],
            confidence=pattern['historical_accuracy'],
            expected_timeline="short_term",
            expected_date=datetime.now() + timedelta(days=pattern['typical_timeline']),
            rationale=pattern['description'],
            supporting_evidence=[latest_event.get('title', 'Microsoft announcement')],
            target_sectors=pattern['focus_areas'],
            target_regions=['Africa'],
            key_requirements=['AI for social good', 'measurable impact', 'sustainability'],
            decision_makers=['AI for Good Director', 'Regional Lead'],
            success_factors=['Clear social impact metrics', 'Technical excellence', 'Partnership potential']
        )
    
    async def _apply_world_bank_pattern(self, events: List[Dict[str, Any]]) -> Optional[OpportunityPrediction]:
        """Apply World Bank-specific patterns"""
        if not events:
            return None
        
        pattern = self.pattern_library['world_bank_pattern']
        latest_event = max(events, key=lambda x: x.get('created_at', datetime.min))
        
        return OpportunityPrediction(
            opportunity_type=OpportunityType.FUNDING_PROGRAM,
            title="World Bank Digital Development Initiative",
            description="Predicted large-scale funding based on World Bank patterns",
            predicted_funder="World Bank",
            estimated_amount=pattern['typical_amounts'][0],
            confidence=pattern['historical_accuracy'],
            expected_timeline="long_term",
            expected_date=datetime.now() + timedelta(days=pattern['typical_timeline']),
            rationale=pattern['description'],
            supporting_evidence=[latest_event.get('title', 'World Bank announcement')],
            target_sectors=pattern['focus_areas'],
            target_regions=['Africa'],
            key_requirements=['Government partnership', 'development impact', 'sustainability'],
            decision_makers=['Country Director', 'Sector Manager'],
            success_factors=['Strong government relations', 'Clear development outcomes', 'Risk mitigation']
        )
    
    def _deduplicate_predictions(self, predictions: List[OpportunityPrediction]) -> List[OpportunityPrediction]:
        """Remove duplicate predictions"""
        seen = set()
        unique_predictions = []
        
        for pred in predictions:
            key = (pred.predicted_funder, pred.opportunity_type, pred.estimated_amount)
            if key not in seen:
                seen.add(key)
                unique_predictions.append(pred)
        
        return unique_predictions
    
    async def estimate_funding_amount_from_context(self, context: str, 
                                                 funder: str, 
                                                 opportunity_type: OpportunityType) -> str:
        """Estimate funding amount based on context and funder profile"""
        
        # Check if amount is explicitly mentioned
        import re
        amount_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand|M|B|K)?',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|billion|thousand|USD|EUR|GBP)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Use funder profile defaults
        if funder in self.funder_profiles:
            profile = self.funder_profiles[funder]
            amounts = profile.get('typical_amounts', ['$100K-1M'])
            
            # Choose amount based on opportunity type
            if opportunity_type in [OpportunityType.FUNDING_PROGRAM, OpportunityType.RESEARCH_GRANT]:
                return amounts[-1] if len(amounts) > 2 else amounts[0]  # Larger amounts
            else:
                return amounts[0]  # Smaller amounts
        
        # Default estimate
        return '$100K-1M'
    
    def calculate_confidence_score(self, prediction: OpportunityPrediction, 
                                 supporting_events: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for a prediction"""
        base_confidence = 0.5
        
        # Increase confidence based on funder recognition
        if prediction.predicted_funder in self.funder_profiles:
            base_confidence += 0.2
        
        # Increase confidence based on multiple supporting events
        if len(supporting_events) > 1:
            base_confidence += 0.1 * min(len(supporting_events) - 1, 3)
        
        # Increase confidence based on explicit amounts
        if '$' in prediction.estimated_amount and 'million' in prediction.estimated_amount:
            base_confidence += 0.1
        
        # Increase confidence based on timeline immediacy
        if prediction.expected_timeline == "immediate":
            base_confidence += 0.1
        elif prediction.expected_timeline == "short_term":
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)


class SuccessStoryAnalyzer:
    """
    Reverse-engineer funding sources from success stories
    """
    
    async def analyze_success(self, content: str) -> Dict[str, Any]:
        """
        Analyze success story for funding insights
        """
        prompt = f"""
        Analyze this success story for funding insights:
        {content}

        Extract:
        1. How was this project/startup funded?
        2. What organizations provided support?
        3. What was the application process?
        4. Are there similar opportunities available?
        5. What can we learn about the funder's priorities?

        Even if not explicitly stated, infer funding sources from:
        - Mentioned partnerships
        - Acknowledged support
        - Program names
        - Event participation
        
        Return structured analysis including:
        - Funding sources discovered
        - Funding amounts (if mentioned)
        - Application processes
        - Success factors
        - Similar opportunities
        - Funder priorities
        """
        
        # TODO: Integrate with LLM service
        # For now, return mock analysis
        return await self._mock_success_analysis(content)
    
    async def _mock_success_analysis(self, content: str) -> Dict[str, Any]:
        """Mock success story analysis"""
        return {
            'funding_sources': ['Google', 'World Bank', 'Y Combinator'],
            'funding_amounts': ['$50K', '$2M', '$10M'],
            'application_processes': ['Online application', 'Pitch competition', 'Partnership approach'],
            'success_factors': ['Strong team', 'Clear market need', 'Scalable technology'],
            'similar_opportunities': ['Google AI for Africa', 'World Bank Innovation Labs'],
            'funder_priorities': ['AI for social good', 'Scalable impact', 'Local presence'],
            'confidence': 0.7
        }


class FundingResearchAgent:
    """
    Autonomous agent that investigates funding leads
    """
    
    async def investigate_lead(self, initial_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Investigate a funding lead in depth
        """
        research_trail = [initial_signal]
        
        # Step 1: Find related content
        related = await self._search_related_content(initial_signal)
        research_trail.extend(related)
        
        # Step 2: Identify key organizations
        orgs = self._extract_organizations(research_trail)
        
        # Step 3: Deep dive on each organization
        for org in orgs:
            # Check for funding history
            funding_history = await self._research_funding_history(org)
            research_trail.extend(funding_history)
            
            # Check social media signals
            social_signals = await self._check_social_signals(org)
            research_trail.extend(social_signals)
        
        # Step 4: Synthesize findings
        synthesis = await self._synthesize_research(research_trail)
        
        return {
            'initial_signal': initial_signal,
            'research_trail': research_trail,
            'organizations_investigated': orgs,
            'synthesis': synthesis,
            'confidence_score': self._calculate_confidence(synthesis),
            'actionable_insights': self._generate_actions(synthesis),
            'investigation_date': datetime.now().isoformat()
        }
    
    async def _search_related_content(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for related content"""
        # TODO: Implement actual search
        return []
    
    def _extract_organizations(self, research_trail: List[Dict[str, Any]]) -> List[str]:
        """Extract organizations from research trail"""
        orgs = set()
        for item in research_trail:
            entities = item.get('extracted_entities', {})
            orgs.update(entities.get('funders', []))
            orgs.update(entities.get('organizations', []))
        return list(orgs)
    
    async def _research_funding_history(self, org: str) -> List[Dict[str, Any]]:
        """Research funding history of an organization"""
        # TODO: Implement actual research
        return []
    
    async def _check_social_signals(self, org: str) -> List[Dict[str, Any]]:
        """Check social media for signals"""
        # TODO: Implement social media monitoring
        return []
    
    async def _synthesize_research(self, research_trail: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize research findings"""
        return {
            'key_findings': ['Finding 1', 'Finding 2'],
            'funding_probability': 0.7,
            'estimated_timeline': '90 days',
            'recommended_actions': ['Action 1', 'Action 2']
        }
    
    def _calculate_confidence(self, synthesis: Dict[str, Any]) -> float:
        """Calculate confidence in research findings"""
        return synthesis.get('funding_probability', 0.5)
    
    def _generate_actions(self, synthesis: Dict[str, Any]) -> List[str]:
        """Generate actionable insights"""
        return synthesis.get('recommended_actions', ['Monitor for updates'])