import os
import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create async engine with asyncpg
        engine = create_async_engine(
            database_url.replace("postgresql://", "postgresql+asyncpg://"), 
            echo=True
        )
        
        # Test the connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Successfully connected to database. Version: {version}")
            
            # Check if the ai_intelligence_feed table exists
            result = await conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'ai_intelligence_feed'
                )
                """)
            )
            table_exists = result.scalar()
            logger.info(f"ai_intelligence_feed table exists: {table_exists}")
            
            if table_exists:
                # Get count of records
                result = await conn.execute(text("SELECT COUNT(*) FROM ai_intelligence_feed"))
                count = result.scalar()
                logger.info(f"Found {count} records in ai_intelligence_feed table")
                
                # Check for enriched records
                result = await conn.execute(
                    text("""
                    SELECT COUNT(*) 
                    FROM ai_intelligence_feed 
                    WHERE funding_amount IS NOT NULL 
                    OR application_deadline IS NOT NULL
                    OR contact_email IS NOT NULL
                    """)
                )
                enriched_count = result.scalar()
                logger.info(f"Found {enriched_count} enriched records")
            
            return True
            
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
