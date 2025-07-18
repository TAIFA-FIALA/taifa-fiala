import os
import sys
import asyncio
from typing import Optional, List, Dict, Any

# Add project root to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv()

# Import the database config and models
from backend.app.core.database import engine, SessionLocal
from backend.app.models.organization import Organization
from backend.app.models.funding import AfricaIntelligenceItem

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
        from datetime import datetime
        
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

async def link_opportunities_to_organizations():
    """Update existing intelligence feed to link them to organizations"""
    async with SessionLocal() as db:
        try:
            # Get all intelligence feed
            result = await db.execute(select(AfricaIntelligenceItem))
            opportunities = result.scalars().all()
            
            print(f"Found {len(opportunities)} intelligence feed to process")
            updated_count = 0
            
            for opp in opportunities:
                # Get organization name from the opportunity
                org_name = opp.organization_name
                
                if not org_name or org_name == "Unknown":
                    print(f"Skipping opportunity {opp.id}: {opp.title} (no organization name)")
                    continue
                    
                # Get or create organization
                organization = await get_or_create_organization(db, org_name)
                
                if organization:
                    # Update the raw_data to include organization info
                    if not opp.raw_data:
                        opp.raw_data = {}
                        
                    opp.raw_data["organization_id"] = organization.id
                    opp.raw_data["organization_type"] = organization.type
                    updated_count += 1
                    print(f"Linked opportunity {opp.id}: '{opp.title[:30]}...' to organization {organization.id}: '{organization.name}'")
            
            if updated_count > 0:
                await db.commit()
                print(f"Successfully updated {updated_count} intelligence feed with organization links")
            else:
                print("No intelligence feed were updated")
                
        except Exception as e:
            await db.rollback()
            print(f"Error updating organization links: {e}")

if __name__ == "__main__":
    asyncio.run(link_opportunities_to_organizations())
