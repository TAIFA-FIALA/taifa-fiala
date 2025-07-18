#!/usr/bin/env python3
"""
Dynamic RSS Feed Ingestion for TAIFA-FIALA
==========================================

This script reads RSS feeds from the database and collects intelligence data.
It replaces the hardcoded RSS feeds with dynamic database-driven feeds.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, Any, List, Optional
import feedparser
import requests
import json
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DynamicRSSIngestion:
    """Dynamic RSS ingestion engine that reads feeds from database"""
    
    def __init__(self):
        self.supabase_client = None
        self.total_items_processed = 0
        self.items_added = 0
        self.items_skipped = 0
        
    async def initialize(self):
        """Initialize the dynamic RSS ingestion engine"""
        logger.info("🚀 Initializing Dynamic RSS Ingestion Engine")
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("❌ Missing Supabase credentials")
            return False
        
        self.supabase_client = create_client(supabase_url, supabase_key)
        logger.info("✅ Connected to Supabase")
        
        return True
    
    async def get_active_feeds(self) -> List[Dict[str, Any]]:
        """Get all active RSS feeds from the database"""
        try:
            result = self.supabase_client.table('rss_feeds').select('*').eq('is_active', True).execute()
            
            if result.data:
                logger.info(f"📡 Found {len(result.data)} active RSS feeds")
                return result.data
            else:
                logger.warning("⚠️ No active RSS feeds found in database")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching RSS feeds: {e}")
            return []
    
    async def process_feed(self, feed_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single RSS feed"""
        feed_name = feed_config['name']
        feed_url = feed_config['url']
        feed_id = feed_config['id']
        
        logger.info(f"🔄 Processing feed: {feed_name}")
        
        try:
            # Update last_checked timestamp
            self.supabase_client.table('rss_feeds').update({
                'last_checked': datetime.utcnow().isoformat()
            }).eq('id', feed_id).execute()
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                error_msg = f"Invalid RSS feed format: {feed.bozo_exception}"
                logger.error(f"❌ {feed_name}: {error_msg}")
                await self.update_feed_error(feed_id, error_msg)
                return {'success': False, 'error': error_msg, 'items_processed': 0}
            
            # Process feed items
            items_processed = 0
            items_added = 0
            keywords = json.loads(feed_config.get('keywords', '[]'))
            exclude_keywords = json.loads(feed_config.get('exclude_keywords', '[]'))
            max_items = feed_config.get('max_items_per_check', 50)
            
            for entry in feed.entries[:max_items]:
                try:
                    # Check if item is relevant
                    if not self.is_relevant_item(entry, keywords, exclude_keywords):
                        continue
                    
                    # Create intelligence item
                    intelligence_item = self.create_intelligence_item(entry, feed_config)
                    
                    # Check for duplicates
                    if await self.is_duplicate_item(intelligence_item):
                        logger.debug(f"⏭️ Skipping duplicate: {intelligence_item['title'][:50]}...")
                        continue
                    
                    # Save to database
                    result = self.supabase_client.table('africa_intelligence_feed').insert(intelligence_item).execute()
                    
                    if result.data:
                        items_added += 1
                        logger.info(f"✅ Added: {intelligence_item['title'][:50]}...")
                    
                    items_processed += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing item: {e}")
                    continue
            
            # Update feed statistics
            await self.update_feed_stats(feed_id, items_processed, items_added, True)
            
            logger.info(f"✅ {feed_name}: {items_added} new items added ({items_processed} processed)")
            
            return {
                'success': True,
                'items_processed': items_processed,
                'items_added': items_added,
                'feed_name': feed_name
            }
            
        except Exception as e:
            error_msg = f"Error processing feed: {str(e)}"
            logger.error(f"❌ {feed_name}: {error_msg}")
            await self.update_feed_error(feed_id, error_msg)
            return {'success': False, 'error': error_msg, 'items_processed': 0}
    
    def is_relevant_item(self, entry: Dict, keywords: List[str], exclude_keywords: List[str]) -> bool:
        """Check if an RSS item is relevant based on keywords"""
        title = entry.get('title', '').lower()
        description = entry.get('description', '').lower()
        content = title + ' ' + description
        
        # Check exclude keywords first
        if exclude_keywords:
            for exclude_keyword in exclude_keywords:
                if exclude_keyword.lower() in content:
                    return False
        
        # Check include keywords
        if keywords:
            for keyword in keywords:
                if keyword.lower() in content:
                    return True
            return False  # No keywords matched
        
        return True  # No keyword filtering
    
    def create_intelligence_item(self, entry: Dict, feed_config: Dict) -> Dict[str, Any]:
        """Create an intelligence item from RSS entry"""
        title = entry.get('title', 'Untitled')
        description = entry.get('description', '') or entry.get('summary', '')
        link = entry.get('link', '')
        
        # Create content hash for duplicate detection
        content_hash = hashlib.md5((title + link).encode()).hexdigest()
        
        return {
            'title': title,
            'description': description,
            'source_url': link,
            'application_url': link,
            'funding_type': 'opportunity',
            'application_deadline': None,
            'funding_amount': None,
            'eligibility_criteria': None,
            'application_process': None,
            'contact_information': link,
            'additional_notes': f'Collected from RSS feed: {feed_config["name"]}. Category: {feed_config["category"]}. Region: {feed_config["region"]}',
            'source_type': 'rss',
            'keywords': feed_config.get('keywords', '[]'),
            'status': 'active',
            'content_hash': content_hash
        }
    
    async def is_duplicate_item(self, item: Dict[str, Any]) -> bool:
        """Check if an item already exists in the database"""
        try:
            result = self.supabase_client.table('africa_intelligence_feed').select('id').eq(
                'content_hash', item['content_hash']
            ).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking for duplicates: {e}")
            return False
    
    async def update_feed_stats(self, feed_id: int, items_processed: int, items_added: int, success: bool):
        """Update feed statistics in the database"""
        try:
            # Get current stats
            current_feed = self.supabase_client.table('rss_feeds').select('total_items_collected,error_count,success_rate').eq('id', feed_id).execute()
            
            if current_feed.data:
                current_total = current_feed.data[0].get('total_items_collected', 0)
                current_errors = current_feed.data[0].get('error_count', 0)
                current_success_rate = current_feed.data[0].get('success_rate', 0)
                
                # Calculate new stats
                new_total = current_total + items_added
                new_errors = current_errors if success else current_errors + 1
                
                # Simple success rate calculation
                total_checks = max(1, (new_total + new_errors))
                new_success_rate = ((total_checks - new_errors) / total_checks) * 100
                
                # Update database
                self.supabase_client.table('rss_feeds').update({
                    'total_items_collected': new_total,
                    'error_count': new_errors,
                    'success_rate': new_success_rate,
                    'last_successful_check': datetime.utcnow().isoformat() if success else None,
                    'last_error': None if success else 'Processing error'
                }).eq('id', feed_id).execute()
                
        except Exception as e:
            logger.warning(f"⚠️ Error updating feed stats: {e}")
    
    async def update_feed_error(self, feed_id: int, error_message: str):
        """Update feed with error information"""
        try:
            self.supabase_client.table('rss_feeds').update({
                'last_error': error_message,
                'error_count': self.supabase_client.rpc('increment_error_count', {'feed_id': feed_id}).execute()
            }).eq('id', feed_id).execute()
            
        except Exception as e:
            logger.warning(f"⚠️ Error updating feed error: {e}")
    
    async def run_ingestion(self):
        """Run the complete RSS ingestion process"""
        logger.info("🚀 Starting Dynamic RSS Ingestion")
        
        # Get active feeds
        feeds = await self.get_active_feeds()
        
        if not feeds:
            logger.warning("⚠️ No active RSS feeds found. Please add feeds through the dashboard.")
            return
        
        # Process each feed
        results = []
        for feed in feeds:
            result = await self.process_feed(feed)
            results.append(result)
            
            if result['success']:
                self.items_added += result['items_added']
                self.total_items_processed += result['items_processed']
        
        # Summary
        successful_feeds = len([r for r in results if r['success']])
        failed_feeds = len([r for r in results if not r['success']])
        
        logger.info(f"🎉 Dynamic RSS Ingestion Complete!")
        logger.info(f"✅ Successful feeds: {successful_feeds}")
        logger.info(f"❌ Failed feeds: {failed_feeds}")
        logger.info(f"📊 Total items processed: {self.total_items_processed}")
        logger.info(f"📈 New items added: {self.items_added}")
        
        return {
            'successful_feeds': successful_feeds,
            'failed_feeds': failed_feeds,
            'total_items_processed': self.total_items_processed,
            'items_added': self.items_added
        }

async def main():
    """Main function to run dynamic RSS ingestion"""
    ingestion = DynamicRSSIngestion()
    
    # Initialize
    if not await ingestion.initialize():
        logger.error("❌ Failed to initialize RSS ingestion")
        return
    
    # Run ingestion
    await ingestion.run_ingestion()

if __name__ == "__main__":
    asyncio.run(main())