#!/usr/bin/env python3
"""
Step-by-step enhanced schema migration for TAIFA
Handles migration failures gracefully and applies changes incrementally
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def apply_migration_step_by_step():
    """Apply migration changes step by step with error handling"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("🔧 Step-by-Step Enhanced Schema Migration")
    print("=" * 60)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Step 1: Create lookup tables one by one
        print("1️⃣ Creating lookup tables...")
        
        tables = [
            {
                "name": "funding_types",
                "sql": """
                    CREATE TABLE IF NOT EXISTS funding_types (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL UNIQUE,
                        description TEXT,
                        typical_amount_range VARCHAR(100),
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
            },
            {
                "name": "ai_domains", 
                "sql": """
                    CREATE TABLE IF NOT EXISTS ai_domains (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        description TEXT,
                        parent_domain_id INTEGER,
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
            },
            {
                "name": "geographic_scopes",
                "sql": """
                    CREATE TABLE IF NOT EXISTS geographic_scopes (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        code VARCHAR(10),
                        type VARCHAR(20) DEFAULT 'country',
                        parent_scope_id INTEGER,
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
            },
            {
                "name": "community_users",
                "sql": """
                    CREATE TABLE IF NOT EXISTS community_users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE,
                        email VARCHAR(255) UNIQUE,
                        reputation_score INTEGER DEFAULT 0,
                        contributions_count INTEGER DEFAULT 0,
                        is_verified BOOLEAN DEFAULT false,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
            }
        ]
        
        for table in tables:
            try:
                await conn.execute(table["sql"])
                print(f"   ✅ {table['name']} table created")
            except Exception as e:
                print(f"   ⚠️  {table['name']} table: {e}")
        
        # Step 2: Add foreign key constraints
        print("\n2️⃣ Adding foreign key constraints...")
        
        constraints = [
            "ALTER TABLE ai_domains ADD CONSTRAINT fk_ai_domains_parent FOREIGN KEY (parent_domain_id) REFERENCES ai_domains(id)",
            "ALTER TABLE geographic_scopes ADD CONSTRAINT fk_geographic_scopes_parent FOREIGN KEY (parent_scope_id) REFERENCES geographic_scopes(id)"
        ]
        
        for constraint in constraints:
            try:
                await conn.execute(constraint)
                print(f"   ✅ Foreign key constraint added")
            except Exception as e:
                print(f"   ⚠️  Foreign key constraint: {e}")
        
        # Step 3: Add columns to africa_intelligence_feed
        print("\n3️⃣ Enhancing africa_intelligence_feed table...")
        
        opportunity_columns = [
            ("type_id", "INTEGER"),
            ("status", "VARCHAR(20) DEFAULT 'open'"),
            ("currency", "VARCHAR(10) DEFAULT 'USD'"),
            ("community_rating", "DECIMAL(2,1)"),
            ("application_tips", "TEXT"),
            ("submitted_by_user_id", "INTEGER"),
            ("view_count", "INTEGER DEFAULT 0"),
            ("application_count", "INTEGER DEFAULT 0"),
            ("tags", "JSONB")
        ]
        
        for col_name, col_def in opportunity_columns:
            try:
                await conn.execute(f"ALTER TABLE africa_intelligence_feed ADD COLUMN IF NOT EXISTS {col_name} {col_def}")
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                print(f"   ⚠️  Column {col_name}: {e}")
        
        # Step 4: Add computed deadline urgency column (special handling)
        print("\n4️⃣ Adding deadline urgency calculation...")
        try:
            # First check if column exists
            column_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'africa_intelligence_feed' 
                    AND column_name = 'deadline_urgency'
                )
            """)
            
            if not column_exists:
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
                print("   ✅ Deadline urgency column added")
            else:
                print("   ⚠️  Deadline urgency column already exists")
        except Exception as e:
            print(f"   ❌ Deadline urgency column failed: {e}")
        
        # Step 5: Add columns to organizations
        print("\n5️⃣ Enhancing organizations table...")
        
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
        
        for col_name, col_def in org_columns:
            try:
                await conn.execute(f"ALTER TABLE organizations ADD COLUMN IF NOT EXISTS {col_name} {col_def}")
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                print(f"   ⚠️  Column {col_name}: {e}")
        
        # Step 6: Create junction tables
        print("\n6️⃣ Creating junction tables...")
        
        junction_tables = [
            {
                "name": "intelligence_item_ai_domains",
                "sql": """
                    CREATE TABLE IF NOT EXISTS intelligence_item_ai_domains (
                        intelligence_item_id INTEGER NOT NULL,
                        ai_domain_id INTEGER NOT NULL,
                        PRIMARY KEY (intelligence_item_id, ai_domain_id)
                    )
                """
            },
            {
                "name": "intelligence_item_geographic_scopes",
                "sql": """
                    CREATE TABLE IF NOT EXISTS intelligence_item_geographic_scopes (
                        intelligence_item_id INTEGER NOT NULL,
                        geographic_scope_id INTEGER NOT NULL,
                        PRIMARY KEY (intelligence_item_id, geographic_scope_id)
                    )
                """
            },
            {
                "name": "organization_geographic_focus",
                "sql": """
                    CREATE TABLE IF NOT EXISTS organization_geographic_focus (
                        organization_id INTEGER NOT NULL,
                        geographic_scope_id INTEGER NOT NULL,
                        PRIMARY KEY (organization_id, geographic_scope_id)
                    )
                """
            }
        ]
        
        for table in junction_tables:
            try:
                await conn.execute(table["sql"])
                print(f"   ✅ {table['name']} junction table created")
            except Exception as e:
                print(f"   ⚠️  {table['name']}: {e}")
        
        # Step 7: Add foreign key constraints to junction tables
        print("\n7️⃣ Adding junction table foreign keys...")
        
        junction_fks = [
            "ALTER TABLE intelligence_item_ai_domains ADD CONSTRAINT fk_fo_ai_domains_fo FOREIGN KEY (intelligence_item_id) REFERENCES africa_intelligence_feed(id) ON DELETE CASCADE",
            "ALTER TABLE intelligence_item_ai_domains ADD CONSTRAINT fk_fo_ai_domains_ai FOREIGN KEY (ai_domain_id) REFERENCES ai_domains(id) ON DELETE CASCADE",
            "ALTER TABLE intelligence_item_geographic_scopes ADD CONSTRAINT fk_fo_geo_scopes_fo FOREIGN KEY (intelligence_item_id) REFERENCES africa_intelligence_feed(id) ON DELETE CASCADE",
            "ALTER TABLE intelligence_item_geographic_scopes ADD CONSTRAINT fk_fo_geo_scopes_geo FOREIGN KEY (geographic_scope_id) REFERENCES geographic_scopes(id) ON DELETE CASCADE",
            "ALTER TABLE organization_geographic_focus ADD CONSTRAINT fk_org_geo_focus_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE",
            "ALTER TABLE organization_geographic_focus ADD CONSTRAINT fk_org_geo_focus_geo FOREIGN KEY (geographic_scope_id) REFERENCES geographic_scopes(id) ON DELETE CASCADE",
            "ALTER TABLE africa_intelligence_feed ADD CONSTRAINT fk_africa_intelligence_feed_type FOREIGN KEY (type_id) REFERENCES funding_types(id)",
            "ALTER TABLE africa_intelligence_feed ADD CONSTRAINT fk_africa_intelligence_feed_user FOREIGN KEY (submitted_by_user_id) REFERENCES community_users(id)"
        ]
        
        for fk in junction_fks:
            try:
                await conn.execute(fk)
                print(f"   ✅ Foreign key constraint added")
            except Exception as e:
                print(f"   ⚠️  Foreign key constraint: {e}")
        
        # Step 8: Create performance indexes
        print("\n8️⃣ Creating performance indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_type_id ON africa_intelligence_feed(type_id)",
            "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_status ON africa_intelligence_feed(status)",
            "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_deadline_urgency ON africa_intelligence_feed(deadline_urgency)",
            "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_currency ON africa_intelligence_feed(currency)",
            "CREATE INDEX IF NOT EXISTS idx_africa_intelligence_feed_community_rating ON africa_intelligence_feed(community_rating)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_ai_relevance_score ON organizations(ai_relevance_score)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_africa_relevance_score ON organizations(africa_relevance_score)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_monitoring_status ON organizations(monitoring_status)",
            "CREATE INDEX IF NOT EXISTS idx_organizations_source_type ON organizations(source_type)"
        ]
        
        for index in indexes:
            try:
                await conn.execute(index)
                print(f"   ✅ Index created")
            except Exception as e:
                print(f"   ⚠️  Index creation: {e}")
        
        print("\n✅ Step-by-step migration completed!")
        
        # Verify what we've created
        print("\n📊 Verification Summary:")
        
        tables_to_check = ['funding_types', 'ai_domains', 'geographic_scopes', 'community_users']
        for table in tables_to_check:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"   ✅ {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Not accessible")
        
        # Check new columns
        new_columns = ['status', 'currency', 'deadline_urgency', 'type_id']
        for col in new_columns:
            try:
                exists = await conn.fetchval(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'africa_intelligence_feed' 
                        AND column_name = '{col}'
                    )
                """)
                status = "✅" if exists else "❌"
                print(f"   {status} africa_intelligence_feed.{col}: {'Available' if exists else 'Missing'}")
            except Exception:
                print(f"   ❌ africa_intelligence_feed.{col}: Check failed")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(apply_migration_step_by_step())
