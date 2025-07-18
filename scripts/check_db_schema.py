import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Define database settings directly
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

print(f"DEBUG: DATABASE_URL being used: {DATABASE_URL}")

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
    class_=AsyncSession,  # Use AsyncSession for async operations
)


async def check_tables():
    """Check database tables and their columns"""
    try:
        async with engine.connect() as conn:
            # Get all table names
            result = await conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            
            print(f"Found {len(tables)} tables: {', '.join(tables)}")
            
            # Check if africa_intelligence_feed table exists
            if 'africa_intelligence_feed' in tables:
                # Get columns for africa_intelligence_feed table
                result = await conn.execute(text("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'africa_intelligence_feed'
                    ORDER BY ordinal_position
                """))
                
                columns = [(row[0], row[1], row[2]) for row in result]
                print("\nColumns in 'africa_intelligence_feed' table:")
                for col_name, data_type, max_length in columns:
                    if max_length:
                        print(f"  - {col_name}: {data_type}({max_length})")
                    else:
                        print(f"  - {col_name}: {data_type}")
            else:
                print("Table 'africa_intelligence_feed' does not exist")
                
                # Create tables if they don't exist
                from backend.app.models import AfricaIntelligenceItem, Organization, DataSource
                print("\nModel AfricaIntelligenceItem columns:")
                for column in AfricaIntelligenceItem.__table__.columns:
                    print(f"  - {column.name}: {column.type}")
    except Exception as e:
        print(f"Error checking database schema: {e}")


if __name__ == "__main__":
    asyncio.run(check_tables())
