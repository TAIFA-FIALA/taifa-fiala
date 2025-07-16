"""
Apply Alembic Migrations to Supabase

This script applies the existing Alembic migrations to the Supabase database
using the connection details from the .env file.
"""

import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def update_database_url():
    """Update the DATABASE_URL environment variable to use Supabase"""
    # Load environment variables
    load_dotenv()
    
    # Get Supabase connection details
    supabase_url = os.getenv("SUPABASE_PROJECT_URL")
    database_url = os.getenv("DATABASE_URL")
    
    if not supabase_url:
        logger.error("❌ Missing SUPABASE_PROJECT_URL environment variable")
        return False
    
    if not database_url:
        logger.error("❌ Missing DATABASE_URL environment variable")
        return False
        
    logger.info(f"ℹ️ Using Supabase database: {database_url}")
    
    # We're good to go - the DATABASE_URL from the .env is what we need
    return True

def run_migrations():
    """Run Alembic migrations"""
    try:
        logger.info("Running Alembic migrations...")
        
        # Change to the directory containing the alembic.ini file
        os.chdir(os.path.join(current_dir, "alembic"))
        
        # Run the migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info("✅ Migrations applied successfully!")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running migrations: {e}")
        return False

def verify_database():
    """Verify the database by checking for key tables"""
    try:
        # This would require a database connection library
        # We'll use our existing test_supabase_pinecone_db.py for this
        logger.info("Verifying database tables...")
        logger.info("Run tests/test_supabase_pinecone_db.py after migrations to verify")
        return True
    except Exception as e:
        logger.error(f"❌ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    logger.info("====== Supabase Migration Tool ======")
    
    # Prepare the database URL
    if update_database_url():
        # Run the migrations
        if run_migrations():
            # Verify the database
            verify_database()
    
    logger.info("====== Migration Complete ======")
