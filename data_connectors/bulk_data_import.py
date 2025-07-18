#!/usr/bin/env python3
"""
Bulk Data Import Script for AI Africa Funding Tracker Demo
This script rapidly imports intelligence feed from multiple sources for demo purposes.
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.connector import DatabaseConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BulkDataImporter:
    """Bulk data importer for demo purposes"""
    
    def __init__(self):
        self.db_connector = None
        self.session = None
        
    async def initialize(self):
        """Initialize database connection"""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        self.db_connector = DatabaseConnector(database_url)
        await self.db_connector.initialize()
        
        self.session = aiohttp.ClientSession()
        logger.info("✅ Bulk data importer initialized")
    
    async def import_sample_africa_intelligence_feed(self):
        """Import sample intelligence feed for demo"""
        
        sample_opportunities = [
            {
                "title": "Google AI for Social Good Africa Program 2025",
                "description": "Google's AI for Social Good initiative is seeking African startups and organizations developing AI solutions for social impact. Focus areas include healthcare, education, agriculture, and climate change. Up to $100,000 in funding plus technical support.",
                "source_name": "Google AI for Social Good",
                "source_url": "https://ai.google/social-good/",
                "deadline": "2025-09-15",
                "amount": "$100,000",
                "location": "Africa",
                "eligibility": "African startups and organizations",
                "keywords": ["AI", "social good", "Africa", "healthcare", "education", "agriculture", "climate"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "Microsoft AI for Good Lab - Africa Initiative",
                "description": "Microsoft's AI for Good Lab is launching an Africa-focused initiative to support AI research and development addressing local challenges. Provides cloud credits, technical mentorship, and potential funding up to $250,000 for selected projects.",
                "source_name": "Microsoft AI for Good",
                "source_url": "https://www.microsoft.com/ai/ai-for-good",
                "deadline": "2025-08-30",
                "amount": "$250,000",
                "location": "Africa",
                "eligibility": "African researchers and organizations",
                "keywords": ["AI", "Microsoft", "Africa", "research", "development", "cloud"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "African Development Bank Digital Innovation Challenge",
                "description": "The AfDB is launching a digital innovation challenge focused on AI and blockchain solutions for financial inclusion across Africa. Winners receive up to $500,000 in funding plus mentorship and market access support.",
                "source_name": "African Development Bank",
                "source_url": "https://www.afdb.org/en",
                "deadline": "2025-10-01",
                "amount": "$500,000",
                "location": "Africa",
                "eligibility": "African fintech companies",
                "keywords": ["AI", "blockchain", "fintech", "financial inclusion", "Africa", "AfDB"],
                "category": "Challenge",
                "priority": "high"
            },
            {
                "title": "IDRC AI4D (Artificial Intelligence for Development) Africa Fund",
                "description": "IDRC's AI4D initiative supports research and innovation in artificial intelligence for development across Africa. Funding ranges from $50,000 to $200,000 for projects addressing local development challenges through AI applications.",
                "source_name": "IDRC",
                "source_url": "https://idrc-crdi.ca/en/funding",
                "deadline": "2025-11-15",
                "amount": "$200,000",
                "location": "Africa",
                "eligibility": "African researchers and institutions",
                "keywords": ["AI4D", "IDRC", "Africa", "development", "research", "innovation"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "Mozilla Foundation Africa Mradi Research Grants",
                "description": "Mozilla's Africa Mradi program supports community-led research on AI, data governance, and digital rights in Africa. Grants range from $10,000 to $75,000 for projects promoting digital equity and inclusion.",
                "source_name": "Mozilla Foundation",
                "source_url": "https://foundation.mozilla.org/en/",
                "deadline": "2025-12-01",
                "amount": "$75,000",
                "location": "Africa",
                "eligibility": "African civil society organizations",
                "keywords": ["Mozilla", "Africa", "AI", "data governance", "digital rights", "equity"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "Gates Foundation Grand Challenges AI in Health",
                "description": "The Gates Foundation's Grand Challenges program is seeking AI solutions for global health challenges, with special focus on applications in sub-Saharan Africa. Funding up to $1,000,000 for breakthrough innovations.",
                "source_name": "Gates Foundation",
                "source_url": "https://grandchallenges.org/",
                "deadline": "2025-09-30",
                "amount": "$1,000,000",
                "location": "Sub-Saharan Africa",
                "eligibility": "Global applicants with Africa focus",
                "keywords": ["Gates Foundation", "AI", "health", "Africa", "innovation", "breakthrough"],
                "category": "Challenge",
                "priority": "high"
            },
            {
                "title": "World Bank Digital Africa Initiative",
                "description": "The World Bank's Digital Africa initiative supports digital transformation projects across the continent, with specific funding streams for AI and machine learning applications in governance, agriculture, and education.",
                "source_name": "World Bank",
                "source_url": "https://www.worldbank.org/en/region/afr",
                "deadline": "2025-08-15",
                "amount": "$300,000",
                "location": "Africa",
                "eligibility": "African governments and organizations",
                "keywords": ["World Bank", "digital transformation", "AI", "governance", "agriculture", "education"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "OpenAI Startup Fund Africa Expansion",
                "description": "OpenAI's Startup Fund is expanding to Africa, seeking startups building AI-powered solutions for local and global markets. Provides funding from $100,000 to $5,000,000 plus access to OpenAI's latest models and technical support.",
                "source_name": "OpenAI",
                "source_url": "https://openai.com/fund/",
                "deadline": "2025-10-31",
                "amount": "$5,000,000",
                "location": "Africa",
                "eligibility": "African AI startups",
                "keywords": ["OpenAI", "startup fund", "Africa", "AI models", "technical support"],
                "category": "Investment",
                "priority": "high"
            },
            {
                "title": "UN Women Africa AI Gender Equality Fund",
                "description": "UN Women launches AI fund focused on gender equality and women's empowerment in Africa. Supports AI projects that address gender-based violence, economic empowerment, and women's health. Funding up to $150,000.",
                "source_name": "UN Women",
                "source_url": "https://www.unwomen.org/",
                "deadline": "2025-09-01",
                "amount": "$150,000",
                "location": "Africa",
                "eligibility": "Women-led organizations in Africa",
                "keywords": ["UN Women", "AI", "gender equality", "women empowerment", "Africa", "health"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "African Union STISA-2024 AI Innovation Fund",
                "description": "The African Union's Science, Technology and Innovation Strategy for Africa 2024 (STISA-2024) launches AI innovation fund to support continental AI development. Funding ranges from $25,000 to $400,000 for collaborative projects.",
                "source_name": "African Union",
                "source_url": "https://au.int/",
                "deadline": "2025-11-30",
                "amount": "$400,000",
                "location": "Africa",
                "eligibility": "African Union member states",
                "keywords": ["African Union", "STISA-2024", "AI innovation", "continental development", "collaboration"],
                "category": "Grant",
                "priority": "high"
            },
            {
                "title": "Meta AI Research Collaborations Africa Program",
                "description": "Meta's AI Research division is establishing partnerships with African universities and research institutions. Provides funding, compute resources, and research collaboration opportunities. Up to $200,000 per project.",
                "source_name": "Meta AI Research",
                "source_url": "https://ai.meta.com/research/",
                "deadline": "2025-12-15",
                "amount": "$200,000",
                "location": "Africa",
                "eligibility": "African universities and research institutions",
                "keywords": ["Meta", "AI research", "Africa", "universities", "collaboration", "compute"],
                "category": "Partnership",
                "priority": "medium"
            },
            {
                "title": "USAID Digital Development Africa AI Fund",
                "description": "USAID's Digital Development initiative launches AI fund for African organizations developing digital solutions for development challenges. Focus on health, education, agriculture, and governance. Funding up to $300,000.",
                "source_name": "USAID",
                "source_url": "https://www.usaid.gov/digital-development",
                "deadline": "2025-08-01",
                "amount": "$300,000",
                "location": "Africa",
                "eligibility": "African development organizations",
                "keywords": ["USAID", "digital development", "AI", "health", "education", "agriculture", "governance"],
                "category": "Grant",
                "priority": "high"
            }
        ]
        
        logger.info(f"📝 Importing {len(sample_opportunities)} sample intelligence feed...")
        
        # Convert to the format expected by the database
        formatted_opportunities = []
        for opp in sample_opportunities:
            formatted_opp = {
                "title": opp["title"],
                "description": opp["description"],
                "source_name": opp["source_name"],
                "source_url": opp["source_url"],
                "published_date": datetime.now().isoformat(),
                "deadline": opp.get("deadline"),
                "amount": opp.get("amount"),
                "location": opp.get("location"),
                "eligibility": opp.get("eligibility"),
                "keywords": ", ".join(opp.get("keywords", [])),
                "category": opp.get("category", "Grant"),
                "priority": opp.get("priority", "medium"),
                "url": opp["source_url"],
                "content": opp["description"]
            }
            formatted_opportunities.append(formatted_opp)
        
        # Save to database
        result = await self.db_connector.save_opportunities(formatted_opportunities, "bulk_import")
        
        logger.info(f"✅ Bulk import completed: {result['saved']} saved, {result['duplicates']} duplicates, {result['errors']} errors")
        return result
    
    async def import_african_tech_ecosystem_data(self):
        """Import African tech ecosystem funding data"""
        
        ecosystem_data = [
            {
                "title": "Techstars Africa Accelerator Program 2025",
                "description": "Techstars is launching its first Africa-focused accelerator program with emphasis on AI and fintech startups. Provides $100,000 investment plus mentorship and global network access.",
                "source_name": "Techstars",
                "source_url": "https://www.techstars.com/",
                "deadline": "2025-07-31",
                "amount": "$100,000",
                "location": "Africa",
                "eligibility": "African startups",
                "keywords": ["Techstars", "accelerator", "Africa", "AI", "fintech", "startups"],
                "category": "Accelerator",
                "priority": "high"
            },
            {
                "title": "Y Combinator Africa Initiative",
                "description": "Y Combinator launches dedicated Africa initiative supporting AI and tech startups across the continent. Standard YC program with $500,000 funding and Silicon Valley mentorship.",
                "source_name": "Y Combinator",
                "source_url": "https://www.ycombinator.com/",
                "deadline": "2025-08-10",
                "amount": "$500,000",
                "location": "Africa",
                "eligibility": "African tech startups",
                "keywords": ["Y Combinator", "Africa", "AI", "tech startups", "Silicon Valley"],
                "category": "Accelerator",
                "priority": "high"
            },
            {
                "title": "Andreessen Horowitz Africa Fund",
                "description": "a16z announces $200M Africa fund focused on AI, fintech, and consumer technology startups. Investments range from $1M to $50M for growth-stage companies.",
                "source_name": "Andreessen Horowitz",
                "source_url": "https://a16z.com/",
                "deadline": "2025-12-31",
                "amount": "$50,000,000",
                "location": "Africa",
                "eligibility": "Growth-stage African startups",
                "keywords": ["a16z", "Africa fund", "AI", "fintech", "consumer tech", "growth-stage"],
                "category": "Investment",
                "priority": "high"
            },
            {
                "title": "Google for Startups Accelerator: AI-First Africa",
                "description": "Google's accelerator program specifically for AI-first startups in Africa. Equity-free program providing mentorship, Google Cloud credits, and potential follow-up funding.",
                "source_name": "Google for Startups",
                "source_url": "https://startup.google.com/programs/accelerator/",
                "deadline": "2025-09-15",
                "amount": "Equity-free",
                "location": "Africa",
                "eligibility": "African AI startups",
                "keywords": ["Google", "accelerator", "AI-first", "Africa", "equity-free", "cloud credits"],
                "category": "Accelerator",
                "priority": "high"
            },
            {
                "title": "TLcom Capital TIDE Africa Fund III",
                "description": "TLcom's third fund focused on African tech startups with AI and data-driven solutions. Invests $1M-$15M in Series A and B rounds across Africa.",
                "source_name": "TLcom Capital",
                "source_url": "https://tlcom.co.uk/",
                "deadline": "2025-11-30",
                "amount": "$15,000,000",
                "location": "Africa",
                "eligibility": "Series A/B African startups",
                "keywords": ["TLcom", "TIDE Africa", "AI", "data-driven", "Series A", "Series B"],
                "category": "Investment",
                "priority": "high"
            }
        ]
        
        logger.info(f"📝 Importing {len(ecosystem_data)} African tech ecosystem opportunities...")
        
        # Convert to the format expected by the database
        formatted_opportunities = []
        for opp in ecosystem_data:
            formatted_opp = {
                "title": opp["title"],
                "description": opp["description"],
                "source_name": opp["source_name"],
                "source_url": opp["source_url"],
                "published_date": datetime.now().isoformat(),
                "deadline": opp.get("deadline"),
                "amount": opp.get("amount"),
                "location": opp.get("location"),
                "eligibility": opp.get("eligibility"),
                "keywords": ", ".join(opp.get("keywords", [])),
                "category": opp.get("category", "Investment"),
                "priority": opp.get("priority", "medium"),
                "url": opp["source_url"],
                "content": opp["description"]
            }
            formatted_opportunities.append(formatted_opp)
        
        # Save to database
        result = await self.db_connector.save_opportunities(formatted_opportunities, "ecosystem_import")
        
        logger.info(f"✅ Ecosystem import completed: {result['saved']} saved, {result['duplicates']} duplicates, {result['errors']} errors")
        return result
    
    async def run_bulk_import(self):
        """Run complete bulk import for demo"""
        logger.info("🚀 Starting bulk data import for demo...")
        
        total_saved = 0
        total_duplicates = 0
        total_errors = 0
        
        # Import sample intelligence feed
        result1 = await self.import_sample_africa_intelligence_feed()
        total_saved += result1['saved']
        total_duplicates += result1['duplicates']
        total_errors += result1['errors']
        
        # Import African tech ecosystem data
        result2 = await self.import_african_tech_ecosystem_data()
        total_saved += result2['saved']
        total_duplicates += result2['duplicates']
        total_errors += result2['errors']
        
        logger.info(f"🎉 Bulk import completed!")
        logger.info(f"📊 Total Results: {total_saved} saved, {total_duplicates} duplicates, {total_errors} errors")
        
        return {
            "saved": total_saved,
            "duplicates": total_duplicates,
            "errors": total_errors
        }
    
    async def close(self):
        """Close connections"""
        if self.session:
            await self.session.close()
        if self.db_connector:
            await self.db_connector.close()
        logger.info("✅ Bulk data importer closed")

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
    
    importer = BulkDataImporter()
    try:
        await importer.initialize()
        result = await importer.run_bulk_import()
        print(f"\\n✅ DEMO DATA IMPORT COMPLETED!")
        print(f"📊 {result['saved']} opportunities added to your database")
        print(f"🎯 Ready for demo presentation!")
    except Exception as e:
        logger.error(f"❌ Bulk import failed: {e}")
    finally:
        await importer.close()

if __name__ == "__main__":
    asyncio.run(main())