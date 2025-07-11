#!/usr/bin/env python3
"""
Database initialization script for AI Africa Funding Tracker
Creates initial database tables and loads sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, test_connection
from app.models import *

def create_database():
    """Check if database exists (TAIFA_db should already exist)"""
    try:
        # Test connection to the existing database
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            current_db = result.fetchone()[0]
            
            if current_db == settings.DATABASE_NAME:
                print(f"✅ Connected to existing database: {settings.DATABASE_NAME}")
            else:
                print(f"⚠️  Connected to {current_db}, expected {settings.DATABASE_NAME}")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure TAIFA_db exists on mac-mini and Tailscale is connected")
        return False

def create_tables():
    """Create all database tables"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def load_sample_data():
    """Load sample data for testing"""
    try:
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Sample organizations
        sample_orgs = [
            Organization(
                name="Bill & Melinda Gates Foundation",
                type="funder",
                country="United States",
                region="Global",
                website="https://www.gatesfoundation.org",
                description="Global foundation focused on health, development, and education",
                funding_capacity="Large",
                focus_areas='["Health", "Development", "AI for Good"]'
            ),
            Organization(
                name="Science for Africa Foundation",
                type="funder", 
                country="Kenya",
                region="East Africa",
                website="https://scienceforafrica.foundation",
                description="Supporting African-led scientific innovation",
                funding_capacity="Medium",
                focus_areas='["Science", "Innovation", "AI Research"]'
            )
        ]
        
        # Sample AI domains
        sample_domains = [
            AIDomain(name="Healthcare AI", description="AI applications in healthcare and medical research"),
            AIDomain(name="Agricultural AI", description="AI for agriculture and food security"),
            AIDomain(name="Education AI", description="AI in education and learning"),
            AIDomain(name="Governance AI", description="AI for governance and public services"),
        ]
        
        # Sample funding categories
        sample_categories = [
            FundingCategory(name="Research Grants", description="Funding for research projects"),
            FundingCategory(name="Implementation Funding", description="Funding for deploying AI solutions"),
            FundingCategory(name="Capacity Building", description="Training and education funding"),
            FundingCategory(name="Innovation Prizes", description="Competition-based funding"),
        ]
        
        # Add to database
        for org in sample_orgs:
            db.add(org)
        for domain in sample_domains:
            db.add(domain)
        for category in sample_categories:
            db.add(category)
        
        db.commit()
        
        # Sample funding opportunity
        sample_funding = FundingOpportunity(
            title="AI for Health Innovation Grant",
            description="Supporting AI innovations to improve healthcare outcomes in Africa",
            amount=100000,
            currency="USD",
            amount_usd=100000,
            status="active",
            source_url="https://example.com/grant",
            geographical_scope="Sub-Saharan Africa",
            eligibility_criteria="African organizations and researchers",
            source_organization_id=1  # Gates Foundation
        )
        
        db.add(sample_funding)
        db.commit()
        
        print("✅ Sample data loaded successfully")
        
        db.close()
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing AI Africa Funding Tracker Database")
    print(f"Database: {settings.DATABASE_NAME} on {settings.DATABASE_HOST}")
    print("=" * 50)
    
    # Test connection first
    print("Testing database connection...")
    if not test_connection():
        print("❌ Cannot connect to database. Check your configuration.")
        return False
    
    # Check database
    print("\nChecking database...")
    if not create_database():
        return False
    
    # Create tables
    print("\nCreating tables...")
    if not create_tables():
        return False
    
    # Load sample data
    print("\nLoading sample data...")
    if not load_sample_data():
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print(f"\nTAIFA_db is ready on {settings.DATABASE_HOST}!")
    print("\nNext steps:")
    print("1. Start the backend: uvicorn app.main:app --reload")
    print("2. Start the Streamlit app: streamlit run frontend/streamlit_app/app.py")
    print("3. Visit http://localhost:8000/docs for API documentation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
