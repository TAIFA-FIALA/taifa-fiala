#!/usr/bin/env python3
"""
Intelligent Serper Search System
===============================

This system uses Serper strategically for targeted searches when:
1. New organizations are detected
2. Geographic/sector gaps are identified
3. Specific funding details are missing
4. Trend analysis reveals new intelligence_items

No more wasteful bulk searches - only intelligent, targeted queries.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SearchRequest:
    """Represents a targeted search request"""
    trigger: str  # 'new_org', 'missing_data', 'gap_analysis', 'trend_detection'
    search_type: str  # 'organization', 'deadline', 'amount', 'geographic', 'sector'
    query: str
    priority: str  # 'high', 'medium', 'low'
    context: Dict[str, Any]  # Additional context for the search
    expected_results: int  # Expected number of useful results

class IntelligentSerperSystem:
    """Smart Serper system that searches only when needed"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.supabase: Client = None
        self.session = None
        
        # Track what we've already searched to avoid duplicates
        self.searched_queries: Set[str] = set()
        
        # Search statistics
        self.searches_performed = 0
        self.useful_results_found = 0
        self.api_calls_saved = 0
        
    async def initialize(self):
        """Initialize the intelligent search system"""
        logger.info("🧠 Initializing Intelligent Serper System")
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()
        
        logger.info("✅ Intelligent Serper System initialized")
    
    async def detect_search_intelligence_items(self) -> List[SearchRequest]:
        """Analyze database to detect when targeted searches are needed"""
        search_requests = []
        
        # 1. Detect new organizations mentioned in RSS feeds
        new_org_requests = await self._detect_new_organizations()
        search_requests.extend(new_org_requests)
        
        # 2. Find intelligence_items missing critical data
        missing_data_requests = await self._detect_missing_data()
        search_requests.extend(missing_data_requests)
        
        # 3. Identify geographic gaps
        geographic_requests = await self._detect_geographic_gaps()
        search_requests.extend(geographic_requests)
        
        # 4. Identify sector gaps
        sector_requests = await self._detect_sector_gaps()
        search_requests.extend(sector_requests)
        
        # 5. Trend-based searches (new funding patterns)
        trend_requests = await self._detect_trending_intelligence_items()
        search_requests.extend(trend_requests)
        
        # Filter out duplicates and prioritize
        unique_requests = self._deduplicate_and_prioritize(search_requests)
        
        logger.info(f"🎯 Detected {len(unique_requests)} intelligent search intelligence_items")
        return unique_requests
    
    async def _detect_new_organizations(self) -> List[SearchRequest]:
        """Detect new organizations mentioned in RSS feeds that need funding program searches"""
        requests = []
        
        try:
            # Get recent intelligence_items mentioning organization names
            recent_intelligence_items = self.supabase.table('africa_intelligence_feed').select(
                'id,title,description,additional_notes,created_at'
            ).gte('created_at', (datetime.now() - timedelta(days=7)).isoformat()).execute()
            
            if not recent_intelligence_items.data:
                return requests
            
            # Extract organization names from content
            org_keywords = [
                'foundation', 'institute', 'university', 'bank', 'fund', 'agency',
                'organization', 'centre', 'center', 'council', 'association'
            ]
            
            detected_orgs = set()
            
            for opp in recent_intelligence_items.data:
                text = f"{opp.get('title', '')} {opp.get('description', '')} {opp.get('additional_notes', '')}"
                
                # Simple organization detection
                words = text.split()
                for i, word in enumerate(words):
                    if any(keyword in word.lower() for keyword in org_keywords):
                        # Extract potential organization name (2-3 words around keyword)
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        org_name = ' '.join(words[start:end])
                        
                        if len(org_name) > 10 and len(org_name) < 100:
                            detected_orgs.add(org_name.strip())
            
            # Create search requests for detected organizations
            for org_name in list(detected_orgs)[:5]:  # Limit to 5 most recent
                requests.append(SearchRequest(
                    trigger='new_org',
                    search_type='organization',
                    query=f'"{org_name}" AND (funding OR grants OR program) AND Africa AND AI',
                    priority='high',
                    context={'organization_name': org_name},
                    expected_results=3
                ))
            
            logger.info(f"🏢 Detected {len(requests)} new organizations for funding searches")
            
        except Exception as e:
            logger.error(f"❌ Error detecting new organizations: {e}")
        
        return requests
    
    async def _detect_missing_data(self) -> List[SearchRequest]:
        """Detect intelligence_items with missing critical data"""
        requests = []
        
        try:
            # Get intelligence_items missing key fields
            incomplete_intelligence_items = self.supabase.table('africa_intelligence_feed').select(
                'id,title,source_url,funding_amount,application_deadline,eligibility_criteria'
            ).is_('funding_amount', 'null').limit(10).execute()
            
            if not incomplete_intelligence_items.data:
                return requests
            
            for opp in incomplete_intelligence_items.data:
                # Search for missing funding amount
                if not opp.get('funding_amount'):
                    requests.append(SearchRequest(
                        trigger='missing_data',
                        search_type='amount',
                        query=f'"{opp["title"]}" AND (amount OR funding OR grant OR prize) AND (USD OR dollar OR euro)',
                        priority='medium',
                        context={'opportunity_id': opp['id'], 'missing_field': 'funding_amount'},
                        expected_results=2
                    ))
                
                # Search for missing deadline
                if not opp.get('application_deadline'):
                    requests.append(SearchRequest(
                        trigger='missing_data',
                        search_type='deadline',
                        query=f'"{opp["title"]}" AND (deadline OR "closing date" OR "application due" OR "submit by")',
                        priority='medium',
                        context={'opportunity_id': opp['id'], 'missing_field': 'application_deadline'},
                        expected_results=2
                    ))
            
            logger.info(f"📋 Detected {len(requests)} intelligence_items with missing data")
            
        except Exception as e:
            logger.error(f"❌ Error detecting missing data: {e}")
        
        return requests
    
    async def _detect_geographic_gaps(self) -> List[SearchRequest]:
        """Identify underrepresented countries/regions"""
        requests = []
        
        try:
            # Target countries with high AI potential but low funding representation
            underrepresented_countries = [
                'Rwanda', 'Ghana', 'Botswana', 'Tanzania', 'Uganda', 'Zambia',
                'Senegal', 'Ivory Coast', 'Madagascar', 'Cameroon'
            ]
            
            for country in underrepresented_countries[:3]:  # Limit to 3 per run
                requests.append(SearchRequest(
                    trigger='gap_analysis',
                    search_type='geographic',
                    query=f'{country} AND AI AND (funding OR grants OR program OR accelerator OR startup)',
                    priority='low',
                    context={'country': country, 'gap_type': 'geographic'},
                    expected_results=5
                ))
            
            logger.info(f"🌍 Detected {len(requests)} geographic gap searches")
            
        except Exception as e:
            logger.error(f"❌ Error detecting geographic gaps: {e}")
        
        return requests
    
    async def _detect_sector_gaps(self) -> List[SearchRequest]:
        """Identify underrepresented AI sectors"""
        requests = []
        
        try:
            # Focus on high-impact sectors with limited coverage
            underrepresented_sectors = [
                ('climate', 'climate change OR environmental OR sustainability'),
                ('governance', 'governance OR transparency OR democracy'),
                ('disaster', 'disaster response OR emergency OR humanitarian'),
                ('energy', 'energy OR power OR electricity OR renewable'),
                ('transport', 'transport OR logistics OR mobility OR smart cities')
            ]
            
            for sector_name, sector_query in underrepresented_sectors[:2]:  # Limit to 2 per run
                requests.append(SearchRequest(
                    trigger='gap_analysis',
                    search_type='sector',
                    query=f'Africa AND AI AND ({sector_query}) AND (funding OR grants OR program)',
                    priority='low',
                    context={'sector': sector_name, 'gap_type': 'sector'},
                    expected_results=4
                ))
            
            logger.info(f"🏭 Detected {len(requests)} sector gap searches")
            
        except Exception as e:
            logger.error(f"❌ Error detecting sector gaps: {e}")
        
        return requests
    
    async def _detect_trending_intelligence_items(self) -> List[SearchRequest]:
        """Detect trending funding patterns or new programs"""
        requests = []
        
        try:
            # Search for very recent funding announcements
            current_year = datetime.now().year
            
            trending_searches = [
                f'{current_year} AND "new funding" AND AI AND Africa',
                f'{current_year} AND "launches" AND (funding OR grant OR program) AND Africa AND AI',
                f'"just announced" AND funding AND AI AND Africa'
            ]
            
            for query in trending_searches:
                requests.append(SearchRequest(
                    trigger='trend_detection',
                    search_type='trending',
                    query=query,
                    priority='high',
                    context={'trend_type': 'new_programs'},
                    expected_results=3
                ))
            
            logger.info(f"📈 Detected {len(requests)} trending opportunity searches")
            
        except Exception as e:
            logger.error(f"❌ Error detecting trending intelligence_items: {e}")
        
        return requests
    
    def _deduplicate_and_prioritize(self, requests: List[SearchRequest]) -> List[SearchRequest]:
        """Remove duplicates and prioritize searches"""
        
        # Remove duplicates based on query
        unique_requests = []
        seen_queries = set()
        
        for request in requests:
            if request.query not in seen_queries and request.query not in self.searched_queries:
                unique_requests.append(request)
                seen_queries.add(request.query)
        
        # Sort by priority (high -> medium -> low)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        unique_requests.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        # Limit total searches to avoid API quota issues
        limited_requests = unique_requests[:8]  # Max 8 searches per run
        
        # Calculate saved API calls
        self.api_calls_saved += len(requests) - len(limited_requests)
        
        return limited_requests
    
    async def perform_intelligent_search(self, request: SearchRequest) -> Dict[str, Any]:
        """Perform a targeted search based on the request"""
        logger.info(f"🎯 Performing {request.search_type} search: {request.query}")
        
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': request.query,
                'num': request.expected_results + 2,  # Get a few extra for filtering
                'hl': 'en',
                'gl': 'us'
            }
            
            async with self.session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Mark query as searched
                    self.searched_queries.add(request.query)
                    self.searches_performed += 1
                    
                    # Process results based on search type
                    processed_results = await self._process_search_results(data, request)
                    
                    return {
                        'success': True,
                        'results': processed_results,
                        'search_request': request,
                        'api_response': data
                    }
                else:
                    logger.error(f"❌ Serper API error: {response.status}")
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"❌ Error in targeted search: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _process_search_results(self, data: Dict[str, Any], request: SearchRequest) -> List[Dict[str, Any]]:
        """Process search results based on the search type"""
        processed_results = []
        
        organic_results = data.get('organic', [])
        
        for result in organic_results:
            # Basic filtering
            if self._is_relevant_result(result, request):
                processed_result = {
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'search_type': request.search_type,
                    'trigger': request.trigger,
                    'context': request.context,
                    'relevance_score': self._calculate_relevance_score(result, request)
                }
                processed_results.append(processed_result)
        
        # Sort by relevance score
        processed_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Limit to expected results
        limited_results = processed_results[:request.expected_results]
        
        if limited_results:
            self.useful_results_found += len(limited_results)
            
        return limited_results
    
    def _is_relevant_result(self, result: Dict[str, Any], request: SearchRequest) -> bool:
        """Check if a search result is relevant to the request"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        text = f"{title} {snippet}"
        
        # Basic relevance filtering
        if 'funding' not in text and 'grant' not in text and 'program' not in text:
            return False
        
        # Check for AI relevance
        if 'ai' not in text and 'artificial' not in text and 'machine learning' not in text:
            return False
        
        # Check for Africa relevance
        if 'africa' not in text and 'african' not in text:
            # Check for specific countries
            african_countries = ['nigeria', 'kenya', 'south africa', 'ghana', 'rwanda', 'uganda']
            if not any(country in text for country in african_countries):
                return False
        
        return True
    
    def _calculate_relevance_score(self, result: Dict[str, Any], request: SearchRequest) -> float:
        """Calculate relevance score for a search result"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        text = f"{title} {snippet}"
        
        score = 0.0
        
        # Basic relevance keywords
        if 'funding' in text: score += 0.3
        if 'grant' in text: score += 0.3
        if 'program' in text: score += 0.2
        if 'ai' in text: score += 0.3
        if 'africa' in text: score += 0.3
        
        # Context-specific scoring
        if request.search_type == 'organization':
            org_name = request.context.get('organization_name', '').lower()
            if org_name in text:
                score += 0.4
        
        elif request.search_type == 'amount':
            if any(term in text for term in ['$', 'usd', 'million', 'amount', 'funding']):
                score += 0.3
        
        elif request.search_type == 'deadline':
            if any(term in text for term in ['deadline', 'closing', 'application', 'due']):
                score += 0.3
        
        return min(score, 1.0)
    
    async def run_intelligent_search_cycle(self) -> Dict[str, Any]:
        """Run one cycle of intelligent searches"""
        logger.info("🧠 Starting intelligent search cycle")
        
        # Detect search intelligence_items
        search_requests = await self.detect_search_intelligence_items()
        
        if not search_requests:
            logger.info("💤 No intelligent search intelligence_items detected")
            return {
                'searches_performed': 0,
                'results_found': 0,
                'api_calls_saved': self.api_calls_saved
            }
        
        # Perform searches
        all_results = []
        
        for request in search_requests:
            result = await self.perform_intelligent_search(request)
            
            if result['success']:
                all_results.extend(result['results'])
                
                # Queue results for scraping if they need detailed information
                await self._queue_results_for_scraping(result['results'])
            
            # Small delay between searches
            await asyncio.sleep(1)
        
        # Summary
        cycle_summary = {
            'searches_performed': self.searches_performed,
            'results_found': len(all_results),
            'api_calls_saved': self.api_calls_saved,
            'efficiency_gain': f"{self.api_calls_saved / max(self.searches_performed, 1) * 100:.1f}%"
        }
        
        logger.info(f"📊 Intelligent search cycle completed: {cycle_summary}")
        return cycle_summary
    
    async def _queue_results_for_scraping(self, results: List[Dict[str, Any]]):
        """Queue high-value search results for detailed scraping"""
        from scraping_queue_processor import ScrapeQueueManager
        
        queue_manager = ScrapeQueueManager()
        await queue_manager.initialize()
        
        for result in results:
            if result['relevance_score'] > 0.7:  # High relevance threshold
                await queue_manager.queue_scrape_request(
                    url=result['link'],
                    requested_fields=['title', 'description', 'amount', 'deadline', 'eligibility_criteria'],
                    priority='high' if result['relevance_score'] > 0.8 else 'medium',
                    source_context=f"Intelligent search result: {result['title']}"
                )
    
    async def close(self):
        """Close the search system"""
        if self.session:
            await self.session.close()
        logger.info("🔒 Intelligent Serper System closed")

async def main():
    """Test the intelligent search system"""
    api_key = os.getenv('SERPER_DEV_API_KEY')
    
    if not api_key:
        logger.error("❌ SERPER_DEV_API_KEY not found")
        return
    
    search_system = IntelligentSerperSystem(api_key)
    await search_system.initialize()
    
    # Run one intelligent search cycle
    summary = await search_system.run_intelligent_search_cycle()
    
    logger.info(f"🎉 Test completed: {summary}")
    
    await search_system.close()

if __name__ == "__main__":
    asyncio.run(main())