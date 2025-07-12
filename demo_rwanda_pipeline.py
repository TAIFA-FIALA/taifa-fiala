#!/usr/bin/env python3
"""
TAIFA-FIALA Rwanda Demo Pipeline
Live demonstration of the complete funding discovery workflow:
SERPER API → Parse → Database → User Search → n8n → Notion

Demo Flow:
1. Search for Rwanda-specific AI funding using SERPER
2. Parse and process the results
3. Insert new opportunities into database
4. Show user search experience
5. Trigger n8n workflow to Notion (bonus)
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

# Load environment variables
load_dotenv()

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='🎬 %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class RwandaDemoOrchestrator:
    """Orchestrates the complete Rwanda demo pipeline"""
    
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_DEV_API_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")  # For bonus points
        
        # Rwanda-specific search queries for demo
        self.demo_queries = [
            {
                "name": "Rwanda AI Healthcare Funding 2025",
                "query": "Rwanda AND (AI OR \"artificial intelligence\") AND healthcare AND funding AND 2025",
                "demo_context": "Healthcare is a priority sector for Rwanda's Vision 2050"
            },
            {
                "name": "Rwanda Digital Transformation Grants",
                "query": "Rwanda AND digital transformation AND grants AND technology AND innovation",
                "demo_context": "Rwanda is positioning itself as a tech hub in East Africa"
            },
            {
                "name": "East Africa AI Research Funding",
                "query": "\"East Africa\" AND AI research AND funding AND universities AND partnerships",
                "demo_context": "Regional collaboration opportunities for Rwandan institutions"
            }
        ]
        
        self.demo_stats = {
            "opportunities_found": 0,
            "new_opportunities_added": 0,
            "database_updates": 0,
            "search_results": 0
        }
    
    async def run_complete_demo(self):
        """Run the complete demo pipeline"""
        logger.info("🇷🇼 STARTING TAIFA-FIALA RWANDA DEMO")
        logger.info("=" * 60)
        
        print("\n🎯 DEMO OVERVIEW:")
        print("1. 🔍 Search for Rwanda AI funding opportunities using SERPER")
        print("2. 📊 Parse and process the discovered opportunities")
        print("3. 💾 Add new opportunities to TAIFA database")
        print("4. 👤 Simulate user search experience")
        print("5. 🔗 Trigger n8n workflow to Notion (bonus)")
        print("=" * 60)
        
        # Part 1: SERPER Discovery
        print("\n🔍 PART 1: DISCOVERING OPPORTUNITIES WITH SERPER")
        discovered_opportunities = await self.demo_serper_discovery()
        
        # Part 2: Database Processing
        print("\n💾 PART 2: PROCESSING AND STORING IN DATABASE")
        stored_opportunities = await self.demo_database_storage(discovered_opportunities)
        
        # Part 3: User Experience
        print("\n👤 PART 3: USER SEARCH EXPERIENCE")
        search_results = await self.demo_user_search()
        
        # Part 4: n8n Integration (bonus)
        if self.n8n_webhook_url and stored_opportunities:
            print("\n🔗 PART 4: N8N WORKFLOW TO NOTION (BONUS)")
            await self.demo_n8n_integration(stored_opportunities[0])
        
        # Demo Summary
        self.print_demo_summary()
        
        return {
            "discovered": len(discovered_opportunities),
            "stored": len(stored_opportunities),
            "search_results": len(search_results)
        }
    
    async def demo_serper_discovery(self):
        """Demo Part 1: SERPER API discovery"""
        print("\n🔍 Searching for Rwanda AI funding opportunities...")
        
        discovered_opportunities = []
        
        async with aiohttp.ClientSession() as session:
            for query_config in self.demo_queries:
                print(f"\n📡 Executing search: {query_config['name']}")
                print(f"📝 Context: {query_config['demo_context']}")
                
                opportunities = await self._search_serper(session, query_config)
                discovered_opportunities.extend(opportunities)
                
                # Show live results
                if opportunities:
                    print(f"✅ Found {len(opportunities)} relevant opportunities")
                    for i, opp in enumerate(opportunities[:2], 1):  # Show top 2
                        print(f"   {i}. {opp['title'][:80]}...")
                        print(f"      🌐 {opp['domain']}")
                        print(f"      📊 Relevance: {opp['overall_relevance_score']:.2f}")
                else:
                    print("   ℹ️  No new opportunities found for this query")
                
                # Demo pacing - pause between searches
                await asyncio.sleep(2)
        
        # Remove duplicates
        unique_opportunities = self._deduplicate_opportunities(discovered_opportunities)
        
        print(f"\n🎯 DISCOVERY SUMMARY:")
        print(f"   📊 Total results: {len(discovered_opportunities)}")
        print(f"   🎯 Unique opportunities: {len(unique_opportunities)}")
        print(f"   🇷🇼 Rwanda-relevant: {len([o for o in unique_opportunities if o['africa_relevance_score'] > 0.5])}")
        
        self.demo_stats["opportunities_found"] = len(unique_opportunities)
        return unique_opportunities
    
    async def _search_serper(self, session: aiohttp.ClientSession, query_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Execute a single SERPER search with demo-specific processing"""
        
        payload = {
            "q": query_config["query"],
            "location": "Kigali, Rwanda",  # Rwanda-specific for demo
            "gl": "rw",
            "num": 10,  # Smaller number for demo
            "type": "search"
        }
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            async with session.post("https://google.serper.dev/search", headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_demo_results(data, query_config)
                else:
                    logger.error(f"❌ SERPER API error {response.status}")
                    return []
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []
    
    def _parse_demo_results(self, data: Dict[str, Any], query_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse SERPER results with demo-specific relevance scoring"""
        opportunities = []
        
        organic_results = data.get("organic", [])
        
        for result in organic_results:
            if self._is_demo_relevant(result):
                opportunity = {
                    "title": result.get("title", ""),
                    "description": result.get("snippet", ""),
                    "source_url": result.get("link", ""),
                    "search_query": query_config["name"],
                    "discovered_date": datetime.utcnow().isoformat(),
                    "source_type": "serper_demo",
                    "content_hash": self._generate_content_hash(result.get("title", "") + result.get("link", "")),
                    "ai_relevance_score": self._calculate_ai_relevance(result),
                    "africa_relevance_score": self._calculate_africa_relevance(result),
                    "funding_relevance_score": self._calculate_funding_relevance(result),
                    "domain": self._extract_domain(result.get("link", "")),
                    "demo_context": query_config["demo_context"]
                }
                
                # Calculate overall score
                opportunity["overall_relevance_score"] = (
                    opportunity["ai_relevance_score"] * 0.4 +
                    opportunity["africa_relevance_score"] * 0.4 +
                    opportunity["funding_relevance_score"] * 0.2
                )
                
                # Only include high-quality results for demo
                if opportunity["overall_relevance_score"] >= 0.3:
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _is_demo_relevant(self, result: Dict[str, Any]) -> bool:
        """Demo-specific relevance filtering"""
        text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
        
        # Must have funding keywords
        funding_keywords = ["funding", "grant", "grants", "program", "opportunity", "call", "award", "scholarship"]
        has_funding = any(keyword in text for keyword in funding_keywords)
        
        # Should have AI or tech keywords
        ai_keywords = ["ai", "artificial intelligence", "technology", "digital", "innovation", "research"]
        has_ai_tech = any(keyword in text for keyword in ai_keywords)
        
        # Should mention Africa, Rwanda, or regional terms
        africa_keywords = ["africa", "rwanda", "east africa", "african", "developing", "emerging"]
        has_africa = any(keyword in text for keyword in africa_keywords)
        
        # Exclude irrelevant content
        exclude_keywords = ["job", "hiring", "salary", "employment", "career"]
        is_irrelevant = any(keyword in text for keyword in exclude_keywords)
        
        return has_funding and (has_ai_tech or has_africa) and not is_irrelevant
    
    async def demo_database_storage(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Demo Part 2: Store opportunities in database"""
        print("\n💾 Processing opportunities for database storage...")
        
        if not opportunities:
            print("   ℹ️  No opportunities to store")
            return []
        
        stored_opportunities = []
        
        try:
            # Connect to database
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            for opp in opportunities:
                # Check if opportunity already exists
                cursor.execute(
                    "SELECT id, title FROM funding_opportunities WHERE source_url = %s OR title = %s",
                    (opp['source_url'], opp['title'])
                )
                existing = cursor.fetchone()
                
                if existing:
                    print(f"   ⚠️  Already exists: {existing['title'][:50]}...")
                    continue
                
                # Insert new opportunity
                insert_query = """
                INSERT INTO funding_opportunities (
                    title, description, source_url, status, 
                    geographical_scope, created_at, last_checked
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, title
                """
                
                cursor.execute(insert_query, (
                    opp['title'],
                    opp['description'],
                    opp['source_url'],
                    'active',
                    'Rwanda, East Africa',  # Demo-specific scope
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                result = cursor.fetchone()
                if result:
                    print(f"   ✅ Added: {result['title'][:60]}...")
                    print(f"      🆔 ID: {result['id']}")
                    print(f"      🌐 Source: {opp['domain']}")
                    
                    # Add to stored list with database ID
                    opp['database_id'] = result['id']
                    stored_opportunities.append(opp)
                    
                    self.demo_stats["new_opportunities_added"] += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"\n📊 DATABASE STORAGE SUMMARY:")
            print(f"   ✅ New opportunities added: {len(stored_opportunities)}")
            print(f"   🗄️  Total database records updated: {self.demo_stats['new_opportunities_added']}")
            
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return []
        
        return stored_opportunities
    
    async def demo_user_search(self) -> List[Dict[str, Any]]:
        """Demo Part 3: Simulate user search experience"""
        print("\n👤 Simulating user search experience...")
        
        search_terms = [
            "Rwanda AI",
            "healthcare funding",
            "digital transformation",
            "East Africa research"
        ]
        
        all_results = []
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            for term in search_terms:
                print(f"\n🔍 User searches for: '{term}'")
                
                # Search in database
                search_query = """
                SELECT id, title, description, source_url, created_at
                FROM funding_opportunities 
                WHERE (title ILIKE %s OR description ILIKE %s)
                AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 5
                """
                
                search_pattern = f"%{term}%"
                cursor.execute(search_query, (search_pattern, search_pattern))
                results = cursor.fetchall()
                
                if results:
                    print(f"   ✅ Found {len(results)} opportunities:")
                    for i, result in enumerate(results, 1):
                        print(f"      {i}. {result['title'][:60]}...")
                        print(f"         🆔 ID: {result['id']} | 📅 Added: {result['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        
                        # Highlight if this was newly added
                        if result['created_at'] > datetime.utcnow().replace(hour=0, minute=0, second=0):
                            print(f"         🆕 NEWLY DISCOVERED TODAY!")
                    
                    all_results.extend(results)
                else:
                    print(f"   ℹ️  No opportunities found for '{term}'")
                
                # Demo pacing
                await asyncio.sleep(1)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
        
        self.demo_stats["search_results"] = len(all_results)
        return all_results
    
    async def demo_n8n_integration(self, opportunity: Dict[str, Any]):
        """Demo Part 4: n8n webhook integration to Notion"""
        print("\n🔗 Triggering n8n workflow to Notion...")
        
        # Prepare data for n8n webhook
        webhook_data = {
            "title": opportunity.get('title'),
            "description": opportunity.get('description'),
            "source_url": opportunity.get('source_url'),
            "discovered_date": opportunity.get('discovered_date'),
            "database_id": opportunity.get('database_id'),
            "relevance_score": opportunity.get('overall_relevance_score'),
            "demo_source": "TAIFA Rwanda Demo",
            "trigger_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.n8n_webhook_url, json=webhook_data) as response:
                    if response.status == 200:
                        print("   ✅ n8n webhook triggered successfully!")
                        print("   📝 Opportunity sent to Notion database")
                        print(f"   🔗 Webhook response: {response.status}")
                    else:
                        print(f"   ⚠️  Webhook response: {response.status}")
        except Exception as e:
            print(f"   ℹ️  n8n webhook not configured or unreachable: {e}")
    
    def print_demo_summary(self):
        """Print comprehensive demo summary"""
        print("\n" + "=" * 60)
        print("🎉 TAIFA-FIALA RWANDA DEMO COMPLETE!")
        print("=" * 60)
        
        print(f"\n📊 DEMO STATISTICS:")
        print(f"   🔍 Opportunities discovered: {self.demo_stats['opportunities_found']}")
        print(f"   💾 New records added: {self.demo_stats['new_opportunities_added']}")
        print(f"   🔍 Search results shown: {self.demo_stats['search_results']}")
        
        print(f"\n🎯 DEMONSTRATED CAPABILITIES:")
        print(f"   ✅ Real-time funding discovery via SERPER API")
        print(f"   ✅ Intelligent parsing and relevance scoring")
        print(f"   ✅ Database integration and deduplication")
        print(f"   ✅ User search experience simulation")
        print(f"   ✅ Bilingual platform foundation (EN/FR)")
        if self.n8n_webhook_url:
            print(f"   ✅ n8n workflow integration to Notion")
        
        print(f"\n🇷🇼 RWANDA IMPACT POTENTIAL:")
        print(f"   🎯 Centralized AI funding discovery for Rwanda")
        print(f"   🌍 Regional East African collaboration opportunities")
        print(f"   🔄 Real-time updates from 44 global sources")
        print(f"   🗣️  Bilingual access (English/French)")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   📈 Scale to continuous monitoring")
        print(f"   🌍 Deploy bilingual frontend")
        print(f"   🤝 Partner with Rwandan institutions")
        print(f"   📱 Launch mobile-optimized interface")
        
        print("\n" + "=" * 60)
        print("🎬 Demo complete! Ready for Rwanda presentation.")
        print("=" * 60)
    
    # Helper methods (same as in original collector)
    def _calculate_ai_relevance(self, result: Dict[str, Any]) -> float:
        text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
        ai_keywords = {
            "artificial intelligence": 1.0, "ai": 0.8, "machine learning": 1.0,
            "digital": 0.4, "technology": 0.3, "innovation": 0.5
        }
        score = sum(weight for keyword, weight in ai_keywords.items() if keyword in text)
        return min(score, 1.0)
    
    def _calculate_africa_relevance(self, result: Dict[str, Any]) -> float:
        text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
        africa_keywords = {
            "rwanda": 1.0, "africa": 1.0, "african": 1.0, "east africa": 1.0,
            "developing": 0.4, "emerging": 0.4, "kigali": 0.8
        }
        score = sum(weight for keyword, weight in africa_keywords.items() if keyword in text)
        return min(score, 1.0)
    
    def _calculate_funding_relevance(self, result: Dict[str, Any]) -> float:
        text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
        funding_keywords = {
            "funding": 1.0, "grant": 1.0, "grants": 1.0, "scholarship": 1.0,
            "program": 0.5, "opportunity": 0.6, "call": 0.7
        }
        score = sum(weight for keyword, weight in funding_keywords.items() if keyword in text)
        return min(score, 1.0)
    
    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        try:
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _generate_content_hash(self, content: str) -> str:
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _deduplicate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_hashes = set()
        unique = []
        for opp in opportunities:
            if opp["content_hash"] not in seen_hashes:
                seen_hashes.add(opp["content_hash"])
                unique.append(opp)
        return unique

async def main():
    """Run the Rwanda demo"""
    demo = RwandaDemoOrchestrator()
    
    # Check prerequisites
    if not demo.serper_api_key:
        print("❌ SERPER_DEV_API_KEY not found in environment")
        print("   Please add your SERPER API key to .env file")
        return
    
    if not demo.database_url:
        print("❌ DATABASE_URL not found in environment")
        print("   Please check your database configuration")
        return
    
    print("🎬 Prerequisites checked. Starting demo in 3 seconds...")
    await asyncio.sleep(3)
    
    # Run the complete demo
    results = await demo.run_complete_demo()
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
