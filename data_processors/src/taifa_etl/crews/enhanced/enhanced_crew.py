"""
TAIFA Enhanced CrewAI Intelligence Item Processing System
Advanced ETL pipeline with learning, conflict resolution, and rejection analysis
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Database imports (adapt to your actual database setup)
from app.models.funding import AfricaIntelligenceItem
from app.models.organization import Organization
from app.core.database import get_db

class ConflictType(Enum):
    AMOUNT_PARSING = "amount_parsing"
    ORGANIZATION_IDENTIFICATION = "organization_identification"
    DEADLINE_EXTRACTION = "deadline_extraction"
    RELEVANCE_SCORING = "relevance_scoring"
    GEOGRAPHIC_SCOPE = "geographic_scope"

class ReviewStatus(Enum):
    AUTO_APPROVED = "auto_approved"
    COMMUNITY_REVIEW = "community_review_queue"
    HUMAN_REVIEW = "human_review_queue"
    REJECTED = "rejection_database"

@dataclass
class AgentOutput:
    """Standardized output format for all agents"""
    agent_name: str
    data: Dict[str, Any]
    confidence_score: float
    processing_time_ms: int
    errors: List[str] = None
    warnings: List[str] = None

@dataclass
class Conflict:
    """Represents a conflict between agent outputs"""
    conflict_type: ConflictType
    conflicting_values: Dict[str, Any]
    agents_involved: List[str]
    confidence_difference: float

class OrganizationKnowledgeBase:
    """Dynamic knowledge base for organization learning"""
    
    def __init__(self):
        self.known_organizations = self._load_known_organizations()
        self.embeddings = OpenAIEmbeddings()
        self.last_update = datetime.utcnow()
        self.update_frequency = timedelta(hours=6)
    
    def _load_known_organizations(self) -> List[Dict[str, Any]]:
        """Load known organizations from database"""
        # This would connect to your actual database
        try:
            db = next(get_db())
            organizations = db.query(Organization).all()
            
            return [
                {
                    "name": org.name,
                    "type": org.type,
                    "country": org.country,
                    "funding_focus": org.funding_focus,
                    "ai_relevant": org.ai_relevant
                }
                for org in organizations
            ]
        except Exception as e:
            print(f"Warning: Could not load organizations from DB: {e}")
            return []
    
    def get_organization_examples(self) -> str:
        """Generate prompt text with organization examples"""
        if not self.known_organizations:
            return "No known organizations yet - you're helping build this knowledge base!"
        
        examples = []
        for org in self.known_organizations[-20:]:  # Use last 20 for prompt efficiency
            examples.append(f"- {org['name']} ({org['type']}, {org['country']})")
        
        return "Organizations supporting AI research and implementation in Africa include:\n" + "\n".join(examples)
    
    def should_update(self) -> bool:
        """Check if knowledge base needs updating"""
        return datetime.utcnow() - self.last_update > self.update_frequency
    
    async def update_if_needed(self):
        """Update knowledge base if needed"""
        if self.should_update():
            self.known_organizations = self._load_known_organizations()
            self.last_update = datetime.utcnow()

class ConflictResolver:
    """Advanced conflict resolution system"""
    
    def __init__(self):
        self.resolution_strategies = {
            ConflictType.AMOUNT_PARSING: self._resolve_amount_conflict,
            ConflictType.ORGANIZATION_IDENTIFICATION: self._resolve_organization_conflict,
            ConflictType.DEADLINE_EXTRACTION: self._resolve_deadline_conflict,
            ConflictType.RELEVANCE_SCORING: self._resolve_relevance_conflict,
            ConflictType.GEOGRAPHIC_SCOPE: self._resolve_geographic_conflict
        }
    
    def identify_conflicts(self, agent_outputs: List[AgentOutput]) -> List[Conflict]:
        """Identify conflicts between agent outputs"""
        conflicts = []
        
        # Extract relevant data from agents
        parser_data = next((ao.data for ao in agent_outputs if ao.agent_name == "parser"), {})
        extractor_data = next((ao.data for ao in agent_outputs if ao.agent_name == "extractor"), {})
        relevancy_data = next((ao.data for ao in agent_outputs if ao.agent_name == "relevancy"), {})
        
        # Check amount conflicts
        parser_amount = parser_data.get("amount")
        extractor_amount = extractor_data.get("amount")
        if parser_amount and extractor_amount:
            if abs(float(parser_amount) - float(extractor_amount)) > 1000:  # $1000 threshold
                conflicts.append(Conflict(
                    conflict_type=ConflictType.AMOUNT_PARSING,
                    conflicting_values={"parser": parser_amount, "extractor": extractor_amount},
                    agents_involved=["parser", "extractor"],
                    confidence_difference=abs(parser_data.get("amount_confidence", 0.5) - 
                                           extractor_data.get("amount_confidence", 0.5))
                ))
        
        # Check organization conflicts
        parser_org = parser_data.get("organization_name", "").lower()
        extractor_org = extractor_data.get("organization_name", "").lower()
        if parser_org and extractor_org:
            similarity = self._calculate_string_similarity(parser_org, extractor_org)
            if similarity < 0.8:  # Less than 80% similar
                conflicts.append(Conflict(
                    conflict_type=ConflictType.ORGANIZATION_IDENTIFICATION,
                    conflicting_values={"parser": parser_org, "extractor": extractor_org},
                    agents_involved=["parser", "extractor"],
                    confidence_difference=abs(parser_data.get("org_confidence", 0.5) - 
                                           extractor_data.get("organization_match_confidence", 0.5))
                ))
        
        # Add more conflict detection logic as needed...
        
        return conflicts
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()
    
    def resolve_conflicts(self, conflicts: List[Conflict], agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve all identified conflicts"""
        resolved_data = {}
        
        for conflict in conflicts:
            if conflict.conflict_type in self.resolution_strategies:
                resolution = self.resolution_strategies[conflict.conflict_type](conflict, agent_outputs)
                resolved_data[conflict.conflict_type.value] = resolution
                
                # Log resolution for learning
                self._log_conflict_resolution(conflict, resolution)
        
        return resolved_data
    
    def _resolve_amount_conflict(self, conflict: Conflict, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve amount parsing conflicts"""
        # Use confidence scores to determine best value
        values = conflict.conflicting_values
        
        # Additional validation strategies could be added here
        # For now, use the higher confidence value
        parser_confidence = next((ao.confidence_score for ao in agent_outputs if ao.agent_name == "parser"), 0.5)
        extractor_confidence = next((ao.confidence_score for ao in agent_outputs if ao.agent_name == "extractor"), 0.5)
        
        if parser_confidence > extractor_confidence:
            resolved_amount = values["parser"]
            resolution_method = "parser_higher_confidence"
        else:
            resolved_amount = values["extractor"]
            resolution_method = "extractor_higher_confidence"
        
        return {
            "resolved_value": resolved_amount,
            "resolution_method": resolution_method,
            "confidence_scores": {"parser": parser_confidence, "extractor": extractor_confidence}
        }
    
    def _resolve_organization_conflict(self, conflict: Conflict, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve organization identification conflicts"""
        # Could implement fuzzy matching against known organizations
        # For now, use simple confidence-based resolution
        values = conflict.conflicting_values
        
        # Check against known organizations database
        # This is where we'd implement fuzzy matching logic
        
        return {
            "resolved_value": values["extractor"],  # Default to extractor for now
            "resolution_method": "default_to_extractor",
            "requires_human_review": True
        }
    
    def _resolve_deadline_conflict(self, conflict: Conflict, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve deadline extraction conflicts"""
        # Implement date parsing validation logic
        return {"resolved_value": None, "resolution_method": "manual_review_required"}
    
    def _resolve_relevance_conflict(self, conflict: Conflict, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve relevance scoring conflicts"""
        # Could implement ensemble scoring
        return {"resolved_value": None, "resolution_method": "ensemble_average"}
    
    def _resolve_geographic_conflict(self, conflict: Conflict, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve geographic scope conflicts"""
        # Implement geographic validation logic
        return {"resolved_value": None, "resolution_method": "geographic_validation"}
    
    def _log_conflict_resolution(self, conflict: Conflict, resolution: Dict[str, Any]):
        """Log conflict resolution for learning"""
        # This would write to your conflict_resolutions table
        log_data = {
            "conflict_type": conflict.conflict_type.value,
            "conflicting_values": conflict.conflicting_values,
            "resolution": resolution,
            "timestamp": datetime.utcnow().isoformat()
        }
        print(f"Conflict resolved: {log_data}")  # Replace with actual logging

class EnhancedAfricaIntelligenceItemProcessor:
    """Enhanced processor with learning and conflict resolution"""
    
    def __init__(self):
        self.llm = OpenAI(temperature=0.1)
        self.serper_tool = SerperDevTool()
        self.web_tool = WebsiteSearchTool()
        
        # Advanced components
        self.org_knowledge = OrganizationKnowledgeBase()
        self.conflict_resolver = ConflictResolver()
        
        # Initialize agents with dynamic knowledge
        self._initialize_agents()
        
        # Create the crew
        self.crew = self._create_enhanced_crew()
    
    def _initialize_agents(self):
        """Initialize agents with dynamic organization knowledge"""
        org_examples = self.org_knowledge.get_organization_examples()
        
        self.parser_agent = Agent(
            role='Content Parser Specialist',
            goal='Extract clean, structured data from raw web content and search results',
            backstory="""You are an expert at parsing web content, search results, and documents. 
            You excel at extracting meaningful text from HTML, cleaning up formatting issues, 
            and identifying key content sections. You have deep experience with funding announcements, 
            grant calls, and academic/government publications.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.web_tool]
        )
        
        self.relevancy_agent = Agent(
            role='Africa AI Funding Relevancy Expert',
            goal='Assess whether content is relevant to AI intelligence feed in Africa',
            backstory=f"""You are a leading expert on African AI ecosystem, funding landscapes, 
            and technology development across the continent. You deeply understand:
            - All 54 African countries and their tech ecosystems
            - AI/ML domains: healthcare, agriculture, education, fintech, governance
            - Funding types: grants, accelerators, competitions, scholarships, VC
            - African development priorities and Vision 2063
            - Multilingual context (English, French, Arabic, Portuguese, local languages)
            
            {org_examples}
            
            Use these organizations as examples of the types of funders and implementers 
            you should recognize and prioritize.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.summarizer_agent = Agent(
            role='Technical Content Summarizer',
            goal='Create clear, concise, and standardized descriptions of intelligence feed',
            backstory="""You are an expert technical writer specializing in funding and grant descriptions. 
            You excel at:
            - Creating clear, jargon-free summaries accessible to diverse audiences
            - Maintaining consistent tone and format across all descriptions
            - Preserving critical details while removing unnecessary complexity
            - Adapting content for both English and French-speaking African audiences
            - Following funding industry best practices for opportunity descriptions""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.extractor_agent = Agent(
            role='Structured Data Extraction Expert',
            goal='Extract specific database fields from intelligence item content',
            backstory=f"""You are a data extraction specialist with expertise in:
            - Parsing monetary amounts in various currencies and formats
            - Extracting and standardizing dates across different formats
            - Identifying organization names, types, and hierarchies
            - Extracting contact information (emails, websites, addresses)
            - Parsing eligibility criteria and application requirements
            - Standardizing geographic scope and target audiences
            
            Known organizations you should recognize:
            {org_examples}
            
            When you encounter organizations similar to these, mark them with high confidence.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_enhanced_crew(self) -> Crew:
        """Create enhanced crew with better task definitions"""
        
        parse_task = Task(
            description="""Parse the raw content and extract clean, structured text.
            
            CRITICAL: Include confidence scores for all your extractions.
            
            Your job:
            1. Clean up any HTML tags, encoding issues, or formatting problems
            2. Extract the main content, title, and key metadata
            3. Identify and preserve important structural elements
            4. Note the source type (website, PDF, news article, etc.)
            5. Provide confidence scores for each piece of extracted data
            
            Output format: JSON with confidence scores for each field""",
            agent=self.parser_agent,
            expected_output="""JSON with: {
                "title": "string",
                "description": "string", 
                "source_url": "string",
                "content_type": "string",
                "amount": "number or null",
                "amount_confidence": "0.0-1.0",
                "organization_name": "string or null",
                "org_confidence": "0.0-1.0",
                "deadline": "ISO date or null",
                "deadline_confidence": "0.0-1.0",
                "raw_metadata": "object",
                "overall_confidence": "0.0-1.0"
            }"""
        )
        
        assess_task = Task(
            description="""Evaluate the relevance of this content to AI funding in Africa.
            
            CRITICAL: Provide detailed reasoning and confidence scores.
            
            Assess three key dimensions:
            1. AI/Technology Relevance (0-1): Does this involve AI, ML, or relevant technology?
            2. Africa Relevance (0-1): Is this specifically for African organizations/projects?
            3. Funding Relevance (0-1): Is this actually a intelligence item (not just news)?
            
            Pay special attention to organizations you recognize from your knowledge base.
            
            Provide detailed reasoning for all scores and flag any uncertainties.""",
            agent=self.relevancy_agent,
            expected_output="""JSON with: {
                "ai_relevance_score": "0.0-1.0",
                "africa_relevance_score": "0.0-1.0", 
                "funding_relevance_score": "0.0-1.0",
                "overall_relevance_score": "0.0-1.0",
                "confidence_level": "high/medium/low",
                "detailed_reasoning": "string",
                "geographic_scope": "array",
                "ai_domains": "array",
                "funding_type": "string",
                "red_flags": "array",
                "review_required": "boolean"
            }"""
        )
        
        summarize_task = Task(
            description="""Create a clear, standardized summary of this intelligence item.
            
            Requirements:
            1. Write a concise 2-3 sentence summary highlighting key opportunity details
            2. Create a detailed description (150-300 words)
            3. Generate relevant tags for categorization
            4. Assess translation priority for French localization
            5. Ensure content is accessible to both technical and non-technical audiences
            
            Include quality scores for your output.""",
            agent=self.summarizer_agent,
            expected_output="""JSON with: {
                "summary": "string",
                "description": "string",
                "tags": "array",
                "language_detected": "string",
                "content_quality_score": "0.0-1.0",
                "translation_priority": "high/medium/low",
                "reading_level": "string",
                "tone_analysis": "string"
            }""",
            context=[parse_task, assess_task]
        )
        
        extract_task = Task(
            description="""Extract specific structured fields for database storage.
            
            CRITICAL: Provide confidence scores for all extractions and cross-validate with parser output.
            
            Extract with confidence scores:
            1. Funding details (amount, currency, type)
            2. Timeline (deadline, start date, duration)
            3. Organization (name, type, country)
            4. Eligibility and contact information
            5. Classification (domains, sectors, categories)
            
            Cross-reference organization names with your knowledge base.""",
            agent=self.extractor_agent,
            expected_output="""JSON with all database fields and confidence scores: {
                "amount": "number", "amount_confidence": "0.0-1.0",
                "currency": "string", "deadline": "ISO date",
                "deadline_confidence": "0.0-1.0",
                "organization_name": "string",
                "organization_match_confidence": "0.0-1.0",
                "organization_type": "string",
                "organization_country": "string",
                "contact_email": "string", "application_url": "string",
                "eligibility_criteria": "array", "ai_domains": "array",
                "target_sectors": "array", "geographic_scope": "array",
                "extraction_confidence": "0.0-1.0"
            }""",
            context=[parse_task, assess_task, summarize_task]
        )
        
        return Crew(
            agents=[self.parser_agent, self.relevancy_agent, self.summarizer_agent, self.extractor_agent],
            tasks=[parse_task, assess_task, summarize_task, extract_task],
            process=Process.sequential,
            verbose=True
        )
    
    async def process_opportunity_enhanced(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced processing with conflict resolution and learning"""
        
        # Update organization knowledge if needed
        await self.org_knowledge.update_if_needed()
        
        # Record processing start time
        start_time = datetime.utcnow()
        
        try:
            # Execute the crew and capture individual agent outputs
            agent_outputs = []
            
            # Run the crew (this would need to be modified to capture individual outputs)
            crew_result = self.crew.kickoff(inputs={
                "raw_content": raw_data,
                "processing_timestamp": start_time.isoformat(),
                "source_type": raw_data.get("source_type", "serper_search")
            })
            
            # Parse individual agent results (this is simplified - you'd need to capture actual outputs)
            agent_outputs = self._parse_crew_outputs(crew_result)
            
            # Identify and resolve conflicts
            conflicts = self.conflict_resolver.identify_conflicts(agent_outputs)
            resolved_conflicts = self.conflict_resolver.resolve_conflicts(conflicts, agent_outputs)
            
            # Calculate overall confidence and determine routing
            overall_confidence = self._calculate_overall_confidence(agent_outputs, resolved_conflicts)
            review_status = self._determine_review_status(overall_confidence, conflicts)
            
            # Structure final output
            final_output = self._structure_enhanced_output(
                agent_outputs, resolved_conflicts, overall_confidence, 
                review_status, raw_data, start_time
            )
            
            # Log for learning
            await self._log_processing_result(final_output, agent_outputs, conflicts)
            
            return final_output
            
        except Exception as e:
            # Handle errors gracefully
            return self._handle_processing_error(e, raw_data, start_time)
    
    def _parse_crew_outputs(self, crew_result: str) -> List[AgentOutput]:
        """Parse individual agent outputs from crew result"""
        # This is a simplified implementation
        # In practice, you'd need to modify CrewAI to capture individual agent outputs
        try:
            parsed_result = json.loads(crew_result)
            return [
                AgentOutput(
                    agent_name="combined",
                    data=parsed_result,
                    confidence_score=parsed_result.get("overall_confidence", 0.5),
                    processing_time_ms=1000  # Placeholder
                )
            ]
        except json.JSONDecodeError:
            return [
                AgentOutput(
                    agent_name="error",
                    data={"error": "Failed to parse crew output"},
                    confidence_score=0.0,
                    processing_time_ms=0,
                    errors=["JSON parsing failed"]
                )
            ]
    
    def _calculate_overall_confidence(self, agent_outputs: List[AgentOutput], conflicts: Dict) -> float:
        """Calculate overall confidence score"""
        if not agent_outputs:
            return 0.0
        
        base_confidence = sum(ao.confidence_score for ao in agent_outputs) / len(agent_outputs)
        
        # Reduce confidence based on conflicts
        conflict_penalty = len(conflicts) * 0.1
        
        return max(0.0, base_confidence - conflict_penalty)
    
    def _determine_review_status(self, confidence: float, conflicts: List[Conflict]) -> ReviewStatus:
        """Determine appropriate review status"""
        if confidence >= 0.9 and not conflicts:
            return ReviewStatus.AUTO_APPROVED
        elif confidence >= 0.7:
            return ReviewStatus.COMMUNITY_REVIEW
        elif confidence >= 0.5:
            return ReviewStatus.HUMAN_REVIEW
        else:
            return ReviewStatus.REJECTED
    
    def _structure_enhanced_output(self, agent_outputs: List[AgentOutput], 
                                 resolved_conflicts: Dict, overall_confidence: float,
                                 review_status: ReviewStatus, raw_data: Dict, 
                                 start_time: datetime) -> Dict[str, Any]:
        """Structure the enhanced output with all metadata"""
        
        # Extract data from agent outputs (simplified)
        primary_data = agent_outputs[0].data if agent_outputs else {}
        
        return {
            # Core opportunity data
            "title": primary_data.get("title"),
            "description": primary_data.get("description"),
            "summary": primary_data.get("summary"),
            "source_url": primary_data.get("source_url"),
            
            # Funding details
            "amount": primary_data.get("amount"),
            "currency": primary_data.get("currency", "USD"),
            "funding_type": primary_data.get("funding_type"),
            
            # Timeline
            "deadline": primary_data.get("deadline"),
            "start_date": primary_data.get("start_date"),
            
            # Organization
            "organization_name": primary_data.get("organization_name"),
            "organization_type": primary_data.get("organization_type"),
            
            # Classification
            "ai_domains": primary_data.get("ai_domains", []),
            "tags": primary_data.get("tags", []),
            "geographical_scope": primary_data.get("geographical_scope"),
            
            # Quality metrics
            "ai_relevance_score": primary_data.get("ai_relevance_score"),
            "africa_relevance_score": primary_data.get("africa_relevance_score"),
            "funding_relevance_score": primary_data.get("funding_relevance_score"),
            "overall_relevance_score": primary_data.get("overall_relevance_score"),
            "overall_confidence": overall_confidence,
            "review_status": review_status.value,
            
            # Processing metadata
            "processing_metadata": {
                "agent_outputs": [ao.__dict__ for ao in agent_outputs],
                "conflicts_detected": resolved_conflicts,
                "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "org_knowledge_version": self.org_knowledge.last_update.isoformat(),
                "processed_at": datetime.utcnow().isoformat(),
                "processing_version": "enhanced_crewai_v1.0"
            },
            
            # Original data for debugging
            "raw_data": raw_data
        }
    
    def _handle_processing_error(self, error: Exception, raw_data: Dict, start_time: datetime) -> Dict[str, Any]:
        """Handle processing errors gracefully"""
        return {
            "error": "Processing failed",
            "error_details": str(error),
            "error_type": type(error).__name__,
            "review_status": ReviewStatus.REJECTED.value,
            "processing_metadata": {
                "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "processed_at": datetime.utcnow().isoformat(),
                "processing_version": "enhanced_crewai_v1.0_error"
            },
            "raw_data": raw_data
        }
    
    async def _log_processing_result(self, final_output: Dict, agent_outputs: List[AgentOutput], conflicts: List[Conflict]):
        """Log processing results for learning and monitoring"""
        # This would write to your agent_processing_logs and conflict_resolutions tables
        log_data = {
            "opportunity_data": final_output,
            "agent_performance": [ao.__dict__ for ao in agent_outputs],
            "conflicts": [c.__dict__ for c in conflicts],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In production, this would write to your database
        print(f"Logged processing result: {final_output.get('title', 'Unknown')}")

# Enhanced usage function
async def process_serper_results_enhanced(search_results: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Enhanced processing with rejection tracking"""
    
    processor = EnhancedAfricaIntelligenceItemProcessor()
    processed_opportunities = []
    rejected_opportunities = []
    
    for result in search_results:
        try:
            processed = await processor.process_opportunity_enhanced(result)
            
            # Route based on review status
            if processed.get("review_status") == ReviewStatus.REJECTED.value:
                rejected_opportunities.append(processed)
            else:
                processed_opportunities.append(processed)
                
                # Trigger organization enrichment if needed
                if processed.get("organization_name"):
                    await trigger_organization_enrichment_if_needed(
                        processed["organization_name"],
                        processed.get("organization_type"),
                        processed.get("organization_country")
                    )
            
        except Exception as e:
            # Log error and continue
            print(f"Error processing opportunity: {e}")
            rejected_opportunities.append({
                "error": str(e),
                "raw_data": result,
                "processed_at": datetime.utcnow().isoformat()
            })
    
    return processed_opportunities, rejected_opportunities

async def trigger_organization_enrichment_if_needed(org_name: str, org_type: str, org_country: str):
    """Enhanced organization enrichment trigger"""
    # This would integrate with your organization enrichment pipeline
    print(f"Triggering enrichment for: {org_name}")
