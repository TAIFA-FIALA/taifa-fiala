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
    """Set up initial data sources if they don't exist"""
    
    try:
        client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
        
        # Check if we have funding opportunities
        result = client.table('funding_opportunities').select('*').limit(1).execute()
        
        if len(result.data) == 0:
            logger.info("No funding opportunities found. Setting up initial data sources...")
            
            # Initial RSS feeds for testing
            initial_feeds = [
                {
                    'name': 'AllAfrica Technology News',
                    'url': 'https://allafrica.com/tools/headlines/rdf/technology/headlines.rdf',
                    'source_type': 'rss',
                    'keywords': '["AI", "artificial intelligence", "technology", "innovation", "funding"]',
                    'check_interval_minutes': 60,
                    'enabled': True
                },
                {
                    'name': 'African Business Tech',
                    'url': 'https://african.business/technology/feed',
                    'source_type': 'rss',
                    'keywords': '["startup", "investment", "funding", "AI", "technology"]',
                    'check_interval_minutes': 120,
                    'enabled': True
                }
            ]
            
            # Try to add to data_sources table if it exists
            try:
                for feed in initial_feeds:
                    # For now, let's just log what we would add
                    logger.info(f"Would add data source: {feed['name']}")
                    
            except Exception as e:
                logger.warning(f"Could not add initial data sources: {e}")
                logger.info("You'll need to add data sources manually or create the data_sources table")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up initial data sources: {e}")
        return False

async def start_basic_ingestion():
    """Start basic data ingestion using existing RSS feeds"""
    
    logger.info("🚀 Starting basic data ingestion...")
    
    # Import RSS feed reader
    try:
        import feedparser
        import requests
        from datetime import datetime
        
        # Sample RSS feeds for AI and funding news in Africa
        rss_feeds = [
            'https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf',
            'https://techcentral.co.za/feed/',
            'https://ventureburn.com/feed/',
        ]
        
        client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
        
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
                        # This looks relevant, let's store it
                        # Use all available fields
                        opportunity_data = {
                            'title': title,
                            'description': summary,
                            'organization_name': feed.feed.get('title', 'Unknown'),
                            'funding_type': 'opportunity',  # Default type
                            'application_deadline': None,
                            'funding_amount': None,
                            'eligibility_criteria': None,
                            'application_process': None,
                            'contact_information': entry.get('link', ''),
                            'additional_notes': f'Collected from RSS feed: {feed_url}',
                            'source_url': entry.get('link', ''),
                            'source_type': 'rss',
                            'keywords': '[]',  # Empty JSON array as string
                            'status': 'active'
                        }
                        
                        try:
                            # Try to insert into funding_opportunities table
                            result = client.table('funding_opportunities').insert(opportunity_data).execute()
                            total_items += 1
                            logger.info(f"✅ Added: {title[:50]}...")
                            
                        except Exception as e:
                            logger.warning(f"Could not insert item: {e}")
                            continue
                
            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}")
                continue
        
        logger.info(f"🎉 Basic ingestion completed! Added {total_items} items to database")
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
        logger.info("- Check the funding_opportunities table for new data")
        logger.info("- Set up the full ingestion schema for high-volume processing")
        logger.info("- Configure additional RSS feeds and data sources")
        logger.info("- Set up scheduled ingestion jobs")
    else:
        logger.error("❌ Data ingestion startup failed")

if __name__ == "__main__":
    asyncio.run(main())
