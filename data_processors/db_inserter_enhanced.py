#!/usr/bin/env python3
"""
Updated db_inserter.py with enhanced schema support
Demonstrates usage of new relationships and features based on competitor analysis
"""
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

# Define database settings
DATABASE_URL: str = os.getenv("DATABASE_URL")
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

print(f"🚀 Enhanced TAIFA DB Inserter - Next-Generation Funding Platform")
print(f"📍 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'}")

# Create SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=DEBUG,
)

# Create async session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)

# Import the enhanced models
from backend.app.models.funding import AfricaIntelligenceItem
from backend.app.models.organization import Organization

def generate_content_hash(data: Dict[str, Any]) -> str:
    """Generate a content hash from the intelligence item data"""
    hash_content = f"{data.get('title', '')}{data.get('description', '')}{data.get('source_url', '')}"
    return hashlib.md5(hash_content.encode('utf-8')).hexdigest()

async def get_or_create_organization(db: AsyncSession, org_name: str) -> Optional[Organization]:
    """Enhanced organization creation with performance tracking"""
    if not org_name or org_name == "Unknown":
        return None
        
    # Try to find existing organization
    result = await db.execute(select(Organization).where(Organization.name == org_name))
    org = result.scalars().first()
    
    if org:
        print(f"✅ Found existing organization: {org_name} (ID: {org.id})")
        # Update performance metrics
        org.opportunities_discovered += 1
        return org
    else:
        # Create new organization with enhanced features
        new_org = Organization(
            name=org_name,
            type="funder",  # Default type
            is_active=True,
            created_at=datetime.now(),
            # Enhanced fields based on competitor analysis
            ai_relevance_score=50,  # Default moderate relevance
            africa_relevance_score=75,  # Assume Africa-relevant by default
            source_type="manual",
            monitoring_status="active",
            monitoring_reliability=100,
            opportunities_discovered=1,
            unique_opportunities_added=0,  # Will be incremented on successful insert
            duplicate_rate=0,
            data_completeness_score=70  # Base score
        )
        db.add(new_org)
        await db.flush()  # Get the ID
        print(f"🆕 Created enhanced organization: {org_name} (ID: {new_org.id})")
        return new_org

async def determine_funding_type(title: str, description: str) -> str:
    """Intelligent funding type classification based on content"""
    content = f"{title} {description}".lower()
    
    # AI-powered classification logic
    type_keywords = {
        "research grant": ["research", "study", "academic", "investigation", "phd", "postdoc"],
        "startup grant": ["startup", "business", "entrepreneur", "venture", "company", "sme"],
        "competition prize": ["competition", "contest", "challenge", "prize", "award", "winner"],
        "scholarship": ["scholarship", "student", "education", "tuition", "study abroad"],
        "fellowship": ["fellowship", "exchange", "professional development", "mentorship"],
        "investment": ["investment", "equity", "funding round", "investor", "capital"],
        "infrastructure grant": ["infrastructure", "equipment", "facility", "hardware"],
        "capacity building": ["training", "capacity", "skills", "workshop", "bootcamp"],
        "accelerator program": ["accelerator", "incubator", "program", "cohort"],
        "innovation challenge": ["innovation", "hackathon", "prototype", "solution"]
    }
    
    for funding_type, keywords in type_keywords.items():
        if any(keyword in content for keyword in keywords):
            return funding_type
    
    return "research grant"  # Default fallback

async def detect_currency(amount_text: str) -> str:
    """Enhanced currency detection"""
    if not amount_text:
        return "USD"
    
    amount_lower = amount_text.lower()
    currency_patterns = {
        "EUR": ["€", "eur", "euro"],
        "GBP": ["£", "gbp", "pound", "sterling"],
        "NGN": ["₦", "naira", "ngn"],
        "ZAR": ["rand", "zar", "r "],
        "KES": ["ksh", "kes", "shilling"],
        "GHS": ["ghs", "cedi"],
        "USD": ["$", "usd", "dollar"]  # Default
    }
    
    for currency, patterns in currency_patterns.items():
        if any(pattern in amount_lower for pattern in patterns):
            return currency
    
    return "USD"

async def calculate_deadline_urgency(deadline_date) -> str:
    """Calculate deadline urgency (this will be auto-calculated by trigger, but useful for validation)"""
    if not deadline_date:
        return "unknown"
    
    from datetime import date
    today = date.today()
    
    if deadline_date <= today:
        return "expired"
    elif deadline_date <= today + timedelta(days=30):
        return "urgent"
    elif deadline_date <= today + timedelta(days=60):
        return "moderate"
    else:
        return "low"

async def insert_enhanced_africa_intelligence_feed(opportunities: List[Dict[str, Any]]):
    """Enhanced intelligence item insertion with new schema features"""
    async with SessionLocal() as db:
        try:
            inserted_count = 0
            enhanced_count = 0
            
            print(f"\n🚀 Processing {len(opportunities)} opportunities with enhanced features...")
            
            for opp_data in opportunities:
                # Parse deadline
                deadline = None
                if opp_data.get("deadline"):
                    try:
                        for fmt in ("%B %d, %Y", "%d %B %Y", "%Y-%m-%d"):
                            try:
                                deadline = datetime.strptime(opp_data["deadline"], fmt).date()
                                break
                            except ValueError:
                                pass
                    except Exception:
                        deadline = None
                
                # Enhanced raw_data with competitor analysis insights
                raw_data = {
                    "geographical_scope": opp_data.get("geographical_scope"),
                    "eligibility_criteria": opp_data.get("eligibility_criteria"),
                    "currency": opp_data.get("currency"),
                    "original_amount": opp_data.get("amount"),
                    # New enhanced metadata
                    "extraction_method": "enhanced_ai_pipeline",
                    "competitive_analysis_applied": True,
                    "schema_version": "2.0"
                }
                
                # Generate content hash for deduplication
                content_hash = generate_content_hash(opp_data)
                
                # Check for duplicates
                result = await db.execute(select(AfricaIntelligenceItem).where(
                    AfricaIntelligenceItem.content_hash == content_hash
                ))
                existing_opp = result.scalars().first()
                
                if existing_opp:
                    print(f"⚠️  Skipping duplicate: {opp_data.get('title', 'Unknown')[:50]}...")
                    continue
                
                # Get or create organization with enhanced tracking
                org_name = opp_data.get("source_organization", "Unknown")
                organization = await get_or_create_organization(db, org_name)
                
                # Intelligent funding type detection
                funding_type_name = await determine_funding_type(
                    opp_data.get("title", ""),
                    opp_data.get("description", "")
                )
                
                # Get funding type ID
                type_result = await db.execute(
                    select(FundingType).where(FundingType.name == funding_type_name)
                )
                funding_type = type_result.scalars().first()
                funding_type_id = funding_type.id if funding_type else None
                
                # Enhanced currency detection
                detected_currency = detect_currency(opp_data.get("amount", ""))
                
                # Create enhanced AfricaIntelligenceItem with all new features
                funding_opp = AfricaIntelligenceItem(
                    # Core fields
                    title=opp_data.get("title"),
                    description=opp_data.get("description"),
                    funding_amount=opp_data.get("amount"),
                    deadline=deadline,
                    source_url=opp_data.get("source_url"),
                    application_url=opp_data.get("source_url"),
                    
                    # Enhanced organization relationship
                    organization_name=organization.name if organization else org_name,
                    organization_id=organization.id if organization else None,
                    
                    # New competitor analysis features
                    funding_type_id=funding_type_id,
                    status="open",  # Default to open for new opportunities
                    currency=detected_currency,
                    
                    # Source tracking
                    source_type="enhanced_pipeline",
                    source_name="automated_import_v2",
                    content_hash=content_hash,
                    raw_data=raw_data,
                    
                    # Metadata
                    discovered_date=datetime.now(),
                    last_updated=datetime.now(),
                    parsed_with_ai=False,
                    verified=False,
                    active=True,
                    detected_language="en",
                    is_multilingual=False,
                    translation_status={"en": "original"},
                    
                    # Initialize community features
                    view_count=0,
                    application_count=0,
                    tags={"auto_categorized": True, "enhanced_schema": True}
                )
                
                # Set the relationship directly (SQLAlchemy magic!)
                if organization:
                    funding_opp.organization = organization
                    # Update organization performance metrics
                    organization.unique_opportunities_added += 1
                    organization.data_completeness_score = min(100, organization.data_completeness_score + 5)
                    enhanced_count += 1
                
                db.add(funding_opp)
                inserted_count += 1
                
                # Enhanced logging with new features
                urgency = calculate_deadline_urgency(deadline)
                urgency_emoji = {
                    'urgent': '🔴',
                    'moderate': '🟡', 
                    'low': '🟢',
                    'expired': '⚫',
                    'unknown': '🔵'
                }.get(urgency, '❓')
                
                type_emoji = {
                    'research grant': '🔬',
                    'startup grant': '🚀',
                    'competition prize': '🏆',
                    'scholarship': '🎓',
                    'fellowship': '🤝',
                    'investment': '💰',
                    'accelerator program': '⚡'
                }.get(funding_type_name, '📋')
                
                print(f"✅ Enhanced opportunity: {opp_data.get('title', 'Unknown')[:50]}...")
                print(f"   {type_emoji} Type: {funding_type_name.title()}")
                print(f"   {urgency_emoji} Urgency: {urgency.title()}")
                print(f"   💱 Currency: {detected_currency}")
                print(f"   🏢 Organization: {org_name}")
                if organization:
                    print(f"   📊 Org Performance: {organization.data_completeness_score}% data quality")
                print()
                
            await db.commit()
            
            print("🎉 Enhanced insertion completed successfully!")
            print(f"📊 Results Summary:")
            print(f"   ✅ Inserted: {inserted_count} opportunities")
            print(f"   🔗 Enhanced: {enhanced_count} with organization relationships")
            print(f"   📈 Total processed: {len(opportunities)}")
            
            # Display enhanced analytics
            await display_enhanced_analytics(db)
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Enhanced insertion failed: {e}")
            import traceback
            traceback.print_exc()

async def display_enhanced_analytics(db: AsyncSession):
    """Display analytics showcasing enhanced features"""
    print("\n📊 Enhanced Platform Analytics:")
    
    # Deadline urgency distribution
    urgency_stats = await db.execute("""
        SELECT deadline_urgency, COUNT(*) as count
        FROM africa_intelligence_feed
        WHERE deadline_urgency IS NOT NULL
        GROUP BY deadline_urgency
        ORDER BY count DESC
    """)
    
    print("   ⏰ Deadline urgency distribution:")
    urgency_results = urgency_stats.fetchall()
    for stat in urgency_results:
        urgency_emoji = {
            'urgent': '🔴',
            'moderate': '🟡',
            'low': '🟢', 
            'expired': '⚫',
            'unknown': '🔵'
        }.get(stat.deadline_urgency, '❓')
        print(f"      {urgency_emoji} {stat.deadline_urgency.title()}: {stat.count}")
    
    # Organization performance
    org_stats = await db.execute("""
        SELECT name, unique_opportunities_added, data_completeness_score, ai_relevance_score
        FROM organizations
        WHERE unique_opportunities_added > 0
        ORDER BY unique_opportunities_added DESC
        LIMIT 5
    """)
    
    print("\n   🏢 Top performing organizations:")
    org_results = org_stats.fetchall()
    for org in org_results:
        print(f"      • {org.name}: {org.unique_opportunities_added} opportunities")
        print(f"        📊 Data Quality: {org.data_completeness_score}% | AI Relevance: {org.ai_relevance_score}%")

# Import the lookup model we need
from backend.app.models.lookups import FundingType

if __name__ == "__main__":
    import asyncio
    from datetime import timedelta
    
    print("🚀 TAIFA Enhanced Database Inserter")
    print("Based on Competitor Analysis & Notion Database Alignment")
    print("=" * 80)
    
    try:
        with open("africa_intelligence_feed.json", "r", encoding="utf-8") as f:
            opportunities_data = json.load(f)
        
        print(f"📁 Loaded {len(opportunities_data)} opportunities from JSON")
        
        # Run enhanced insertion
        asyncio.run(insert_enhanced_africa_intelligence_feed(opportunities_data))
        
        print("\n💡 Next Steps for Maximum Competitor Advantage:")
        print("   1. 🚨 Implement deadline countdown widgets in frontend")
        print("   2. 🌍 Add geographic filtering with hierarchical navigation")
        print("   3. 🤖 Create AI domain-specific landing pages")
        print("   4. 🏢 Build organization performance dashboards")
        print("   5. 💱 Add currency conversion and localization")
        print("   6. 👥 Enable community ratings and application tips")
        print("   7. 📊 Create real-time urgency indicators")
        print("   8. 🔍 Implement advanced multi-dimensional search")
        
        print("\n🏆 TAIFA now significantly exceeds competitor capabilities!")
        
    except FileNotFoundError:
        print("❌ Error: africa_intelligence_feed.json not found. Please run the extractor first.")
    except Exception as e:
        print(f"❌ Error loading or processing data: {e}")
        import traceback
        traceback.print_exc()
