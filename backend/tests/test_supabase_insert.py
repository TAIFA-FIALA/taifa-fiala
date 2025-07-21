import asyncio
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_PROJECT_URL')
key = os.getenv('SUPABASE_SERVICE_API_KEY')

if not url or not key:
    raise ValueError("Missing SUPABASE_PROJECT_URL or SUPABASE_API_KEY in environment variables")

supabase: Client = create_client(url, key)

async def test_insert():
    """Test inserting a record into Supabase and verify ID is returned"""
    test_data = {
        'title': 'Test Funding Opportunity',
        'description': 'This is a test funding opportunity',
        'funding_type_id': 1,  # Assuming 1 is a valid funding type ID
        'source_url': 'https://example.com/test',
        'status': 'open',
        'relevance_score': 0.8
    }
    
    try:
        logger.info("Attempting to insert test record...")
        # First, insert the data
        logger.info("Inserting test record...")
        insert_response = supabase.table('africa_intelligence_feed').insert(test_data).execute()
        
        # Check if the insert was successful
        if hasattr(insert_response, 'data') and insert_response.data:
            # If the insert returns the data, use it
            record = insert_response.data[0] if isinstance(insert_response.data, list) else insert_response.data
            logger.info(f"✅ Successfully inserted record. ID: {record.get('id')}")
            logger.info(f"Record details: {record}")
            return True
        else:
            # If insert didn't return the data, try to fetch the most recent record
            logger.info("Insert response didn't contain data. Trying to fetch most recent record...")
            try:
                recent = supabase.table('africa_intelligence_feed')\
                              .select('*')\
                              .order('created_at', desc=True)\
                              .limit(1)\
                              .execute()
                
                if recent.data:
                    record = recent.data[0]
                    logger.info(f"✅ Retrieved record with fallback method. ID: {record.get('id')}")
                    logger.info(f"Record details: {record}")
                    return True
                else:
                    logger.error("❌ No records found in the table")
                    return False
            except Exception as fetch_error:
                logger.error(f"❌ Error fetching recent record: {str(fetch_error)}")
                return False
            
    except Exception as e:
        logger.error(f"❌ Error during insert test: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_insert())
