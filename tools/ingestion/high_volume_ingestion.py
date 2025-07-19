#!/usr/bin/env python3
"""
High-Volume Ingestion Pipeline
==============================

With robust deduplication in place, we can now scale up ingestion volume
by processing multiple sources concurrently and expanding our data collection.

Features:
- Multiple RSS feed sources
- Concurrent processing
- Enhanced keyword filtering
- Real-time statistics
- Rate limiting and error handling
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import feedparser
import httpx
from concurrent.futures import ThreadPoolExecutor
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Import our enhanced deduplication system
from start_data_ingestion import EnhancedDeduplicator, TaifaAPIClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HighVolumeIngestionPipeline:
    """High-volume ingestion pipeline with concurrent processing"""
    
    def __init__(self, max_concurrent_feeds=5, max_items_per_feed=100):
        self.max_concurrent_feeds = max_concurrent_feeds
        self.max_items_per_feed = max_items_per_feed
        self.deduplicator = None
        self.api_client = None
        
        # Enhanced RSS feed sources for African tech/funding
        self.rss_feeds = [
            # Primary aggregate feed
            'https://www.inoreader.com/stream/user/1005214099/tag/Ai-Africa',
            
            # African tech news sources
            'https://techcabal.com/feed/',
            'https://disrupt-africa.com/feed/',
            'https://ventureburn.com/feed/',
            'https://www.itnewsafrica.com/feed/',
            
            # Funding and startup news
            'https://feeds.feedburner.com/oreilly/radar',
            'https://techcrunch.com/feed/',
            'https://www.crunchbase.com/feed',
            
            # African business news
            'https://www.businessdailyafrica.com/feed',
            'https://www.theafricareport.com/feed/',
            
            # AI and tech general feeds
            'https://www.artificialintelligence-news.com/feed/',
            'https://www.technologyreview.com/feed/',
        ]
        
        # Enhanced keywords for better filtering
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'ML', 'deep learning',
            'neural network', 'computer vision', 'natural language processing', 'NLP',
            'automation', 'robotics', 'data science', 'algorithm'
        ]
        
        self.funding_keywords = [
            'funding', 'investment', 'venture capital', 'VC', 'seed funding',
            'series A', 'series B', 'grant', 'accelerator', 'incubator',
            'startup', 'entrepreneur', 'innovation fund', 'angel investor',
            'crowdfunding', 'IPO', 'acquisition', 'merger'
        ]
        
        self.africa_keywords = [
            'Africa', 'African', 'Nigeria', 'Kenya', 'South Africa', 'Ghana',
            'Egypt', 'Morocco', 'Tunisia', 'Ethiopia', 'Uganda', 'Tanzania',
            'Rwanda', 'Senegal', 'Ivory Coast', 'Cameroon', 'Zimbabwe',
            'Botswana', 'Namibia', 'Zambia', 'Malawi', 'Madagascar'
        ]
        
        # Statistics tracking
        self.stats = {
            'feeds_processed': 0,
            'total_items_found': 0,
            'relevant_items': 0,
            'duplicates_skipped': 0,
            'items_ingested': 0,
            'errors': 0,
            'processing_time': 0,
            'feeds_failed': 0
        }
    
    async def initialize(self):
        """Initialize the pipeline components"""
        logger.info("🚀 Initializing High-Volume Ingestion Pipeline")
        
        # Initialize deduplicator
        self.deduplicator = EnhancedDeduplicator()
        await self.deduplicator.load_existing_opportunities()
        
        # Initialize API client
        self.api_client = TaifaAPIClient()
        
        logger.info(f"📡 Configured {len(self.rss_feeds)} RSS feed sources")
        logger.info(f"⚡ Max concurrent feeds: {self.max_concurrent_feeds}")
        logger.info(f"📊 Max items per feed: {self.max_items_per_feed}")
    
    async def process_feed(self, feed_url: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Process a single RSS feed with rate limiting"""
        async with semaphore:
            feed_stats = {
                'url': feed_url,
                'items_found': 0,
                'relevant_items': 0,
                'duplicates_skipped': 0,
                'items_ingested': 0,
                'errors': 0,
                'processing_time': 0
            }
            
            start_time = time.time()
            
            try:
                logger.info(f"📡 Processing feed: {feed_url}")
                
                # Parse RSS feed with timeout
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    feed = await loop.run_in_executor(executor, feedparser.parse, feed_url)
                
                feed_stats['items_found'] = len(feed.entries)
                logger.info(f"Found {len(feed.entries)} items in {feed_url}")
                
                # Process items (limit to max_items_per_feed)
                items_to_process = feed.entries[:self.max_items_per_feed]
                
                for entry in items_to_process:
                    try:
                        # Extract content
                        title = entry.get('title', '')[:255]
                        summary = (entry.get('summary', '') or entry.get('description', ''))[:500]
                        link = str(entry.link) if hasattr(entry, 'link') else ''
                        
                        # Enhanced relevance scoring
                        relevance_score = self.calculate_relevance_score(title, summary)
                        
                        # Only process highly relevant items
                        if relevance_score >= 0.3:  # 30% relevance threshold
                            feed_stats['relevant_items'] += 1
                            
                            opportunity_data = {
                                'title': title,
                                'description': summary,
                                'source_url': link[:255],
                                'application_url': link[:255],
                                'funding_type_id': 1,  # Default to 'Other' type
                                'status': 'open',
                                'amount_min': None,
                                'amount_max': None,
                                'amount_exact': None,
                                'currency': 'USD',
                                'relevance_score': relevance_score
                            }
                            
                            # Enhanced deduplication check
                            dedup_result = self.deduplicator.check_for_duplicate(opportunity_data)
                            
                            if dedup_result['is_duplicate']:
                                feed_stats['duplicates_skipped'] += 1
                                logger.debug(f"⏭️ Skipping duplicate: {title[:30]}...")
                                continue
                            
                            # Ingest the item
                            try:
                                created_item = await self.api_client.create_intelligence_item(opportunity_data)
                                if created_item:
                                    feed_stats['items_ingested'] += 1
                                    logger.info(f"✅ Ingested ({relevance_score:.1%}): {title[:40]}...")
                                else:
                                    feed_stats['errors'] += 1
                            
                            except Exception as e:
                                feed_stats['errors'] += 1
                                logger.warning(f"API error for {title[:30]}...: {e}")
                    
                    except Exception as e:
                        feed_stats['errors'] += 1
                        logger.warning(f"Error processing entry: {e}")
                        continue
                
                feed_stats['processing_time'] = time.time() - start_time
                logger.info(f"✅ Completed {feed_url}: {feed_stats['items_ingested']} ingested, {feed_stats['duplicates_skipped']} duplicates")
                
            except Exception as e:
                feed_stats['errors'] += 1
                feed_stats['processing_time'] = time.time() - start_time
                logger.error(f"❌ Failed to process {feed_url}: {e}")
            
            return feed_stats
    
    def calculate_relevance_score(self, title: str, description: str) -> float:
        """Calculate relevance score based on keywords"""
        text = (title + ' ' + description).lower()
        
        # Score components
        ai_score = sum(1 for keyword in self.ai_keywords if keyword.lower() in text)
        funding_score = sum(1 for keyword in self.funding_keywords if keyword.lower() in text)
        africa_score = sum(1 for keyword in self.africa_keywords if keyword.lower() in text)
        
        # Weighted scoring
        total_score = (
            ai_score * 0.4 +      # AI relevance: 40%
            funding_score * 0.4 + # Funding relevance: 40%
            africa_score * 0.2    # Africa relevance: 20%
        )
        
        # Normalize to 0-1 scale (max possible score is ~10)
        return min(total_score / 10.0, 1.0)
    
    async def run_high_volume_ingestion(self):
        """Run the high-volume ingestion pipeline"""
        logger.info("🔥 Starting HIGH-VOLUME ingestion with enhanced deduplication")
        
        start_time = time.time()
        
        # Create semaphore for concurrent processing
        semaphore = asyncio.Semaphore(self.max_concurrent_feeds)
        
        # Process all feeds concurrently
        tasks = [
            self.process_feed(feed_url, semaphore)
            for feed_url in self.rss_feeds
        ]
        
        # Wait for all feeds to complete
        feed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate statistics
        for result in feed_results:
            if isinstance(result, dict):
                self.stats['feeds_processed'] += 1
                self.stats['total_items_found'] += result['items_found']
                self.stats['relevant_items'] += result['relevant_items']
                self.stats['duplicates_skipped'] += result['duplicates_skipped']
                self.stats['items_ingested'] += result['items_ingested']
                self.stats['errors'] += result['errors']
            else:
                self.stats['feeds_failed'] += 1
                logger.error(f"Feed processing failed: {result}")
        
        self.stats['processing_time'] = time.time() - start_time
        
        # Log comprehensive statistics
        self.log_final_statistics()
        
        return self.stats
    
    def log_final_statistics(self):
        """Log comprehensive ingestion statistics"""
        logger.info("🎯 HIGH-VOLUME INGESTION COMPLETED!")
        logger.info("=" * 50)
        logger.info(f"📡 Feeds processed: {self.stats['feeds_processed']}/{len(self.rss_feeds)}")
        logger.info(f"📊 Total items found: {self.stats['total_items_found']}")
        logger.info(f"🎯 Relevant items: {self.stats['relevant_items']}")
        logger.info(f"🔍 Duplicates skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"✅ Items ingested: {self.stats['items_ingested']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info(f"⏱️ Total processing time: {self.stats['processing_time']:.1f}s")
        logger.info("=" * 50)
        
        # Calculate rates
        if self.stats['total_items_found'] > 0:
            relevance_rate = self.stats['relevant_items'] / self.stats['total_items_found'] * 100
            duplicate_rate = self.stats['duplicates_skipped'] / self.stats['relevant_items'] * 100 if self.stats['relevant_items'] > 0 else 0
            ingestion_rate = self.stats['items_ingested'] / self.stats['relevant_items'] * 100 if self.stats['relevant_items'] > 0 else 0
            
            logger.info(f"📈 Relevance rate: {relevance_rate:.1f}%")
            logger.info(f"🔄 Duplicate rate: {duplicate_rate:.1f}%")
            logger.info(f"💾 Ingestion success rate: {ingestion_rate:.1f}%")
            
            # Performance metrics
            items_per_second = self.stats['total_items_found'] / self.stats['processing_time']
            logger.info(f"⚡ Processing speed: {items_per_second:.1f} items/second")


async def main():
    """Main function to run high-volume ingestion"""
    try:
        # Create and initialize pipeline
        pipeline = HighVolumeIngestionPipeline(
            max_concurrent_feeds=5,  # Process 5 feeds simultaneously
            max_items_per_feed=50    # Limit items per feed to manage load
        )
        
        await pipeline.initialize()
        
        # Run the high-volume ingestion
        results = await pipeline.run_high_volume_ingestion()
        
        logger.info(f"🎉 High-volume ingestion completed! Ingested {results['items_ingested']} new opportunities")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ High-volume ingestion failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
