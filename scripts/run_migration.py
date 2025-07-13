#!/usr/bin/env python3
"""
Database migration script to add organization_id foreign key relationship
"""
import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def run_migration():
    """Run the database migration to add organization_id foreign key"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    print("🚀 Starting database migration: add organization_id foreign key")
    print(f"📍 Database: {database_url.split('@')[1] if '@' in database_url else 'hidden'}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Check if migration is already applied
        try:
            await conn.fetchval("SELECT organization_id FROM funding_opportunities LIMIT 1")
            print("⚠️  Migration already applied - organization_id column exists")
            return
        except asyncpg.UndefinedColumnError:
            print("✅ Migration needed - organization_id column does not exist")
        
        # Start transaction
        async with conn.transaction():
            print("📝 Adding organization_id column...")
            await conn.execute("""
                ALTER TABLE funding_opportunities 
                ADD COLUMN organization_id INTEGER
            """)
            
            print("🔗 Adding foreign key constraint...")
            await conn.execute("""
                ALTER TABLE funding_opportunities 
                ADD CONSTRAINT fk_funding_opportunities_organization_id 
                FOREIGN KEY (organization_id) REFERENCES organizations(id)
            """)
            
            print("⚡ Adding performance index...")
            await conn.execute("""
                CREATE INDEX idx_funding_opportunities_organization_id 
                ON funding_opportunities(organization_id)
            """)
            
            # Create alembic_version table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL PRIMARY KEY
                )
            """)
            
            # Record migration version
            await conn.execute("""
                INSERT INTO alembic_version (version_num) VALUES ('001') 
                ON CONFLICT (version_num) DO NOTHING
            """)
            
            print("📊 Verifying migration...")
            
            # Verify the column was added
            column_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'funding_opportunities' 
                    AND column_name = 'organization_id'
                )
            """)
            
            if column_exists:
                print("✅ Migration completed successfully!")
                print("   - organization_id column added")
                print("   - Foreign key constraint created")
                print("   - Performance index created")
                print("   - Migration version recorded")
            else:
                raise Exception("Migration verification failed")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

async def test_relationship():
    """Test the new relationship functionality"""
    print("\n🧪 Testing relationship functionality...")
    
    # Test imports
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app.models.funding import FundingOpportunity
        from app.models.organization import Organization
        print("✅ Model imports successful")
        
        # Test relationship attributes
        if hasattr(FundingOpportunity, 'organization'):
            print("✅ FundingOpportunity.organization relationship exists")
        else:
            print("❌ FundingOpportunity.organization relationship missing")
            
        if hasattr(Organization, 'funding_opportunities'):
            print("✅ Organization.funding_opportunities relationship exists")
        else:
            print("❌ Organization.funding_opportunities relationship missing")
            
    except ImportError as e:
        print(f"⚠️  Could not test relationships due to import error: {e}")
        print("   This is expected if backend modules have path issues")

if __name__ == "__main__":
    print("=" * 60)
    print("TAIFA Database Migration: Organization Relationships")
    print("=" * 60)
    
    asyncio.run(run_migration())
    asyncio.run(test_relationship())
    
    print("\n🎉 Migration complete! You can now use proper SQLAlchemy relationships.")
    print("\nNext steps:")
    print("1. Update db_inserter.py to use the new organization_id field")
    print("2. Migrate existing data from organization_name to organization_id")
    print("3. Test the new relationship functionality")
