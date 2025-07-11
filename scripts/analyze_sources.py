#!/usr/bin/env python3
"""
Source Analysis Script - Test known funding sources for parsing difficulty
"""

import asyncio
import aiohttp
import feedparser
import requests
from datetime import datetime
import json
from bs4 import BeautifulSoup
import sys

# Our known funding sources
FUNDING_SOURCES = [
    {
        "name": "IDRC AI4D Program",
        "type": "rss",
        "url": "https://idrc-crdi.ca/en/funding/funding-opportunities/rss",
        "backup_urls": [
            "https://idrc-crdi.ca/en/funding",
            "https://idrc-crdi.ca/en/what-we-do/projects-we-support"
        ],
        "keywords": ["AI", "artificial intelligence", "AI4D", "machine learning", "Africa"]
    },
    {
        "name": "Science for Africa Foundation",
        "type": "rss", 
        "url": "https://scienceforafrica.foundation/feed/",
        "backup_urls": [
            "https://scienceforafrica.foundation/funding-resources/",
            "https://scienceforafrica.foundation/category/funding/"
        ],
        "keywords": ["AI", "artificial intelligence", "grand challenges", "innovation"]
    },
    {
        "name": "Gates Foundation",
        "type": "rss",
        "url": "https://www.gatesfoundation.org/ideas/rss/",
        "backup_urls": [
            "https://www.gatesfoundation.org/our-work/programs/global-development/integrated-delivery",
            "https://www.gatesfoundation.org/ideas/"
        ],
        "keywords": ["AI", "artificial intelligence", "health", "development", "Africa"]
    },
    {
        "name": "Milken-Motsepe Innovation Prize",
        "type": "web",
        "url": "https://www.milkeninstitute.org/motsepe-prize",
        "backup_urls": [
            "https://www.milkeninstitute.org/prizes",
            "https://www.mlken-motsepe.org/"
        ],
        "keywords": ["AI", "artificial intelligence", "innovation", "Africa", "manufacturing"]
    },
    {
        "name": "European Commission - Digital Strategy",
        "type": "web",
        "url": "https://digital-strategy.ec.europa.eu/en/funding",
        "backup_urls": [
            "https://digital-strategy.ec.europa.eu/en/funding/commission-funds-projects-unlock-potential-generative-ai-africa"
        ],
        "keywords": ["AI", "artificial intelligence", "Africa", "funding", "calls"]
    },
    {
        "name": "Llama Impact Accelerator",
        "type": "web", 
        "url": "https://llama.meta.com/llama-impact-grants/",
        "backup_urls": [
            "https://about.fb.com/news/",
            "https://ai.meta.com/blog/"
        ],
        "keywords": ["Llama", "AI", "grants", "Africa", "accelerator"]
    }
]

class SourceAnalyzer:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def analyze_all_sources(self):
        """Analyze all funding sources"""
        print("🔍 Analyzing AI Africa Funding Sources")
        print("=" * 60)
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'AI-Africa-Funding-Tracker-Analyzer/1.0'}
        )
        
        try:
            for source in FUNDING_SOURCES:
                print(f"\n📊 Analyzing: {source['name']}")
                print("-" * 40)
                
                result = await self.analyze_source(source)
                self.results.append(result)
                
                # Print immediate results
                self.print_source_result(result)
                
        finally:
            if self.session:
                await self.session.close()
        
        # Print summary
        self.print_summary()
    
    async def analyze_source(self, source):
        """Analyze a single source"""
        result = {
            "name": source["name"],
            "type": source["type"],
            "url": source["url"],
            "status": "unknown",
            "accessibility": "unknown",
            "data_format": "unknown", 
            "parsing_difficulty": "unknown",
            "ai_content_found": False,
            "africa_content_found": False,
            "sample_entries": [],
            "errors": [],
            "recommendations": []
        }
        
        try:
            if source["type"] == "rss":
                result = await self.analyze_rss_feed(source, result)
            else:
                result = await self.analyze_web_source(source, result)
                
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Analysis failed: {str(e)}")
            
        return result
    
    async def analyze_rss_feed(self, source, result):
        """Analyze RSS feed"""
        try:
            # Try to fetch RSS feed
            async with self.session.get(source["url"]) as response:
                if response.status == 200:
                    feed_content = await response.text()
                    result["accessibility"] = "accessible"
                    result["status"] = "success"
                    
                    # Parse with feedparser
                    feed = feedparser.parse(feed_content)
                    
                    if feed.entries:
                        result["data_format"] = "valid_rss"
                        result["parsing_difficulty"] = "easy"
                        
                        # Analyze entries
                        for i, entry in enumerate(feed.entries[:3]):  # Sample first 3
                            entry_text = (
                                getattr(entry, 'title', '') + ' ' + 
                                getattr(entry, 'summary', '') + ' ' +
                                getattr(entry, 'description', '')
                            ).lower()
                            
                            # Check for AI keywords
                            ai_found = any(kw.lower() in entry_text for kw in source["keywords"])
                            if ai_found:
                                result["ai_content_found"] = True
                            
                            # Check for Africa keywords
                            africa_terms = ['africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana']
                            africa_found = any(term in entry_text for term in africa_terms)
                            if africa_found:
                                result["africa_content_found"] = True
                            
                            # Save sample
                            sample = {
                                "title": getattr(entry, 'title', 'No title'),
                                "date": getattr(entry, 'published', 'No date'),
                                "relevant": ai_found and africa_found
                            }
                            result["sample_entries"].append(sample)
                        
                        # Set recommendations
                        if result["ai_content_found"] and result["africa_content_found"]:
                            result["recommendations"] = ["High priority - implement RSS monitor", "Easy integration"]
                        elif result["ai_content_found"]:
                            result["recommendations"] = ["Medium priority - some AI content", "May need keyword filtering"]
                        else:
                            result["recommendations"] = ["Low priority - limited relevant content"]
                            
                    else:
                        result["data_format"] = "empty_feed"
                        result["parsing_difficulty"] = "medium"
                        result["errors"].append("RSS feed is empty")
                        
                else:
                    result["accessibility"] = f"http_error_{response.status}"
                    result["status"] = "error"
                    result["errors"].append(f"HTTP {response.status}")
                    
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"RSS analysis failed: {str(e)}")
            
        return result
    
    async def analyze_web_source(self, source, result):
        """Analyze web source"""
        try:
            async with self.session.get(source["url"]) as response:
                if response.status == 200:
                    content = await response.text()
                    result["accessibility"] = "accessible"
                    result["status"] = "success"
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Get page text
                    page_text = soup.get_text().lower()
                    
                    # Check for AI and Africa content
                    ai_found = any(kw.lower() in page_text for kw in source["keywords"])
                    result["ai_content_found"] = ai_found
                    
                    africa_terms = ['africa', 'african', 'nigeria', 'kenya', 'south africa', 'ghana']
                    africa_found = any(term in page_text for term in africa_terms)
                    result["africa_content_found"] = africa_found
                    
                    # Look for structured data
                    if soup.find_all(['script'], {'type': 'application/ld+json'}):
                        result["data_format"] = "structured_data"
                        result["parsing_difficulty"] = "medium"
                    elif soup.find_all(['table', 'ul', 'ol']):
                        result["data_format"] = "semi_structured"
                        result["parsing_difficulty"] = "medium"
                    else:
                        result["data_format"] = "unstructured"
                        result["parsing_difficulty"] = "hard"
                    
                    # Sample some content
                    titles = soup.find_all(['h1', 'h2', 'h3'], limit=3)
                    for title in titles:
                        if title.get_text():
                            sample = {
                                "title": title.get_text().strip()[:100],
                                "type": "heading",
                                "relevant": ai_found and africa_found
                            }
                            result["sample_entries"].append(sample)
                    
                    # Set recommendations
                    if result["ai_content_found"] and result["africa_content_found"]:
                        if result["parsing_difficulty"] == "medium":
                            result["recommendations"] = ["High priority - develop custom parser", "Structured scraping needed"]
                        else:
                            result["recommendations"] = ["Medium priority - complex parsing required", "Consider manual monitoring"]
                    else:
                        result["recommendations"] = ["Low priority - limited relevant content"]
                        
                else:
                    result["accessibility"] = f"http_error_{response.status}"
                    result["status"] = "error"
                    result["errors"].append(f"HTTP {response.status}")
                    
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Web analysis failed: {str(e)}")
            
        return result
    
    def print_source_result(self, result):
        """Print analysis result for a source"""
        status_emoji = "✅" if result["status"] == "success" else "❌"
        print(f"{status_emoji} Status: {result['status']}")
        print(f"🌐 Accessibility: {result['accessibility']}")
        print(f"📄 Data Format: {result['data_format']}")
        print(f"🔧 Parsing Difficulty: {result['parsing_difficulty']}")
        print(f"🤖 AI Content: {'Yes' if result['ai_content_found'] else 'No'}")
        print(f"🌍 Africa Content: {'Yes' if result['africa_content_found'] else 'No'}")
        
        if result["sample_entries"]:
            print("📋 Sample Content:")
            for i, sample in enumerate(result["sample_entries"][:2]):
                print(f"  {i+1}. {sample.get('title', 'No title')[:80]}...")
        
        if result["recommendations"]:
            print("💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"  • {rec}")
        
        if result["errors"]:
            print("⚠️  Errors:")
            for error in result["errors"]:
                print(f"  • {error}")
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "=" * 60)
        print("📊 FUNDING SOURCES ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Categorize sources
        easy_sources = []
        medium_sources = []
        hard_sources = []
        failed_sources = []
        
        for result in self.results:
            if result["status"] != "success":
                failed_sources.append(result)
            elif result["parsing_difficulty"] == "easy":
                easy_sources.append(result)
            elif result["parsing_difficulty"] == "medium":
                medium_sources.append(result)
            else:
                hard_sources.append(result)
        
        print(f"\n🟢 LOW HANGING FRUIT (Easy Implementation) - {len(easy_sources)} sources:")
        for source in easy_sources:
            relevance = "High" if source["ai_content_found"] and source["africa_content_found"] else "Medium" if source["ai_content_found"] else "Low"
            print(f"  ✅ {source['name']} - {source['data_format']} - Relevance: {relevance}")
        
        print(f"\n🟡 MEDIUM EFFORT (Custom Parsing Needed) - {len(medium_sources)} sources:")
        for source in medium_sources:
            relevance = "High" if source["ai_content_found"] and source["africa_content_found"] else "Medium" if source["ai_content_found"] else "Low"
            print(f"  🔧 {source['name']} - {source['data_format']} - Relevance: {relevance}")
        
        print(f"\n🔴 HIGH EFFORT (Complex Development) - {len(hard_sources)} sources:")
        for source in hard_sources:
            relevance = "High" if source["ai_content_found"] and source["africa_content_found"] else "Medium" if source["ai_content_found"] else "Low"
            print(f"  🛠️  {source['name']} - {source['data_format']} - Relevance: {relevance}")
        
        print(f"\n❌ FAILED TO ACCESS - {len(failed_sources)} sources:")
        for source in failed_sources:
            print(f"  💥 {source['name']} - {', '.join(source['errors'])}")
        
        print(f"\n🎯 IMPLEMENTATION PRIORITY:")
        print("1. Start with LOW HANGING FRUIT sources")
        print("2. Implement RSS monitors for easy sources")
        print("3. Develop custom parsers for medium effort sources")
        print("4. Consider manual monitoring for hard sources initially")
        
        # Save results to file
        with open("source_analysis_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: source_analysis_results.json")

async def main():
    analyzer = SourceAnalyzer()
    await analyzer.analyze_all_sources()

if __name__ == "__main__":
    asyncio.run(main())
