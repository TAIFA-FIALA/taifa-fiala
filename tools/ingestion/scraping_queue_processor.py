#!/usr/bin/env python3
"""
Queue-Based Web Scraping System
===============================

This system processes scraping requests from a queue, using crawl4ai for 
intelligent content extraction when the main engine needs more detailed information.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Import crawl4ai for intelligent scraping
try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("⚠️  crawl4ai not available. Install with: pip install crawl4ai")

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapeRequest:
    """Represents a scraping request from the queue"""
    id: int
    url: str
    priority: str
    scraping_instructions: Dict[str, Any]
    requested_fields: List[str]
    source_opportunity_id: Optional[int]
    source_context: Optional[str]
    attempts: int
    max_attempts: int

class ScrapingQueueProcessor:
    """Queue-based web scraping processor using crawl4ai"""
    
    def __init__(self):
        self.processor_id = str(uuid.uuid4())
        self.supabase: Client = None
        self.is_running = False
        self.processed_count = 0
        self.succeeded_count = 0
        self.failed_count = 0
        
    async def initialize(self):
        """Initialize the processor"""
        logger.info(f"🚀 Initializing scraping queue processor {self.processor_id}")
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Check crawl4ai availability
        if not CRAWL4AI_AVAILABLE:
            logger.error("❌ crawl4ai not available. Install with: pip install crawl4ai")
            raise ImportError("crawl4ai required for queue processor")
        
        # Register processor in database
        await self._register_processor()
        
        logger.info("✅ Scraping queue processor initialized")
    
    async def _register_processor(self):
        """Register this processor instance in the database"""
        try:
            # Note: This would need the scraping_queue_status table to exist
            # For now, just log the registration
            logger.info(f"📝 Registered processor {self.processor_id}")
        except Exception as e:
            logger.warning(f"⚠️  Could not register processor: {e}")
    
    async def start_processing(self, batch_size: int = 5):
        """Start processing the scraping queue"""
        logger.info(f"🔄 Starting queue processing (batch size: {batch_size})")
        self.is_running = True
        
        while self.is_running:
            try:
                # Get pending items from queue
                pending_items = await self._get_pending_items(batch_size)
                
                if not pending_items:
                    logger.info("💤 No pending items, sleeping...")
                    await asyncio.sleep(30)  # Wait 30 seconds
                    continue
                
                logger.info(f"📋 Processing {len(pending_items)} items from queue")
                
                # Process items in parallel
                tasks = []
                for item in pending_items:
                    task = asyncio.create_task(self._process_item(item))
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Short pause between batches
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Error in processing loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _get_pending_items(self, limit: int) -> List[ScrapeRequest]:
        """Get pending items from the scraping queue"""
        try:
            # This would query the scraping_queue table
            # For now, return empty list since table doesn't exist yet
            logger.debug("🔍 Checking for pending scraping requests...")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting pending items: {e}")
            return []
    
    async def _process_item(self, item: ScrapeRequest):
        """Process a single scraping request"""
        logger.info(f"🕷️  Processing scrape request: {item.url}")
        
        # Mark as processing
        await self._update_item_status(item.id, 'processing')
        
        try:
            # Perform the scraping
            result = await self._scrape_url(item)
            
            if result:
                # Save successful result
                await self._save_scraping_result(item, result)
                await self._update_item_status(item.id, 'completed')
                
                # Update opportunity if linked
                if item.source_opportunity_id:
                    await self._update_opportunity_with_scraped_data(item.source_opportunity_id, result)
                
                self.succeeded_count += 1
                logger.info(f"✅ Successfully scraped: {item.url}")
                
            else:
                # Handle failure
                await self._handle_failed_scrape(item, "No data extracted")
                
        except Exception as e:
            logger.error(f"❌ Error processing {item.url}: {e}")
            await self._handle_failed_scrape(item, str(e))
        
        finally:
            self.processed_count += 1
    
    async def _scrape_url(self, item: ScrapeRequest) -> Optional[Dict[str, Any]]:
        """Scrape a URL using crawl4ai"""
        try:
            # Create extraction strategy based on requested fields
            extraction_strategy = self._create_extraction_strategy(item)
            
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Crawl the URL
                result = await crawler.arun(
                    url=item.url,
                    extraction_strategy=extraction_strategy,
                    word_count_threshold=10,
                    bypass_cache=True,
                    timeout=30
                )
                
                if result.success:
                    # Parse the extracted content
                    extracted_data = self._parse_extraction_result(result, item)
                    
                    return {
                        'title': extracted_data.get('title', ''),
                        'description': extracted_data.get('description', ''),
                        'content': result.cleaned_html[:5000],  # Limit content size
                        'amount': extracted_data.get('amount', ''),
                        'deadline': extracted_data.get('deadline', ''),
                        'eligibility_criteria': extracted_data.get('eligibility_criteria', ''),
                        'application_process': extracted_data.get('application_process', ''),
                        'contact_information': extracted_data.get('contact_information', ''),
                        'extracted_fields': extracted_data,
                        'extraction_confidence': self._calculate_confidence(extracted_data, item.requested_fields),
                        'data_completeness': self._calculate_completeness(extracted_data, item.requested_fields)
                    }
                else:
                    logger.error(f"❌ Crawl failed for {item.url}: {result.error_message}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Scraping error for {item.url}: {e}")
            return None
    
    def _create_extraction_strategy(self, item: ScrapeRequest) -> LLMExtractionStrategy:
        """Create an extraction strategy based on the scraping request"""
        
        # Build extraction prompt based on requested fields
        fields_text = ", ".join(item.requested_fields)
        
        extraction_prompt = f"""
        Extract the following information from this intelligence item webpage:
        
        Required fields: {fields_text}
        
        Please extract:
        - Title: The main title of the intelligence item
        - Description: A comprehensive description of the opportunity
        - Amount: Any funding amounts mentioned
        - Deadline: Application deadline or closing date
        - Eligibility: Who can apply or eligibility criteria
        - Application Process: How to apply
        - Contact Information: Contact details for inquiries
        
        Context: {item.source_context or 'General intelligence item'}
        
        Return the information in JSON format with clear field names.
        """
        
        return LLMExtractionStrategy(
            provider="ollama/llama3.2:3b",  # Use local model
            api_token=None,
            instruction=extraction_prompt,
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "amount": {"type": "string"},
                    "deadline": {"type": "string"},
                    "eligibility_criteria": {"type": "string"},
                    "application_process": {"type": "string"},
                    "contact_information": {"type": "string"}
                }
            }
        )
    
    def _parse_extraction_result(self, result, item: ScrapeRequest) -> Dict[str, Any]:
        """Parse the extraction result from crawl4ai"""
        try:
            if result.extracted_content:
                # Try to parse JSON response
                extracted_data = json.loads(result.extracted_content)
                return extracted_data
            else:
                # Fallback to basic extraction
                return {
                    'title': result.metadata.get('title', ''),
                    'description': result.cleaned_html[:1000],  # First 1000 chars
                }
        except json.JSONDecodeError:
            logger.warning(f"⚠️  Could not parse extraction result as JSON for {item.url}")
            return {
                'title': result.metadata.get('title', ''),
                'description': result.cleaned_html[:1000],
            }
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], requested_fields: List[str]) -> float:
        """Calculate extraction confidence score"""
        if not requested_fields:
            return 0.5
        
        filled_fields = sum(1 for field in requested_fields if extracted_data.get(field))
        return filled_fields / len(requested_fields)
    
    def _calculate_completeness(self, extracted_data: Dict[str, Any], requested_fields: List[str]) -> float:
        """Calculate data completeness score"""
        if not requested_fields:
            return 0.5
        
        total_chars = sum(len(str(extracted_data.get(field, ''))) for field in requested_fields)
        max_expected_chars = len(requested_fields) * 100  # Assume 100 chars per field
        
        return min(total_chars / max_expected_chars, 1.0)
    
    async def _save_scraping_result(self, item: ScrapeRequest, result: Dict[str, Any]):
        """Save successful scraping result to database"""
        try:
            # This would save to scraping_results table
            logger.info(f"💾 Saving scraping result for {item.url}")
            # For now, just log - would need database table
            
        except Exception as e:
            logger.error(f"❌ Error saving scraping result: {e}")
    
    async def _update_opportunity_with_scraped_data(self, opportunity_id: int, scraped_data: Dict[str, Any]):
        """Update the intelligence item with scraped data"""
        try:
            # Update intelligence_feed table with scraped data
            update_data = {}
            
            # Map scraped fields to opportunity fields
            if scraped_data.get('description') and len(scraped_data['description']) > 100:
                update_data['description'] = scraped_data['description']
            
            if scraped_data.get('amount'):
                update_data['additional_notes'] = f"Funding Amount: {scraped_data['amount']}"
            
            if scraped_data.get('deadline'):
                update_data['application_deadline'] = scraped_data['deadline']
            
            if scraped_data.get('eligibility_criteria'):
                update_data['eligibility_criteria'] = scraped_data['eligibility_criteria']
            
            if scraped_data.get('application_process'):
                update_data['application_process'] = scraped_data['application_process']
            
            if scraped_data.get('contact_information'):
                update_data['contact_information'] = scraped_data['contact_information']
            
            if update_data:
                result = self.supabase.table('africa_intelligence_feed').update(update_data).eq('id', opportunity_id).execute()
                logger.info(f"✅ Updated opportunity {opportunity_id} with scraped data")
                
        except Exception as e:
            logger.error(f"❌ Error updating opportunity {opportunity_id}: {e}")
    
    async def _update_item_status(self, item_id: int, status: str):
        """Update the status of a queue item"""
        try:
            # This would update the scraping_queue table
            logger.debug(f"📝 Updating item {item_id} status to {status}")
            
        except Exception as e:
            logger.error(f"❌ Error updating item status: {e}")
    
    async def _handle_failed_scrape(self, item: ScrapeRequest, error_message: str):
        """Handle failed scraping attempts"""
        try:
            attempts = item.attempts + 1
            
            if attempts >= item.max_attempts:
                # Mark as failed
                await self._update_item_status(item.id, 'failed')
                logger.error(f"❌ Item {item.id} failed after {attempts} attempts: {error_message}")
                self.failed_count += 1
            else:
                # Schedule retry
                await self._update_item_status(item.id, 'retrying')
                logger.warning(f"⚠️  Item {item.id} will be retried (attempt {attempts}/{item.max_attempts})")
                
        except Exception as e:
            logger.error(f"❌ Error handling failed scrape: {e}")
    
    async def stop_processing(self):
        """Stop the queue processor"""
        logger.info("🛑 Stopping scraping queue processor")
        self.is_running = False

# Helper functions for main engine integration
class ScrapeQueueManager:
    """Manager for adding items to the scraping queue"""
    
    def __init__(self):
        self.supabase: Client = None
    
    async def initialize(self):
        """Initialize the queue manager"""
        supabase_url = os.getenv('SUPABASE_PROJECT_URL')
        supabase_key = os.getenv('SUPABASE_API_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(supabase_url, supabase_key)
    
    async def queue_scrape_request(self, 
                                 url: str, 
                                 requested_fields: List[str],
                                 priority: str = 'medium',
                                 source_opportunity_id: Optional[int] = None,
                                 source_context: Optional[str] = None,
                                 scraping_instructions: Optional[Dict[str, Any]] = None) -> bool:
        """Add a scraping request to the queue"""
        try:
            # This would insert into scraping_queue table
            logger.info(f"📋 Queuing scrape request for {url}")
            logger.info(f"   Fields needed: {', '.join(requested_fields)}")
            logger.info(f"   Priority: {priority}")
            
            # For now, just log - would need database table
            return True
            
        except Exception as e:
            logger.error(f"❌ Error queuing scrape request: {e}")
            return False

async def main():
    """Main function for testing the queue processor"""
    logger.info("🧪 Testing Scraping Queue Processor")
    
    processor = ScrapingQueueProcessor()
    await processor.initialize()
    
    # Test queue manager
    queue_manager = ScrapeQueueManager()
    await queue_manager.initialize()
    
    # Add a test request
    await queue_manager.queue_scrape_request(
        url="https://idrc-crdi.ca/en/funding",
        requested_fields=["title", "description", "deadline", "amount"],
        priority="high",
        source_context="Testing queue system for IDRC funding intelligence_items"
    )
    
    logger.info("✅ Queue processor test completed")

if __name__ == "__main__":
    asyncio.run(main())