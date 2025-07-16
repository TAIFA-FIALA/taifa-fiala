#!/usr/bin/env python3
"""
Simple data migration script using direct SQL to move organization data to foreign key relationships
"""
import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def migrate_organization_data():
    """Migrate existing data to use proper organization relationships"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("🚀 Starting organization data migration")
    print("=" * 60)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Check current state
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_opportunities,
                COUNT(organization_id) as with_org_id,
                COUNT(*) FILTER (WHERE organization_id IS NULL) as without_org_id
            FROM funding_opportunities
        """)
        
        print(f"📊 Current state:")
        print(f"   Total opportunities: {stats['total_opportunities']}")
        print(f"   With organization_id: {stats['with_org_id']}")
        print(f"   Without organization_id: {stats['without_org_id']}")
        
        if stats['without_org_id'] == 0:
            print("✅ All opportunities already have organization relationships!")
            return
        
        # Get opportunities without organization_id
        opportunities = await conn.fetch("""
            SELECT id, title, organization_name, raw_data, source_url
            FROM funding_opportunities 
            WHERE organization_id IS NULL
            LIMIT 50
        """)
        
        print(f"\n🔄 Migrating {len(opportunities)} opportunities...")
        
        migrated_count = 0
        created_orgs_count = 0
        skipped_count = 0
        
        async with conn.transaction():
            for opp in opportunities:
                org_id = None
                org_name = None
                
                try:
                    # Strategy 1: Check raw_data for organization_id
                    raw_data_dict = {}
                    if opp['raw_data']:
                        if isinstance(opp['raw_data'], dict):
                            raw_data_dict = opp['raw_data']
                        elif isinstance(opp['raw_data'], str):
                            try:
                                raw_data_dict = json.loads(opp['raw_data'])
                            except:
                                raw_data_dict = {}
                        
                        if 'organization_id' in raw_data_dict:
                            potential_org_id = raw_data_dict['organization_id']
                            # Verify the organization exists
                            existing_org = await conn.fetchrow(
                                "SELECT id, name FROM organizations WHERE id = $1",
                                potential_org_id
                            )
                            if existing_org:
                                org_id = existing_org['id']
                                org_name = existing_org['name']
                                print(f"✅ Found org by raw_data ID: {org_name}")
                    
                    # Strategy 2: Use organization_name field
                    if not org_id and opp['organization_name'] and opp['organization_name'] != "Unknown":
                        org_name = opp['organization_name'].strip()
                        
                        # Try to find existing organization
                        existing_org = await conn.fetchrow(
                            "SELECT id, name FROM organizations WHERE name = $1",
                            org_name
                        )
                        
                        if existing_org:
                            org_id = existing_org['id']
                            print(f"✅ Found existing org: {org_name}")
                        else:
                            # Create new organization
                            org_id = await conn.fetchval("""
                                INSERT INTO organizations (name, type, is_active, created_at)
                                VALUES ($1, 'funder', true, NOW())
                                RETURNING id
                            """, org_name)
                            created_orgs_count += 1
                            print(f"🆕 Created new org: {org_name} (ID: {org_id})")
                    
                    # Strategy 3: Extract from content
                    if not org_id:
                        org_name = extract_org_from_content(opp)
                        if org_name:
                            # Check if organization exists
                            existing_org = await conn.fetchrow(
                                "SELECT id FROM organizations WHERE name = $1",
                                org_name
                            )
                            
                            if existing_org:
                                org_id = existing_org['id']
                                print(f"✅ Found org by content: {org_name}")
                            else:
                                # Create new organization
                                org_id = await conn.fetchval("""
                                    INSERT INTO organizations (name, type, is_active, created_at)
                                    VALUES ($1, 'funder', true, NOW())
                                    RETURNING id
                                """, org_name)
                                created_orgs_count += 1
                                print(f"🆕 Created org from content: {org_name}")
                    
                    # Update funding opportunity
                    if org_id:
                        # Prepare updated raw_data
                        if not raw_data_dict:
                            raw_data_dict = {}
                        raw_data_dict['organization_id'] = org_id
                        
                        await conn.execute("""
                            UPDATE funding_opportunities 
                            SET organization_id = $1, raw_data = $2
                            WHERE id = $3
                        """, org_id, json.dumps(raw_data_dict), opp['id'])
                        
                        migrated_count += 1
                        print(f"✅ Migrated: {opp['title'][:50]}... -> {org_name}")
                    else:
                        skipped_count += 1
                        print(f"⚠️  Skipped: {opp['title'][:50]}... (no organization identified)")
                        
                except Exception as e:
                    print(f"❌ Error processing opportunity {opp['id']}: {e}")
                    skipped_count += 1
        
        print("\n" + "=" * 60)
        print("📊 Migration Results:")
        print(f"   ✅ Migrated: {migrated_count} opportunities")
        print(f"   🆕 Created: {created_orgs_count} organizations")
        print(f"   ⚠️  Skipped: {skipped_count} opportunities")
        
        # Verify results
        final_stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total,
                COUNT(organization_id) as with_org_id,
                COUNT(*) FILTER (WHERE organization_id IS NULL) as without_org_id
            FROM funding_opportunities
        """)
        
        print(f"\n📊 Final state:")
        print(f"   Total opportunities: {final_stats['total']}")
        print(f"   With organization_id: {final_stats['with_org_id']}")
        print(f"   Without organization_id: {final_stats['without_org_id']}")
        
        # Show organization distribution
        org_counts = await conn.fetch("""
            SELECT o.name, COUNT(f.id) as opportunity_count
            FROM organizations o
            JOIN funding_opportunities f ON o.id = f.organization_id
            GROUP BY o.name
            ORDER BY opportunity_count DESC
        """)
        
        print(f"\n🏢 Organizations with opportunities:")
        for row in org_counts:
            print(f"   • {row['name']}: {row['opportunity_count']} opportunities")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

def extract_org_from_content(opp):
    """Extract organization name from title, description, or URL"""
    content = f"{opp['title'] or ''} {opp.get('description', '') or ''} {opp['source_url'] or ''}".lower()
    
    # Common organization patterns
    org_patterns = {
        "gates foundation": "Gates Foundation",
        "bill & melinda gates": "Gates Foundation",
        "world bank": "World Bank", 
        "african development bank": "African Development Bank",
        "afdb": "African Development Bank",
        "united nations": "United Nations",
        "undp": "United Nations Development Programme",
        "unesco": "UNESCO",
        "usaid": "USAID",
        "european union": "European Union",
        "google": "Google",
        "microsoft": "Microsoft",
        "meta": "Meta",
        "facebook": "Meta",
        "science for africa": "Science for Africa Foundation",
        "idrc": "International Development Research Centre",
        "milken": "Milken Institute",
        "mastercard foundation": "Mastercard Foundation",
        "ford foundation": "Ford Foundation",
        "rockefeller": "Rockefeller Foundation",
        "grantsdatabase": "GrantsDatabase.org",
        "mozilla": "Mozilla Foundation",
        "mcgovern": "Patrick J. McGovern Foundation"
    }
    
    for pattern, org_name in org_patterns.items():
        if pattern in content:
            return org_name
    
    return None

async def test_relationships():
    """Test that relationships work after migration"""
    print("\n🧪 Testing relationships...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Test joining opportunities with organizations
        test_data = await conn.fetch("""
            SELECT f.title, o.name as org_name
            FROM funding_opportunities f
            JOIN organizations o ON f.organization_id = o.id
            LIMIT 5
        """)
        
        if test_data:
            print("✅ Relationship test successful! Sample relationships:")
            for row in test_data:
                print(f"   • {row['title'][:50]}... → {row['org_name']}")
        else:
            print("⚠️  No relationships found in test")
            
    except Exception as e:
        print(f"❌ Relationship test failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_organization_data())
    asyncio.run(test_relationships())
    print("\n🎉 Migration completed!")
