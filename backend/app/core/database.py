from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

# Import settings for configuration
from app.core.config import settings

# Load environment variables directly
from dotenv import load_dotenv
load_dotenv()

# Load database URL directly from environment variables
database_url = os.environ.get('DATABASE_URL')

# Use the original asyncpg driver since it was working before
if not database_url:
    # Fallback to hardcoded values if environment variable is not set
    db_params = {
        "user": "postgres.turcbnsgdlyelzmcqixd",
        "password": "cbGzmHCTZqbEsg6afVhL",
        "host": "aws-0-eu-central-2.pooler.supabase.com",
        "port": "5432",
        "database": "postgres"
    }
    database_url = f"postgresql+asyncpg://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    print("Using fallback database configuration")

# Add SSL parameters to fix authentication issues
if database_url and 'supabase.com' in database_url:
    if '?' not in database_url:
        database_url += '?ssl=require'
    else:
        database_url += '&ssl=require'

print(f"Using database URL: {database_url.split('@')[0].split('://')[-1].split(':')[0]}@...(truncated)")



# Create SQLAlchemy async engine with original configuration
engine = create_async_engine(
    database_url,
    poolclass=NullPool,  # Use NullPool for development
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    connect_args={
        "server_settings": {
            "application_name": "ai-africa-funding-tracker",
        }
    }
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
        print(f"Database URL format: {database_url.split('@')[0].split('://')[1].split(':')[0]}@...")
        return False
