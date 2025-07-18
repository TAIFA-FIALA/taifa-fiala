from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import logging
from urllib.parse import quote_plus

# Import settings for configuration
from app.core.config import settings

# Load environment variables directly
from dotenv import load_dotenv
load_dotenv()

# Import Supabase client for API-based operations
from app.core.supabase_client import get_supabase_client, test_supabase_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load database URL directly from environment variables
database_url = os.environ.get('DATABASE_URL')

# Check if we can use the production database or fall back to SQLite
use_sqlite_fallback = os.environ.get('USE_SQLITE_FALLBACK', 'false').lower() == 'true'

if use_sqlite_fallback:
    # Use SQLite for development when Supabase is not available
    # Create the database in the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(backend_dir, "ai_africa_funding.db")
    database_url = f"sqlite+aiosqlite:///{db_path}"
    logger.info(f"Using SQLite fallback database for development: {db_path}")
elif not database_url:
    # Fallback to hardcoded Supabase values if environment variable is not set
    db_params = {
        "user": "postgres.turcbnsgdlyelzmcqixd",
        "password": "cbGzmHCTZqbEsg6afVhL",
        "host": "aws-0-eu-central-2.pooler.supabase.com",
        "port": "5432",
        "database": "postgres"
    }
    # URL-encode the password to handle special characters properly
    encoded_password = quote_plus(db_params['password'])
    # Try psycopg instead of asyncpg for better Supabase compatibility
    database_url = f"postgresql+psycopg://{db_params['user']}:{encoded_password}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    logger.info("Using fallback database configuration with psycopg driver")
else:
    # Also ensure the existing DATABASE_URL has properly encoded password
    # Parse and re-encode if needed, and switch to psycopg driver
    if '@' in database_url and ':' in database_url:
        parts = database_url.split('://')
        if len(parts) == 2:
            protocol = parts[0]
            rest = parts[1]
            if '@' in rest:
                auth_part, host_part = rest.split('@', 1)
                if ':' in auth_part:
                    user, password = auth_part.split(':', 1)
                    encoded_password = quote_plus(password)
                    # Switch to psycopg driver for better compatibility
                    database_url = f"postgresql+psycopg://{user}:{encoded_password}@{host_part}"
                    logger.info("Re-encoded password and switched to psycopg driver")

# Configure for Supabase compatibility
supabase_connection = database_url and 'supabase.com' in database_url
sqlite_connection = database_url and 'sqlite' in database_url

if supabase_connection:
    logger.info("Configuring connection parameters for Supabase compatibility")
elif sqlite_connection:
    logger.info("Configuring connection parameters for SQLite compatibility")

logger.info(f"Using database URL: {database_url.split('@')[0].split('://')[-1].split(':')[0] if '@' in database_url else 'sqlite'}@...(truncated)")



# Create SQLAlchemy async engine with appropriate configuration
if supabase_connection:
    engine = create_async_engine(
        database_url,
        poolclass=NullPool,  # Use NullPool for development
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        connect_args={
            "application_name": "ai-africa-funding-tracker",
            "sslmode": "require",  # Force SSL for Supabase
            "gssencmode": "disable",  # Disable GSSAPI encryption for compatibility
        }
    )
elif sqlite_connection:
    engine = create_async_engine(
        database_url,
        poolclass=NullPool,  # Use NullPool for development
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_async_engine(
        database_url,
        poolclass=NullPool,  # Use NullPool for development
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        connect_args={
            "application_name": "ai-africa-funding-tracker",
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
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"⚠️ Database table creation failed: {e}")
        logger.info("🔄 Application will continue with limited functionality")

async def test_connection():
    """Test database connection - tries Supabase API first, then SQLAlchemy"""
    
    # First try Supabase API connection
    if not sqlite_connection:
        logger.info("🔄 Testing Supabase API connection...")
        supabase_success = await test_supabase_connection()
        if supabase_success:
            logger.info("✅ Supabase API connection successful")
            return True
        else:
            logger.warning("⚠️ Supabase API connection failed, trying SQLAlchemy...")
    
    # Fallback to SQLAlchemy connection
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ SQLAlchemy database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy database connection failed: {e}")
        if '@' in database_url:
            logger.error(f"Database URL format: {database_url.split('@')[0].split('://')[1].split(':')[0]}@...")
        else:
            logger.error(f"Database URL format: {database_url}")
        
        # Try to provide more specific error information
        if "authentication" in str(e).lower():
            logger.error("🔐 Authentication error - check credentials and connection string")
        elif "timeout" in str(e).lower():
            logger.error("⏱️ Connection timeout - check network and host")
        elif "ssl" in str(e).lower():
            logger.error("🔒 SSL connection error - check SSL configuration")
        
        return False
