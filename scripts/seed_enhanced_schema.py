#!/usr/bin/env python3
"""
Data seeding script for enhanced TAIFA schema
Populates lookup tables with initial data based on competitor analysis
"""
import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def seed_lookup_tables():
    """Populate lookup tables with initial data"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("🌱 Seeding TAIFA Enhanced Schema Lookup Tables")
    print("=" * 60)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        async with conn.transaction():
            
            # 1. Seed Funding Types
            print("1️⃣ Seeding funding types...")
            funding_types = [
                {
                    "name": "Research Grant",
                    "description": "Academic and scientific research funding",
                    "typical_amount_range": "$5,000 - $500,000"
                },
                {
                    "name": "Startup Grant", 
                    "description": "Early-stage business funding",
                    "typical_amount_range": "$10,000 - $100,000"
                },
                {
                    "name": "Competition Prize",
                    "description": "Innovation and entrepreneurship competitions", 
                    "typical_amount_range": "$1,000 - $1,000,000"
                },
                {
                    "name": "Scholarship",
                    "description": "Educational and training support",
                    "typical_amount_range": "$1,000 - $50,000"
                },
                {
                    "name": "Fellowship",
                    "description": "Professional development and exchange programs",
                    "typical_amount_range": "$5,000 - $100,000"
                },
                {
                    "name": "Investment",
                    "description": "Venture capital and angel investment",
                    "typical_amount_range": "$50,000 - $10,000,000"
                },
                {
                    "name": "Infrastructure Grant",
                    "description": "Equipment and facility funding",
                    "typical_amount_range": "$10,000 - $1,000,000"
                },
                {
                    "name": "Capacity Building",
                    "description": "Training and skills development programs",
                    "typical_amount_range": "$5,000 - $200,000"
                },
                {
                    "name": "Accelerator Program",
                    "description": "Business acceleration and mentorship",
                    "typical_amount_range": "$10,000 - $250,000"
                },
                {
                    "name": "Innovation Challenge",
                    "description": "Problem-solving and innovation competitions",
                    "typical_amount_range": "$5,000 - $500,000"
                }
            ]
            
            for ft in funding_types:
                await conn.execute("""
                    INSERT INTO funding_types (name, description, typical_amount_range, is_active)
                    VALUES ($1, $2, $3, true)
                    ON CONFLICT (name) DO NOTHING
                """, ft["name"], ft["description"], ft["typical_amount_range"])
            
            print(f"   ✅ Added {len(funding_types)} funding types")
            
            # 2. Seed AI Domains
            print("2️⃣ Seeding AI domains...")
            ai_domains = [
                {
                    "name": "Healthcare & Medical AI",
                    "description": "AI applications in healthcare, medical diagnosis, and public health"
                },
                {
                    "name": "Agricultural Technology",
                    "description": "AI for agriculture, food security, and rural development"
                },
                {
                    "name": "Financial Technology",
                    "description": "AI in fintech, digital payments, and financial inclusion"
                },
                {
                    "name": "Education Technology",
                    "description": "AI-powered educational tools and platforms"
                },
                {
                    "name": "Climate & Environment",
                    "description": "AI for climate change, environmental monitoring, and sustainability"
                },
                {
                    "name": "Transportation & Logistics",
                    "description": "AI in transportation, logistics, and supply chain"
                },
                {
                    "name": "Cybersecurity",
                    "description": "AI-powered security solutions and threat detection"
                },
                {
                    "name": "Natural Language Processing",
                    "description": "Language AI, translation, and communication technologies"
                },
                {
                    "name": "Computer Vision",
                    "description": "Image recognition, visual AI, and video analysis"
                },
                {
                    "name": "Robotics & Automation",
                    "description": "AI-powered robotics and industrial automation"
                },
                {
                    "name": "Data Science & Analytics",
                    "description": "AI for data analysis, business intelligence, and insights"
                },
                {
                    "name": "AI Ethics & Governance",
                    "description": "Responsible AI, ethics, policy, and governance"
                },
                {
                    "name": "Smart Cities",
                    "description": "AI for urban planning, smart infrastructure, and city services"
                },
                {
                    "name": "Energy & Utilities",
                    "description": "AI in energy management, renewable energy, and utilities"
                },
                {
                    "name": "Manufacturing & Industry 4.0",
                    "description": "AI in manufacturing, quality control, and industrial processes"
                },
                {
                    "name": "Social Good & Development",
                    "description": "AI for social impact, humanitarian aid, and development"
                },
                {
                    "name": "Media & Entertainment",
                    "description": "AI in content creation, media production, and entertainment"
                },
                {
                    "name": "Government & Public Service",
                    "description": "AI in public administration, e-government, and citizen services"
                }
            ]
            
            for domain in ai_domains:
                await conn.execute("""
                    INSERT INTO ai_domains (name, description, is_active)
                    VALUES ($1, $2, true)
                    ON CONFLICT (name) DO NOTHING
                """, domain["name"], domain["description"])
            
            print(f"   ✅ Added {len(ai_domains)} AI domains")
            
            # 3. Seed Geographic Scopes
            print("3️⃣ Seeding geographic scopes...")
            
            # Continental level
            await conn.execute("""
                INSERT INTO geographic_scopes (name, type, is_active)
                VALUES ('Global', 'global', true), ('Africa', 'continent', true)
                ON CONFLICT (name) DO NOTHING
            """)
            
            # Get Africa ID for parent relationships
            africa_id = await conn.fetchval("SELECT id FROM geographic_scopes WHERE name = 'Africa'")
            
            # Regional level
            regions = [
                "West Africa", "East Africa", "Southern Africa", "North Africa", "Central Africa"
            ]
            
            region_ids = {}
            for region in regions:
                region_id = await conn.fetchval("""
                    INSERT INTO geographic_scopes (name, type, parent_scope_id, is_active)
                    VALUES ($1, 'region', $2, true)
                    ON CONFLICT (name) DO UPDATE SET parent_scope_id = $2
                    RETURNING id
                """, region, africa_id)
                region_ids[region] = region_id
            
            # Country level with regional associations
            countries = [
                # West Africa
                {"name": "Nigeria", "code": "NG", "region": "West Africa"},
                {"name": "Ghana", "code": "GH", "region": "West Africa"},
                {"name": "Senegal", "code": "SN", "region": "West Africa"},
                {"name": "Mali", "code": "ML", "region": "West Africa"},
                {"name": "Burkina Faso", "code": "BF", "region": "West Africa"},
                {"name": "Ivory Coast", "code": "CI", "region": "West Africa"},
                {"name": "Guinea", "code": "GN", "region": "West Africa"},
                {"name": "Benin", "code": "BJ", "region": "West Africa"},
                {"name": "Togo", "code": "TG", "region": "West Africa"},
                {"name": "Sierra Leone", "code": "SL", "region": "West Africa"},
                {"name": "Liberia", "code": "LR", "region": "West Africa"},
                {"name": "Niger", "code": "NE", "region": "West Africa"},
                {"name": "Gambia", "code": "GM", "region": "West Africa"},
                {"name": "Guinea-Bissau", "code": "GW", "region": "West Africa"},
                {"name": "Cape Verde", "code": "CV", "region": "West Africa"},
                
                # East Africa
                {"name": "Kenya", "code": "KE", "region": "East Africa"},
                {"name": "Ethiopia", "code": "ET", "region": "East Africa"},
                {"name": "Tanzania", "code": "TZ", "region": "East Africa"},
                {"name": "Uganda", "code": "UG", "region": "East Africa"},
                {"name": "Rwanda", "code": "RW", "region": "East Africa"},
                {"name": "Burundi", "code": "BI", "region": "East Africa"},
                {"name": "Somalia", "code": "SO", "region": "East Africa"},
                {"name": "Djibouti", "code": "DJ", "region": "East Africa"},
                {"name": "Eritrea", "code": "ER", "region": "East Africa"},
                {"name": "South Sudan", "code": "SS", "region": "East Africa"},
                
                # Southern Africa
                {"name": "South Africa", "code": "ZA", "region": "Southern Africa"},
                {"name": "Zimbabwe", "code": "ZW", "region": "Southern Africa"},
                {"name": "Botswana", "code": "BW", "region": "Southern Africa"},
                {"name": "Namibia", "code": "NA", "region": "Southern Africa"},
                {"name": "Zambia", "code": "ZM", "region": "Southern Africa"},
                {"name": "Malawi", "code": "MW", "region": "Southern Africa"},
                {"name": "Mozambique", "code": "MZ", "region": "Southern Africa"},
                {"name": "Lesotho", "code": "LS", "region": "Southern Africa"},
                {"name": "Eswatini", "code": "SZ", "region": "Southern Africa"},
                {"name": "Madagascar", "code": "MG", "region": "Southern Africa"},
                {"name": "Mauritius", "code": "MU", "region": "Southern Africa"},
                {"name": "Seychelles", "code": "SC", "region": "Southern Africa"},
                {"name": "Comoros", "code": "KM", "region": "Southern Africa"},
                
                # North Africa
                {"name": "Egypt", "code": "EG", "region": "North Africa"},
                {"name": "Libya", "code": "LY", "region": "North Africa"},
                {"name": "Tunisia", "code": "TN", "region": "North Africa"},
                {"name": "Algeria", "code": "DZ", "region": "North Africa"},
                {"name": "Morocco", "code": "MA", "region": "North Africa"},
                {"name": "Sudan", "code": "SD", "region": "North Africa"},
                
                # Central Africa
                {"name": "Democratic Republic of Congo", "code": "CD", "region": "Central Africa"},
                {"name": "Cameroon", "code": "CM", "region": "Central Africa"},
                {"name": "Central African Republic", "code": "CF", "region": "Central Africa"},
                {"name": "Chad", "code": "TD", "region": "Central Africa"},
                {"name": "Republic of Congo", "code": "CG", "region": "Central Africa"},
                {"name": "Equatorial Guinea", "code": "GQ", "region": "Central Africa"},
                {"name": "Gabon", "code": "GA", "region": "Central Africa"},
                {"name": "São Tomé and Príncipe", "code": "ST", "region": "Central Africa"}
            ]
            
            for country in countries:
                parent_id = region_ids.get(country["region"], africa_id)
                await conn.execute("""
                    INSERT INTO geographic_scopes (name, code, type, parent_scope_id, is_active)
                    VALUES ($1, $2, 'country', $3, true)
                    ON CONFLICT (name) DO UPDATE SET 
                        code = $2, parent_scope_id = $3
                """, country["name"], country["code"], parent_id)
            
            print(f"   ✅ Added {len(countries)} countries in {len(regions)} regions")
            
            # 4. Verify seeding results
            print("4️⃣ Verifying seeded data...")
            
            counts = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM funding_types) as funding_types,
                    (SELECT COUNT(*) FROM ai_domains) as ai_domains,
                    (SELECT COUNT(*) FROM geographic_scopes WHERE type = 'country') as countries,
                    (SELECT COUNT(*) FROM geographic_scopes WHERE type = 'region') as regions,
                    (SELECT COUNT(*) FROM geographic_scopes) as total_geographic_scopes
            """)
            
            print(f"   📊 Final counts:")
            print(f"      • Funding Types: {counts['funding_types']}")
            print(f"      • AI Domains: {counts['ai_domains']}")
            print(f"      • Countries: {counts['countries']}")
            print(f"      • Regions: {counts['regions']}")
            print(f"      • Total Geographic Scopes: {counts['total_geographic_scopes']}")
            
        print("\n✅ All lookup tables seeded successfully!")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

async def update_existing_opportunities():
    """Update existing opportunities with default values for new fields"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("\n🔄 Updating existing opportunities with default values...")
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Set default status for existing opportunities
        updated_status = await conn.execute("""
            UPDATE funding_opportunities 
            SET status = CASE 
                WHEN deadline IS NULL THEN 'open'
                WHEN deadline < CURRENT_DATE THEN 'closed' 
                ELSE 'open'
            END
            WHERE status IS NULL
        """)
        
        # Set default currency based on content analysis
        await conn.execute("""
            UPDATE funding_opportunities 
            SET currency = CASE 
                WHEN funding_amount ILIKE '%€%' OR funding_amount ILIKE '%eur%' THEN 'EUR'
                WHEN funding_amount ILIKE '%£%' OR funding_amount ILIKE '%gbp%' THEN 'GBP'
                WHEN funding_amount ILIKE '%naira%' THEN 'NGN'
                WHEN funding_amount ILIKE '%rand%' THEN 'ZAR'
                ELSE 'USD'
            END
            WHERE currency IS NULL OR currency = 'USD'
        """)
        
        # Set view_count and application_count to 0 for existing records
        await conn.execute("""
            UPDATE funding_opportunities 
            SET view_count = 0, application_count = 0 
            WHERE view_count IS NULL OR application_count IS NULL
        """)
        
        print("   ✅ Updated existing opportunities with default values")
        
    except Exception as e:
        print(f"   ❌ Update failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 TAIFA Enhanced Schema Data Seeding")
    print("=" * 60)
    
    asyncio.run(seed_lookup_tables())
    asyncio.run(update_existing_opportunities())
    
    print("\n🎉 Data seeding completed!")
    print("\n💡 Next steps:")
    print("   1. Run the enhanced schema migration")
    print("   2. Update SQLAlchemy models with new relationships")
    print("   3. Test the new filtering and categorization features")
    print("   4. Implement frontend changes for deadline urgency display")
