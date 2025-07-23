import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_supabase_connection():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_PROJECT_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase URL or API key not found in environment variables")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching a single record
        result = supabase.table('ai_intelligence_feed').select("*").limit(1).execute()
        
        if hasattr(result, 'data') and isinstance(result.data, list):
            logger.info(f"Successfully connected to Supabase. Found {len(result.data)} records in ai_intelligence_feed")
            
            # Get total count of records
            count_result = supabase.table('ai_intelligence_feed').select("id", count='exact').execute()
            total_count = len(count_result.data) if hasattr(count_result, 'data') else 0
            logger.info(f"Total records in ai_intelligence_feed: {total_count}")
            
            # Count enriched records (with funding amount, deadline, or contact)
            enriched_result = supabase.table('ai_intelligence_feed').select(
                "id"
            ).or_(
                "funding_amount.not.is.null,"
                "application_deadline.not.is.null,"
                "contact_email.not.is.null"
            ).execute()
            
            enriched_count = len(enriched_result.data) if hasattr(enriched_result, 'data') else 0
            logger.info(f"Enriched records (with funding, deadline, or contact): {enriched_count}")
            
            # Check for recent enrichment activity
            recent_result = supabase.table('ai_intelligence_feed').select(
                "id, created_at, updated_at, title"
            ).order("updated_at", desc=True).limit(5).execute()
            
            if hasattr(recent_result, 'data') and recent_result.data:
                logger.info("\nMost recently updated records:")
                for i, record in enumerate(recent_result.data, 1):
                    updated = record.get('updated_at', 'N/A')
                    title = record.get('title', 'No title')[:50] + '...' if record.get('title') else 'No title'
                    logger.info(f"{i}. {updated} - {title}")
            
            return True
        else:
            logger.error("Unexpected response format from Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Supabase connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
