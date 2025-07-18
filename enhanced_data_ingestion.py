#!/usr/bin/env python3
"""
Enhanced Data Ingestion with Queue-Based Scraping
=================================================

This enhanced version of the data ingestion script integrates with the 
scraping queue system to get detailed information when RSS feeds don't 
provide enough data.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, Any, List, Optional
import feedparser
import requests

# Import our queue manager
from scraping_queue_processor import ScrapeQueueManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedDataIngestionEngine:
    """Enhanced data ingestion engine with queue-based scraping"""
    
    def __init__(self):
        self.supabase_client = None
        self.scrape_queue_manager = None
        self.total_items_processed = 0
        self.items_queued_for_scraping = 0
        
    async def initialize(self):
        """Initialize the enhanced ingestion engine"""
        logger.info("🚀 Initializing Enhanced Data Ingestion Engine")
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase_client = create_client(supabase_url, supabase_key)
        
        # Initialize scraping queue manager
        self.scrape_queue_manager = ScrapeQueueManager()
        await self.scrape_queue_manager.initialize()
        
        logger.info("✅ Enhanced ingestion engine initialized")
    
    def check_connections(self) -> bool:
        """Check database connections"""
        try:
            # Check Supabase connection
            result = self.supabase_client.table('health_check').select('*').limit(1).execute()
            logger.info("✅ Supabase connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def _needs_detailed_scraping(self, opportunity_data: Dict[str, Any]) -> bool:
        """Determine if an opportunity needs detailed scraping"""
        
        # Check if essential fields are missing or too brief
        missing_fields = []
        brief_fields = []
        
        # Check for missing critical fields
        if not opportunity_data.get('funding_amount'):
            missing_fields.append('funding_amount')
        
        if not opportunity_data.get('application_deadline'):
            missing_fields.append('application_deadline')
        
        if not opportunity_data.get('eligibility_criteria'):
            missing_fields.append('eligibility_criteria')
        
        if not opportunity_data.get('application_process'):
            missing_fields.append('application_process')
        
        # Check for brief descriptions
        description = opportunity_data.get('description', '')
        if len(description) < 200:  # Less than 200 characters
            brief_fields.append('description')
        
        # If we have missing fields or brief description, we need scraping
        needs_scraping = len(missing_fields) > 2 or len(brief_fields) > 0
        
        if needs_scraping:
            logger.info(f"📋 Opportunity needs scraping - Missing: {missing_fields}, Brief: {brief_fields}")
        
        return needs_scraping
    
    def _get_missing_fields(self, opportunity_data: Dict[str, Any]) -> List[str]:
        """Get list of fields that need to be scraped"""
        missing_fields = []
        
        if not opportunity_data.get('funding_amount'):
            missing_fields.append('amount')
        
        if not opportunity_data.get('application_deadline'):
            missing_fields.append('deadline')
        
        if not opportunity_data.get('eligibility_criteria'):
            missing_fields.append('eligibility_criteria')
        
        if not opportunity_data.get('application_process'):
            missing_fields.append('application_process')
        
        if not opportunity_data.get('contact_information') or len(opportunity_data.get('contact_information', '')) < 20:
            missing_fields.append('contact_information')
        
        # Always try to get a better description
        if len(opportunity_data.get('description', '')) < 200:
            missing_fields.append('description')
        
        return missing_fields
    
    async def process_rss_feed(self, feed_url: str) -> int:
        """Process RSS feed with enhanced scraping integration"""
        logger.info(f"📡 Processing RSS feed: {feed_url}")
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            logger.info(f"Found {len(feed.entries)} items in feed")
            
            items_processed = 0
            items_queued = 0
            
            for entry in feed.entries:
                # Check if content is relevant to AI/funding
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                
                # Basic keyword filtering
                keywords = ['AI', 'artificial intelligence', 'funding', 'investment', 'startup', 
                           'technology', 'innovation', 'grant', 'venture capital', 'accelerator',
                           'incubator', 'competition', 'challenge', 'award', 'scholarship']
                
                content_text = (title + ' ' + summary).lower()
                
                if any(keyword.lower() in content_text for keyword in keywords):
                    # This looks relevant, let's store it
                    opportunity_data = {
                        'title': title,
                        'description': summary,
                        'funding_type': 'opportunity',
                        'application_deadline': None,
                        'funding_amount': None,
                        'eligibility_criteria': None,
                        'application_process': None,
                        'contact_information': entry.get('link', ''),
                        'additional_notes': f'Collected from RSS feed: {feed_url}',
                        'source_url': entry.get('link', ''),
                        'source_type': 'rss',
                        'keywords': '[]',
                        'status': 'active'
                    }
                    
                    # Check if we need more detailed information
                    needs_scraping = self._needs_detailed_scraping(opportunity_data)
                    
                    try:
                        # Insert into funding_opportunities table
                        result = self.supabase_client.table('funding_opportunities').insert(opportunity_data).execute()
                        
                        if result.data and len(result.data) > 0:
                            opportunity_id = result.data[0]['id']
                            items_processed += 1
                            logger.info(f"✅ Added: {title[:50]}...")
                            
                            # Queue for scraping if needed
                            if needs_scraping and entry.get('link'):
                                missing_fields = self._get_missing_fields(opportunity_data)
                                
                                success = await self.scrape_queue_manager.queue_scrape_request(
                                    url=entry.get('link'),
                                    requested_fields=missing_fields,
                                    priority='medium',
                                    source_opportunity_id=opportunity_id,
                                    source_context=f"RSS feed item: {title}"
                                )
                                
                                if success:
                                    items_queued += 1
                                    logger.info(f"📋 Queued for scraping: {entry.get('link')}")
                        
                    except Exception as e:
                        logger.warning(f"Could not insert/queue item: {e}")
                        continue
            
            logger.info(f"📊 RSS Processing Complete: {items_processed} items added, {items_queued} queued for scraping")
            self.total_items_processed += items_processed
            self.items_queued_for_scraping += items_queued
            
            return items_processed
            
        except Exception as e:
            logger.error(f"❌ Error processing RSS feed {feed_url}: {e}")
            return 0
    
    async def run_enhanced_ingestion(self):
        """Run enhanced data ingestion with scraping queue integration"""
        logger.info("🚀 Starting Enhanced Data Ingestion")
        
        # Sample RSS feeds for AI and funding news in Africa
        rss_feeds = [
            'https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf',
            'https://techcentral.co.za/feed/',
            'https://ventureburn.com/feed/',
            'https://disrupt-africa.com/feed/',
            'https://african.business/technology/feed'
        ]
        
        total_items = 0
        
        for feed_url in rss_feeds:
            try:
                items = await self.process_rss_feed(feed_url)
                total_items += items
                
                # Short pause between feeds
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error processing feed {feed_url}: {e}")
                continue
        
        # Summary
        logger.info("🎉 Enhanced Ingestion Summary:")
        logger.info(f"   📊 Total items processed: {self.total_items_processed}")
        logger.info(f"   📋 Items queued for scraping: {self.items_queued_for_scraping}")
        logger.info(f"   🎯 Completion rate: {(self.total_items_processed - self.items_queued_for_scraping)/max(self.total_items_processed, 1)*100:.1f}%")
        
        if self.items_queued_for_scraping > 0:
            logger.info("💡 Next steps:")
            logger.info("   - Start the scraping queue processor to get detailed information")
            logger.info("   - Monitor the scraping_queue table for progress")
            logger.info("   - Check funding_opportunities table for updated records")
    
    async def start_queue_processor_demo(self):
        """Demo function to show how the queue processor would work"""
        logger.info("🧪 Demo: Queue Processor Integration")
        
        # This would normally be run as a separate service
        from scraping_queue_processor import ScrapingQueueProcessor
        
        processor = ScrapingQueueProcessor()
        await processor.initialize()
        
        logger.info("🔄 Queue processor initialized and ready")
        logger.info("   In production, this would run as a separate service")
        logger.info("   Processing items from the scraping_queue table")
        
        # Don't actually start processing in demo
        # await processor.start_processing()

async def main():
    """Main function for enhanced data ingestion"""
    logger.info("🚀 Enhanced AI Africa Funding Tracker - Data Ingestion")
    logger.info("=" * 70)
    
    engine = EnhancedDataIngestionEngine()
    
    try:
        # Initialize
        await engine.initialize()
        
        # Check connections
        if not engine.check_connections():
            logger.error("❌ Connection check failed")
            return
        
        # Run enhanced ingestion
        await engine.run_enhanced_ingestion()
        
        # Demo queue processor integration
        await engine.start_queue_processor_demo()
        
        logger.info("✅ Enhanced ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Enhanced ingestion failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())