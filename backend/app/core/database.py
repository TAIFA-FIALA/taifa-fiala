from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

# Load environment variables directly
from dotenv import load_dotenv
load_dotenv()

# Define hard-coded database parameters from environment
# These values come from running the backend/db_config.py script
DB_USER = "postgres.turcbnsgdlyelzmcqixd"
DB_PASSWORD = "cbGzmHCTZqbEsg6afVhL"
DB_HOST = "aws-0-eu-central-2.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"

# Construct URL directly without using regex manipulation
database_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Using direct database URL construction: {database_url[:20]}...(truncated)")



# Create SQLAlchemy async engine
engine = create_async_engine(
    database_url,
    poolclass=NullPool,  # Use NullPool for development
    echo=settings.DEBUG  # Log SQL queries in debug mode
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

# Metadata for table operations
# metadata = MetaData() # Not needed with declarative_base for this purpose

async def get_db():
    """Dependency to get async database session"""
    async with SessionLocal() as session:
        yield session

# Alias for backward compatibility
get_database = get_db

async def create_tables():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")

async def test_connection():
    """Test async database connection"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
