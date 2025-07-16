#!/usr/bin/env python3
"""
Enhanced Serper Search for AI Africa Funding Tracker Demo
This script uses Serper.dev API to find the latest funding opportunities
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import hashlib

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.connector import DatabaseConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSerperSearch:
    """Enhanced Serper search for comprehensive funding discovery"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.session = None
        self.db_connector = None
        
        # Comprehensive search queries for maximum coverage
        self.search_queries = [
            # === IMMEDIATE HIGH-VALUE SEARCHES ===
            {
                "name": "AI Africa Funding 2025",
                "query": "\"AI funding\" OR \"AI grants\" OR \"AI program\" AND Africa AND 2025 AND (applications OR apply OR deadline)",
                "priority": "critical"
            },
            {
                "name": "African AI Startup Funding",
                "query": "\"African AI startup\" OR \"Africa AI startup\" AND (funding OR investment OR accelerator) AND 2025",
                "priority": "critical"
            },
            {
                "name": "Google AI Africa Programs",
                "query": "Google AND (\"AI for Good\" OR \"AI for Everyone\" OR \"AI for Africa\") AND (funding OR grants OR program OR accelerator)",
                "priority": "critical"
            },
            {
                "name": "Microsoft AI Africa Initiative",
                "query": "Microsoft AND \"AI for Good\" AND Africa AND (funding OR grants OR program OR initiative)",
                "priority": "critical"
            },
            {
                "name": "Gates Foundation AI Africa",
                "query": "\"Gates Foundation\" AND AI AND Africa AND (funding OR grants OR program OR Grand Challenges)",
                "priority": "critical"
            },
            {
                "name": "World Bank Digital Africa AI",
                "query": "\"World Bank\" AND Africa AND (AI OR \"artificial intelligence\" OR digital) AND (funding OR grants OR program)",
                "priority": "critical"
            },
            {
                "name": "OpenAI Africa Expansion",
                "query": "OpenAI AND Africa AND (funding OR startup OR program OR initiative OR expansion)",
                "priority": "high"
            },
            {
                "name": "Y Combinator Africa",
                "query": "\"Y Combinator\" AND Africa AND (AI OR startup OR program OR initiative)",
                "priority": "high"
            },
            {
                "name": "Techstars Africa AI",
                "query": "Techstars AND Africa AND (AI OR artificial intelligence OR accelerator OR program)",
                "priority": "high"
            },
            {
                "name": "African Development Bank AI",
                "query": "\"African Development Bank\" OR AfDB AND (AI OR digital OR innovation) AND (funding OR grants OR program)",
                "priority": "high"
            },
            
            # === SECTOR-SPECIFIC SEARCHES ===
            {
                "name": "Health AI Africa Funding",
                "query": "(health OR healthcare OR medical) AND AI AND Africa AND (funding OR grants OR program) AND 2025",
                "priority": "high"
            },
            {
                "name": "Agriculture AI Africa Funding",
                "query": "(agriculture OR farming OR food security) AND AI AND Africa AND (funding OR grants OR program)",
                "priority": "high"
            },
            {
                "name": "Education AI Africa Funding",
                "query": "(education OR edtech OR learning) AND AI AND Africa AND (funding OR grants OR program)",
                "priority": "medium"
            },
            {
                "name": "Climate AI Africa Funding",
                "query": "(climate OR environment OR sustainability) AND AI AND Africa AND (funding OR grants OR program)",
                "priority": "medium"
            },
            {
                "name": "Fintech AI Africa Funding",
                "query": "(fintech OR financial OR banking) AND AI AND Africa AND (funding OR grants OR investment)",
                "priority": "medium"
            },
            
            # === RESEARCH AND ACADEMIC FUNDING ===
            {
                "name": "AI Research Africa Funding",
                "query": "(research OR academic OR university) AND AI AND Africa AND (funding OR grants OR fellowship)",
                "priority": "high"
            },
            {
                "name": "IDRC AI4D Africa",
                "query": "IDRC AND (AI4D OR \"AI for Development\") AND Africa AND (funding OR grants OR program)",
                "priority": "high"
            },
            {
                "name": "Mozilla Africa AI Research",
                "query": "Mozilla AND Africa AND (AI OR artificial intelligence) AND (grants OR research OR Mradi)",
                "priority": "medium"
            },
            
            # === VENTURE CAPITAL AND INVESTMENT ===
            {
                "name": "AI Venture Capital Africa",
                "query": "\"venture capital\" OR \"VC fund\" AND AI AND Africa AND (investment OR funding OR startup)",
                "priority": "medium"
            },
            {
                "name": "African AI Accelerators",
                "query": "Africa AND AI AND (accelerator OR incubator OR startup program) AND 2025",
                "priority": "medium"
            },
            {
                "name": "Silicon Valley Africa AI",
                "query": "\"Silicon Valley\" AND Africa AND AI AND (funding OR investment OR program OR initiative)",
                "priority": "medium"
            },
            
            # === COUNTRY-SPECIFIC SEARCHES ===
            {
                "name": "Nigeria AI Funding",
                "query": "Nigeria AND AI AND (funding OR grants OR investment OR accelerator) AND 2025",
                "priority": "medium"
            },
            {
                "name": "Kenya AI Funding",
                "query": "Kenya AND AI AND (funding OR grants OR investment OR accelerator) AND 2025",
                "priority": "medium"
            },
            {
                "name": "South Africa AI Funding",
                "query": "\"South Africa\" AND AI AND (funding OR grants OR investment OR accelerator) AND 2025",
                "priority": "medium"
            },
            {
                "name": "Ghana AI Funding",
                "query": "Ghana AND AI AND (funding OR grants OR investment OR accelerator) AND 2025",
                "priority": "medium"
            },
            {
                "name": "Rwanda AI Funding",
                "query": "Rwanda AND AI AND (funding OR grants OR investment OR accelerator) AND 2025",
                "priority": "medium"
            },
            
            # === LATEST OPPORTUNITIES ===
            {
                "name": "AI Africa Funding July 2025",
                "query": "AI AND Africa AND funding AND \"July 2025\" OR \"August 2025\" OR \"September 2025\"",
                "priority": "critical"
            },
            {
                "name": "African AI Call for Proposals",
                "query": "Africa AND AI AND (\"call for proposals\" OR \"applications open\" OR \"now accepting\") AND 2025",
                "priority": "critical"
            },
            {
                "name": "AI Africa Deadline 2025",
                "query": "AI AND Africa AND (deadline OR \"application deadline\" OR \"submissions due\") AND 2025",
                "priority": "critical"
            }
        ]
    
    async def initialize(self):
        """Initialize connections"""
        self.session = aiohttp.ClientSession()
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        self.db_connector = DatabaseConnector(database_url)
        await self.db_connector.initialize()
        
        logger.info("✅ Enhanced Serper search initialized")
    
    async def search_query(self, query_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for funding opportunities using Serper API"""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query_info["query"],
            "type": "search",
            "engine": "google",
            "location": "United States",
            "gl": "us",
            "hl": "en",
            "num": 20,  # Get more results
            "page": 1
        }
        
        try:
            async with self.session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_search_results(data, query_info)
                else:
                    logger.error(f"Serper API error {response.status} for query: {query_info['name']}")
                    return []
        except Exception as e:
            logger.error(f"Error searching '{query_info['name']}': {e}")
            return []
    
    def _process_search_results(self, data: Dict[str, Any], query_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process search results into funding opportunities"""
        opportunities = []
        
        # Process organic results
        for result in data.get("organic", []):
            opportunity = {
                "title": result.get("title", ""),
                "description": result.get("snippet", ""),
                "url": result.get("link", ""),
                "source_name": self._extract_domain(result.get("link", "")),
                "source_url": result.get("link", ""),
                "published_date": datetime.now().isoformat(),
                "keywords": query_info["query"],
                "priority": query_info["priority"],
                "search_query": query_info["name"],
                "content": result.get("snippet", ""),
                "relevance_score": self._calculate_relevance_score(result, query_info)
            }
            
            # Only include high-relevance results
            if opportunity["relevance_score"] > 0.3:
                opportunities.append(opportunity)
        
        # Process knowledge graph if available
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            opportunity = {
                "title": kg.get("title", ""),
                "description": kg.get("description", ""),
                "url": kg.get("website", ""),
                "source_name": self._extract_domain(kg.get("website", "")),
                "source_url": kg.get("website", ""),
                "published_date": datetime.now().isoformat(),
                "keywords": query_info["query"],
                "priority": "high",
                "search_query": query_info["name"],
                "content": kg.get("description", ""),
                "relevance_score": 0.8
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace("www.", "")
        except:
            return url
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query_info: Dict[str, Any]) -> float:
        """Calculate relevance score for filtering"""
        score = 0.0
        
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        
        # High-value keywords
        high_value_keywords = [
            "funding", "grants", "program", "apply", "application", 
            "deadline", "call for proposals", "initiative", "accelerator",
            "investment", "startup", "research", "fellowship"
        ]
        
        # AI-related keywords
        ai_keywords = ["ai", "artificial intelligence", "machine learning", "deep learning"]
        
        # Africa-related keywords
        africa_keywords = ["africa", "african", "nigeria", "kenya", "south africa", "ghana", "rwanda"]
        
        # Calculate score based on keyword presence
        for keyword in high_value_keywords:
            if keyword in title:
                score += 0.15
            if keyword in snippet:
                score += 0.10
        
        for keyword in ai_keywords:
            if keyword in title:
                score += 0.20
            if keyword in snippet:
                score += 0.15
        
        for keyword in africa_keywords:
            if keyword in title:
                score += 0.20
            if keyword in snippet:
                score += 0.15
        
        # Boost for high-priority queries
        if query_info["priority"] == "critical":
            score *= 1.5
        elif query_info["priority"] == "high":
            score *= 1.2
        
        return min(score, 1.0)
    
    async def run_comprehensive_search(self) -> Dict[str, Any]:
        """Run comprehensive search across all queries"""
        logger.info("🔍 Starting comprehensive Serper search for demo...")
        
        total_opportunities = []
        total_saved = 0
        total_duplicates = 0
        total_errors = 0
        
        # Process critical priority queries first
        critical_queries = [q for q in self.search_queries if q["priority"] == "critical"]
        high_queries = [q for q in self.search_queries if q["priority"] == "high"]
        medium_queries = [q for q in self.search_queries if q["priority"] == "medium"]
        
        all_queries = critical_queries + high_queries + medium_queries
        
        for i, query_info in enumerate(all_queries, 1):
            logger.info(f"🔍 [{i}/{len(all_queries)}] Searching: {query_info['name']} ({query_info['priority']})")
            
            opportunities = await self.search_query(query_info)
            
            if opportunities:
                logger.info(f"📊 Found {len(opportunities)} opportunities")
                
                # Save to database
                result = await self.db_connector.save_opportunities(opportunities, "serper_search")
                total_saved += result['saved']
                total_duplicates += result['duplicates']
                total_errors += result['errors']
                
                total_opportunities.extend(opportunities)
                
                logger.info(f"💾 Saved: {result['saved']}, Duplicates: {result['duplicates']}, Errors: {result['errors']}")
            else:
                logger.info("📊 No opportunities found")
            
            # Rate limiting - wait between requests
            await asyncio.sleep(1)
        
        logger.info(f"🎉 Comprehensive search completed!")
        logger.info(f"📊 Total: {len(total_opportunities)} found, {total_saved} saved, {total_duplicates} duplicates, {total_errors} errors")
        
        return {
            "total_found": len(total_opportunities),
            "saved": total_saved,
            "duplicates": total_duplicates,
            "errors": total_errors,
            "opportunities": total_opportunities
        }
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()
        if self.db_connector:
            await self.db_connector.close()
        logger.info("✅ Enhanced Serper search closed")

async def main():
    """Main function"""
    # Load environment variables
    def load_env_vars(env_path=".env"):
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    load_env_vars()
    
    serper_api_key = os.getenv("SERPER_DEV_API_KEY")
    if not serper_api_key:
        logger.error("❌ SERPER_DEV_API_KEY environment variable not set")
        return
    
    searcher = EnhancedSerperSearch(serper_api_key)
    try:
        await searcher.initialize()
        result = await searcher.run_comprehensive_search()
        
        print(f"\\n✅ ENHANCED SERPER SEARCH COMPLETED!")
        print(f"📊 {result['total_found']} opportunities found")
        print(f"💾 {result['saved']} new opportunities saved to database")
        print(f"🔄 {result['duplicates']} duplicates detected")
        print(f"🎯 Database now contains comprehensive funding data for demo!")
        
    except Exception as e:
        logger.error(f"❌ Enhanced Serper search failed: {e}")
    finally:
        await searcher.close()

if __name__ == "__main__":
    asyncio.run(main())