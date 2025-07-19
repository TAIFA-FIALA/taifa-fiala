#!/usr/bin/env python3
"""
Stage 2: Intelligent Scraping Pipeline
======================================

This module implements Stage 2 of the data ingestion pipeline:
1. Identifies records with high relevance scores from Stage 1
2. Queues them for detailed scraping with crawl4ai
3. Extracts comprehensive funding opportunity details
4. Updates records with enhanced information

The pipeline uses relevance scores to prioritize which records need detailed scraping:
- overall_relevance_score >= 0.7: High priority scraping
- overall_relevance_score >= 0.5: Medium priority scraping  
- overall_relevance_score < 0.5: Low priority or skip
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from supabase import create_client

# Import crawl4ai integration
from backend.app.services.data_ingestion.crawl4ai_integration import (
    EnhancedCrawl4AIProcessor, 
    Crawl4AIConfig, 
    CrawlTarget
)
from backend.app.services.data_ingestion.monitoring_system import ComprehensiveMonitoringSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrapingPriority(Enum):
    """Priority levels for scraping based on relevance scores"""
    HIGH = "high"           # overall_relevance_score >= 0.7
    MEDIUM = "medium"       # overall_relevance_score >= 0.5
    LOW = "low"            # overall_relevance_score >= 0.3
    SKIP = "skip"          # overall_relevance_score < 0.3


@dataclass
class ScrapingCandidate:
    """Represents a record candidate for detailed scraping"""
    id: int
    title: str
    source_url: str
    application_url: Optional[str]
    overall_relevance_score: float
    ai_relevance_score: float
    africa_relevance_score: float
    funding_relevance_score: float
    priority: ScrapingPriority
    last_scraped: Optional[datetime] = None
    scraping_attempts: int = 0
    scraping_errors: List[str] = None
    
    def __post_init__(self):
        if self.scraping_errors is None:
            self.scraping_errors = []


class IntelligentScrapingQueue:
    """Manages the intelligent scraping queue based on relevance scores"""
    
    def __init__(self, supabase_client, crawl4ai_processor: EnhancedCrawl4AIProcessor):
        self.supabase = supabase_client
        self.crawl4ai_processor = crawl4ai_processor
        self.high_priority_queue: List[ScrapingCandidate] = []
        self.medium_priority_queue: List[ScrapingCandidate] = []
        self.low_priority_queue: List[ScrapingCandidate] = []
        
        # Configuration
        self.min_relevance_threshold = 0.3
        self.high_priority_threshold = 0.7
        self.medium_priority_threshold = 0.5
        self.max_scraping_attempts = 3
        self.scraping_cooldown_hours = 24
        
        # Statistics
        self.stats = {
            'candidates_identified': 0,
            'high_priority_queued': 0,
            'medium_priority_queued': 0,
            'low_priority_queued': 0,
            'successfully_scraped': 0,
            'scraping_errors': 0,
            'records_updated': 0
        }
    
    async def identify_scraping_candidates(self, limit: int = 100) -> List[ScrapingCandidate]:
        """
        Identify records that need detailed scraping based on relevance scores
        
        Criteria:
        1. overall_relevance_score >= min_relevance_threshold
        2. source_url is not null and not empty
        3. Not recently scraped (within cooldown period)
        4. Haven't exceeded max scraping attempts
        """
        logger.info(f"🔍 Identifying scraping candidates with relevance >= {self.min_relevance_threshold}")
        
        # Calculate cooldown timestamp
        cooldown_time = datetime.utcnow() - timedelta(hours=self.scraping_cooldown_hours)
        
        # Query for candidates
        query = self.supabase.table('africa_intelligence_feed').select(
            'id, title, source_url, application_url, '
            'overall_relevance_score, ai_relevance_score, '
            'africa_relevance_score, funding_relevance_score, '
            'collected_at, updated_at'
        ).gte(
            'overall_relevance_score', self.min_relevance_threshold
        ).not_.is_(
            'source_url', 'null'
        ).neq(
            'source_url', ''
        ).limit(limit)
        
        response = query.execute()
        
        if not response.data:
            logger.info("No scraping candidates found")
            return []
        
        candidates = []
        for record in response.data:
            # Determine priority based on relevance score
            relevance = record.get('overall_relevance_score', 0.0)
            if relevance >= self.high_priority_threshold:
                priority = ScrapingPriority.HIGH
            elif relevance >= self.medium_priority_threshold:
                priority = ScrapingPriority.MEDIUM
            else:
                priority = ScrapingPriority.LOW
            
            candidate = ScrapingCandidate(
                id=record['id'],
                title=record['title'],
                source_url=record['source_url'],
                application_url=record.get('application_url'),
                overall_relevance_score=relevance,
                ai_relevance_score=record.get('ai_relevance_score', 0.0),
                africa_relevance_score=record.get('africa_relevance_score', 0.0),
                funding_relevance_score=record.get('funding_relevance_score', 0.0),
                priority=priority
            )
            
            candidates.append(candidate)
        
        self.stats['candidates_identified'] = len(candidates)
        logger.info(f"✅ Identified {len(candidates)} scraping candidates")
        
        return candidates
    
    def queue_candidates_by_priority(self, candidates: List[ScrapingCandidate]):
        """Queue candidates into priority-based queues"""
        
        for candidate in candidates:
            if candidate.priority == ScrapingPriority.HIGH:
                self.high_priority_queue.append(candidate)
                self.stats['high_priority_queued'] += 1
            elif candidate.priority == ScrapingPriority.MEDIUM:
                self.medium_priority_queue.append(candidate)
                self.stats['medium_priority_queued'] += 1
            elif candidate.priority == ScrapingPriority.LOW:
                self.low_priority_queue.append(candidate)
                self.stats['low_priority_queued'] += 1
        
        # Sort queues by relevance score (highest first)
        self.high_priority_queue.sort(key=lambda x: x.overall_relevance_score, reverse=True)
        self.medium_priority_queue.sort(key=lambda x: x.overall_relevance_score, reverse=True)
        self.low_priority_queue.sort(key=lambda x: x.overall_relevance_score, reverse=True)
        
        logger.info(f"📋 Queued candidates - High: {len(self.high_priority_queue)}, "
                   f"Medium: {len(self.medium_priority_queue)}, Low: {len(self.low_priority_queue)}")
    
    async def process_scraping_queue(self, max_items_per_priority: Dict[str, int] = None):
        """Process the scraping queues starting with highest priority"""
        
        if max_items_per_priority is None:
            max_items_per_priority = {
                'high': 20,    # Process up to 20 high priority items
                'medium': 10,  # Process up to 10 medium priority items  
                'low': 5       # Process up to 5 low priority items
            }
        
        logger.info("🚀 Starting intelligent scraping queue processing")
        
        # Process high priority queue first
        await self._process_priority_queue(
            self.high_priority_queue, 
            "HIGH", 
            max_items_per_priority['high']
        )
        
        # Process medium priority queue
        await self._process_priority_queue(
            self.medium_priority_queue, 
            "MEDIUM", 
            max_items_per_priority['medium']
        )
        
        # Process low priority queue
        await self._process_priority_queue(
            self.low_priority_queue, 
            "LOW", 
            max_items_per_priority['low']
        )
        
        logger.info("✅ Completed intelligent scraping queue processing")
    
    async def _process_priority_queue(self, queue: List[ScrapingCandidate], 
                                    priority_name: str, max_items: int):
        """Process a specific priority queue"""
        
        if not queue:
            logger.info(f"📭 No items in {priority_name} priority queue")
            return
        
        items_to_process = queue[:max_items]
        logger.info(f"🔄 Processing {len(items_to_process)} {priority_name} priority items")
        
        for candidate in items_to_process:
            try:
                await self._scrape_candidate(candidate)
                queue.remove(candidate)  # Remove from queue after successful processing
            except Exception as e:
                logger.error(f"❌ Error processing candidate {candidate.id}: {e}")
                candidate.scraping_errors.append(str(e))
                candidate.scraping_attempts += 1
                self.stats['scraping_errors'] += 1
                
                # Remove from queue if max attempts reached
                if candidate.scraping_attempts >= self.max_scraping_attempts:
                    queue.remove(candidate)
                    logger.warning(f"🚫 Removing candidate {candidate.id} after {self.max_scraping_attempts} failed attempts")
    
    async def _scrape_candidate(self, candidate: ScrapingCandidate):
        """Scrape a single candidate using crawl4ai"""
        
        logger.info(f"🕷️ Scraping candidate {candidate.id}: {candidate.title[:50]}...")
        
        # Create crawl target
        crawl_target = CrawlTarget(
            url=candidate.source_url,
            target_type="funding_opportunity",
            priority=1 if candidate.priority == ScrapingPriority.HIGH else 2,
            extraction_strategy="intelligence_item",
            metadata={
                'record_id': candidate.id,
                'relevance_score': candidate.overall_relevance_score,
                'title': candidate.title
            }
        )
        
        # Process with crawl4ai
        result = await self.crawl4ai_processor._process_single_target(crawl_target)
        
        if result and result.get('success'):
            # Update database record with enhanced information
            await self._update_record_with_scraped_data(candidate, result)
            self.stats['successfully_scraped'] += 1
            logger.info(f"✅ Successfully scraped and updated record {candidate.id}")
        else:
            raise Exception(f"Crawl4AI processing failed: {result.get('error', 'Unknown error')}")
    
    async def _update_record_with_scraped_data(self, candidate: ScrapingCandidate, scraped_data: Dict[str, Any]):
        """Update database record with enhanced scraped information"""
        
        # Extract enhanced data from scraped result
        enhanced_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'collected_at': datetime.utcnow().isoformat(),
            'ai_extracted': True,
        }
        
        # Add scraped content if available
        if 'extracted_content' in scraped_data:
            content = scraped_data['extracted_content']
            
            # Update description if we got better content
            if content.get('description') and len(content['description']) > len(candidate.title):
                enhanced_data['description'] = content['description']
            
            # Add funding details if extracted
            if content.get('amount'):
                enhanced_data['funding_amount'] = content['amount']
            
            if content.get('deadline'):
                enhanced_data['application_deadline'] = content['deadline']
            
            if content.get('eligibility'):
                enhanced_data['eligibility_criteria'] = json.dumps(content['eligibility'])
            
            # Add contact information if available
            if content.get('contact'):
                enhanced_data['contact_information'] = content['contact']
            
            # Add application process details
            if content.get('application_process'):
                enhanced_data['application_process'] = content['application_process']
        
        # Update the record
        response = self.supabase.table('africa_intelligence_feed').update(
            enhanced_data
        ).eq('id', candidate.id).execute()
        
        if response.data:
            self.stats['records_updated'] += 1
            logger.debug(f"📝 Updated record {candidate.id} with enhanced data")
        else:
            logger.warning(f"⚠️ Failed to update record {candidate.id}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current status of all queues"""
        return {
            'queues': {
                'high_priority': len(self.high_priority_queue),
                'medium_priority': len(self.medium_priority_queue),
                'low_priority': len(self.low_priority_queue),
                'total_queued': len(self.high_priority_queue) + len(self.medium_priority_queue) + len(self.low_priority_queue)
            },
            'statistics': self.stats,
            'configuration': {
                'min_relevance_threshold': self.min_relevance_threshold,
                'high_priority_threshold': self.high_priority_threshold,
                'medium_priority_threshold': self.medium_priority_threshold,
                'max_scraping_attempts': self.max_scraping_attempts,
                'scraping_cooldown_hours': self.scraping_cooldown_hours
            }
        }


async def run_stage2_pipeline():
    """Main function to run Stage 2 intelligent scraping pipeline"""
    
    logger.info("🚀 Starting Stage 2: Intelligent Scraping Pipeline")
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_PROJECT_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Initialize crawl4ai components
    monitoring_system = ComprehensiveMonitoringSystem()
    crawl4ai_config = Crawl4AIConfig(
        max_concurrent_crawlers=3,  # Conservative for Stage 2
        batch_size=10,
        relevance_threshold=0.3
    )
    
    crawl4ai_processor = EnhancedCrawl4AIProcessor(crawl4ai_config, monitoring_system)
    await crawl4ai_processor.initialize()
    
    # Initialize intelligent scraping queue
    scraping_queue = IntelligentScrapingQueue(supabase, crawl4ai_processor)
    
    try:
        # Step 1: Identify scraping candidates based on relevance scores
        candidates = await scraping_queue.identify_scraping_candidates(limit=50)
        
        if not candidates:
            logger.info("📭 No scraping candidates found. Stage 2 complete.")
            return True
        
        # Step 2: Queue candidates by priority
        scraping_queue.queue_candidates_by_priority(candidates)
        
        # Step 3: Process scraping queues
        await scraping_queue.process_scraping_queue()
        
        # Step 4: Report results
        status = scraping_queue.get_queue_status()
        logger.info("📊 Stage 2 Pipeline Results:")
        logger.info(f"   🎯 Candidates identified: {status['statistics']['candidates_identified']}")
        logger.info(f"   🔥 High priority processed: {status['statistics']['high_priority_queued']}")
        logger.info(f"   🔶 Medium priority processed: {status['statistics']['medium_priority_queued']}")
        logger.info(f"   🔸 Low priority processed: {status['statistics']['low_priority_queued']}")
        logger.info(f"   ✅ Successfully scraped: {status['statistics']['successfully_scraped']}")
        logger.info(f"   📝 Records updated: {status['statistics']['records_updated']}")
        logger.info(f"   ❌ Scraping errors: {status['statistics']['scraping_errors']}")
        
        logger.info("🎉 Stage 2: Intelligent Scraping Pipeline completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Stage 2 pipeline failed: {e}")
        return False
    
    finally:
        # Cleanup
        await crawl4ai_processor.close()


if __name__ == "__main__":
    asyncio.run(run_stage2_pipeline())
