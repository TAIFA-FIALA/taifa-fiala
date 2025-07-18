"""
AI-Powered Content Analysis System for Funding Intelligence
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class FundingEventType(Enum):
    PARTNERSHIP_ANNOUNCEMENT = "partnership_announcement"
    STRATEGY_LAUNCH = "strategy_launch"
    PILOT_SUCCESS = "pilot_success"
    INVESTMENT_ROUND = "investment_round"
    CORPORATE_INITIATIVE = "corporate_initiative"
    CONFERENCE_ANNOUNCEMENT = "conference_announcement"
    SUCCESS_STORY = "success_story"
    GOVERNMENT_POLICY = "government_policy"
    RESEARCH_COLLABORATION = "research_collaboration"
    UNKNOWN = "unknown"


@dataclass
class FundingIntelligence:
    """Structured analysis of funding-related content"""
    has_funding_implications: bool
    confidence: float
    funding_type: str  # direct, indirect, potential
    timeline: str  # immediate, short_term, long_term
    entities: Dict[str, List[str]] = field(default_factory=dict)
    key_insights: str = ""
    suggested_actions: List[str] = field(default_factory=list)
    priority_score: int = 0
    event_type: FundingEventType = FundingEventType.UNKNOWN
    expected_funding_date: Optional[datetime] = None
    estimated_amount: Optional[str] = None
    rationale: str = ""


class FundingEventClassifier:
    """
    Classify any news item into funding lifecycle stages
    """
    
    EVENT_PATTERNS = {
        FundingEventType.PARTNERSHIP_ANNOUNCEMENT: {
            'patterns': ['partnership', 'collaboration', 'MOU signed', 'alliance', 'cooperation'],
            'funding_probability': 0.7,
            'typical_delay_days': 90
        },
        FundingEventType.STRATEGY_LAUNCH: {
            'patterns': ['AI strategy', 'national plan', 'roadmap', 'digital transformation', 'policy framework'],
            'funding_probability': 0.8,
            'typical_delay_days': 180
        },
        FundingEventType.PILOT_SUCCESS: {
            'patterns': ['pilot successful', 'proof of concept', 'scaled', 'pilot program', 'trial successful'],
            'funding_probability': 0.6,
            'typical_delay_days': 120
        },
        FundingEventType.INVESTMENT_ROUND: {
            'patterns': ['raises', 'funding round', 'investment', 'series A', 'venture capital'],
            'funding_probability': 0.9,
            'typical_delay_days': 30
        },
        FundingEventType.CORPORATE_INITIATIVE: {
            'patterns': ['CSR', 'corporate responsibility', 'initiative', 'program launch', 'foundation'],
            'funding_probability': 0.6,
            'typical_delay_days': 120
        },
        FundingEventType.CONFERENCE_ANNOUNCEMENT: {
            'patterns': ['conference', 'summit', 'symposium', 'workshop', 'event'],
            'funding_probability': 0.5,
            'typical_delay_days': 60
        }
    }
    
    async def classify_and_predict(self, content: str) -> FundingIntelligence:
        """
        Use AI to understand context beyond keywords
        """
        # First, try pattern matching for quick classification
        event_type = self._classify_by_patterns(content)
        
        # Then use LLM for deep analysis
        analysis = await self._llm_analysis(content, event_type)
        
        return analysis
    
    def _classify_by_patterns(self, content: str) -> FundingEventType:
        """Quick pattern-based classification"""
        content_lower = content.lower()
        
        for event_type, config in self.EVENT_PATTERNS.items():
            if any(pattern in content_lower for pattern in config['patterns']):
                return event_type
        
        return FundingEventType.UNKNOWN
    
    async def _llm_analysis(self, content: str, initial_event_type: FundingEventType) -> FundingIntelligence:
        """
        Deep LLM analysis of content
        """
        prompt = f"""
        Analyze this content for funding implications:
        {content}

        Initial classification: {initial_event_type.value}

        Extract:
        1. Event type and stage in funding lifecycle
        2. Organizations involved (funders and recipients)
        3. Explicit or implicit funding amounts
        4. Geographic focus
        5. Sector/domain focus
        6. Timeline indicators
        7. Future funding probability (0-1)
        8. Likely follow-up opportunities

        Look for:
        - Direct funding announcements (grants, investments, RFPs)
        - Indirect funding signals:
          * Partnerships that might lead to funding
          * New programs or initiatives being launched
          * Success stories that reveal funding sources
          * Organizations expanding into Africa
          * Government AI strategies or policies
          * Conference sponsorships
          * Pilot program results

        Key entities:
        - Who has money? (funders, sponsors, investors)
        - Who needs money? (startups, researchers, NGOs)
        - Who connects them? (accelerators, hubs, consultants)

        Timeline clues:
        - "Will launch" → future opportunity
        - "Recently partnered" → funding likely coming
        - "Successful pilot" → scale-up funding probable

        Money trails:
        - Any mention of amounts (even vague like "multi-million")
        - Budget allocations
        - Investment rounds
        - Program costs

        Return structured JSON with these fields:
        {{
            "has_funding_implications": boolean,
            "confidence": 0-1,
            "funding_type": "direct|indirect|potential",
            "timeline": "immediate|short_term|long_term",
            "entities": {{
                "funders": [],
                "recipients": [],
                "amounts": [],
                "programs": [],
                "locations": [],
                "people": []
            }},
            "key_insights": "What this might lead to",
            "suggested_actions": ["Follow up on X", "Monitor Y", "Research Z"],
            "priority_score": 0-100,
            "event_type": "{initial_event_type.value}",
            "estimated_amount": "amount if mentioned",
            "rationale": "Why this is funding-relevant"
        }}
        """
        
        # TODO: Integrate with your LLM service (OpenAI, Anthropic, etc.)
        # For now, return a mock response
        return await self._mock_llm_response(content, initial_event_type)
    
    async def _mock_llm_response(self, content: str, event_type: FundingEventType) -> FundingIntelligence:
        """Mock LLM response for development"""
        # Extract basic information
        has_funding = any(word in content.lower() for word in 
                         ['funding', 'investment', 'grant', 'million', 'partnership', 'program'])
        
        confidence = 0.7 if has_funding else 0.3
        
        return FundingIntelligence(
            has_funding_implications=has_funding,
            confidence=confidence,
            funding_type="indirect" if event_type != FundingEventType.INVESTMENT_ROUND else "direct",
            timeline="short_term",
            entities={
                "funders": ["TBD"],
                "recipients": ["TBD"],
                "amounts": [],
                "programs": []
            },
            key_insights="Requires further analysis",
            suggested_actions=["Monitor for follow-up", "Research organizations mentioned"],
            priority_score=int(confidence * 100),
            event_type=event_type,
            rationale="Contains funding-related keywords"
        )


class AIFundingIntelligence:
    """
    This is where the magic happens - AI understands context
    """
    
    def __init__(self):
        self.classifier = FundingEventClassifier()
    
    async def process_raw_content(self, content_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process content in batches for efficiency
        """
        enriched_content = []
        
        # Process in parallel batches
        batch_size = 10
        for i in range(0, len(content_batch), batch_size):
            batch = content_batch[i:i+batch_size]
            batch_results = await asyncio.gather(
                *[self.analyze_for_funding_relevance(content) for content in batch]
            )
            
            for content, analysis in zip(batch, batch_results):
                if analysis.has_funding_implications:
                    enriched_content.append({
                        'original': content,
                        'analysis': analysis,
                        'priority': analysis.priority_score,
                        'next_actions': analysis.suggested_actions,
                        'processed_at': datetime.now().isoformat()
                    })
        
        return enriched_content
    
    async def analyze_for_funding_relevance(self, content: Dict[str, Any]) -> FundingIntelligence:
        """
        Analyze content for ANY funding-related implications
        """
        text = content.get('text', '') or content.get('content', '') or content.get('description', '')
        
        if not text:
            return FundingIntelligence(
                has_funding_implications=False,
                confidence=0.0,
                funding_type="none",
                timeline="none",
                rationale="No text content found"
            )
        
        # Use the classifier to analyze
        analysis = await self.classifier.classify_and_predict(text)
        
        # Add estimated funding date based on timeline
        if analysis.timeline == "immediate":
            analysis.expected_funding_date = datetime.now() + timedelta(days=30)
        elif analysis.timeline == "short_term":
            analysis.expected_funding_date = datetime.now() + timedelta(days=90)
        elif analysis.timeline == "long_term":
            analysis.expected_funding_date = datetime.now() + timedelta(days=180)
        
        return analysis


class CrossContentIntelligence:
    """
    Find patterns across multiple pieces of content
    """
    
    async def find_funding_patterns(self, content_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find patterns across multiple pieces of content
        """
        from collections import defaultdict
        
        # Group by organizations
        org_mentions = defaultdict(list)
        
        for content in content_batch:
            analysis = content.get('analysis')
            if analysis and analysis.entities:
                for org in analysis.entities.get('funders', []):
                    org_mentions[org].append(content)
        
        # Look for patterns
        patterns = []
        for org, mentions in org_mentions.items():
            if len(mentions) > 2:  # Multiple mentions = something brewing
                pattern = await self.analyze_org_pattern(org, mentions)
                patterns.append(pattern)
        
        return patterns
    
    async def analyze_org_pattern(self, org: str, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze pattern for a specific organization
        """
        # Sort by date
        timeline = sorted(mentions, key=lambda x: x.get('date', datetime.now()))
        
        # TODO: Use LLM to analyze pattern
        # For now, return basic analysis
        return {
            'organization': org,
            'mentions_count': len(mentions),
            'timeline': [m.get('date', datetime.now()).isoformat() for m in timeline],
            'pattern_analysis': f"{org} mentioned {len(mentions)} times - potential funding activity",
            'confidence': 0.7,
            'suggested_actions': [
                f"Monitor {org} for announcements",
                f"Research {org}'s funding history",
                f"Set up alerts for {org} + AI + Africa"
            ]
        }


class IntelligentDeduplication:
    """
    Not just matching titles - understanding the story
    """
    
    async def deduplicate_with_intelligence(self, new_content: Dict[str, Any], 
                                          existing_db: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intelligent deduplication based on content understanding
        """
        # Find similar entries
        similar_entries = self._find_similar_entries(new_content, existing_db)
        
        if not similar_entries:
            return {
                "is_duplicate": False,
                "duplicate_of_id": None,
                "relationship": "none",
                "new_information": "Completely new content"
            }
        
        # Use LLM to analyze relationship
        return await self._llm_deduplication_analysis(new_content, similar_entries)
    
    def _find_similar_entries(self, new_content: Dict[str, Any], 
                            existing_db: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potentially similar entries using basic similarity
        """
        new_text = new_content.get('text', '').lower()
        similar = []
        
        for entry in existing_db:
            entry_text = entry.get('text', '').lower()
            # Simple similarity check - could be enhanced with embeddings
            common_words = set(new_text.split()) & set(entry_text.split())
            if len(common_words) > 5:  # Threshold for similarity
                similar.append(entry)
        
        return similar[:5]  # Return top 5 similar entries
    
    async def _llm_deduplication_analysis(self, new_content: Dict[str, Any], 
                                        similar_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use LLM to analyze content relationships
        """
        # TODO: Implement LLM analysis
        # For now, return basic analysis
        return {
            "is_duplicate": False,
            "duplicate_of_id": None,
            "relationship": "related",
            "new_information": "Contains new details not in existing entries"
        }