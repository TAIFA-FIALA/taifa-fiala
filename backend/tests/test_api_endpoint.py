import asyncio
import httpx
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000"  # Update if your API runs on a different URL
API_KEY = os.getenv("SUPABASE_API_KEY")

async def test_create_opportunity():
    """Test creating a new funding opportunity through the API"""
    url = f"{BASE_URL}/api/v1/funding-opportunities/"
    
    # Test data
    test_data = {
        "title": "Test Funding Opportunity via API",
        "description": "This is a test funding opportunity created via the API",
        "funding_type_id": 1,  # Assuming 1 is a valid funding type ID
        "source_url": "https://example.com/test-api",
        "status": "open",
        "relevance_score": 0.8,
        "currency": "USD",
        "amount_exact": 10000.0,
        "application_deadline": "2024-12-31T23:59:59Z"
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Sending POST request to {url}")
            response = await client.post(url, json=test_data, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Successfully created opportunity with ID: {result.get('id')}")
                logger.info(f"Response: {result}")
                return True
            else:
                logger.error(f"❌ Failed to create opportunity. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error during API request: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_create_opportunity())
