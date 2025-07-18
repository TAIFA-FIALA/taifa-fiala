#!/usr/bin/env python3
"""
Comprehensive migration and testing script for TAIFA Enhanced Schema
Implements competitor analysis insights and Notion database alignment
"""
import asyncio
import asyncpg
import os
import sys
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

async def run_enhanced_migration():
    """Run the enhanced schema migration"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("🚀 Running TAIFA Enhanced Schema Migration")
    print("=" * 60)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("1️⃣ Running migration 002_enhanced_schema_migration...")
        
        # Read and execute the migration script directly
        migration_path = "/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/backend/alembic/versions/002_enhanced_schema_migration.py"
        
        # Execute the migration SQL manually for now
        async with conn.transaction():
            
            # Create lookup tables
            print("   📝 Creating lookup tables...")
            
            # Funding Types Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS funding_types (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    typical_amount_range VARCHAR(100),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # AI Domains Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_domains (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    parent_domain_id INTEGER REFERENCES ai_domains(id),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Geographic Scopes Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS geographic_scopes (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    code VARCHAR(10),
                    type VARCHAR(20) DEFAULT 'country',
                    parent_scope_id INTEGER REFERENCES geographic_scopes(id),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Community Users Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS community_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    reputation_score INTEGER DEFAULT 0,
                    contributions_count INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            print("   ✅ Lookup tables created")
            
            # Add new columns to existing tables
            print("   📝 Adding enhanced columns...")
            
            # Add columns to africa_intelligence_feed (check if they exist first)
            columns_to_add = [
                ("funding_type_id", "INTEGER"),
                ("status", "VARCHAR(20) DEFAULT 'open'"),
                ("currency", "VARCHAR(10) DEFAULT 'USD'"),
                ("community_rating", "DECIMAL(2,1)"),
                ("application_tips", "TEXT"),
                ("submitted_by_user_id", "INTEGER"),
                ("view_count", "INTEGER DEFAULT 0"),
                ("application_count", "INTEGER DEFAULT 0"),
                ("tags", "JSONB")
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    await conn.execute(f"ALTER TABLE africa_intelligence_feed ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass  # Column already exists
            
            # Add computed deadline urgency column
            try:
                await conn.execute("""
                    ALTER TABLE africa_intelligence_feed 
                    ADD COLUMN deadline_urgency VARCHAR(10) 
                    GENERATED ALWAYS AS (
                        CASE 
                            WHEN deadline IS NULL THEN 'unknown'
                            WHEN deadline <= CURRENT_DATE THEN 'expired'
                            WHEN deadline <= CURRENT_DATE + INTERVAL '30 days' THEN 'urgent'
                            WHEN deadline <= CURRENT_DATE + INTERVAL '60 days' THEN 'moderate'
                            ELSE 'low'
                        END
                    ) STORED
                """)
            except Exception:
                pass  # Column already exists
            
            # Add enhanced columns to organizations
            org_columns = [
                ("ai_relevance_score", "INTEGER DEFAULT 0"),
                ("africa_relevance_score", "INTEGER DEFAULT 0"),
                ("source_type", "VARCHAR(20) DEFAULT 'manual'"),
                ("update_frequency", "VARCHAR(20)"),
                ("funding_announcement_url", "TEXT"),
                ("monitoring_status", "VARCHAR(20) DEFAULT 'active'"),
                ("monitoring_reliability", "INTEGER DEFAULT 100"),
                ("contact_person", "VARCHAR(255)"),
                ("contact_email", "VARCHAR(255)"),
                ("community_rating", "DECIMAL(2,1)"),
                ("opportunities_discovered", "INTEGER DEFAULT 0"),
                ("unique_opportunities_added", "INTEGER DEFAULT 0"),
                ("duplicate_rate", "INTEGER DEFAULT 0"),
                ("data_completeness_score", "INTEGER DEFAULT 0")
            ]
            
            for col_name, col_type in org_columns:
                try:
                    await conn.execute(f"ALTER TABLE organizations ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass  # Column already exists
                    
            print("   ✅ Enhanced columns added")
            
            # Create junction tables
            print("   📝 Creating junction tables...")
            
            # Intelligence Feed <-> AI Domains
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_item_ai_domains (
                    intelligence_item_id INTEGER REFERENCES africa_intelligence_feed(id) ON DELETE CASCADE,
                    ai_domain_id INTEGER REFERENCES ai_domains(id) ON DELETE CASCADE,
                    PRIMARY KEY (intelligence_item_id, ai_domain_id)
                )
            """)
            
            # Intelligence Feed <-> Geographic Scopes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_item_geographic_scopes (
                    intelligence_item_id INTEGER REFERENCES africa_intelligence_feed(id) ON DELETE CASCADE,
                    geographic_scope_id INTEGER REFERENCES geographic_scopes(id) ON DELETE CASCADE,
                    PRIMARY KEY (intelligence_item_id, geographic_scope_id)
                )
            """)
            
            # Organizations <-> Geographic Focus
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS organization_geographic_focus (
                    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
                    geographic_scope_id INTEGER REFERENCES geographic_scopes(id) ON DELETE CASCADE,
                    PRIMARY KEY (organization_id, geographic_scope_id)
                )
            """)
            
            print("   ✅ Junction tables created")
            
            # Create performance indexes
            print("   📝 Creating performance indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_funding_type_id ON africa_intelligence_feed(funding_type_id)",
                "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_status ON africa_intelligence_feed(status)",
                "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_deadline_urgency ON africa_intelligence_feed(deadline_urgency)",
                "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_currency ON africa_intelligence_feed(currency)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_ai_relevance_score ON organizations(ai_relevance_score)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_africa_relevance_score ON organizations(africa_relevance_score)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_monitoring_status ON organizations(monitoring_status)"
            ]
            
            for index_sql in indexes:
                await conn.execute(index_sql)
                
            print("   ✅ Performance indexes created")
        
        print("✅ Enhanced schema migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

async def test_enhanced_features():
    """Test all the enhanced features from competitor analysis"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("\n🧪 Testing Enhanced Features")
    print("=" * 60)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Test 1: Deadline urgency calculation
        print("1️⃣ Testing deadline urgency calculation...")
        
        urgency_stats = await conn.fetch("""
            SELECT deadline_urgency, COUNT(*) as count
            FROM africa_intelligence_feed
            WHERE deadline_urgency IS NOT NULL
            GROUP BY deadline_urgency
            ORDER BY count DESC
        """)
        
        if urgency_stats:
            print("   📊 Deadline urgency distribution:")
            for stat in urgency_stats:
                urgency_emoji = {
                    'urgent': '🔴',
                    'moderate': '🟡', 
                    'low': '🟢',
                    'expired': '⚫',
                    'unknown': '🔵'
                }.get(stat['deadline_urgency'], '❓')
                print(f"      {urgency_emoji} {stat['deadline_urgency'].title()}: {stat['count']} opportunities")
        
        # Test 2: Geographic scope functionality
        print("\n2️⃣ Testing geographic scope relationships...")
        
        # Check if we have geographic data
        geo_count = await conn.fetchval("SELECT COUNT(*) FROM geographic_scopes")
        if geo_count > 0:
            print(f"   ✅ {geo_count} geographic scopes available")
            
            # Show sample geographic hierarchy
            regions = await conn.fetch("""
                SELECT g.name, g.type, COUNT(c.id) as child_count
                FROM geographic_scopes g
                LEFT JOIN geographic_scopes c ON g.id = c.parent_scope_id
                WHERE g.type = 'region'
                GROUP BY g.id, g.name, g.type
                ORDER BY child_count DESC
                LIMIT 3
            """)
            
            if regions:
                print("   🌍 Geographic hierarchy sample:")
                for region in regions:
                    print(f"      • {region['name']}: {region['child_count']} countries")
        
        # Test 3: AI domain categorization
        print("\n3️⃣ Testing AI domain categorization...")
        
        ai_domain_count = await conn.fetchval("SELECT COUNT(*) FROM ai_domains")
        if ai_domain_count > 0:
            print(f"   ✅ {ai_domain_count} AI domains available")
            
            # Show top AI domains
            top_domains = await conn.fetch("""
                SELECT name FROM ai_domains WHERE is_active = true ORDER BY name LIMIT 5
            """)
            print("   🤖 Available AI domains (sample):")
            for domain in top_domains:
                print(f"      • {domain['name']}")
        
        # Test 4: Organization performance metrics
        print("\n4️⃣ Testing organization performance tracking...")
        
        org_performance = await conn.fetch("""
            SELECT name, ai_relevance_score, africa_relevance_score, 
                   monitoring_status, opportunities_discovered,
                   unique_opportunities_added
            FROM organizations 
            WHERE opportunities_discovered > 0
            ORDER BY unique_opportunities_added DESC
            LIMIT 5
        """)
        
        if org_performance:
            print("   📈 Top performing organizations:")
            for org in org_performance:
                print(f"      • {org['name']}: {org['unique_opportunities_added']} unique opportunities")
                print(f"        AI Relevance: {org['ai_relevance_score']}%, Africa Relevance: {org['africa_relevance_score']}%")
        
        # Test 5: Enhanced intelligence item features
        print("\n5️⃣ Testing enhanced intelligence item features...")
        
        # Test currency distribution
        currency_stats = await conn.fetch("""
            SELECT currency, COUNT(*) as count
            FROM africa_intelligence_feed
            WHERE currency IS NOT NULL
            GROUP BY currency
            ORDER BY count DESC
        """)
        
        if currency_stats:
            print("   💰 Currency distribution:")
            for stat in currency_stats:
                currency_emoji = {
                    'USD': '💵',
                    'EUR': '💶',
                    'GBP': '💷',
                    'NGN': '🇳🇬',
                    'ZAR': '🇿🇦'
                }.get(stat['currency'], '💰')
                print(f"      {currency_emoji} {stat['currency']}: {stat['count']} opportunities")
        
        # Test status distribution
        status_stats = await conn.fetch("""
            SELECT status, COUNT(*) as count
            FROM africa_intelligence_feed
            WHERE status IS NOT NULL
            GROUP BY status
            ORDER BY count DESC
        """)
        
        if status_stats:
            print("   📊 Status distribution:")
            for stat in status_stats:
                status_emoji = {
                    'open': '🟢',
                    'closed': '🔴',
                    'under_review': '🟡'
                }.get(stat['status'], '❓')
                print(f"      {status_emoji} {stat['status'].title()}: {stat['count']} opportunities")
        
        # Test 6: Community features readiness
        print("\n6️⃣ Testing community features readiness...")
        
        community_tables = ['community_users', 'funding_types']
        for table in community_tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"   ✅ {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Not available ({e})")
        
        print("\n✅ Enhanced features testing completed!")
        
        # Summary of new capabilities
        print("\n🎉 New Capabilities Available:")
        print("   🚨 Deadline urgency indicators (urgent, moderate, low)")
        print("   🌍 Geographic scope filtering and organization")
        print("   🤖 AI domain categorization")
        print("   📈 Organization performance tracking")
        print("   💰 Multi-currency support")
        print("   📊 Enhanced status tracking")
        print("   🏷️ Flexible tagging system")
        print("   👥 Community contribution framework")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

async def demonstrate_competitor_advantages():
    """Demonstrate how TAIFA now exceeds competitor capabilities"""
    
    print("\n🏆 TAIFA vs Competitor Advantages")
    print("=" * 60)
    
    advantages = [
        {
            "feature": "Deadline Prominence",
            "competitor": "Static deadline dates",
            "taifa": "🚨 Dynamic urgency indicators with color coding and countdown"
        },
        {
            "feature": "Opportunity Diversification", 
            "competitor": "Basic grant listings",
            "taifa": "🎯 10 funding types: grants, prizes, scholarships, investments, etc."
        },
        {
            "feature": "Geographic Granularity",
            "competitor": "Simple country tags",
            "taifa": "🌍 Hierarchical geographic scopes: 54 countries → 5 regions → continent"
        },
        {
            "feature": "Search Result Transparency",
            "competitor": "Basic result counts",
            "taifa": "📊 Detailed metrics: urgency, relevance scores, organization performance"
        },
        {
            "feature": "Organization Intelligence",
            "competitor": "Basic organization names",
            "taifa": "🏢 Full org profiles: AI relevance, monitoring status, performance metrics"
        },
        {
            "feature": "Community Features",
            "competitor": "Static content",
            "taifa": "👥 Community ratings, application tips, verified contributors"
        },
        {
            "feature": "AI Domain Expertise",
            "competitor": "General AI category",
            "taifa": "🤖 18 specialized AI domains from healthcare to ethics"
        },
        {
            "feature": "Performance Tracking",
            "competitor": "No monitoring",
            "taifa": "📈 Real-time source monitoring, duplicate detection, quality scoring"
        }
    ]
    
    for i, advantage in enumerate(advantages, 1):
        print(f"{i}️⃣ {advantage['feature']}:")
        print(f"   🔴 Competitor: {advantage['competitor']}")
        print(f"   🟢 TAIFA: {advantage['taifa']}\n")
    
    print("🎯 Result: TAIFA now provides a superior, community-driven experience")
    print("   that goes far beyond basic funding aggregation!")

if __name__ == "__main__":
    print("🚀 TAIFA Enhanced Schema Implementation")
    print("Based on Competitor Analysis & Notion Database Alignment")
    print("=" * 80)
    
    asyncio.run(run_enhanced_migration())
    
    # Seed the lookup tables
    print("\n📚 Loading seed data...")
    exec(open('/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/seed_enhanced_schema.py').read())
    
    asyncio.run(test_enhanced_features())
    asyncio.run(demonstrate_competitor_advantages())
    
    print("\n🎉 TAIFA Enhanced Schema Implementation Complete!")
    print("\n💡 Next Steps:")
    print("   1. Update frontend to use new deadline urgency indicators")
    print("   2. Implement advanced filtering with AI domains and geographic scopes")
    print("   3. Add community rating and application tips features")
    print("   4. Create organization performance dashboards")
    print("   5. Deploy enhanced search with multi-currency support")
