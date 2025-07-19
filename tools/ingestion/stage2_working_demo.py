#!/usr/bin/env python3
"""
Stage 2: Working Intelligent Scraping Demo
==========================================

This module demonstrates Stage 2 of the data ingestion pipeline:
1. Identifies records with high relevance scores from Stage 1
2. Queues them for detailed scraping (simulated for now)
3. Updates records with enhanced information

This version focuses on the intelligent queuing logic and demonstrates
how the system would prioritize records based on relevance scores.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
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


class IntelligentScrapingDemo:
    """Demonstrates the intelligent scraping queue based on relevance scores"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.high_priority_queue: List[ScrapingCandidate] = []
        self.medium_priority_queue: List[ScrapingCandidate] = []
        self.low_priority_queue: List[ScrapingCandidate] = []
        
        # Configuration
        self.min_relevance_threshold = 0.3
        self.high_priority_threshold = 0.7
        self.medium_priority_threshold = 0.5
        
        # Statistics
        self.stats = {
            'candidates_identified': 0,
            'high_priority_queued': 0,
            'medium_priority_queued': 0,
            'low_priority_queued': 0,
            'successfully_processed': 0,
            'records_updated': 0
        }
    
    async def identify_scraping_candidates(self, limit: int = 50) -> List[ScrapingCandidate]:
        """
        Identify records that need detailed scraping based on relevance scores
        """
        logger.info(f"🔍 Identifying scraping candidates with relevance >= {self.min_relevance_threshold}")
        
        # Query for candidates - use default relevance scoring if field doesn't exist
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
            # Get relevance score or calculate default
            relevance = record.get('relevance_score', self._calculate_default_relevance(record))
            
            # Skip if below threshold
            if relevance < self.min_relevance_threshold:
                continue
            
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
    
    async def demonstrate_intelligent_processing(self, max_items_per_priority: Dict[str, int] = None):
        """Demonstrate the intelligent processing of queues"""
        
        if max_items_per_priority is None:
            max_items_per_priority = {
                'high': 5,     # Process up to 5 high priority items
                'medium': 3,   # Process up to 3 medium priority items  
                'low': 2       # Process up to 2 low priority items
            }
        
        logger.info("🚀 Starting intelligent processing demonstration")
        
        # Process high priority queue first
        await self._demonstrate_priority_queue(
            self.high_priority_queue, 
            "HIGH", 
            max_items_per_priority['high']
        )
        
        # Process medium priority queue
        await self._demonstrate_priority_queue(
            self.medium_priority_queue, 
            "MEDIUM", 
            max_items_per_priority['medium']
        )
        
        # Process low priority queue
        await self._demonstrate_priority_queue(
            self.low_priority_queue, 
            "LOW", 
            max_items_per_priority['low']
        )
        
        logger.info("✅ Completed intelligent processing demonstration")
    
    async def _demonstrate_priority_queue(self, queue: List[ScrapingCandidate], 
                                        priority_name: str, max_items: int):
        """Demonstrate processing of a specific priority queue"""
        
        if not queue:
            logger.info(f"📭 No items in {priority_name} priority queue")
            return
        
        items_to_process = queue[:max_items]
        logger.info(f"🔄 Demonstrating processing of {len(items_to_process)} {priority_name} priority items")
        
        for i, candidate in enumerate(items_to_process, 1):
            logger.info(f"   {i}. Processing: {candidate.title[:60]}...")
            logger.info(f"      📊 Relevance Score: {candidate.relevance_score:.3f}")
            logger.info(f"      🔗 Source URL: {candidate.source_url[:80]}...")
            
            # Simulate processing time based on priority
            if candidate.priority == ScrapingPriority.HIGH:
                await asyncio.sleep(0.5)  # High priority gets more processing time
            elif candidate.priority == ScrapingPriority.MEDIUM:
                await asyncio.sleep(0.3)
            else:
                await asyncio.sleep(0.1)
            
            # Simulate updating the record with enhanced data
            await self._simulate_record_update(candidate)
            
            self.stats['successfully_processed'] += 1
            logger.info(f"      ✅ Simulated enhancement complete")
    
    async def _simulate_record_update(self, candidate: ScrapingCandidate):
        """Simulate updating a record with enhanced data"""
        
        # Create simulated enhanced data
        enhanced_data = {
            'updated_at': datetime.utcnow().isoformat(),
            'ai_extracted': True,
            'additional_notes': f'Enhanced via Stage 2 intelligent scraping (Priority: {candidate.priority.value}, Score: {candidate.relevance_score:.3f})'
        }
        
        # Update the record
        response = self.supabase.table('africa_intelligence_feed').update(
            enhanced_data
        ).eq('id', candidate.id).execute()
        
        if response.data:
            self.stats['records_updated'] += 1
        else:
            logger.warning(f"⚠️ Failed to update record {candidate.id}")
    
    def print_detailed_analysis(self):
        """Print detailed analysis of the candidates and queues"""
        
        logger.info("📊 DETAILED STAGE 2 ANALYSIS")
        logger.info("=" * 50)
        
        # High Priority Analysis
        if self.high_priority_queue:
            logger.info(f"🔥 HIGH PRIORITY QUEUE ({len(self.high_priority_queue)} items):")
            for i, candidate in enumerate(self.high_priority_queue[:5], 1):
                logger.info(f"   {i}. Score: {candidate.relevance_score:.3f} | {candidate.title[:50]}...")
        
        # Medium Priority Analysis
        if self.medium_priority_queue:
            logger.info(f"🔶 MEDIUM PRIORITY QUEUE ({len(self.medium_priority_queue)} items):")
            for i, candidate in enumerate(self.medium_priority_queue[:5], 1):
                logger.info(f"   {i}. Score: {candidate.relevance_score:.3f} | {candidate.title[:50]}...")
        
        # Low Priority Analysis
        if self.low_priority_queue:
            logger.info(f"🔸 LOW PRIORITY QUEUE ({len(self.low_priority_queue)} items):")
            for i, candidate in enumerate(self.low_priority_queue[:5], 1):
                logger.info(f"   {i}. Score: {candidate.relevance_score:.3f} | {candidate.title[:50]}...")
        
        logger.info("=" * 50)
    
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
                'medium_priority_threshold': self.medium_priority_threshold
            }
        }


async def run_stage2_demo():
    """Main function to run Stage 2 intelligent scraping demonstration"""
    
    logger.info("🚀 Starting Stage 2: Intelligent Scraping Demonstration")
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_PROJECT_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Initialize intelligent scraping demo
    scraping_demo = IntelligentScrapingDemo(supabase)
    
    try:
        # Step 1: Identify scraping candidates based on relevance scores
        candidates = await scraping_demo.identify_scraping_candidates(limit=20)
        
        if not candidates:
            logger.info("📭 No scraping candidates found. Stage 2 demo complete.")
            return True
        
        # Step 2: Queue candidates by priority
        scraping_demo.queue_candidates_by_priority(candidates)
        
        # Step 3: Print detailed analysis
        scraping_demo.print_detailed_analysis()
        
        # Step 4: Demonstrate intelligent processing
        await scraping_demo.demonstrate_intelligent_processing()
        
        # Step 5: Report results
        status = scraping_demo.get_queue_status()
        logger.info("📊 Stage 2 Demo Results:")
        logger.info(f"   🎯 Candidates identified: {status['statistics']['candidates_identified']}")
        logger.info(f"   🔥 High priority queued: {status['statistics']['high_priority_queued']}")
        logger.info(f"   🔶 Medium priority queued: {status['statistics']['medium_priority_queued']}")
        logger.info(f"   🔸 Low priority queued: {status['statistics']['low_priority_queued']}")
        logger.info(f"   ✅ Successfully processed: {status['statistics']['successfully_processed']}")
        logger.info(f"   📝 Records updated: {status['statistics']['records_updated']}")
        
        logger.info("🎉 Stage 2: Intelligent Scraping Demo completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Stage 2 demo failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(run_stage2_demo())
