"""
Enhanced Search Strategy for AI-Powered Funding Intelligence Pipeline
Based on the Notion note: "Where to go from here? AI-Powered Funding Intelligence Pipeline"
"""

from typing import List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


class SearchType(Enum):
    DIRECT_FUNDING = "direct_funding"
    INDIRECT_SIGNALS = "indirect_signals"
    SUCCESS_TRACKING = "success_tracking"
    PARTNERSHIP_ANNOUNCEMENTS = "partnership_announcements"
    STRATEGY_LAUNCHES = "strategy_launches"
    CORPORATE_INITIATIVES = "corporate_initiatives"
    CONFERENCE_INTELLIGENCE = "conference_intelligence"


@dataclass
class SearchQuery:
    query: str
    search_type: SearchType
    priority: int = 1
    expected_delay_days: int = 0
    funding_probability: float = 0.5


class EnhancedSearchStrategy:
    """
    Cast a wide net with intelligent search queries covering the full funding lifecycle
    """
    
    def __init__(self):
        self.intelligent_search_queries = self._build_query_library()
    
    def _build_query_library(self) -> Dict[SearchType, List[SearchQuery]]:
        """Build comprehensive search query library"""
        return {
            SearchType.DIRECT_FUNDING: [
                SearchQuery("AI Africa investment million", SearchType.DIRECT_FUNDING, 1, 30, 0.9),
                SearchQuery("artificial intelligence Africa funding", SearchType.DIRECT_FUNDING, 1, 30, 0.9),
                SearchQuery("AI startup Africa raises", SearchType.DIRECT_FUNDING, 1, 30, 0.9),
                SearchQuery("Africa AI grant program", SearchType.DIRECT_FUNDING, 1, 30, 0.9),
                SearchQuery("AI research collaboration Africa", SearchType.DIRECT_FUNDING, 1, 30, 0.8),
                SearchQuery("Africa digital transformation fund", SearchType.DIRECT_FUNDING, 1, 30, 0.8),
                SearchQuery("machine learning Africa funding", SearchType.DIRECT_FUNDING, 1, 30, 0.8),
                SearchQuery("AI innovation challenge Africa", SearchType.DIRECT_FUNDING, 1, 30, 0.8),
            ],
            
            SearchType.INDIRECT_SIGNALS: [
                SearchQuery("AI conference Africa 2024 2025", SearchType.INDIRECT_SIGNALS, 2, 120, 0.6),
                SearchQuery("Africa AI summit sponsors", SearchType.INDIRECT_SIGNALS, 2, 120, 0.6),
                SearchQuery("Microsoft Google Meta AI Africa", SearchType.INDIRECT_SIGNALS, 2, 90, 0.7),
                SearchQuery("World Bank AI Africa project", SearchType.INDIRECT_SIGNALS, 2, 180, 0.8),
                SearchQuery("AI pilot program Africa success", SearchType.INDIRECT_SIGNALS, 2, 120, 0.6),
                SearchQuery("Africa AI partnership announcement", SearchType.INDIRECT_SIGNALS, 2, 90, 0.7),
                SearchQuery("AI strategy launch Africa", SearchType.INDIRECT_SIGNALS, 2, 180, 0.8),
            ],
            
            SearchType.SUCCESS_TRACKING: [
                SearchQuery("African AI startup wins", SearchType.SUCCESS_TRACKING, 3, 0, 0.4),
                SearchQuery("AI competition winner Africa", SearchType.SUCCESS_TRACKING, 3, 0, 0.4),
                SearchQuery("Africa AI accelerator cohort", SearchType.SUCCESS_TRACKING, 3, 0, 0.4),
                SearchQuery("AI startup Africa funding success", SearchType.SUCCESS_TRACKING, 3, 0, 0.5),
                SearchQuery("Africa AI research breakthrough", SearchType.SUCCESS_TRACKING, 3, 0, 0.3),
            ],
            
            SearchType.PARTNERSHIP_ANNOUNCEMENTS: [
                SearchQuery("AI partnership Africa announced", SearchType.PARTNERSHIP_ANNOUNCEMENTS, 2, 90, 0.7),
                SearchQuery("MOU signed AI Africa", SearchType.PARTNERSHIP_ANNOUNCEMENTS, 2, 90, 0.7),
                SearchQuery("collaboration agreement AI Africa", SearchType.PARTNERSHIP_ANNOUNCEMENTS, 2, 90, 0.7),
                SearchQuery("joint venture AI Africa", SearchType.PARTNERSHIP_ANNOUNCEMENTS, 2, 90, 0.7),
            ],
            
            SearchType.STRATEGY_LAUNCHES: [
                SearchQuery("national AI strategy Africa", SearchType.STRATEGY_LAUNCHES, 1, 180, 0.8),
                SearchQuery("AI roadmap Africa country", SearchType.STRATEGY_LAUNCHES, 1, 180, 0.8),
                SearchQuery("government AI plan Africa", SearchType.STRATEGY_LAUNCHES, 1, 180, 0.8),
                SearchQuery("AI policy framework Africa", SearchType.STRATEGY_LAUNCHES, 1, 180, 0.8),
            ],
            
            SearchType.CORPORATE_INITIATIVES: [
                SearchQuery("corporate AI initiative Africa", SearchType.CORPORATE_INITIATIVES, 2, 120, 0.6),
                SearchQuery("CSR AI program Africa", SearchType.CORPORATE_INITIATIVES, 2, 120, 0.6),
                SearchQuery("tech giant AI Africa investment", SearchType.CORPORATE_INITIATIVES, 2, 90, 0.7),
                SearchQuery("multinational AI Africa program", SearchType.CORPORATE_INITIATIVES, 2, 120, 0.6),
            ],
            
            SearchType.CONFERENCE_INTELLIGENCE: [
                SearchQuery("AI conference Africa speakers", SearchType.CONFERENCE_INTELLIGENCE, 3, 60, 0.5),
                SearchQuery("Africa tech summit AI track", SearchType.CONFERENCE_INTELLIGENCE, 3, 60, 0.5),
                SearchQuery("AI workshop Africa program", SearchType.CONFERENCE_INTELLIGENCE, 3, 60, 0.5),
                SearchQuery("Africa AI event sponsors", SearchType.CONFERENCE_INTELLIGENCE, 3, 60, 0.5),
            ]
        }
    
    def get_base_search_queries(self) -> List[str]:
        """Simple, broad queries for initial content gathering"""
        return [
            '("AI" OR "Artificial Intelligence") AND ("Africa" OR "African")',
            '("Machine Learning" OR "ML") AND ("Africa" OR "African")',
            '("Data Science") AND ("Africa" OR "African")',
            'AI Africa',
            'Artificial Intelligence Africa',
            'Machine Learning Africa',
            'Data Science Africa'
        ]
    
    def get_targeted_queries(self, search_type: SearchType = None) -> List[SearchQuery]:
        """Get targeted queries for specific search types"""
        if search_type:
            return self.intelligent_search_queries.get(search_type, [])
        
        # Return all queries if no specific type requested
        all_queries = []
        for queries in self.intelligent_search_queries.values():
            all_queries.extend(queries)
        return all_queries
    
    def get_high_priority_queries(self) -> List[SearchQuery]:
        """Get only high priority queries (priority 1)"""
        high_priority = []
        for queries in self.intelligent_search_queries.values():
            high_priority.extend([q for q in queries if q.priority == 1])
        return high_priority
    
    def get_queries_by_funding_probability(self, min_probability: float = 0.7) -> List[SearchQuery]:
        """Get queries with high funding probability"""
        high_prob_queries = []
        for queries in self.intelligent_search_queries.values():
            high_prob_queries.extend([q for q in queries if q.funding_probability >= min_probability])
        return high_prob_queries
    
    def get_query_context(self, query: str) -> Dict[str, Any]:
        """Get context information for a query"""
        for search_type, queries in self.intelligent_search_queries.items():
            for q in queries:
                if q.query == query:
                    return {
                        'search_type': search_type.value,
                        'priority': q.priority,
                        'expected_delay_days': q.expected_delay_days,
                        'funding_probability': q.funding_probability,
                        'description': self._get_search_type_description(search_type)
                    }
        return {}
    
    def _get_search_type_description(self, search_type: SearchType) -> str:
        """Get description for search type"""
        descriptions = {
            SearchType.DIRECT_FUNDING: "Direct funding announcements and opportunities",
            SearchType.INDIRECT_SIGNALS: "Indirect signals that may lead to funding",
            SearchType.SUCCESS_TRACKING: "Success stories that reveal funding sources",
            SearchType.PARTNERSHIP_ANNOUNCEMENTS: "Partnership announcements that typically lead to funding",
            SearchType.STRATEGY_LAUNCHES: "Government and organizational strategy launches",
            SearchType.CORPORATE_INITIATIVES: "Corporate CSR and initiative programs",
            SearchType.CONFERENCE_INTELLIGENCE: "Conference and event-based intelligence"
        }
        return descriptions.get(search_type, "Unknown search type")


class WideNetSearchModule:
    """
    Dead simple searching - cast a wide net, let AI do the heavy lifting
    """
    
    def __init__(self):
        self.search_strategy = EnhancedSearchStrategy()
        self.sources = ['news', 'blogs', 'announcements', 'social', 'academic', 'government']
    
    async def cast_net(self, search_mode: str = "comprehensive") -> Dict[str, Any]:
        """
        Cast a wide net and gather all relevant content
        
        Args:
            search_mode: 'simple', 'targeted', 'comprehensive'
        """
        all_content = []
        
        if search_mode == "simple":
            queries = self.search_strategy.get_base_search_queries()
            search_queries = [SearchQuery(q, SearchType.DIRECT_FUNDING) for q in queries]
        elif search_mode == "targeted":
            search_queries = self.search_strategy.get_high_priority_queries()
        else:  # comprehensive
            search_queries = self.search_strategy.get_targeted_queries()
        
        for query in search_queries:
            for source in self.sources:
                # This would integrate with your existing search modules
                # (SerperSearch, RSS feeds, etc.)
                results = await self._search_source(query.query, source)
                
                # Add query context to each result
                for result in results:
                    result['query_context'] = self.search_strategy.get_query_context(query.query)
                    result['search_type'] = query.search_type.value
                    result['funding_probability'] = query.funding_probability
                    result['expected_delay_days'] = query.expected_delay_days
                
                all_content.extend(results)
        
        return {
            'total_results': len(all_content),
            'content': all_content,
            'search_mode': search_mode,
            'sources_searched': self.sources,
            'queries_used': len(search_queries)
        }
    
    async def _search_source(self, query: str, source: str) -> List[Dict[str, Any]]:
        """
        Placeholder for actual search implementation
        This would integrate with your existing search modules
        """
        # TODO: Integrate with existing SerperSearch, RSS feeds, etc.
        return []