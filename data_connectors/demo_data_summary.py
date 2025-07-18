#!/usr/bin/env python3
"""
Demo Data Summary Script
Shows current intelligence feed data for stakeholder demo
"""

import asyncio
import asyncpg
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DemoDataSummary:
    """Generate demo data summary for stakeholder presentation"""
    
    def __init__(self):
        self.db_pool = None
        
    async def initialize(self):
        """Initialize database connection"""
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
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create database connection pool
        self.db_pool = await asyncpg.create_pool(database_url)
        logger.info("✅ Database connection initialized")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        async with self.db_pool.acquire() as conn:
            stats = {}
            
            # Total opportunities count
            total_count = await conn.fetchval(
                "SELECT COUNT(*) FROM africa_intelligence_feed"
            )
            stats["total_opportunities"] = total_count
            
            # Opportunities by source
            source_stats = await conn.fetch("""
                SELECT source_name, COUNT(*) as count 
                FROM africa_intelligence_feed 
                GROUP BY source_name 
                ORDER BY count DESC
            """)
            stats["by_source"] = [{"source": row["source_name"], "count": row["count"]} for row in source_stats]
            
            # Recent opportunities (last 7 days)
            recent_count = await conn.fetchval("""
                SELECT COUNT(*) FROM africa_intelligence_feed 
                WHERE discovered_date >= NOW() - INTERVAL '7 days'
            """)
            stats["recent_opportunities"] = recent_count
            
            # Opportunities by category/type
            category_stats = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN LOWER(title) LIKE '%grant%' OR LOWER(title) LIKE '%funding%' THEN 'Grants'
                        WHEN LOWER(title) LIKE '%accelerator%' OR LOWER(title) LIKE '%incubator%' THEN 'Accelerators'
                        WHEN LOWER(title) LIKE '%investment%' OR LOWER(title) LIKE '%venture%' THEN 'Investment'
                        WHEN LOWER(title) LIKE '%research%' OR LOWER(title) LIKE '%fellowship%' THEN 'Research'
                        WHEN LOWER(title) LIKE '%challenge%' OR LOWER(title) LIKE '%competition%' THEN 'Challenges'
                        ELSE 'Other'
                    END as category,
                    COUNT(*) as count
                FROM africa_intelligence_feed
                GROUP BY category
                ORDER BY count DESC
            """)
            stats["by_category"] = [{"category": row["category"], "count": row["count"]} for row in category_stats]
            
            # AI-related opportunities
            ai_count = await conn.fetchval("""
                SELECT COUNT(*) FROM africa_intelligence_feed 
                WHERE LOWER(title) LIKE '%ai%' OR LOWER(title) LIKE '%artificial intelligence%' 
                OR LOWER(description) LIKE '%ai%' OR LOWER(description) LIKE '%artificial intelligence%'
            """)
            stats["ai_related"] = ai_count
            
            # Africa-related opportunities
            africa_count = await conn.fetchval("""
                SELECT COUNT(*) FROM africa_intelligence_feed 
                WHERE LOWER(title) LIKE '%africa%' OR LOWER(title) LIKE '%african%' 
                OR LOWER(description) LIKE '%africa%' OR LOWER(description) LIKE '%african%'
            """)
            stats["africa_related"] = africa_count
            
            # Top search queries
            query_stats = await conn.fetch("""
                SELECT 
                    search_query,
                    COUNT(*) as count
                FROM africa_intelligence_feed 
                WHERE search_query IS NOT NULL
                GROUP BY search_query
                ORDER BY count DESC
                LIMIT 10
            """)
            stats["top_keywords"] = [{"keyword": row["search_query"], "count": row["count"]} for row in query_stats if row["search_query"]]
            
            return stats
    
    async def get_sample_opportunities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample opportunities for demo"""
        async with self.db_pool.acquire() as conn:
            opportunities = await conn.fetch("""
                SELECT 
                    title, 
                    description, 
                    source_name, 
                    source_url,
                    discovered_date,
                    search_query,
                    application_url
                FROM africa_intelligence_feed 
                ORDER BY discovered_date DESC 
                LIMIT $1
            """, limit)
            
            return [
                {
                    "title": row["title"],
                    "description": row["description"][:200] + "..." if len(row["description"]) > 200 else row["description"],
                    "source": row["source_name"],
                    "url": row["source_url"] or row["application_url"],
                    "created_at": row["discovered_date"].isoformat() if row["discovered_date"] else None,
                    "keywords": row["search_query"]
                }
                for row in opportunities
            ]
    
    async def get_high_value_opportunities(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get high-value opportunities for demo"""
        async with self.db_pool.acquire() as conn:
            opportunities = await conn.fetch("""
                SELECT 
                    title, 
                    description, 
                    source_name, 
                    source_url,
                    discovered_date,
                    search_query,
                    application_url
                FROM africa_intelligence_feed 
                WHERE 
                    (LOWER(title) LIKE '%ai%' OR LOWER(title) LIKE '%artificial intelligence%')
                    AND (LOWER(title) LIKE '%africa%' OR LOWER(title) LIKE '%african%' OR LOWER(description) LIKE '%africa%')
                    AND (LOWER(title) LIKE '%funding%' OR LOWER(title) LIKE '%grant%' OR LOWER(title) LIKE '%program%')
                ORDER BY discovered_date DESC 
                LIMIT $1
            """, limit)
            
            return [
                {
                    "title": row["title"],
                    "description": row["description"][:300] + "..." if len(row["description"]) > 300 else row["description"],
                    "source": row["source_name"],
                    "url": row["source_url"] or row["application_url"],
                    "created_at": row["discovered_date"].isoformat() if row["discovered_date"] else None,
                    "keywords": row["search_query"]
                }
                for row in opportunities
            ]
    
    async def generate_demo_report(self) -> Dict[str, Any]:
        """Generate comprehensive demo report"""
        logger.info("📊 Generating demo data report...")
        
        # Get database statistics
        stats = await self.get_database_stats()
        
        # Get sample opportunities
        recent_opportunities = await self.get_sample_opportunities(15)
        
        # Get high-value opportunities
        high_value_opportunities = await self.get_high_value_opportunities(10)
        
        # Generate report
        report = {
            "generated_at": datetime.now().isoformat(),
            "database_stats": stats,
            "recent_opportunities": recent_opportunities,
            "high_value_opportunities": high_value_opportunities,
            "summary": {
                "total_opportunities": stats["total_opportunities"],
                "ai_related": stats["ai_related"],
                "africa_related": stats["africa_related"],
                "recent_count": stats["recent_opportunities"],
                "active_sources": len(stats["by_source"]),
                "coverage": f"{stats['ai_related']}/{stats['total_opportunities']} AI-related, {stats['africa_related']}/{stats['total_opportunities']} Africa-related"
            }
        }
        
        logger.info("✅ Demo report generated successfully")
        return report
    
    async def print_demo_summary(self):
        """Print formatted demo summary for stakeholder presentation"""
        report = await self.generate_demo_report()
        
        print("\\n" + "="*80)
        print("🎯 AI AFRICA FUNDING TRACKER - DEMO DATA SUMMARY")
        print("="*80)
        print(f"📅 Generated: {report['generated_at']}")
        print(f"🎯 For Demo Presentation: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Key metrics
        print("\\n📊 KEY METRICS:")
        print(f"   • Total Intelligence Feed: {report['summary']['total_opportunities']:,}")
        print(f"   • AI-Related Opportunities: {report['summary']['ai_related']:,}")
        print(f"   • Africa-Related Opportunities: {report['summary']['africa_related']:,}")
        print(f"   • Recent Opportunities (7 days): {report['summary']['recent_count']:,}")
        print(f"   • Active Data Sources: {report['summary']['active_sources']:,}")
        
        # Data sources
        print("\\n🌐 DATA SOURCES:")
        for source in report['database_stats']['by_source'][:10]:
            print(f"   • {source['source']}: {source['count']} opportunities")
        
        # Categories
        print("\\n📂 OPPORTUNITY CATEGORIES:")
        for category in report['database_stats']['by_category']:
            print(f"   • {category['category']}: {category['count']} opportunities")
        
        # Top keywords
        print("\\n🔍 TOP KEYWORDS:")
        for keyword in report['database_stats']['top_keywords'][:8]:
            if keyword['keyword'].strip():
                print(f"   • {keyword['keyword']}: {keyword['count']} mentions")
        
        # High-value opportunities
        print("\\n🎯 HIGH-VALUE OPPORTUNITIES (AI + Africa + Funding):")
        for i, opp in enumerate(report['high_value_opportunities'][:5], 1):
            print(f"   {i}. {opp['title']}")
            print(f"      Source: {opp['source']}")
            print(f"      Added: {opp['created_at'][:10] if opp['created_at'] else 'N/A'}")
            print()
        
        # Recent opportunities
        print("\\n📰 RECENT OPPORTUNITIES (Last Added):")
        for i, opp in enumerate(report['recent_opportunities'][:8], 1):
            print(f"   {i}. {opp['title']}")
            print(f"      Source: {opp['source']}")
            print(f"      Added: {opp['created_at'][:10] if opp['created_at'] else 'N/A'}")
            print()
        
        print("="*80)
        print("✅ DEMO READY: Database contains comprehensive funding data")
        print("🎯 STAKEHOLDER IMPACT: Real-time tracking of AI funding in Africa")
        print("🚀 NEXT STEPS: Present live dashboard and search capabilities")
        print("="*80)
    
    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()
        logger.info("✅ Database connection closed")

async def main():
    """Main function"""
    summary = DemoDataSummary()
    try:
        await summary.initialize()
        await summary.print_demo_summary()
    except Exception as e:
        logger.error(f"❌ Demo summary failed: {e}")
    finally:
        await summary.close()

if __name__ == "__main__":
    asyncio.run(main())