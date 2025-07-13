import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SerperSearchCollector:
    """Collects funding opportunities using Serper Google Search API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.session = None
        
        # Comprehensive search queries for maximum funding discovery
        self.search_queries = [
            # === CORE AI FUNDING SEARCHES ===
            {
                "name": "AI Africa Research Funding",
                "query": "(funding OR grants OR scholarships) AND (AI OR \"artificial intelligence\" OR \"machine learning\") AND Africa AND (research OR academic)",
                "priority": "high"
            },
            {
                "name": "AI Africa Implementation Funding", 
                "query": "(funding OR grants OR prizes) AND (AI OR \"artificial intelligence\") AND Africa AND (implementation OR deployment OR innovation)",
                "priority": "high"
            },
            {
                "name": "African AI Development Programs",
                "query": "Africa AND (\"AI development\" OR \"AI4D\" OR \"artificial intelligence development\") AND (funding OR grants OR program)",
                "priority": "high"
            },
            
            # === SECTOR-SPECIFIC AI FUNDING ===
            {
                "name": "Africa Health AI Funding",
                "query": "(health OR healthcare OR medical) AND AI AND Africa AND (funding OR grants OR innovation)",
                "priority": "high"
            },
            {
                "name": "Africa Agriculture AI Funding",
                "query": "(agriculture OR farming OR food security) AND AI AND Africa AND (funding OR grants)",
                "priority": "high"
            },
            {
                "name": "Africa Education AI Funding",
                "query": "(education OR learning OR training) AND AI AND Africa AND (funding OR grants OR program)",
                "priority": "medium"
            },
            {
                "name": "Africa Fintech AI Funding",
                "query": "(fintech OR financial OR banking) AND AI AND Africa AND (funding OR grants OR investment)",
                "priority": "medium"
            },
            
            # === ORGANIZATION-SPECIFIC SEARCHES ===
            {
                "name": "Gates Foundation AI Africa",
                "query": "\"Gates Foundation\" AND AI AND Africa AND (funding OR grants OR program OR initiative)",
                "priority": "high"
            },
            {
                "name": "World Bank AI Africa",
                "query": "\"World Bank\" AND AI AND Africa AND (funding OR grants OR program OR digital)",
                "priority": "high"
            },
            {
                "name": "USAID AI Africa",
                "query": "USAID AND AI AND Africa AND (funding OR grants OR program OR digital)",
                "priority": "medium"
            },
            {
                "name": "Google AI Africa",
                "query": "Google AND (\"AI for Good\" OR \"AI for Everyone\") AND Africa AND (funding OR grants OR program)",
                "priority": "medium"
            },
            {
                "name": "Microsoft AI Africa",
                "query": "Microsoft AND \"AI for Good\" AND Africa AND (funding OR grants OR program)",
                "priority": "medium"
            },
            
            # === COUNTRY-SPECIFIC SEARCHES ===
            {
                "name": "Nigeria AI Funding",
                "query": "Nigeria AND AI AND (funding OR grants OR investment OR accelerator OR startup)",
                "priority": "medium"
            },
            {
                "name": "Kenya AI Funding", 
                "query": "Kenya AND AI AND (funding OR grants OR investment OR accelerator OR startup)",
                "priority": "medium"
            },
            {
                "name": "South Africa AI Funding",
                "query": "\"South Africa\" AND AI AND (funding OR grants OR investment OR accelerator)",
                "priority": "medium"
            },
            {
                "name": "Ghana AI Funding",
                "query": "Ghana AND AI AND (funding OR grants OR investment OR accelerator OR startup)",
                "priority": "low"
            },
            
            # === STARTUP & INNOVATION FUNDING ===
            {
                "name": "African AI Startup Funding",
                "query": "(startup OR entrepreneur) AND AI AND Africa AND (funding OR investment OR accelerator OR incubator)",
                "priority": "medium"
            },
            {
                "name": "African AI Innovation Prizes",
                "query": "Africa AND AI AND (prize OR competition OR challenge OR award) AND (innovation OR technology)",
                "priority": "medium"
            },
            
            # === RECENT ANNOUNCEMENTS ===
            {
                "name": "Recent AI Africa Funding 2025",
                "query": "AI AND Africa AND funding AND (2025 OR \"this year\" OR recent OR announced)",
                "priority": "high"
            },
            {
                "name": "New AI Africa Programs",
                "query": "Africa AND AI AND (\"new program\" OR \"announces\" OR \"launches\" OR \"opens\") AND funding",
                "priority": "high"
            },
            
            # === ACADEMIC & RESEARCH FUNDING ===
            {
                "name": "Africa AI PhD Scholarships",
                "query": "Africa AND AI AND (PhD OR doctorate OR scholarship OR fellowship OR research)",
                "priority": "low"
            },
            {
                "name": "Africa AI Research Grants",
                "query": "Africa AND \"artificial intelligence\" AND (\"research grant\" OR \"research funding\" OR \"R&D funding\")",
                "priority": "medium"
            }
        ]
    
    async def start_collection(self):
        """Start the Serper search collection process"""
        logger.info("🔍 Starting Serper search collection for AI Africa funding")
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            all_opportunities = []
            
            for query_config in self.search_queries:
                logger.info(f"Searching: {query_config['name']}")
                
                opportunities = await self._search_funding_opportunities(query_config)
                all_opportunities.extend(opportunities)
                
                # Rate limiting - be respectful to the API
                await asyncio.sleep(2)
            
            # Remove duplicates and process results
            unique_opportunities = self._deduplicate_opportunities(all_opportunities)
            processed_opportunities = await self._process_opportunities(unique_opportunities)
            
            logger.info(f"✅ Serper search completed: {len(processed_opportunities)} unique opportunities found")
            return processed_opportunities
            
        finally:
            if self.session:
                await self.session.close()
    
    async def _search_funding_opportunities(self, query_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Execute a single search query with alternating locations"""
        
        # Alternate between London and New York based on day of year
        from datetime import datetime
        day_of_year = datetime.now().timetuple().tm_yday
        
        if day_of_year % 2 == 1:  # Odd days = London
            location = "London, England, United Kingdom"
            gl_code = "gb"
            location_name = "London"
        else:  # Even days = New York
            location = "New York, NY, United States"
            gl_code = "us"
            location_name = "New York"
        
        logger.info(f"🌍 Searching from {location_name} (day {day_of_year})")
        
        payload = {
            "q": query_config["query"],
            "location": location,
            "gl": gl_code,
            "num": 30,
            "type": "search"
        }
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            async with self.session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data, query_config)
                else:
                    logger.error(f"Serper API error {response.status} for query: {query_config['name']}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching '{query_config['name']}': {e}")
            return []
    
    def _parse_search_results(self, data: Dict[str, Any], query_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Serper search results into funding opportunities"""
        opportunities = []
        
        # Parse organic results
        organic_results = data.get("organic", [])
        
        for result in organic_results:
            # Filter for relevant results
            if self._is_funding_relevant(result):
                opportunity = {
                    "title": result.get("title", ""),
                    "description": result.get("snippet", ""),
                    "source_url": result.get("link", ""),
                    "search_query": query_config["name"],
                    "priority": query_config["priority"],
                    "discovered_date": datetime.utcnow().isoformat(),
                    "source_type": "serper_search",
                    "raw_data": json.dumps(result),
                    
                    # Generate a unique ID for deduplication
                    "content_hash": self._generate_content_hash(result.get("title", "") + result.get("link", "")),
                    
                    # Classification scores
                    "ai_relevance_score": self._calculate_ai_relevance(result),
                    "africa_relevance_score": self._calculate_africa_relevance(result),
                    "funding_relevance_score": self._calculate_funding_relevance(result)
                }
                
                opportunities.append(opportunity)
        
        # Parse knowledge graph results if available
        knowledge_graph = data.get("knowledgeGraph", {})
        if knowledge_graph and self._is_funding_relevant(knowledge_graph):
            opportunity = {
                "title": knowledge_graph.get("title", ""),
                "description": knowledge_graph.get("description", ""),
                "source_url": knowledge_graph.get("website", ""),
                "search_query": query_config["name"],
                "priority": query_config["priority"],
                "discovered_date": datetime.utcnow().isoformat(),
                "source_type": "serper_knowledge_graph",
                "raw_data": json.dumps(knowledge_graph),
                "content_hash": self._generate_content_hash(knowledge_graph.get("title", "") + knowledge_graph.get("website", "")),
                "ai_relevance_score": self._calculate_ai_relevance(knowledge_graph),
                "africa_relevance_score": self._calculate_africa_relevance(knowledge_graph),
                "funding_relevance_score": self._calculate_funding_relevance(knowledge_graph)
            }
            opportunities.append(opportunity)
        
        logger.info(f"Found {len(opportunities)} opportunities for query: {query_config['name']}")
        return opportunities
    
    def _is_funding_relevant(self, result: Dict[str, Any]) -> bool:
        """Check if a search result is funding-relevant"""
        text = (result.get("title", "") + " " + result.get("snippet", "") + " " + result.get("description", "")).lower()
        
        # Must contain funding-related keywords
        funding_keywords = ["funding", "grant", "grants", "scholarship", "prize", "award", "investment", "accelerator", "incubator", "call", "opportunity"]
        has_funding = any(keyword in text for keyword in funding_keywords)
        
        # Must contain AI-related keywords
        ai_keywords = ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural", "algorithm", "automation"]
        has_ai = any(keyword in text for keyword in ai_keywords)
        
        # Must contain Africa-related keywords
        africa_keywords = ["africa", "african", "nigeria", "kenya", "south africa", "ghana", "rwanda", "uganda", "tanzania", "senegal", "morocco", "egypt", "sub-saharan"]
        has_africa = any(keyword in text for keyword in africa_keywords)
        
        # Filter out job postings and irrelevant content
        exclude_keywords = ["job", "hiring", "career", "recruitment", "salary", "resume", "cv", "interview"]
        is_job = any(keyword in text for keyword in exclude_keywords)
        
        return has_funding and has_ai and has_africa and not is_job
    
    def _calculate_ai_relevance(self, result: Dict[str, Any]) -> float:
        """Calculate AI relevance score (0-1)"""
        text = (result.get("title", "") + " " + result.get("snippet", "") + " " + result.get("description", "")).lower()
        
        ai_keywords = {
            "artificial intelligence": 1.0,
            "ai": 0.8,
            "machine learning": 1.0,
            "deep learning": 1.0,
            "neural network": 1.0,
            "ml": 0.6,
            "algorithm": 0.5,
            "automation": 0.4,
            "digital": 0.3,
            "technology": 0.2
        }
        
        score = 0.0
        for keyword, weight in ai_keywords.items():
            if keyword in text:
                score += weight
        
        return min(score, 1.0)
    
    def _calculate_africa_relevance(self, result: Dict[str, Any]) -> float:
        """Calculate Africa relevance score (0-1)"""
        text = (result.get("title", "") + " " + result.get("snippet", "") + " " + result.get("description", "")).lower()
        
        africa_keywords = {
            "africa": 1.0,
            "african": 1.0,
            "sub-saharan": 1.0,
            "nigeria": 0.8,
            "kenya": 0.8,
            "south africa": 0.8,
            "ghana": 0.8,
            "rwanda": 0.8,
            "uganda": 0.8,
            "tanzania": 0.8,
            "senegal": 0.8,
            "morocco": 0.8,
            "egypt": 0.8,
            "continent": 0.6,
            "developing": 0.3
        }
        
        score = 0.0
        for keyword, weight in africa_keywords.items():
            if keyword in text:
                score += weight
        
        return min(score, 1.0)
    
    def _calculate_funding_relevance(self, result: Dict[str, Any]) -> float:
        """Calculate funding relevance score (0-1)"""
        text = (result.get("title", "") + " " + result.get("snippet", "") + " " + result.get("description", "")).lower()
        
        funding_keywords = {
            "funding": 1.0,
            "grant": 1.0,
            "grants": 1.0,
            "scholarship": 1.0,
            "fellowship": 1.0,
            "prize": 0.8,
            "award": 0.8,
            "investment": 0.6,
            "accelerator": 0.6,
            "incubator": 0.6,
            "competition": 0.5,
            "opportunity": 0.4,
            "call": 0.6,
            "program": 0.3
        }
        
        score = 0.0
        for keyword, weight in funding_keywords.items():
            if keyword in text:
                score += weight
        
        return min(score, 1.0)
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content deduplication"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _deduplicate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate opportunities based on content hash"""
        seen_hashes = set()
        unique_opportunities = []
        
        for opp in opportunities:
            content_hash = opp["content_hash"]
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_opportunities.append(opp)
        
        logger.info(f"Deduplication: {len(opportunities)} -> {len(unique_opportunities)} unique opportunities")
        return unique_opportunities
    
    async def _process_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enrich opportunities"""
        processed = []
        
        for opp in opportunities:
            # Calculate overall relevance score
            overall_score = (
                opp["ai_relevance_score"] * 0.4 +
                opp["africa_relevance_score"] * 0.4 +
                opp["funding_relevance_score"] * 0.2
            )
            opp["overall_relevance_score"] = overall_score
            
            # Only keep high-quality opportunities
            if overall_score >= 0.3:  # Minimum threshold
                # Extract additional metadata
                opp["domain"] = self._extract_domain(opp["source_url"])
                opp["estimated_amount"] = self._extract_funding_amount(opp["description"])
                opp["deadline_mentioned"] = self._extract_deadline_info(opp["description"])
                
                processed.append(opp)
        
        # Sort by relevance score
        processed.sort(key=lambda x: x["overall_relevance_score"], reverse=True)
        
        logger.info(f"Processing: {len(opportunities)} -> {len(processed)} high-quality opportunities")
        return processed
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _extract_funding_amount(self, text: str) -> Optional[str]:
        """Extract funding amounts from text"""
        # Look for common funding amount patterns
        amount_patterns = [
            r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|k|m|b))?',
            r'[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|dollars?|euros?|pounds?)',
            r'up to \$?[\d,]+',
            r'grant of \$?[\d,]+'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_deadline_info(self, text: str) -> bool:
        """Check if deadline information is mentioned"""
        deadline_keywords = ["deadline", "due", "apply by", "closes", "expires", "until", "before"]
        return any(keyword in text.lower() for keyword in deadline_keywords)

async def test_serper_collector():
    """Test the Serper collector"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("SERPER_DEV_API_KEY")
    
    if not api_key:
        print("❌ SERPER_DEV_API_KEY not found in environment")
        return
    
    collector = SerperSearchCollector(api_key)
    opportunities = await collector.start_collection()
    
    print(f"\n🎉 Found {len(opportunities)} funding opportunities!")
    
    # Print top 5 results
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n{i}. {opp['title']}")
        print(f"   Score: {opp['overall_relevance_score']:.2f}")
        print(f"   Domain: {opp['domain']}")
        print(f"   URL: {opp['source_url']}")
        if opp['estimated_amount']:
            print(f"   Amount: {opp['estimated_amount']}")
        print(f"   Query: {opp['search_query']}")

if __name__ == "__main__":
    asyncio.run(test_serper_collector())
