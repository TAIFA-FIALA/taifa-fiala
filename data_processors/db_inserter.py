import json
import os
import sys
import hashlib
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Define database settings directly
DATABASE_URL: str = os.getenv("DATABASE_URL")
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

print(f"DEBUG: DATABASE_URL being used in db_inserter.py: {DATABASE_URL}")

# Create SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Use NullPool for development
    echo=DEBUG,
)

# Create async session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession, # Use AsyncSession for async operations
)

# Create declarative base for models
Base = declarative_base()

# Import the model using the updated path
from backend.app.models.funding import FundingOpportunity
from backend.app.models.organization import Organization


def generate_content_hash(data: Dict[str, Any]) -> str:
    """Generate a content hash from the funding opportunity data"""
    # Create a string representation of key fields to hash
    hash_content = f"{data.get('title', '')}{data.get('description', '')}{data.get('source_url', '')}"
    # Generate MD5 hash (sufficient for deduplication purposes)
    return hashlib.md5(hash_content.encode('utf-8')).hexdigest()


async def get_or_create_organization(db: AsyncSession, org_name: str) -> Optional[Organization]:
    """Find an existing organization by name or create a new one if it doesn't exist"""
    if not org_name or org_name == "Unknown":
        return None
        
    # Try to find existing organization
    result = await db.execute(select(Organization).where(Organization.name == org_name))
    org = result.scalars().first()
    
    if org:
        print(f"Found existing organization: {org_name} (ID: {org.id})")
        return org
    else:
        # Create new organization
        new_org = Organization(
            name=org_name,
            type="funder",  # Default type
            is_active=True,
            created_at=datetime.now()
        )
        db.add(new_org)
        # We need to flush to get the ID, but don't commit yet
        await db.flush()
        print(f"Created new organization: {org_name} (ID: {new_org.id})")
        return new_org

async def insert_funding_opportunities(opportunities: List[Dict[str, Any]]):
    async with SessionLocal() as db: # Use async with for session
        try:
            inserted_count = 0
            for opp_data in opportunities:
                # Prepare deadline date
                deadline = None
                if opp_data.get("deadline"):
                    try:
                        # Attempt to parse various date formats
                        for fmt in ("%B %d, %Y", "%d %B %Y", "%Y-%m-%d"):
                            try:
                                deadline = datetime.strptime(opp_data["deadline"], fmt).date()  # Store as date not datetime
                                break
                            except ValueError:
                                pass
                    except Exception:
                        deadline = None # Handle conversion errors
                
                # Prepare JSONB raw_data field
                raw_data = {
                    "geographical_scope": opp_data.get("geographical_scope"),
                    "eligibility_criteria": opp_data.get("eligibility_criteria"),
                    "currency": opp_data.get("currency"),
                    "original_amount": opp_data.get("amount"),
                }
                
                # Generate content hash for deduplication
                content_hash = generate_content_hash(opp_data)
                
                # Check if this content hash already exists to avoid duplicates
                result = await db.execute(select(FundingOpportunity).where(
                    FundingOpportunity.content_hash == content_hash
                ))
                existing_opp = result.scalars().first()
                
                if existing_opp:
                    print(f"Skipping duplicate funding opportunity: {opp_data.get('title')}")
                    continue
                
                # Get or create the organization
                org_name = opp_data.get("source_organization", "Unknown")
                organization = await get_or_create_organization(db, org_name)
                
                # Create FundingOpportunity object with proper relationship
                funding_opp = FundingOpportunity(
                    title=opp_data.get("title"),
                    description=opp_data.get("description"),
                    funding_amount=opp_data.get("amount"),  # Store as text as per DB schema
                    deadline=deadline,
                    source_url=opp_data.get("source_url"),
                    # Keep organization_name for backward compatibility
                    organization_name=organization.name if organization else org_name,
                    # NEW: Use proper foreign key relationship
                    organization_id=organization.id if organization else None,
                    application_url=opp_data.get("source_url"),  # Use same URL for now
                    source_type="external",
                    source_name="automated_import",
                    content_hash=content_hash,  # Add the content hash
                    raw_data=raw_data,
                    discovered_date=datetime.now(),
                    last_updated=datetime.now(),
                    parsed_with_ai=False,
                    verified=False,
                    active=True,
                    detected_language="en",  # Assume English for now
                    is_multilingual=False,
                    translation_status={"en": "original"}  # Add translation status
                )
                
                # Optional: You can also set the relationship directly
                if organization:
                    funding_opp.organization = organization
                    # Store organization ID in raw_data for backward compatibility
                    raw_data["organization_id"] = organization.id
                    funding_opp.raw_data = raw_data
                
                db.add(funding_opp)
                inserted_count += 1
                
                print(f"✅ Prepared opportunity: {opp_data.get('title')[:50]}... -> Org: {org_name}")
                
            await db.commit() # Await commit
            print(f"🎉 Successfully inserted {inserted_count} funding opportunities with proper relationships!")
            
            # Display relationship summary
            print("\n📊 Relationship Summary:")
            result = await db.execute(
                select(FundingOpportunity.organization_id, FundingOpportunity.organization_name)
                .where(FundingOpportunity.organization_id.isnot(None))
            )
            linked_opportunities = result.fetchall()
            print(f"   - {len(linked_opportunities)} opportunities properly linked to organizations")
            
            # Show organization counts
            from sqlalchemy import func
            result = await db.execute(
                select(Organization.name, func.count(FundingOpportunity.id))
                .join(FundingOpportunity, Organization.id == FundingOpportunity.organization_id)
                .group_by(Organization.name)
            )
            org_counts = result.fetchall()
            print("   - Organization opportunity counts:")
            for org_name, count in org_counts:
                print(f"     • {org_name}: {count} opportunities")
                
        except Exception as e:
            await db.rollback() # Await rollback
            print(f"❌ Error inserting funding opportunities: {e}")
            import traceback
            traceback.print_exc()

async def test_relationships():
    """Test the new relationship functionality"""
    print("\n🧪 Testing SQLAlchemy relationships...")
    
    async with SessionLocal() as db:
        try:
            # Test 1: Load organization with funding opportunities
            result = await db.execute(
                select(Organization)
                .where(Organization.funding_opportunities.any())
                .limit(1)
            )
            org = result.scalars().first()
            
            if org:
                print(f"✅ Found organization: {org.name}")
                
                # Test accessing related funding opportunities
                await db.refresh(org, ['funding_opportunities'])
                opportunities = org.funding_opportunities
                print(f"✅ Related opportunities: {len(opportunities)} found")
                
                for opp in opportunities[:3]:  # Show first 3
                    print(f"   • {opp.title[:60]}...")
            
            # Test 2: Load funding opportunity with organization
            result = await db.execute(
                select(FundingOpportunity)
                .where(FundingOpportunity.organization_id.isnot(None))
                .limit(1)
            )
            opp = result.scalars().first()
            
            if opp:
                print(f"✅ Found opportunity: {opp.title[:60]}...")
                
                # Test accessing related organization
                await db.refresh(opp, ['organization'])
                if opp.organization:
                    print(f"✅ Related organization: {opp.organization.name}")
                else:
                    print("⚠️  No organization relationship found")
            
            print("✅ Relationship testing completed successfully!")
            
        except Exception as e:
            print(f"❌ Relationship testing failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    
    print("🚀 TAIFA Database Inserter with SQLAlchemy Relationships")
    print("=" * 60)
    
    try:
        with open("funding_opportunities.json", "r", encoding="utf-8") as f:
            opportunities_data = json.load(f)
        
        print(f"📁 Loaded {len(opportunities_data)} opportunities from JSON")
        
        # Run insertion with new relationship support
        asyncio.run(insert_funding_opportunities(opportunities_data))
        
        # Test the relationships
        asyncio.run(test_relationships())
        
    except FileNotFoundError:
        print("❌ Error: funding_opportunities.json not found. Please run the extractor first.")
    except Exception as e:
        print(f"❌ Error loading or processing funding_opportunities.json: {e}")
        import traceback
        traceback.print_exc()
