"""
Direct Supabase Migration Script

This script directly applies SQL migrations to the Supabase database.
It uses the DATABASE_URL from the .env file for the Supabase connection.
"""

import os
import sys
import logging
import asyncio
import traceback
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
load_dotenv()

# Define the organizations table schema for TAIFA-FIALA
ORGANIZATIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    website VARCHAR(255),
    logo_url VARCHAR(255),
    headquarters_country VARCHAR(100),
    headquarters_city VARCHAR(100),
    founded_year INTEGER,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    social_media_links JSONB,
    ai_domains JSONB,
    geographic_scopes JSONB,
    
    -- Organization role fields
    role VARCHAR(20) CHECK (role IN ('provider', 'recipient', 'both')),
    provider_type VARCHAR(50) CHECK (provider_type IN ('granting_agency', 'venture_capital', 'angel_investor', 'accelerator', NULL)),
    recipient_type VARCHAR(50) CHECK (recipient_type IN ('grantee', 'startup', 'research_institution', 'non_profit', NULL)),
    startup_stage VARCHAR(50) CHECK (startup_stage IN ('idea', 'prototype', 'seed', 'early_growth', 'expansion', NULL)),
    
    -- Equity and inclusion tracking
    women_led BOOLEAN DEFAULT FALSE,
    underrepresented_led BOOLEAN DEFAULT FALSE,
    inclusion_details JSONB,
    equity_score FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_organizations_role ON organizations(role);
CREATE INDEX IF NOT EXISTS idx_organizations_provider_type ON organizations(provider_type);
CREATE INDEX IF NOT EXISTS idx_organizations_recipient_type ON organizations(recipient_type);
CREATE INDEX IF NOT EXISTS idx_organizations_women_led ON organizations(women_led);
CREATE INDEX IF NOT EXISTS idx_organizations_underrepresented_led ON organizations(underrepresented_led);
"""

# Define the funding_types table schema
FUNDING_TYPES_SCHEMA = """
CREATE TABLE IF NOT EXISTS funding_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Enhanced funding category tracking
    category VARCHAR(50) CHECK (category IN ('grant', 'investment', 'prize', 'other')),
    requires_equity BOOLEAN DEFAULT FALSE,
    requires_repayment BOOLEAN DEFAULT FALSE,
    typical_duration_months INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_funding_types_category ON funding_types(category);
"""

# Define the funding_opportunities table schema
FUNDING_OPPORTUNITIES_SCHEMA = """
CREATE TABLE IF NOT EXISTS funding_opportunities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    amount_min NUMERIC,
    amount_max NUMERIC,
    application_deadline DATE,
    application_url VARCHAR(255),
    eligibility_criteria JSONB,
    ai_domains JSONB,
    geographic_scopes JSONB,
    funding_type_id INTEGER REFERENCES funding_types(id),
    
    -- Organization relationship fields with enhanced roles
    provider_organization_id INTEGER REFERENCES organizations(id),
    recipient_organization_id INTEGER REFERENCES organizations(id),
    
    -- Grant-specific properties
    grant_reporting_requirements TEXT,
    grant_duration_months INTEGER,
    grant_renewable BOOLEAN DEFAULT FALSE,
    
    -- Investment-specific properties
    equity_percentage FLOAT,
    valuation_cap NUMERIC,
    interest_rate FLOAT,
    expected_roi FLOAT,
    
    -- Additional fields
    status VARCHAR(50) DEFAULT 'active',
    additional_resources JSONB,
    equity_focus_details JSONB,
    women_focus BOOLEAN DEFAULT FALSE,
    underserved_focus BOOLEAN DEFAULT FALSE,
    youth_focus BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_funding_opportunities_provider_org ON funding_opportunities(provider_organization_id);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_recipient_org ON funding_opportunities(recipient_organization_id);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_funding_type ON funding_opportunities(funding_type_id);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_women_focus ON funding_opportunities(women_focus);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_underserved_focus ON funding_opportunities(underserved_focus);
CREATE INDEX IF NOT EXISTS idx_funding_opportunities_youth_focus ON funding_opportunities(youth_focus);
"""

# Simple health check table for connection testing
HEALTH_CHECK_SCHEMA = """
CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) DEFAULT 'OK',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

HEALTH_CHECK_INSERT = "INSERT INTO health_check (status) VALUES ('OK');"

async def apply_migrations():
    """Apply the migrations to Supabase"""
    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        return False
        
    # Convert to async SQLAlchemy URL if needed
    if not database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
    logger.info(f"Connecting to database: {database_url.split('@')[1]}")
    
    try:
        # Create engine
        engine = create_async_engine(database_url)
        
        # Apply migrations one statement at a time
        async with engine.begin() as conn:
            # Create health check table
            logger.info("Creating health check table...")
            await conn.execute(text(HEALTH_CHECK_SCHEMA))
            await conn.execute(text(HEALTH_CHECK_INSERT))
            logger.info("✅ Health check table created")
            
            # Create organizations table
            logger.info("Creating organizations table...")
            await conn.execute(text(ORGANIZATIONS_SCHEMA))
            logger.info("✅ Organizations table created")
            
            # Create funding types table
            logger.info("Creating funding types table...")
            await conn.execute(text(FUNDING_TYPES_SCHEMA))
            logger.info("✅ Funding types table created")
            
            # Create funding opportunities table
            logger.info("Creating funding opportunities table...")
            await conn.execute(text(FUNDING_OPPORTUNITIES_SCHEMA))
            logger.info("✅ Funding opportunities table created")
            
        logger.info("✅ All migrations applied successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error applying migrations: {e}")
        logger.error(traceback.format_exc())
        return False

async def test_connection():
    """Test the connection to Supabase"""
    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        return False
        
    # Convert to async SQLAlchemy URL if needed
    if not database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    try:
        # Create engine
        engine = create_async_engine(database_url)
        
        # Test connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Successfully connected to database")
            
            # Check for our tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"Tables in database: {', '.join(tables)}")
            
            return True
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")
        return False

async def main():
    """Main function"""
    logger.info("====== Supabase Direct Migration Tool ======")
    
    # Test connection first
    logger.info("Testing connection to Supabase...")
    if not await test_connection():
        logger.error("❌ Database connection failed. Check your DATABASE_URL.")
        return
    
    # Apply migrations
    logger.info("Applying database migrations...")
    success = await apply_migrations()
    
    if success:
        logger.info("\n🎉 Success! Database migrations applied.")
        logger.info("\nYour database is now set up with:")
        logger.info("- Organization role distinctions (provider/recipient)")
        logger.info("- Funding type categories (grant/investment/prize/other)")
        logger.info("- Grant-specific and investment-specific properties")
        logger.info("- Equity and inclusion tracking fields")
    else:
        logger.error("\n⚠️ Migration failed. Please check the logs.")

if __name__ == "__main__":
    asyncio.run(main())
