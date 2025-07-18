#!/usr/bin/env python3
"""
Start Data Ingestion Pipeline
=============================

This script starts the data ingestion pipeline for the AI Africa Funding Tracker.
It will collect data from various sources and store it in the database.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Add project root to Python path to enable imports from other modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_connections():
    """Check database connections before starting ingestion"""
    
    # Check Supabase connection
    try:
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Missing Supabase credentials")
            return False
        
        client = create_client(supabase_url, supabase_key)
        result = client.table('health_check').select('*').limit(1).execute()
        logger.info("✅ Supabase connection successful")
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False
    
    # Check Pinecone connection
    try:
        from pinecone import Pinecone
        
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        if not pinecone_api_key:
            logger.error("❌ Missing Pinecone API key")
            return False
        
        pc = Pinecone(api_key=pinecone_api_key)
        indexes = pc.list_indexes()
        logger.info("✅ Pinecone connection successful")
        
    except Exception as e:
        logger.error(f"❌ Pinecone connection failed: {e}")
        return False
    
    return True

def setup_initial_data_sources():
    """Set up initial data sources and default funding types if they don't exist"""
    
    try:
        client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
        
        # Ensure default funding types exist
        logger.info("Checking for default funding types...")
        default_funding_types = [
            {"name": "Grant", "category": "grant", "description": "Non-repayable funds given by one party (grantor) to a recipient, often a nonprofit entity, educational institution, business, or individual.", "requires_equity": False, "requires_repayment": False},
            {"name": "Investment", "category": "investment", "description": "Capital provided to a business in exchange for equity or a share in future profits, typically with an expectation of return.", "requires_equity": True, "requires_repayment": False},
            {"name": "Prize", "category": "prize", "description": "A reward given for winning a competition or for achieving a certain level of excellence.", "requires_equity": False, "requires_repayment": False},
            {"name": "Other", "category": "other", "description": "Miscellaneous funding opportunities not falling into other categories.", "requires_equity": False, "requires_repayment": False}
        ]

        for ft_data in default_funding_types:
            existing_ft = client.table('funding_types').select('id').eq('name', ft_data['name']).execute()
            if not existing_ft.data:
                logger.info(f"Adding default funding type: {ft_data['name']}")
                client.table('funding_types').insert(ft_data).execute()
            else:
                logger.info(f"Funding type {ft_data['name']} already exists.")

        # Check if we have funding intelligence_items
        result = client.table('africa_intelligence_feed').select('*').limit(1).execute()
        
        if len(result.data) == 0:
            logger.info("No funding intelligence_items found. Initial data sources will be set up by ingestion.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up initial data sources: {e}")
        return False

async def start_basic_ingestion():
    """Start basic data ingestion using existing RSS feeds"""
    
    logger.info("🚀 Starting basic data ingestion with aggregate feed...")
    logger.info("🔍 Using Inoreader aggregate RSS feed for AI-Africa content")
    
    # Import RSS feed reader and API client
    try:
        logger.info("Attempting to import feedparser...")
        import feedparser
        logger.info("✅ feedparser imported successfully")
        
        logger.info("Attempting to import requests...")
        import requests
        logger.info("✅ requests imported successfully")
        
        logger.info("Attempting to import datetime...")
        from datetime import datetime
        logger.info("✅ datetime imported successfully")
        
        logger.info("Attempting to import TaifaAPIClient...")
        from frontend.streamlit_app.api_client import TaifaAPIClient
        logger.info("✅ TaifaAPIClient imported successfully")
        
        # Use the aggregate RSS feed provided by the user
        logger.info("Using Inoreader aggregate RSS feed for AI-Africa news")
        rss_feeds = [
            'https://www.inoreader.com/stream/user/1005214099/tag/Ai-Africa'
        ]
        
        logger.info(f"Using RSS feed: {rss_feeds[0]}")
        
        # Initialize API client
        api_client = TaifaAPIClient()
        
        # Get the funding_type_id for 'Other'
        client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
        other_funding_type_response = client.table('funding_types').select('id').eq('name', 'Other').execute()
        other_funding_type_id = other_funding_type_response.data[0]['id'] if other_funding_type_response.data else None

        if not other_funding_type_id:
            logger.error("❌ Could not find 'Other' funding type ID. Please ensure default funding types are set up.")
            return False

        total_items = 0
        
        for feed_url in rss_feeds:
            try:
                logger.info(f"Processing RSS feed: {feed_url}")
                
                # Parse RSS feed
                feed = feedparser.parse(feed_url)
                
                logger.info(f"Found {len(feed.entries)} items in feed")
                
                for entry in feed.entries:
                    # Check if content is relevant to AI/funding
                    title = entry.get('title', '')
                    summary = entry.get('summary', '') or entry.get('description', '')
                    
                    # Basic keyword filtering
                    keywords = ['AI', 'artificial intelligence', 'funding', 'investment', 'startup', 
                               'technology', 'innovation', 'grant', 'venture capital']
                    
                    content_text = (title + ' ' + summary).lower()
                    
                    if any(keyword.lower() in content_text for keyword in keywords):
                        # Prepare data for FastAPI endpoint
                        # Ensure all URLs are strings to prevent HttpUrl serialization issues
                        link = str(entry.get('link', '')) if entry.get('link') else ''
                        
                        opportunity_data = {
                            'title': title,
                            'description': summary,
                            'source_url': link,
                            'application_url': link,
                            'funding_type_id': other_funding_type_id, # Use the ID for 'Other'
                            'status': 'active',
                            'geographical_scope': 'Africa',
                            'eligibility_criteria': 'N/A',
                            'contact_info': link,
                            'application_deadline': None,
                            'amount': None,
                            'currency': 'USD'
                        }
                        
                        try:
                            # Call FastAPI endpoint to create intelligence item
                            created_item = await api_client.create_intelligence_item(opportunity_data)
                            if created_item:
                                total_items += 1
                                logger.info(f"✅ Added via API: {title[:50]}...")
                            else:
                                logger.warning(f"Could not add item via API: {title[:50]}...")
                            
                        except Exception as e:
                            logger.warning(f"Error calling API for item {title[:50]}...: {e}")
                            continue
                
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}")
                continue
        
        logger.info(f"🎉 Basic ingestion completed! Added {total_items} items to database via API")
        return True
        
    except ImportError:
        logger.error("❌ Required libraries not installed. Run: pip install feedparser requests")
        return False
    except Exception as e:
        logger.error(f"❌ Error during basic ingestion: {e}")
        return False

async def main():
    """Main function to start data ingestion"""
    
    logger.info("🚀 AI Africa Funding Tracker - Data Ingestion Startup")
    logger.info("=" * 60)
    
    # Check connections
    logger.info("1. Checking database connections...")
    if not check_connections():
        logger.error("❌ Connection check failed. Please fix connection issues before proceeding.")
        return
    
    # Setup initial data sources
    logger.info("2. Setting up initial data sources...")
    if not setup_initial_data_sources():
        logger.warning("⚠️  Could not set up initial data sources")
    
    # Start basic ingestion
    logger.info("3. Starting basic data ingestion...")
    success = await start_basic_ingestion()
    
    if success:
        logger.info("🎉 Data ingestion startup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("- Check the intelligence_feed table for new data")
        logger.info("- Set up the full ingestion schema for high-volume processing")
        logger.info("- Configure additional RSS feeds and data sources")
        logger.info("- Set up scheduled ingestion jobs")
    else:
        logger.error("❌ Data ingestion startup failed")

if __name__ == "__main__":
    asyncio.run(main())
