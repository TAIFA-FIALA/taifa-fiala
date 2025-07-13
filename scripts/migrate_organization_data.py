#!/usr/bin/env python3
"""
Data migration script to move existing organization data from raw_data to proper foreign key relationships
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Import models
from backend.app.models.funding import FundingOpportunity
from backend.app.models.organization import Organization

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:stocksight1484@100.75.201.24:5432/TAIFA_db")

engine = create_async_engine(DATABASE_URL, poolclass=NullPool, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def migrate_existing_data():
    """Migrate existing funding opportunities to use proper organization relationships"""
    
    print("🚀 Starting data migration: raw_data -> organization_id relationships")
    print("=" * 70)
    
    async with SessionLocal() as db:
        try:
            # Get all funding opportunities that don't have organization_id set
            result = await db.execute(
                select(FundingOpportunity)
                .where(FundingOpportunity.organization_id.is_(None))
            )
            opportunities = result.scalars().all()
            
            print(f"📊 Found {len(opportunities)} funding opportunities without organization_id")
            
            if len(opportunities) == 0:
                print("✅ No data migration needed - all opportunities already have proper relationships")
                return
                
            migrated_count = 0
            created_orgs_count = 0
            skipped_count = 0
            
            for opp in opportunities:
                try:
                    organization = None
                    org_name = None
                    
                    # Strategy 1: Check raw_data for organization_id
                    if opp.raw_data and isinstance(opp.raw_data, dict):
                        if 'organization_id' in opp.raw_data:
                            org_id = opp.raw_data['organization_id']
                            result = await db.execute(
                                select(Organization).where(Organization.id == org_id)
                            )
                            organization = result.scalars().first()
                            if organization:
                                print(f"✅ Found org by ID from raw_data: {organization.name}")
                    
                    # Strategy 2: Use organization_name field
                    if not organization and opp.organization_name and opp.organization_name != "Unknown":
                        org_name = opp.organization_name.strip()
                        result = await db.execute(
                            select(Organization).where(Organization.name == org_name)
                        )
                        organization = result.scalars().first()
                        
                        if organization:
                            print(f"✅ Found existing org by name: {org_name}")
                        else:
                            # Create new organization
                            organization = Organization(
                                name=org_name,
                                type="funder",
                                is_active=True
                            )
                            db.add(organization)
                            await db.flush()  # Get the ID
                            created_orgs_count += 1
                            print(f"🆕 Created new organization: {org_name} (ID: {organization.id})")
                    
                    # Strategy 3: Extract from title or description
                    if not organization:
                        org_name = await extract_organization_from_content(opp)
                        if org_name:
                            result = await db.execute(
                                select(Organization).where(Organization.name == org_name)
                            )
                            organization = result.scalars().first()
                            
                            if not organization:
                                organization = Organization(
                                    name=org_name,
                                    type="funder",
                                    is_active=True
                                )
                                db.add(organization)
                                await db.flush()
                                created_orgs_count += 1
                                print(f"🆕 Created org from content extraction: {org_name}")
                    
                    # Update the funding opportunity with proper relationship
                    if organization:
                        opp.organization_id = organization.id
                        opp.organization = organization
                        
                        # Update raw_data to include organization_id for consistency
                        if not opp.raw_data:
                            opp.raw_data = {}
                        opp.raw_data['organization_id'] = organization.id
                        
                        migrated_count += 1
                        print(f"✅ Migrated: {opp.title[:50]}... -> {organization.name}")
                    else:
                        skipped_count += 1
                        print(f"⚠️  Skipped: {opp.title[:50]}... (no organization found)")
                        
                except Exception as e:
                    print(f"❌ Error migrating opportunity {opp.id}: {e}")
                    skipped_count += 1
            
            # Commit all changes
            await db.commit()
            
            print("\n" + "=" * 70)
            print("📊 Migration Summary:")
            print(f"   ✅ Migrated: {migrated_count} funding opportunities")
            print(f"   🆕 Created: {created_orgs_count} new organizations")
            print(f"   ⚠️  Skipped: {skipped_count} opportunities")
            print(f"   📊 Total processed: {len(opportunities)}")
            
            # Verify migration results
            await verify_migration_results(db)
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()

async def extract_organization_from_content(opp: FundingOpportunity) -> str:
    """Extract organization name from title, description, or URL"""
    
    content = f"{opp.title or ''} {opp.description or ''} {opp.source_url or ''}".lower()
    
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
        "eu": "European Union",
        "google": "Google",
        "microsoft": "Microsoft",
        "meta": "Meta",
        "facebook": "Meta",
        "science for africa": "Science for Africa Foundation",
        "idrc": "International Development Research Centre",
        "milken": "Milken Institute",
        "mastercard foundation": "Mastercard Foundation",
        "ford foundation": "Ford Foundation",
        "rockefeller": "Rockefeller Foundation"
    }
    
    for pattern, org_name in org_patterns.items():
        if pattern in content:
            return org_name
    
    return None

async def verify_migration_results(db: AsyncSession):
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration results...")
    
    # Count opportunities with and without organization_id
    from sqlalchemy import func
    
    result = await db.execute(
        select(
            func.count(FundingOpportunity.id).label('total'),
            func.count(FundingOpportunity.organization_id).label('with_org'),
            func.count().filter(FundingOpportunity.organization_id.is_(None)).label('without_org')
        )
    )
    stats = result.first()
    
    print(f"📊 Final statistics:")
    print(f"   Total opportunities: {stats.total}")
    print(f"   With organization_id: {stats.with_org}")
    print(f"   Without organization_id: {stats.without_org}")
    
    # Show organization distribution
    result = await db.execute(
        select(Organization.name, func.count(FundingOpportunity.id))
        .join(FundingOpportunity, Organization.id == FundingOpportunity.organization_id)
        .group_by(Organization.name)
        .order_by(func.count(FundingOpportunity.id).desc())
    )
    org_counts = result.fetchall()
    
    print(f"\n🏢 Organizations with funding opportunities:")
    for org_name, count in org_counts:
        print(f"   • {org_name}: {count} opportunities")
    
    if stats.with_org > 0:
        print(f"\n✅ Migration successful! {stats.with_org}/{stats.total} opportunities now have proper relationships.")
    else:
        print(f"\n⚠️  Migration may need attention - no relationships established.")

async def test_relationships_after_migration():
    """Test that the relationships work correctly after migration"""
    print("\n🧪 Testing relationships after migration...")
    
    async with SessionLocal() as db:
        try:
            # Test 1: Access organization through funding opportunity
            result = await db.execute(
                select(FundingOpportunity)
                .where(FundingOpportunity.organization_id.isnot(None))
                .limit(1)
            )
            opp = result.scalars().first()
            
            if opp:
                await db.refresh(opp, ['organization'])
                if opp.organization:
                    print(f"✅ Opportunity -> Organization: '{opp.title[:40]}...' -> '{opp.organization.name}'")
                else:
                    print("❌ Failed to load organization relationship")
            
            # Test 2: Access funding opportunities through organization
            result = await db.execute(
                select(Organization)
                .where(Organization.funding_opportunities.any())
                .limit(1)
            )
            org = result.scalars().first()
            
            if org:
                await db.refresh(org, ['funding_opportunities'])
                print(f"✅ Organization -> Opportunities: '{org.name}' has {len(org.funding_opportunities)} opportunities")
            
            print("✅ Relationship testing completed successfully!")
            
        except Exception as e:
            print(f"❌ Relationship testing failed: {e}")

if __name__ == "__main__":
    print("🔄 TAIFA Data Migration: Organization Relationships")
    print("=" * 70)
    
    asyncio.run(migrate_existing_data())
    asyncio.run(test_relationships_after_migration())
    
    print("\n🎉 Data migration completed!")
    print("\n💡 Next steps:")
    print("   1. Test the new relationship functionality in your application")
    print("   2. Update any existing queries to use the relationships")
    print("   3. Consider removing organization_name column once fully migrated")
