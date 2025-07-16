"""
Unified Scraper Module for TAIFA - Handles all three data importation methods:
1. User submissions from Next.js frontend
2. Admin-initiated scraping from Streamlit portal  
3. Automated discovery from Serper searches

This module provides a single entry point for all data processing while maintaining
method-specific handling for different input sources.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import sys
import os
from pathlib import Path

# Add data collectors to path
data_collectors_path = Path(__file__).parent.parent.parent.parent / "data_collectors"
sys.path.append(str(data_collectors_path))

from crawl4ai import AsyncWebCrawler, LLMExtractionStrategy
from serper_search.collector import SerperSearchCollector
from database.connector import DatabaseConnector
from app.core.config import settings

logger = logging.getLogger(__name__)

class InputSource(Enum):
    """Enumeration of input sources for the unified scraper"""
    USER_SUBMISSION = "user_submission"
    ADMIN_PORTAL = "admin_portal"
    AUTOMATED_DISCOVERY = "automated_discovery"
    SCHEDULED_SCRAPING = "scheduled_scraping"

class ProcessingPriority(Enum):
    """Processing priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class UnifiedScraperModule:
    """
    Unified scraper that handles all three data importation methods:
    - Method 1: User submissions (validation + processing)
    - Method 2: Admin portal URL scraping (Crawl4AI + validation)
    - Method 3: Automated discovery (Serper + processing)
    """
    
    def __init__(self):
        self.crawl4ai_client = None
        self.serper_client = None
        self.db_connector = None
        self.validation_service = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize all scraping and processing components"""
        if self.is_initialized:
            return
            
        logger.info("🚀 Initializing Unified Scraper Module...")
        
        try:
            # Initialize Crawl4AI client for admin portal scraping
            self.crawl4ai_client = AsyncWebCrawler(
                headless=True,
                browser_type="chromium",
                verbose=False
            )
            await self.crawl4ai_client.start()
            logger.info("✅ Crawl4AI client initialized")
            
            # Initialize Serper client for automated discovery
            if settings.SERPER_DEV_API_KEY:
                self.serper_client = SerperSearchCollector(settings.SERPER_DEV_API_KEY)
                logger.info("✅ Serper client initialized")
            else:
                logger.warning("⚠️  SERPER_DEV_API_KEY not found - automated discovery disabled")
            
            # Initialize database connector
            self.db_connector = DatabaseConnector()
            await self.db_connector.initialize()
            logger.info("✅ Database connector initialized")
            
            # Initialize validation service
            from app.services.simple_validation import validation_service
            self.validation_service = validation_service
            logger.info("✅ Validation service initialized")
            
            self.is_initialized = True
            logger.info("🎉 Unified Scraper Module fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Unified Scraper Module: {e}")
            raise
    
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Universal input processor for all three methods
        
        Args:
            input_data: Dictionary containing:
                - source: InputSource enum value
                - data: Source-specific data
                - priority: ProcessingPriority (optional)
                - validation_required: bool (optional)
        
        Returns:
            Processing result with opportunity ID and status
        """
        if not self.is_initialized:
            await self.initialize()
        
        source = InputSource(input_data["source"])
        priority = ProcessingPriority(input_data.get("priority", "medium"))
        
        logger.info(f"🔄 Processing {source.value} input with {priority.value} priority")
        
        try:
            if source == InputSource.USER_SUBMISSION:
                return await self._handle_user_submission(input_data)
            elif source == InputSource.ADMIN_PORTAL:
                return await self._handle_admin_portal_input(input_data)
            elif source == InputSource.AUTOMATED_DISCOVERY:
                return await self._handle_automated_discovery(input_data)
            elif source == InputSource.SCHEDULED_SCRAPING:
                return await self._handle_scheduled_scraping(input_data)
            else:
                raise ValueError(f"Unsupported input source: {source}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {source.value} input: {e}")
            return {
                "status": "error",
                "error": str(e),
                "source": source.value
            }
    
    async def _handle_user_submission(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Method 1: User submissions from Next.js frontend
        
        Process user-submitted funding opportunities with validation
        """
        logger.info("👤 Processing user submission...")
        
        submission_data = input_data["data"]
        
        # Validate required fields
        required_fields = ["title", "organization", "description", "url"]
        missing_fields = [field for field in required_fields if not submission_data.get(field)]
        
        if missing_fields:
            return {
                "status": "validation_error",
                "error": f"Missing required fields: {missing_fields}",
                "source": "user_submission"
            }
        
        # Create standardized opportunity object
        opportunity = {
            "title": submission_data["title"],
            "organization_name": submission_data["organization"],
            "description": submission_data["description"],
            "amount": submission_data.get("amount"),
            "currency": submission_data.get("currency", "USD"),
            "deadline": submission_data.get("deadline"),
            "source_url": submission_data["url"],
            "contact_email": submission_data.get("contact_email"),
            "source_name": "User Submission",
            "source_type": "manual",
            "processing_metadata": {
                "input_source": "user_submission",
                "submitted_at": datetime.utcnow().isoformat(),
                "requires_validation": True
            }
        }
        
        # Run validation
        validation_result = await self.validation_service.validate_opportunity(opportunity)
        opportunity["validation_score"] = validation_result["score"]
        opportunity["validation_flags"] = validation_result["flags"]
        
        # Store in database
        try:
            result = await self.db_connector.save_opportunities([opportunity], "user_submission")
            
            return {
                "status": "success",
                "opportunity_id": result.get("opportunity_ids", [None])[0],
                "validation_score": validation_result["score"],
                "requires_review": validation_result["score"] < 0.8,
                "source": "user_submission"
            }
            
        except Exception as e:
            logger.error(f"Error saving user submission: {e}")
            return {
                "status": "database_error", 
                "error": str(e),
                "source": "user_submission"
            }
    
    async def _handle_admin_portal_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Method 2: Admin portal URL scraping with Crawl4AI
        
        Process URLs submitted through Streamlit admin portal
        """
        logger.info("🛠️ Processing admin portal URL...")
        
        url = input_data["data"]["url"]
        source_type = input_data["data"].get("source_type", "unknown")
        
        try:
            # Use Crawl4AI to extract content from URL
            result = await self.crawl4ai_client.arun(
                url=url,
                word_count_threshold=10,
                extraction_strategy=LLMExtractionStrategy(
                    provider="openai/gpt-4o-mini",
                    api_token=os.getenv("OPENAI_API_KEY"),
                    instruction="""
                    Extract funding opportunity information from this webpage.
                    Look for:
                    - Funding program titles and names
                    - Organization offering the funding (name and website URL)
                    - Grant amounts and currencies
                    - Application deadlines
                    - Eligibility criteria
                    - Contact information
                    - Application processes
                    - Organization website/homepage URL (different from the current page)
                    
                    Return structured data as JSON with fields:
                    title, organization_name, organization_website, description, amount, currency, deadline, 
                    eligibility_criteria, contact_info, application_process, application_url
                    
                    IMPORTANT: 
                    - organization_website should be the main organization website (e.g., https://gatesfoundation.org)
                    - application_url should be the direct link to apply (if different from current page)
                    - If organization website is not found, set it to null
                    """
                )
            )
            
            if not result.extracted_content:
                return {
                    "status": "extraction_failed",
                    "error": "No content could be extracted from URL",
                    "source": "admin_portal"
                }
            
            # Parse extracted content into opportunities
            opportunities = self._parse_extracted_content(result.extracted_content, url, source_type)
            
            if not opportunities:
                return {
                    "status": "no_opportunities_found",
                    "error": "No funding opportunities detected in content",
                    "source": "admin_portal"
                }
            
            # Validate and store opportunities
            validated_opportunities = []
            for opp in opportunities:
                validation_result = await self.validation_service.validate_opportunity(opp)
                opp["validation_score"] = validation_result["score"]
                opp["validation_flags"] = validation_result["flags"]
                validated_opportunities.append(opp)
            
            # Save to database
            result = await self.db_connector.save_opportunities(validated_opportunities, "admin_portal")
            
            return {
                "status": "success",
                "opportunities_found": len(opportunities),
                "opportunities_saved": result.get("saved", 0),
                "duplicates": result.get("duplicates", 0),
                "opportunity_ids": result.get("opportunity_ids", []),
                "source": "admin_portal"
            }
            
        except Exception as e:
            logger.error(f"Error processing admin portal URL {url}: {e}")
            return {
                "status": "processing_error",
                "error": str(e),
                "source": "admin_portal"
            }
    
    async def _handle_automated_discovery(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Method 3: Automated discovery via Serper searches
        
        Process search terms and discover new funding opportunities
        """
        logger.info("🤖 Processing automated discovery...")
        
        if not self.serper_client:
            return {
                "status": "service_unavailable",
                "error": "Serper client not available",
                "source": "automated_discovery"
            }
        
        search_terms = input_data["data"].get("search_terms")
        
        try:
            # Run Serper search
            if search_terms:
                opportunities = await self.serper_client.search_specific_terms(search_terms)
            else:
                opportunities = await self.serper_client.start_collection()
            
            if not opportunities:
                return {
                    "status": "no_results",
                    "message": "No opportunities found in search",
                    "source": "automated_discovery"
                }
            
            # Filter and validate opportunities
            validated_opportunities = []
            for opp in opportunities:
                # Add automated discovery metadata
                opp["processing_metadata"] = {
                    "input_source": "automated_discovery",
                    "processed_at": datetime.utcnow().isoformat(),
                    "search_terms": search_terms
                }
                
                validation_result = await self.validation_service.validate_opportunity(opp)
                opp["validation_score"] = validation_result["score"]
                opp["validation_flags"] = validation_result["flags"]
                
                # Only keep high-quality opportunities for automated discovery
                if validation_result["score"] >= 0.7:
                    validated_opportunities.append(opp)
            
            if not validated_opportunities:
                return {
                    "status": "low_quality_results",
                    "message": "No high-quality opportunities found",
                    "total_found": len(opportunities),
                    "source": "automated_discovery"
                }
            
            # Save to database
            result = await self.db_connector.save_opportunities(validated_opportunities, "automated_discovery")
            
            return {
                "status": "success",
                "opportunities_found": len(opportunities),
                "opportunities_saved": result.get("saved", 0),
                "duplicates": result.get("duplicates", 0),
                "source": "automated_discovery"
            }
            
        except Exception as e:
            logger.error(f"Error in automated discovery: {e}")
            return {
                "status": "processing_error",
                "error": str(e),
                "source": "automated_discovery"
            }
    
    async def _handle_scheduled_scraping(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle scheduled scraping of known sources
        
        For future implementation of regular monitoring
        """
        logger.info("⏰ Processing scheduled scraping...")
        
        # This will integrate with the existing RSS monitoring and web scraping
        # For now, return a placeholder
        return {
            "status": "not_implemented",
            "message": "Scheduled scraping will be implemented in Phase 2",
            "source": "scheduled_scraping"
        }
    
    def _parse_extracted_content(self, content: str, source_url: str, source_type: str) -> List[Dict[str, Any]]:
        """
        Parse extracted content from Crawl4AI into structured opportunities
        
        This is a simplified parser - can be enhanced with more sophisticated parsing
        """
        import json
        
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{') or content.strip().startswith('['):
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    opportunities = parsed
                else:
                    opportunities = [parsed]
            else:
                # For non-JSON content, create a single opportunity
                opportunities = [{
                    "title": "Extracted Funding Opportunity",
                    "description": content[:1000],  # Truncate long content
                    "source_url": source_url,
                    "source_type": source_type
                }]
            
            # Standardize and enrich opportunities
            standardized_opportunities = []
            for opp in opportunities:
                standardized_opp = {
                    "title": opp.get("title", "Unknown Funding Opportunity"),
                    "organization_name": opp.get("organization_name", "Unknown Organization"),
                    "description": opp.get("description", ""),
                    "amount": opp.get("amount"),
                    "currency": opp.get("currency", "USD"),
                    "deadline": opp.get("deadline"),
                    "source_url": source_url,  # URL where we found this info
                    "application_url": opp.get("application_url") or opp.get("organization_website") or source_url,  # URL to apply or org website
                    "source_name": f"Admin Portal - {source_type}",
                    "source_type": "admin_scraping",
                    "status": "under_review",  # Set new opportunities for review
                    "processing_metadata": {
                        "input_source": "admin_portal",
                        "extracted_at": datetime.utcnow().isoformat(),
                        "extraction_method": "crawl4ai",
                        "organization_website": opp.get("organization_website"),
                        "scraped_from_url": source_url
                    }
                }
                standardized_opportunities.append(standardized_opp)
            
            return standardized_opportunities
            
        except Exception as e:
            logger.error(f"Error parsing extracted content: {e}")
            return []
    
    async def close(self):
        """Clean up resources"""
        if self.crawl4ai_client:
            await self.crawl4ai_client.close()
        if self.db_connector:
            await self.db_connector.close()
        
        logger.info("🔧 Unified Scraper Module closed")

# Export the main class
__all__ = ["UnifiedScraperModule", "InputSource", "ProcessingPriority"]
