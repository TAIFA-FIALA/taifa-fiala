#!/usr/bin/env python3
"""
Stage 2: Simplified Intelligent Scraping Pipeline
=================================================

This module implements Stage 2 of the data ingestion pipeline:
1. Identifies records with high relevance scores from Stage 1
2. Queues them for detailed scraping with crawl4ai
3. Extracts comprehensive funding opportunity details
4. Updates records with enhanced information

The pipeline uses relevance scores to prioritize which records need detailed scraping:
- relevance_score >= 0.7: High priority scraping
- relevance_score >= 0.5: Medium priority scraping  
- relevance_score < 0.5: Low priority or skip
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

# Import crawl4ai directly
try:
    import httpx
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMExtractionStrategy, LLMConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logging.warning("crawl4ai not available, will use basic scraping")

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
    HIGH = "high"           # relevance_score >= 0.7
    MEDIUM = "medium"       # relevance_score >= 0.5
    LOW = "low"            # relevance_score >= 0.3
    SKIP = "skip"          # relevance_score < 0.3


@dataclass
class ScrapingCandidate:
    """Represents a record candidate for detailed scraping"""
    id: int
    title: str
    source_url: str
    application_url: Optional[str]
    relevance_score: float
    priority: ScrapingPriority
    last_scraped: Optional[datetime] = None
    scraping_attempts: int = 0


class SimplifiedScrapingQueue:
    """Manages the intelligent scraping queue based on relevance scores"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
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
        
        # Initialize crawler if available
        self.crawler = None
        if CRAWL4AI_AVAILABLE:
            self.crawler = AsyncWebCrawler(verbose=True)
    
    async def identify_scraping_candidates(self, limit: int = 50) -> List[ScrapingCandidate]:
        """
        Identify records that need detailed scraping based on relevance scores
        """
        logger.info(f"🔍 Identifying scraping candidates with relevance >= {self.min_relevance_threshold}")
        
        # Query for candidates - check if relevance_score field exists
        try:
            # First try with relevance_score field
            query = self.supabase.table('africa_intelligence_feed').select(
                'id, title, source_url, application_url, relevance_score'
            ).gte(
                'relevance_score', self.min_relevance_threshold
            ).not_.is_(
                'source_url', 'null'
            ).neq(
                'source_url', ''
            ).limit(limit)
            
            response = query.execute()
            
        except Exception as e:
            logger.info("relevance_score field not found, using default scoring...")
            # Fallback: get all records with source URLs and assign default scores
            query = self.supabase.table('africa_intelligence_feed').select(
                'id, title, source_url, application_url'
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
            # Get relevance score or assign default based on content
            relevance = record.get('relevance_score', self._calculate_default_relevance(record))
            
            # Determine priority based on relevance score
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
                relevance_score=relevance,
                priority=priority
            )
            
            candidates.append(candidate)
        
        self.stats['candidates_identified'] = len(candidates)
        logger.info(f"✅ Identified {len(candidates)} scraping candidates")
        
        return candidates
    
    def _calculate_default_relevance(self, record: Dict[str, Any]) -> float:
        """Calculate a default relevance score based on title content"""
        title = record.get('title', '').lower()
        
        # AI-related keywords
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural']
        # Funding-related keywords  
        funding_keywords = ['funding', 'grant', 'investment', 'fund', 'capital', 'financing', 'money']
        # Africa-related keywords
        africa_keywords = ['africa', 'african', 'kenya', 'nigeria', 'south africa', 'ghana', 'rwanda']
        
        score = 0.0
        
        # Check for AI relevance (40% weight)
        ai_matches = sum(1 for keyword in ai_keywords if keyword in title)
        if ai_matches > 0:
            score += 0.4 * min(ai_matches / len(ai_keywords), 1.0)
        
        # Check for funding relevance (40% weight)
        funding_matches = sum(1 for keyword in funding_keywords if keyword in title)
        if funding_matches > 0:
            score += 0.4 * min(funding_matches / len(funding_keywords), 1.0)
        
        # Check for Africa relevance (20% weight)
        africa_matches = sum(1 for keyword in africa_keywords if keyword in title)
        if africa_matches > 0:
            score += 0.2 * min(africa_matches / len(africa_keywords), 1.0)
        
        return min(score, 1.0)  # Cap at 1.0
    
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
        self.high_priority_queue.sort(key=lambda x: x.relevance_score, reverse=True)
        self.medium_priority_queue.sort(key=lambda x: x.relevance_score, reverse=True)
        self.low_priority_queue.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"📋 Queued candidates - High: {len(self.high_priority_queue)}, "
                   f"Medium: {len(self.medium_priority_queue)}, Low: {len(self.low_priority_queue)}")
    
    async def process_scraping_queue(self, max_items_per_priority: Dict[str, int] = None):
        """Process the scraping queues starting with highest priority"""
        
        if max_items_per_priority is None:
            max_items_per_priority = {
                'high': 5,     # Process up to 5 high priority items (conservative)
                'medium': 3,   # Process up to 3 medium priority items  
                'low': 2       # Process up to 2 low priority items
            }
        
        logger.info("🚀 Starting intelligent scraping queue processing")
        
        if not CRAWL4AI_AVAILABLE:
            logger.warning("⚠️ crawl4ai not available, simulating scraping process")
        
        # Initialize crawler
        if self.crawler:
            await self.crawler.start()
        
        try:
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
            
        finally:
            # Cleanup crawler
            if self.crawler:
                await self.crawler.close()
        
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
                candidate.scraping_attempts += 1
                self.stats['scraping_errors'] += 1
                
                # Remove from queue if max attempts reached
                if candidate.scraping_attempts >= self.max_scraping_attempts:
                    queue.remove(candidate)
                    logger.warning(f"🚫 Removing candidate {candidate.id} after {self.max_scraping_attempts} failed attempts")
    
    async def _scrape_candidate(self, candidate: ScrapingCandidate):
        """Scrape a single candidate using crawl4ai or simulate"""
        
        logger.info(f"🕷️ Scraping candidate {candidate.id}: {candidate.title[:50]}...")
        
        if not CRAWL4AI_AVAILABLE or not self.crawler:
            # Simulate scraping
            logger.info(f"🎭 Simulating scrape for {candidate.id}")
            await asyncio.sleep(1)  # Simulate processing time
            
            # Update with simulated enhanced data
            await self._update_record_with_scraped_data(candidate, {
                'simulated': True,
                'enhanced_description': f"Enhanced description for {candidate.title}",
                'scraped_at': datetime.utcnow().isoformat()
            })
            
            self.stats['successfully_scraped'] += 1
            return
        
        # Real crawl4ai scraping
        try:
            # Create LLM extraction strategy with new LLMConfig format
            llm_config = LLMConfig(
                provider="openai/gpt-4o-mini",
                api_token=os.getenv("OPENAI_API_KEY")
            )
            
            extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                schema={
                    "type": "object",
                    "properties": {
                        "enhanced_description": {"type": "string"},
                        "funding_amount": {"type": "string"},
                        "deadline": {"type": "string"},
                        "eligibility_criteria": {"type": "string"},
                        "contact_information": {"type": "string"}
                    }
                },
                instruction="Extract detailed funding opportunity information from this webpage."
            )
            
            # Configure crawler
            config = CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                cache_mode=CacheMode.BYPASS,
                page_timeout=30000,
                delay_before_return_html=2.0
            )
            
            # Crawl the page
            result = await self.crawler.arun(
                url=candidate.source_url,
                config=config
            )
            
            if result.success and result.extracted_content:
                # Parse extracted content
                try:
                    extracted_data = json.loads(result.extracted_content)
                    await self._update_record_with_scraped_data(candidate, extracted_data)
                    self.stats['successfully_scraped'] += 1
                    logger.info(f"✅ Successfully scraped and updated record {candidate.id}")
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Could not parse extracted content for {candidate.id}")
                    raise Exception("Failed to parse extracted content")
            else:
                raise Exception(f"Crawling failed: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
                
        except Exception as e:
            logger.error(f"❌ Crawl4AI error for {candidate.id}: {e}")
            raise
    
    async def _update_record_with_scraped_data(self, candidate: ScrapingCandidate, scraped_data: Dict[str, Any]):
        """Update database record with enhanced scraped information"""
        
        # Extract enhanced data from scraped result
        enhanced_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'ai_extracted': True,
        }
        
        # Add scraped content if available
        if scraped_data.get('description'):
            enhanced_data['description'] = scraped_data['description']
        
        if scraped_data.get('funding_amount'):
            enhanced_data['funding_amount'] = scraped_data['funding_amount']
        
        if scraped_data.get('deadline'):
            enhanced_data['application_deadline'] = scraped_data['deadline']
        
        if scraped_data.get('eligibility'):
            enhanced_data['eligibility_criteria'] = json.dumps({'criteria': scraped_data['eligibility']})
        
        if scraped_data.get('contact_info'):
            enhanced_data['contact_information'] = scraped_data['contact_info']
        
        if scraped_data.get('application_process'):
            enhanced_data['application_process'] = scraped_data['application_process']
        
        # Add processing metadata
        if scraped_data.get('simulated'):
            enhanced_data['additional_notes'] = 'Enhanced via simulated scraping process'
        else:
            enhanced_data['additional_notes'] = 'Enhanced via crawl4ai extraction'
        
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
                'scraping_cooldown_hours': self.scraping_cooldown_hours,
                'crawl4ai_available': CRAWL4AI_AVAILABLE
            }
        }


async def run_stage2_pipeline():
    """Main function to run Stage 2 intelligent scraping pipeline"""
    
    logger.info("🚀 Starting Stage 2: Simplified Intelligent Scraping Pipeline")
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_PROJECT_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Initialize intelligent scraping queue
    scraping_queue = SimplifiedScrapingQueue(supabase)
    
    try:
        # Step 1: Identify scraping candidates based on relevance scores
        candidates = await scraping_queue.identify_scraping_candidates(limit=20)
        
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
        logger.info(f"   🤖 Crawl4AI available: {status['configuration']['crawl4ai_available']}")
        
        logger.info("🎉 Stage 2: Simplified Intelligent Scraping Pipeline completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Stage 2 pipeline failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(run_stage2_pipeline())
