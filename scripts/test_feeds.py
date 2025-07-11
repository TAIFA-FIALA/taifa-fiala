#!/usr/bin/env python3
"""
Test the discovered RSS feeds for AI Africa funding content
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime
import json

# Discovered feeds to test
DISCOVERED_FEEDS = [
    {
        "name": "IDRC (AI4D Program)",
        "url": "https://idrc-crdi.ca/rss.xml",
        "funding_page": "https://idrc-crdi.ca/en/funding",
        "priority": "HIGH",
        "ai_keywords": ["AI", "artificial intelligence", "machine learning", "AI4D", "digital", "technology"],
        "africa_keywords": ["Africa", "African", "Nigeria", "Kenya", "Ghana", "South Africa", "Rwanda", "Uganda"]
    },
    {
        "name": "Science for Africa Foundation",
        "url": "https://scienceforafrica.foundation/rss.xml", 
        "funding_page": "https://scienceforafrica.foundation/funding",
        "priority": "HIGH",
        "ai_keywords": ["AI", "artificial intelligence", "innovation", "technology", "digital"],
        "africa_keywords": ["Africa", "African", "continent", "sub-saharan"]
    }
]

# Key funding pages to monitor
FUNDING_PAGES = [
    {
        "name": "Milken-Motsepe Innovation Prize",
        "url": "https://www.milkeninstitute.org/philanthropy/environmental-and-social-innovation/innovation-prize-programs/milken-motsepe-prize-program",
        "priority": "MEDIUM",
        "type": "web_page"
    }
]

async def test_feeds():
    """Test the discovered RSS feeds"""
    print("🧪 Testing Discovered RSS Feeds for AI Africa Content")
    print("=" * 65)
    
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={'User-Agent': 'AI-Africa-Funding-Tracker/1.0'}
    )
    
    results = []
    
    try:
        for feed_info in DISCOVERED_FEEDS:
            print(f"\n🔬 Testing: {feed_info['name']}")
            print("-" * 50)
            
            result = await test_single_feed(session, feed_info)
            results.append(result)
            print_feed_results(result)
            
    finally:
        await session.close()
    
    print_implementation_plan(results)
    
    # Save results
    with open("feed_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Test results saved to: feed_test_results.json")

async def test_single_feed(session, feed_info):
    """Test a single RSS feed"""
    result = {
        "name": feed_info["name"],
        "url": feed_info["url"],
        "priority": feed_info["priority"],
        "status": "unknown",
        "total_entries": 0,
        "ai_relevant_entries": 0,
        "africa_relevant_entries": 0,
        "both_relevant_entries": 0,
        "sample_relevant_entries": [],
        "sample_all_entries": [],
        "recommendation": "",
        "errors": []
    }
    
    try:
        # Fetch the RSS feed
        async with session.get(feed_info["url"]) as response:
            if response.status == 200:
                content = await response.text()
                result["status"] = "accessible"
                
                # Parse the feed
                feed = feedparser.parse(content)
                result["total_entries"] = len(feed.entries)
                
                if feed.entries:
                    # Analyze entries
                    for entry in feed.entries:
                        entry_text = (
                            getattr(entry, 'title', '') + ' ' + 
                            getattr(entry, 'summary', '') + ' ' +
                            getattr(entry, 'description', '')
                        ).lower()
                        
                        # Check for AI content
                        ai_relevant = any(keyword.lower() in entry_text for keyword in feed_info["ai_keywords"])
                        if ai_relevant:
                            result["ai_relevant_entries"] += 1
                        
                        # Check for Africa content
                        africa_relevant = any(keyword.lower() in entry_text for keyword in feed_info["africa_keywords"])
                        if africa_relevant:
                            result["africa_relevant_entries"] += 1
                        
                        # Check for both
                        if ai_relevant and africa_relevant:
                            result["both_relevant_entries"] += 1
                            if len(result["sample_relevant_entries"]) < 3:
                                result["sample_relevant_entries"].append({
                                    "title": getattr(entry, 'title', 'No title'),
                                    "published": getattr(entry, 'published', 'No date'),
                                    "link": getattr(entry, 'link', 'No link'),
                                    "summary": getattr(entry, 'summary', 'No summary')[:200] + "..."
                                })
                        
                        # Save sample of all entries
                        if len(result["sample_all_entries"]) < 5:
                            result["sample_all_entries"].append({
                                "title": getattr(entry, 'title', 'No title'),
                                "published": getattr(entry, 'published', 'No date'),
                                "ai_relevant": ai_relevant,
                                "africa_relevant": africa_relevant
                            })
                    
                    # Generate recommendation
                    if result["both_relevant_entries"] > 0:
                        relevance_rate = (result["both_relevant_entries"] / result["total_entries"]) * 100
                        if relevance_rate > 10:
                            result["recommendation"] = f"HIGH PRIORITY - {relevance_rate:.1f}% relevance rate"
                        elif relevance_rate > 5:
                            result["recommendation"] = f"MEDIUM PRIORITY - {relevance_rate:.1f}% relevance rate"
                        else:
                            result["recommendation"] = f"LOW PRIORITY - {relevance_rate:.1f}% relevance rate"
                    else:
                        result["recommendation"] = "NOT RECOMMENDED - No AI+Africa content found"
                        
                else:
                    result["recommendation"] = "EMPTY FEED - No entries found"
                    result["errors"].append("RSS feed is empty")
            else:
                result["status"] = f"http_error_{response.status}"
                result["errors"].append(f"HTTP {response.status}")
                
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        
    return result

def print_feed_results(result):
    """Print results for one feed"""
    status_emoji = "✅" if result["status"] == "accessible" else "❌"
    print(f"{status_emoji} Status: {result['status']}")
    print(f"📊 Total entries: {result['total_entries']}")
    print(f"🤖 AI relevant: {result['ai_relevant_entries']}")
    print(f"🌍 Africa relevant: {result['africa_relevant_entries']}")
    print(f"🎯 Both AI+Africa: {result['both_relevant_entries']}")
    print(f"💡 Recommendation: {result['recommendation']}")
    
    if result["sample_relevant_entries"]:
        print("\n🔥 Sample Relevant Entries:")
        for i, entry in enumerate(result["sample_relevant_entries"], 1):
            print(f"  {i}. {entry['title']}")
            print(f"     Published: {entry['published']}")
            print(f"     Link: {entry['link']}")
            print()
    
    if result["errors"]:
        print("⚠️  Errors:")
        for error in result["errors"]:
            print(f"  • {error}")

def print_implementation_plan(results):
    """Print implementation priority plan"""
    print("\n" + "=" * 65)
    print("🎯 IMPLEMENTATION PRIORITY PLAN")
    print("=" * 65)
    
    # Categorize feeds
    high_priority = [r for r in results if "HIGH PRIORITY" in r["recommendation"]]
    medium_priority = [r for r in results if "MEDIUM PRIORITY" in r["recommendation"]]
    low_priority = [r for r in results if "LOW PRIORITY" in r["recommendation"]]
    not_recommended = [r for r in results if "NOT RECOMMENDED" in r["recommendation"]]
    
    print(f"\n🟢 IMMEDIATE IMPLEMENTATION ({len(high_priority)} feeds):")
    for result in high_priority:
        print(f"  ✅ {result['name']}")
        print(f"     URL: {result['url']}")
        print(f"     Impact: {result['both_relevant_entries']} relevant entries found")
        print(f"     Action: Implement RSS monitor immediately")
        print()
    
    print(f"🟡 SECONDARY PRIORITY ({len(medium_priority)} feeds):")
    for result in medium_priority:
        print(f"  🔧 {result['name']}")
        print(f"     URL: {result['url']}")
        print(f"     Impact: {result['both_relevant_entries']} relevant entries found")
        print(f"     Action: Implement after high priority feeds")
        print()
    
    print(f"🟠 LOW PRIORITY ({len(low_priority)} feeds):")
    for result in low_priority:
        print(f"  📋 {result['name']}")
        print(f"     Action: Monitor manually or implement later")
        print()
    
    print(f"🔴 NOT RECOMMENDED ({len(not_recommended)} feeds):")
    for result in not_recommended:
        print(f"  ❌ {result['name']}")
        print(f"     Reason: {result['recommendation']}")
        print()
    
    if high_priority:
        print("🚀 NEXT STEPS:")
        print("1. Implement RSS monitors for HIGH PRIORITY feeds")
        print("2. Set up automated parsing and classification")
        print("3. Configure database storage for new opportunities")
        print("4. Test end-to-end data flow")
        print("5. Add monitoring dashboard for feed health")

if __name__ == "__main__":
    asyncio.run(test_feeds())
