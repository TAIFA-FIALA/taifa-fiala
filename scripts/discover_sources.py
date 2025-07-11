#!/usr/bin/env python3
"""
Source Discovery Script - Find current RSS feeds and funding pages
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import json

# Organizations to investigate
ORGANIZATIONS = [
    {
        "name": "IDRC (International Development Research Centre)",
        "main_url": "https://idrc-crdi.ca/",
        "search_terms": ["funding", "opportunities", "grants", "ai", "artificial intelligence"],
        "likely_paths": ["/en/funding", "/funding", "/grants", "/opportunities", "/calls"]
    },
    {
        "name": "Science for Africa Foundation", 
        "main_url": "https://scienceforafrica.foundation/",
        "search_terms": ["funding", "grants", "calls", "opportunities"],
        "likely_paths": ["/funding", "/grants", "/opportunities", "/calls", "/funding-resources"]
    },
    {
        "name": "Gates Foundation",
        "main_url": "https://www.gatesfoundation.org/",
        "search_terms": ["funding", "grants", "opportunities", "calls"],
        "likely_paths": ["/our-work", "/funding", "/grants", "/opportunities"]
    },
    {
        "name": "Milken Institute",
        "main_url": "https://www.milkeninstitute.org/",
        "search_terms": ["motsepe", "prize", "innovation", "africa"],
        "likely_paths": ["/prizes", "/motsepe-prize", "/programs", "/initiatives"]
    }
]

class SourceDiscovery:
    def __init__(self):
        self.session = None
        self.results = {}
        
    async def discover_all_sources(self):
        """Discover RSS feeds and funding pages for all organizations"""
        print("🔍 Discovering Current Funding Sources")
        print("=" * 60)
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'AI-Africa-Funding-Tracker-Discovery/1.0'}
        )
        
        try:
            for org in ORGANIZATIONS:
                print(f"\n🏢 Investigating: {org['name']}")
                print("-" * 50)
                
                result = await self.discover_organization(org)
                self.results[org['name']] = result
                self.print_org_results(result)
                
        finally:
            if self.session:
                await self.session.close()
        
        # Print summary and save results
        self.print_discovery_summary()
        
    async def discover_organization(self, org):
        """Discover feeds and pages for one organization"""
        result = {
            "name": org["name"],
            "main_url": org["main_url"],
            "main_site_accessible": False,
            "rss_feeds": [],
            "funding_pages": [],
            "relevant_pages": [],
            "errors": []
        }
        
        try:
            # Check main site
            main_content = await self.fetch_page(org["main_url"])
            if main_content:
                result["main_site_accessible"] = True
                
                # Look for RSS feeds
                rss_feeds = await self.find_rss_feeds(org["main_url"], main_content)
                result["rss_feeds"] = rss_feeds
                
                # Look for funding-related pages
                funding_pages = await self.find_funding_pages(org["main_url"], main_content, org["search_terms"])
                result["funding_pages"] = funding_pages
                
                # Try likely paths
                for path in org["likely_paths"]:
                    full_url = urljoin(org["main_url"], path)
                    page_content = await self.fetch_page(full_url)
                    if page_content:
                        # Check if it's funding-related
                        if self.is_funding_relevant(page_content, org["search_terms"]):
                            result["relevant_pages"].append({
                                "url": full_url,
                                "title": self.extract_title(page_content),
                                "type": "funding_page"
                            })
            else:
                result["errors"].append("Cannot access main website")
                
        except Exception as e:
            result["errors"].append(f"Discovery failed: {str(e)}")
            
        return result
    
    async def fetch_page(self, url):
        """Fetch a web page"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
        except:
            pass
        return None
    
    async def find_rss_feeds(self, base_url, content):
        """Find RSS feeds on a page"""
        feeds = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for RSS links in <link> tags
        for link in soup.find_all('link', {'type': ['application/rss+xml', 'application/atom+xml']}):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                feeds.append({
                    "url": full_url,
                    "title": link.get('title', 'RSS Feed'),
                    "type": link.get('type', 'rss')
                })
        
        # Look for RSS links in anchor tags
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and any(rss_term in href.lower() for rss_term in ['rss', 'feed', 'atom']):
                full_url = urljoin(base_url, href)
                feeds.append({
                    "url": full_url,
                    "title": link.get_text().strip() or 'RSS Feed',
                    "type": "discovered"
                })
        
        # Test common RSS paths
        common_rss_paths = ['/rss', '/feed', '/rss.xml', '/feed.xml', '/atom.xml', '/rss/', '/feed/']
        for path in common_rss_paths:
            rss_url = urljoin(base_url, path)
            if await self.test_rss_feed(rss_url):
                feeds.append({
                    "url": rss_url,
                    "title": f"RSS Feed ({path})",
                    "type": "common_path"
                })
        
        return feeds
    
    async def test_rss_feed(self, url):
        """Test if a URL is a valid RSS feed"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return any(tag in content.lower() for tag in ['<rss', '<feed', '<atom'])
        except:
            pass
        return False
    
    async def find_funding_pages(self, base_url, content, search_terms):
        """Find funding-related pages"""
        pages = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for links with funding-related text
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().lower()
            
            if href and any(term in text for term in search_terms):
                full_url = urljoin(base_url, href)
                pages.append({
                    "url": full_url,
                    "title": link.get_text().strip(),
                    "relevance_score": sum(1 for term in search_terms if term in text)
                })
        
        # Sort by relevance
        pages.sort(key=lambda x: x["relevance_score"], reverse=True)
        return pages[:10]  # Top 10 most relevant
    
    def is_funding_relevant(self, content, search_terms):
        """Check if page content is funding-relevant"""
        content_lower = content.lower()
        return sum(content_lower.count(term) for term in search_terms) > 2
    
    def extract_title(self, content):
        """Extract page title"""
        soup = BeautifulSoup(content, 'html.parser')
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else "No title"
    
    def print_org_results(self, result):
        """Print results for one organization"""
        if result["main_site_accessible"]:
            print("✅ Main site accessible")
        else:
            print("❌ Main site not accessible")
            
        if result["rss_feeds"]:
            print(f"📡 Found {len(result['rss_feeds'])} RSS feeds:")
            for feed in result["rss_feeds"][:3]:
                print(f"  • {feed['title']}: {feed['url']}")
        else:
            print("📡 No RSS feeds found")
            
        if result["funding_pages"]:
            print(f"💰 Found {len(result['funding_pages'])} funding pages:")
            for page in result["funding_pages"][:3]:
                print(f"  • {page['title']}: {page['url']}")
        else:
            print("💰 No funding pages found")
            
        if result["relevant_pages"]:
            print(f"🔗 Found {len(result['relevant_pages'])} relevant pages:")
            for page in result["relevant_pages"][:3]:
                print(f"  • {page['title']}: {page['url']}")
                
        if result["errors"]:
            print("⚠️  Errors:")
            for error in result["errors"]:
                print(f"  • {error}")
    
    def print_discovery_summary(self):
        """Print discovery summary"""
        print("\n" + "=" * 60)
        print("📊 SOURCE DISCOVERY SUMMARY")
        print("=" * 60)
        
        total_rss_feeds = sum(len(org["rss_feeds"]) for org in self.results.values())
        total_funding_pages = sum(len(org["funding_pages"]) for org in self.results.values())
        accessible_orgs = sum(1 for org in self.results.values() if org["main_site_accessible"])
        
        print(f"🏢 Organizations analyzed: {len(self.results)}")
        print(f"✅ Accessible organizations: {accessible_orgs}")
        print(f"📡 Total RSS feeds found: {total_rss_feeds}")
        print(f"💰 Total funding pages found: {total_funding_pages}")
        
        print("\n🎯 RECOMMENDED NEXT STEPS:")
        
        # Find best RSS feeds
        best_feeds = []
        for org_name, org_data in self.results.items():
            for feed in org_data["rss_feeds"]:
                best_feeds.append(f"{org_name}: {feed['url']}")
        
        if best_feeds:
            print("1. Test these RSS feeds first:")
            for feed in best_feeds[:5]:
                print(f"   • {feed}")
        
        # Find best funding pages
        best_pages = []
        for org_name, org_data in self.results.items():
            for page in org_data["funding_pages"][:2]:
                best_pages.append(f"{org_name}: {page['url']}")
        
        if best_pages:
            print("2. Monitor these funding pages:")
            for page in best_pages[:5]:
                print(f"   • {page}")
        
        print("3. Consider manual monitoring for organizations without RSS feeds")
        print("4. Set up change detection for funding pages")
        
        # Save results
        with open("source_discovery_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Discovery results saved to: source_discovery_results.json")

async def main():
    discovery = SourceDiscovery()
    await discovery.discover_all_sources()

if __name__ == "__main__":
    asyncio.run(main())
