"""
TAIFA Organization Enrichment Pipeline
Hybrid CrewAI + Deterministic Script + Apify Integration
"""

import json
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import time

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool
from langchain.llms import OpenAI
from apify_client import ApifyClient

# Database imports (adapt to your actual setup)
from app.models.organization import Organization
from app.core.database import get_db

class EnrichmentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"

class DataSource(Enum):
    MANUAL = "manual"
    APIFY = "apify"
    AGENT = "agent"
    DETERMINISTIC = "deterministic"
    HYBRID = "hybrid"

@dataclass
class EnrichmentLock:
    """Track organization enrichment locks to prevent duplicates"""
    organization_name: str
    locked_at: datetime
    locked_by: str
    expires_at: datetime
    
class EnrichmentCache:
    """Simple in-memory cache for organization enrichment locks"""
    
    def __init__(self):
        self.locks: Dict[str, EnrichmentLock] = {}
        self.lock_timeout = timedelta(minutes=30)  # Lock expires after 30 minutes
    
    def is_locked(self, org_name: str) -> bool:
        """Check if organization is currently locked for processing"""
        org_key = self._normalize_org_name(org_name)
        
        if org_key in self.locks:
            lock = self.locks[org_key]
            if datetime.utcnow() < lock.expires_at:
                return True
            else:
                # Lock expired, remove it
                del self.locks[org_key]
        
        return False
    
    def acquire_lock(self, org_name: str, processor_id: str) -> bool:
        """Acquire lock for organization processing"""
        org_key = self._normalize_org_name(org_name)
        
        if self.is_locked(org_name):
            return False
        
        # Acquire lock
        self.locks[org_key] = EnrichmentLock(
            organization_name=org_name,
            locked_at=datetime.utcnow(),
            locked_by=processor_id,
            expires_at=datetime.utcnow() + self.lock_timeout
        )
        
        return True
    
    def release_lock(self, org_name: str, processor_id: str) -> bool:
        """Release lock for organization"""
        org_key = self._normalize_org_name(org_name)
        
        if org_key in self.locks:
            lock = self.locks[org_key]
            if lock.locked_by == processor_id:
                del self.locks[org_key]
                return True
        
        return False
    
    def _normalize_org_name(self, org_name: str) -> str:
        """Normalize organization name for consistent locking"""
        return org_name.lower().strip().replace(" ", "_")

class ApifyOrganizationExtractor:
    """Apify-based structured data extraction"""
    
    def __init__(self, api_token: str):
        self.client = ApifyClient(api_token)
        self.scrapers = {
            "linkedin_company": "apify/linkedin-company-scraper",
            "website_metadata": "apify/website-content-crawler", 
            "social_profiles": "apify/social-media-scraper",
            "company_info": "apify/company-info-scraper"
        }
    
    async def extract_organization_data(self, website_url: str, org_name: str) -> Dict[str, Any]:
        """Extract structured organization data using Apify"""
        
        extraction_results = {
            "website_metadata": {},
            "linkedin_data": {},
            "social_profiles": {},
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "extraction_success": False
        }
        
        try:
            # 1. Extract website metadata
            website_data = await self._extract_website_metadata(website_url)
            extraction_results["website_metadata"] = website_data
            
            # 2. Try to find and extract LinkedIn profile
            linkedin_url = await self._find_linkedin_profile(website_url, org_name)
            if linkedin_url:
                linkedin_data = await self._extract_linkedin_data(linkedin_url)
                extraction_results["linkedin_data"] = linkedin_data
            
            # 3. Extract social media profiles
            social_data = await self._extract_social_profiles(website_url, org_name)
            extraction_results["social_profiles"] = social_data
            
            extraction_results["extraction_success"] = True
            
        except Exception as e:
            extraction_results["extraction_error"] = str(e)
            logging.error(f"Apify extraction failed for {org_name}: {e}")
        
        return extraction_results
    
    async def _extract_website_metadata(self, website_url: str) -> Dict[str, Any]:
        """Extract website metadata using Apify"""
        try:
            run_input = {
                "startUrls": [website_url],
                "maxPages": 5,
                "extractContacts": True,
                "extractSocialLinks": True
            }
            
            run = self.client.actor(self.scrapers["website_metadata"]).call(run_input=run_input)
            
            # Get results
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return {
                "pages_scraped": len(items),
                "main_content": items[0] if items else {},
                "all_pages": items,
                "contact_info": self._extract_contact_info(items),
                "social_links": self._extract_social_links(items)
            }
            
        except Exception as e:
            logging.error(f"Website metadata extraction failed: {e}")
            return {"error": str(e)}
    
    async def _find_linkedin_profile(self, website_url: str, org_name: str) -> Optional[str]:
        """Try to find LinkedIn company profile"""
        try:
            # Use Serper to search for LinkedIn profile
            search_query = f'site:linkedin.com/company "{org_name}"'
            
            # This would use your existing Serper integration
            # For now, return None (implement based on your Serper setup)
            return None
            
        except Exception as e:
            logging.error(f"LinkedIn profile search failed: {e}")
            return None
    
    async def _extract_linkedin_data(self, linkedin_url: str) -> Dict[str, Any]:
        """Extract LinkedIn company data"""
        try:
            run_input = {
                "startUrls": [linkedin_url],
                "includeEmployees": False  # Don't scrape employees for privacy
            }
            
            run = self.client.actor(self.scrapers["linkedin_company"]).call(run_input=run_input)
            
            items = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
            
            return items[0] if items else {}
            
        except Exception as e:
            logging.error(f"LinkedIn extraction failed: {e}")
            return {"error": str(e)}
    
    async def _extract_social_profiles(self, website_url: str, org_name: str) -> Dict[str, Any]:
        """Extract social media profiles"""
        try:
            # Implementation would depend on available Apify actors
            # This is a placeholder
            return {
                "twitter": None,
                "facebook": None,
                "instagram": None,
                "youtube": None
            }
            
        except Exception as e:
            logging.error(f"Social profiles extraction failed: {e}")
            return {"error": str(e)}
    
    def _extract_contact_info(self, scraped_pages: List[Dict]) -> Dict[str, Any]:
        """Extract contact information from scraped pages"""
        contact_info = {
            "emails": [],
            "phones": [],
            "addresses": [],
            "contact_pages": []
        }
        
        for page in scraped_pages:
            # Extract emails
            if "emails" in page:
                contact_info["emails"].extend(page["emails"])
            
            # Extract phone numbers
            if "phones" in page:
                contact_info["phones"].extend(page["phones"])
            
            # Extract addresses
            if "addresses" in page:
                contact_info["addresses"].extend(page["addresses"])
        
        # Remove duplicates
        contact_info["emails"] = list(set(contact_info["emails"]))
        contact_info["phones"] = list(set(contact_info["phones"]))
        
        return contact_info
    
    def _extract_social_links(self, scraped_pages: List[Dict]) -> Dict[str, str]:
        """Extract social media links from scraped pages"""
        social_links = {}
        
        for page in scraped_pages:
            if "socialLinks" in page:
                for link in page["socialLinks"]:
                    if "linkedin.com" in link:
                        social_links["linkedin"] = link
                    elif "twitter.com" in link or "x.com" in link:
                        social_links["twitter"] = link
                    elif "facebook.com" in link:
                        social_links["facebook"] = link
                    elif "instagram.com" in link:
                        social_links["instagram"] = link
        
        return social_links

class OrganizationEnrichmentCrew:
    """CrewAI crew for complex organization analysis"""
    
    def __init__(self):
        self.llm = OpenAI(temperature=0.1)
        self.serper_tool = SerperDevTool()
        self.web_tool = WebsiteSearchTool()
        
        # Initialize agents
        self.researcher_agent = self._create_researcher_agent()
        self.financial_agent = self._create_financial_agent()
        self.contact_agent = self._create_contact_agent()
        self.validator_agent = self._create_validator_agent()
        
        # Create crew
        self.crew = self._create_crew()
    
    def _create_researcher_agent(self) -> Agent:
        """Create organization researcher agent"""
        return Agent(
            role='Organization Research Specialist',
            goal='Research and analyze organizations for comprehensive profiling',
            backstory="""You are an expert researcher specializing in analyzing organizations, 
            particularly those involved in funding, development, and technology initiatives in Africa. 
            You excel at:
            - Identifying organization types (government, NGO, foundation, corporate, academic)
            - Determining geographic scope and focus areas
            - Understanding mission, vision, and strategic priorities
            - Assessing credibility and legitimacy
            - Connecting organizations to their parent entities or networks""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.serper_tool, self.web_tool]
        )
    
    def _create_financial_agent(self) -> Agent:
        """Create financial analysis agent"""
        return Agent(
            role='Financial Capacity Analyst',
            goal='Assess organization financial capacity and funding patterns',
            backstory="""You are a financial analyst specializing in development finance 
            and philanthropic funding. You excel at:
            - Estimating funding capacity and budget sizes
            - Identifying funding history and patterns
            - Understanding funding mechanisms and processes
            - Assessing financial stability and sustainability
            - Recognizing co-funding relationships and partnerships""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.serper_tool, self.web_tool]
        )
    
    def _create_contact_agent(self) -> Agent:
        """Create contact information extraction agent"""
        return Agent(
            role='Contact Information Specialist',
            goal='Extract and validate official contact information',
            backstory="""You are a specialist in finding and validating official contact information 
            for organizations. You excel at:
            - Finding official email addresses and contact forms
            - Identifying key personnel and their roles
            - Locating headquarters and regional offices
            - Validating phone numbers and addresses
            - Distinguishing official from unofficial contact methods""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.web_tool]
        )
    
    def _create_validator_agent(self) -> Agent:
        """Create data validation agent"""
        return Agent(
            role='Data Validation Expert',
            goal='Validate and clean extracted organization data',
            backstory="""You are a data validation expert specializing in organization profiles. 
            You excel at:
            - Cross-referencing information from multiple sources
            - Identifying inconsistencies and errors
            - Assessing data quality and reliability
            - Standardizing formats and classifications
            - Flagging potential issues or missing information""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_crew(self) -> Crew:
        """Create the organization enrichment crew"""
        
        research_task = Task(
            description="""Research and analyze the organization comprehensively.
            
            Your job:
            1. Determine organization type, mission, and focus areas
            2. Identify geographic scope and target regions
            3. Assess credibility and legitimacy
            4. Find parent organizations or network affiliations
            5. Understand strategic priorities and recent initiatives
            
            Provide detailed findings with confidence scores.""",
            agent=self.researcher_agent,
            expected_output="""JSON with: {
                "organization_type": "string",
                "mission_statement": "string",
                "focus_areas": "array",
                "geographic_scope": "array",
                "credibility_score": "0.0-1.0",
                "parent_organization": "string or null",
                "network_affiliations": "array",
                "recent_initiatives": "array",
                "confidence_score": "0.0-1.0"
            }"""
        )
        
        financial_task = Task(
            description="""Analyze the organization's financial capacity and funding patterns.
            
            Your job:
            1. Estimate annual budget or funding capacity
            2. Identify major funding sources and mechanisms
            3. Research funding history and patterns
            4. Assess financial stability
            5. Find co-funding partnerships
            
            Focus on funding relevant to African AI/technology initiatives.""",
            agent=self.financial_agent,
            expected_output="""JSON with: {
                "estimated_annual_budget": "number or null",
                "funding_capacity_level": "high/medium/low",
                "major_funding_sources": "array",
                "funding_mechanisms": "array",
                "ai_funding_history": "array",
                "africa_funding_commitment": "string",
                "financial_stability": "high/medium/low",
                "confidence_score": "0.0-1.0"
            }""",
            context=[research_task]
        )
        
        contact_task = Task(
            description="""Extract and validate official contact information.
            
            Your job:
            1. Find official email addresses (general and program-specific)
            2. Locate contact forms and application portals
            3. Identify key personnel (program managers, directors)
            4. Find headquarters and regional office locations
            5. Validate all contact information
            
            Prioritize funding/grants program contacts.""",
            agent=self.contact_agent,
            expected_output="""JSON with: {
                "official_emails": "array",
                "contact_forms": "array",
                "key_personnel": "array",
                "headquarters_address": "string",
                "regional_offices": "array",
                "phone_numbers": "array",
                "funding_program_contacts": "array",
                "confidence_score": "0.0-1.0"
            }""",
            context=[research_task]
        )
        
        validation_task = Task(
            description="""Validate and consolidate all extracted organization data.
            
            Your job:
            1. Cross-check information consistency across all sources
            2. Identify and flag any inconsistencies or gaps
            3. Standardize all data formats
            4. Assess overall data quality
            5. Provide final organization profile
            
            Ensure all data is accurate and properly formatted for database storage.""",
            agent=self.validator_agent,
            expected_output="""JSON with complete validated organization profile: {
                "name": "string",
                "type": "string",
                "mission": "string",
                "focus_areas": "array",
                "geographic_scope": "array",
                "funding_capacity": "object",
                "contact_info": "object",
                "credibility_assessment": "object",
                "data_quality_score": "0.0-1.0",
                "validation_notes": "string",
                "last_updated": "ISO timestamp"
            }""",
            context=[research_task, financial_task, contact_task]
        )
        
        return Crew(
            agents=[self.researcher_agent, self.financial_agent, self.contact_agent, self.validator_agent],
            tasks=[research_task, financial_task, contact_task, validation_task],
            process=Process.sequential,
            verbose=True
        )
    
    async def analyze_organization(self, basic_info: Dict, structured_data: Dict) -> Dict[str, Any]:
        """Analyze organization using CrewAI crew"""
        
        input_data = {
            "basic_info": basic_info,
            "structured_data": structured_data,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            result = self.crew.kickoff(inputs=input_data)
            return json.loads(result)
        except Exception as e:
            logging.error(f"CrewAI organization analysis failed: {e}")
            return {
                "error": str(e),
                "analysis_status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }

class OrganizationEnrichmentPipeline:
    """Main organization enrichment pipeline coordinator"""
    
    def __init__(self, apify_api_token: str):
        self.cache = EnrichmentCache()
        self.apify_extractor = ApifyOrganizationExtractor(apify_api_token)
        self.enrichment_crew = OrganizationEnrichmentCrew()
        
        # Generate unique processor ID
        self.processor_id = f"enricher_{int(time.time())}"
    
    async def enrich_organization(self, org_name: str, org_type: str = None, 
                                org_country: str = None, trigger_source: str = "funding_opportunity") -> Dict[str, Any]:
        """Main enrichment function with full pipeline"""
        
        enrichment_result = {
            "organization_name": org_name,
            "enrichment_status": EnrichmentStatus.PENDING.value,
            "trigger_source": trigger_source,
            "started_at": datetime.utcnow().isoformat(),
            "processor_id": self.processor_id
        }
        
        # Check if already being processed
        if self.cache.is_locked(org_name):
            enrichment_result["enrichment_status"] = EnrichmentStatus.LOCKED.value
            enrichment_result["message"] = "Organization already being processed"
            return enrichment_result
        
        # Acquire processing lock
        if not self.cache.acquire_lock(org_name, self.processor_id):
            enrichment_result["enrichment_status"] = EnrichmentStatus.FAILED.value
            enrichment_result["message"] = "Failed to acquire processing lock"
            return enrichment_result
        
        try:
            enrichment_result["enrichment_status"] = EnrichmentStatus.IN_PROGRESS.value
            
            # Step 1: Quick deterministic checks
            basic_info = await self._get_basic_organization_info(org_name, org_type, org_country)
            enrichment_result["basic_info"] = basic_info
            
            # Step 2: Apify structured data extraction (if website found)
            structured_data = {}
            if basic_info.get("website"):
                structured_data = await self.apify_extractor.extract_organization_data(
                    basic_info["website"], org_name
                )
                enrichment_result["structured_data"] = structured_data
            
            # Step 3: CrewAI agent enrichment for complex analysis
            enriched_data = await self.enrichment_crew.analyze_organization(basic_info, structured_data)
            enrichment_result["enriched_data"] = enriched_data
            
            # Step 4: Consolidate and store final organization profile
            final_profile = self._consolidate_organization_data(
                org_name, basic_info, structured_data, enriched_data
            )
            enrichment_result["final_profile"] = final_profile
            
            # Step 5: Store in database
            org_id = await self._store_organization(final_profile)
            enrichment_result["organization_id"] = org_id
            
            # Step 6: Update known organizations cache (trigger prompt updates)
            await self._update_known_organizations_cache()
            
            enrichment_result["enrichment_status"] = EnrichmentStatus.COMPLETED.value
            enrichment_result["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            enrichment_result["enrichment_status"] = EnrichmentStatus.FAILED.value
            enrichment_result["error"] = str(e)
            enrichment_result["failed_at"] = datetime.utcnow().isoformat()
            logging.error(f"Organization enrichment failed for {org_name}: {e}")
        
        finally:
            # Always release lock
            self.cache.release_lock(org_name, self.processor_id)
        
        return enrichment_result
    
    async def _get_basic_organization_info(self, org_name: str, org_type: str = None, 
                                         org_country: str = None) -> Dict[str, Any]:
        """Quick deterministic organization info gathering"""
        
        basic_info = {
            "name": org_name,
            "type": org_type,
            "country": org_country,
            "website": None,
            "description": None,
            "lookup_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check if organization already exists in database
            existing_org = await self._lookup_existing_organization(org_name)
            if existing_org:
                basic_info.update({
                    "website": existing_org.get("website"),
                    "description": existing_org.get("description"),
                    "type": existing_org.get("type"),
                    "country": existing_org.get("country"),
                    "exists_in_db": True
                })
            else:
                # Quick web search for basic info
                search_info = await self._quick_organization_search(org_name)
                basic_info.update(search_info)
                basic_info["exists_in_db"] = False
        
        except Exception as e:
            basic_info["lookup_error"] = str(e)
            logging.error(f"Basic info lookup failed for {org_name}: {e}")
        
        return basic_info
    
    async def _lookup_existing_organization(self, org_name: str) -> Optional[Dict[str, Any]]:
        """Check if organization already exists in database"""
        try:
            db = next(get_db())
            org = db.query(Organization).filter(Organization.name.ilike(f"%{org_name}%")).first()
            
            if org:
                return {
                    "id": org.id,
                    "name": org.name,
                    "type": org.type,
                    "country": org.country,
                    "website": org.website,
                    "description": org.description
                }
        except Exception as e:
            logging.error(f"Database lookup failed: {e}")
        
        return None
    
    async def _quick_organization_search(self, org_name: str) -> Dict[str, Any]:
        """Quick search for basic organization information"""
        search_info = {
            "website": None,
            "description": None,
            "search_performed": True
        }
        
        try:
            # Use Serper for quick search (implement based on your setup)
            # This is a placeholder - integrate with your existing Serper implementation
            pass
        
        except Exception as e:
            search_info["search_error"] = str(e)
        
        return search_info
    
    def _consolidate_organization_data(self, org_name: str, basic_info: Dict, 
                                     structured_data: Dict, enriched_data: Dict) -> Dict[str, Any]:
        """Consolidate all organization data into final profile"""
        
        final_profile = {
            "name": org_name,
            "type": self._get_best_value("type", basic_info, enriched_data),
            "country": self._get_best_value("country", basic_info, enriched_data),
            "website": self._get_best_value("website", basic_info, structured_data),
            "description": self._get_best_value("mission_statement", enriched_data, basic_info, key2="description"),
            
            # From enrichment
            "focus_areas": enriched_data.get("focus_areas", []),
            "geographic_scope": enriched_data.get("geographic_scope", []),
            "funding_capacity": enriched_data.get("funding_capacity", {}),
            "contact_info": self._consolidate_contact_info(structured_data, enriched_data),
            
            # Quality metadata
            "data_quality_score": enriched_data.get("data_quality_score", 0.5),
            "confidence_score": self._calculate_overall_confidence(basic_info, structured_data, enriched_data),
            "enrichment_timestamp": datetime.utcnow().isoformat(),
            "data_sources": self._identify_data_sources(basic_info, structured_data, enriched_data),
            
            # AI relevance
            "ai_relevant": self._assess_ai_relevance(enriched_data),
            "africa_relevant": self._assess_africa_relevance(enriched_data),
            
            # Raw data for debugging
            "raw_enrichment_data": {
                "basic_info": basic_info,
                "structured_data": structured_data,
                "enriched_data": enriched_data
            }
        }
        
        return final_profile
    
    def _get_best_value(self, key: str, *sources, key2: str = None) -> Any:
        """Get the best value from multiple data sources"""
        for source in sources:
            if isinstance(source, dict):
                value = source.get(key) or source.get(key2) if key2 else source.get(key)
                if value:
                    return value
        return None
    
    def _consolidate_contact_info(self, structured_data: Dict, enriched_data: Dict) -> Dict[str, Any]:
        """Consolidate contact information from all sources"""
        contact_info = {}
        
        # From structured data (Apify)
        if "website_metadata" in structured_data:
            apify_contacts = structured_data["website_metadata"].get("contact_info", {})
            contact_info.update(apify_contacts)
        
        # From enriched data (CrewAI)
        if "contact_info" in enriched_data:
            agent_contacts = enriched_data["contact_info"]
            contact_info.update(agent_contacts)
        
        return contact_info
    
    def _calculate_overall_confidence(self, basic_info: Dict, structured_data: Dict, enriched_data: Dict) -> float:
        """Calculate overall confidence score for the organization profile"""
        confidence_scores = []
        
        # Basic info confidence
        if basic_info.get("exists_in_db"):
            confidence_scores.append(0.9)
        elif basic_info.get("website"):
            confidence_scores.append(0.7)
        else:
            confidence_scores.append(0.3)
        
        # Structured data confidence
        if structured_data.get("extraction_success"):
            confidence_scores.append(0.8)
        else:
            confidence_scores.append(0.4)
        
        # Enriched data confidence
        enrichment_confidence = enriched_data.get("confidence_score", 0.5)
        confidence_scores.append(enrichment_confidence)
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def _identify_data_sources(self, basic_info: Dict, structured_data: Dict, enriched_data: Dict) -> List[str]:
        """Identify which data sources were used"""
        sources = []
        
        if basic_info.get("exists_in_db"):
            sources.append(DataSource.MANUAL.value)
        
        if structured_data.get("extraction_success"):
            sources.append(DataSource.APIFY.value)
        
        if enriched_data and not enriched_data.get("error"):
            sources.append(DataSource.AGENT.value)
        
        return sources
    
    def _assess_ai_relevance(self, enriched_data: Dict) -> bool:
        """Assess if organization is AI-relevant"""
        focus_areas = enriched_data.get("focus_areas", [])
        ai_keywords = ["artificial intelligence", "ai", "machine learning", "ml", "technology", "digital", "innovation"]
        
        return any(keyword in " ".join(focus_areas).lower() for keyword in ai_keywords)
    
    def _assess_africa_relevance(self, enriched_data: Dict) -> bool:
        """Assess if organization is Africa-relevant"""
        geographic_scope = enriched_data.get("geographic_scope", [])
        africa_keywords = ["africa", "african", "saharan", "subsaharan"]
        
        return any(keyword in " ".join(geographic_scope).lower() for keyword in africa_keywords)
    
    async def _store_organization(self, profile: Dict[str, Any]) -> int:
        """Store organization profile in database"""
        try:
            # This would integrate with your actual database layer
            # For now, just return a mock ID
            return hash(profile["name"]) % 10000
        
        except Exception as e:
            logging.error(f"Failed to store organization: {e}")
            raise
    
    async def _update_known_organizations_cache(self):
        """Update the known organizations cache to improve agent prompts"""
        try:
            # This would trigger an update of the OrganizationKnowledgeBase
            # in the CrewAI funding opportunity processor
            pass
        
        except Exception as e:
            logging.error(f"Failed to update organizations cache: {e}")

# Usage functions
async def trigger_organization_enrichment_webhook(enrichment_data: Dict[str, Any]):
    """Webhook endpoint for triggering organization enrichment"""
    
    # Initialize pipeline (in production, this would be a singleton)
    apify_token = "your_apify_token"  # Load from environment
    pipeline = OrganizationEnrichmentPipeline(apify_token)
    
    # Extract data
    org_name = enrichment_data["organization_name"]
    org_type = enrichment_data.get("organization_type")
    org_country = enrichment_data.get("organization_country")
    trigger_source = enrichment_data.get("trigger_source", "webhook")
    
    # Start enrichment process
    result = await pipeline.enrich_organization(
        org_name=org_name,
        org_type=org_type,
        org_country=org_country,
        trigger_source=trigger_source
    )
    
    return result

async def batch_enrich_organizations(organization_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Batch process multiple organizations for enrichment"""
    
    apify_token = "your_apify_token"  # Load from environment
    pipeline = OrganizationEnrichmentPipeline(apify_token)
    
    results = []
    
    for org_data in organization_list:
        try:
            result = await pipeline.enrich_organization(
                org_name=org_data["name"],
                org_type=org_data.get("type"),
                org_country=org_data.get("country"),
                trigger_source="batch_processing"
            )
            results.append(result)
            
            # Add delay to respect rate limits
            await asyncio.sleep(2)
            
        except Exception as e:
            results.append({
                "organization_name": org_data["name"],
                "enrichment_status": EnrichmentStatus.FAILED.value,
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    # Example usage
    async def main():
        test_data = {
            "organization_name": "Gates Foundation",
            "organization_type": "foundation",
            "organization_country": "USA",
            "trigger_source": "test"
        }
        
        result = await trigger_organization_enrichment_webhook(test_data)
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())
