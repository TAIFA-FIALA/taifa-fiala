"""
TAIFA CrewAI Funding Opportunity Processing Crew
Intelligent ETL pipeline using specialized AI agents
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool
from langchain.llms import OpenAI
from typing import Dict, List, Any
import json
from datetime import datetime

class FundingOpportunityProcessor:
    """Main coordinator for funding opportunity processing"""
    
    def __init__(self):
        self.llm = OpenAI(temperature=0.1)
        self.serper_tool = SerperDevTool()
        self.web_tool = WebsiteSearchTool()
        
        # Initialize specialized agents
        self.parser_agent = self._create_parser_agent()
        self.relevancy_agent = self._create_relevancy_agent()
        self.summarizer_agent = self._create_summarizer_agent()
        self.extractor_agent = self._create_extractor_agent()
        
        # Create the crew
        self.crew = self._create_crew()
    
    def _create_parser_agent(self) -> Agent:
        """Create the Parser Agent - Raw data extraction specialist"""
        return Agent(
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
    
    def _create_relevancy_agent(self) -> Agent:
        """Create the Relevancy Assessor Agent"""
        return Agent(
            role='Africa AI Funding Relevancy Expert',
            goal='Assess whether content is relevant to AI funding opportunities in Africa',
            backstory="""You are a leading expert on African AI ecosystem, funding landscapes, 
            and technology development across the continent. You deeply understand:
            - All 54 African countries and their tech ecosystems
            - AI/ML domains: healthcare, agriculture, education, fintech, governance
            - Funding types: grants, accelerators, competitions, scholarships, VC
            - African development priorities and Vision 2063
            - Multilingual context (English, French, Arabic, Portuguese, local languages)
            
            You can accurately assess relevance and assign precise scores.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_summarizer_agent(self) -> Agent:
        """Create the Summarizer Agent"""
        return Agent(
            role='Technical Content Summarizer',
            goal='Create clear, concise, and standardized descriptions of funding opportunities',
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
    
    def _create_extractor_agent(self) -> Agent:
        """Create the Data Extractor Agent"""
        return Agent(
            role='Structured Data Extraction Expert',
            goal='Extract specific database fields from funding opportunity content',
            backstory="""You are a data extraction specialist with expertise in:
            - Parsing monetary amounts in various currencies and formats
            - Extracting and standardizing dates across different formats
            - Identifying organization names, types, and hierarchies
            - Extracting contact information (emails, websites, addresses)
            - Parsing eligibility criteria and application requirements
            - Standardizing geographic scope and target audiences
            
            You ensure data consistency and accuracy for database storage.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_crew(self) -> Crew:
        """Create the coordinated crew with defined tasks"""
        
        # Define the sequential tasks
        parse_task = Task(
            description="""Parse the raw content and extract clean, structured text.
            
            Input: Raw search result with title, snippet, URL, and any additional metadata
            
            Your job:
            1. Clean up any HTML tags, encoding issues, or formatting problems
            2. Extract the main content, title, and key metadata
            3. Identify and preserve important structural elements
            4. Note the source type (website, PDF, news article, etc.)
            
            Output: Clean structured data ready for analysis""",
            agent=self.parser_agent,
            expected_output="JSON with cleaned title, description, source_url, content_type, and raw_metadata"
        )
        
        assess_task = Task(
            description="""Evaluate the relevance of this content to AI funding in Africa.
            
            Assess three key dimensions:
            1. AI/Technology Relevance (0-1): Does this involve AI, ML, or relevant technology?
            2. Africa Relevance (0-1): Is this specifically for African organizations/projects?
            3. Funding Relevance (0-1): Is this actually a funding opportunity (not just news)?
            
            Consider:
            - Geographic scope and eligibility
            - Technology domains and applications
            - Funding mechanisms and amounts
            - Credibility and legitimacy of source
            - Alignment with African development priorities
            
            Provide detailed reasoning for scores.""",
            agent=self.relevancy_agent,
            expected_output="JSON with relevance scores, reasoning, geographic_scope, ai_domains, funding_type, and overall_assessment",
            context=[parse_task]
        )
        
        summarize_task = Task(
            description="""Create a clear, standardized summary of this funding opportunity.
            
            Requirements:
            1. Write a concise 2-3 sentence summary highlighting key opportunity details
            2. Create a detailed description (150-300 words) that includes:
               - What the funding supports
               - Who is eligible to apply
               - Key requirements or focus areas
               - Application process overview
            3. Generate relevant tags for categorization
            4. Ensure content is accessible to both technical and non-technical audiences
            5. Maintain professional, encouraging tone
            
            Style: Clear, direct, informative. Avoid jargon. Focus on actionable information.""",
            agent=self.summarizer_agent,
            expected_output="JSON with summary, description, tags, reading_level, and tone_analysis",
            context=[parse_task, assess_task]
        )
        
        extract_task = Task(
            description="""Extract specific structured fields for database storage.
            
            Extract and standardize:
            1. Funding Details:
               - Amount (convert to USD if possible)
               - Currency
               - Funding type (grant, prize, accelerator, etc.)
            
            2. Timeline:
               - Application deadline
               - Program start date
               - Duration/funding period
            
            3. Organization:
               - Funding organization name
               - Organization type (government, foundation, corporate, etc.)
               - Organization country/region
            
            4. Eligibility:
               - Geographic eligibility
               - Organization types eligible
               - Specific requirements
            
            5. Contact:
               - Application URL
               - Contact email
               - Additional contact info
            
            6. Classification:
               - AI/tech domains
               - Target sectors
               - Program category
            
            Ensure all extracted data is clean, standardized, and ready for database insertion.""",
            agent=self.extractor_agent,
            expected_output="JSON with all database fields properly formatted and validated",
            context=[parse_task, assess_task, summarize_task]
        )
        
        return Crew(
            agents=[self.parser_agent, self.relevancy_agent, self.summarizer_agent, self.extractor_agent],
            tasks=[parse_task, assess_task, summarize_task, extract_task],
            process=Process.sequential,
            verbose=True
        )
    
    def process_opportunity(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single funding opportunity through the crew"""
        
        # Prepare input for the crew
        input_data = {
            "raw_content": raw_data,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": raw_data.get("source_type", "serper_search")
        }
        
        # Execute the crew
        result = self.crew.kickoff(inputs=input_data)
        
        # Parse and structure the final output
        processed_opportunity = self._structure_output(result, raw_data)
        
        return processed_opportunity
    
    def _structure_output(self, crew_result: str, original_data: Dict) -> Dict[str, Any]:
        """Structure the crew output into final database format"""
        
        try:
            # Parse the crew result (should be JSON from the last task)
            extracted_data = json.loads(crew_result)
            
            # Combine with processing metadata
            final_output = {
                # Core opportunity data
                "title": extracted_data.get("title"),
                "description": extracted_data.get("description"),
                "summary": extracted_data.get("summary"),
                "source_url": extracted_data.get("source_url"),
                
                # Funding details
                "amount": extracted_data.get("amount"),
                "currency": extracted_data.get("currency", "USD"),
                "funding_type": extracted_data.get("funding_type"),
                
                # Timeline
                "deadline": extracted_data.get("deadline"),
                "start_date": extracted_data.get("start_date"),
                "duration_months": extracted_data.get("duration_months"),
                
                # Organization (will trigger enrichment if new)
                "organization_name": extracted_data.get("organization_name"),
                "organization_type": extracted_data.get("organization_type"),
                "organization_country": extracted_data.get("organization_country"),
                
                # Geographic and eligibility
                "geographical_scope": extracted_data.get("geographical_scope"),
                "eligibility_criteria": extracted_data.get("eligibility_criteria"),
                
                # Classification
                "ai_domains": extracted_data.get("ai_domains", []),
                "target_sectors": extracted_data.get("target_sectors", []),
                "tags": extracted_data.get("tags", []),
                
                # Contact
                "contact_email": extracted_data.get("contact_email"),
                "application_url": extracted_data.get("application_url"),
                
                # Quality metrics
                "ai_relevance_score": extracted_data.get("ai_relevance_score"),
                "africa_relevance_score": extracted_data.get("africa_relevance_score"),
                "funding_relevance_score": extracted_data.get("funding_relevance_score"),
                "overall_relevance_score": extracted_data.get("overall_relevance_score"),
                "confidence_level": extracted_data.get("confidence_level"),
                
                # Processing metadata
                "processed_at": datetime.utcnow().isoformat(),
                "processing_version": "crewai_v1.0",
                "source_type": original_data.get("source_type", "serper_search"),
                "raw_data": original_data  # Store original for debugging
            }
            
            return final_output
            
        except json.JSONDecodeError as e:
            # Handle parsing errors gracefully
            return {
                "error": "Failed to parse crew output",
                "error_details": str(e),
                "raw_crew_output": crew_result,
                "original_data": original_data,
                "processed_at": datetime.utcnow().isoformat()
            }

# Usage example
def process_serper_results(search_results: List[Dict]) -> List[Dict]:
    """Process SERPER search results through CrewAI pipeline"""
    
    processor = FundingOpportunityProcessor()
    processed_opportunities = []
    
    for result in search_results:
        try:
            processed = processor.process_opportunity(result)
            
            # Quality filter - only keep high-relevance opportunities
            if processed.get("overall_relevance_score", 0) >= 0.7:
                processed_opportunities.append(processed)
                
                # Trigger organization enrichment if new organization
                if processed.get("organization_name"):
                    trigger_organization_enrichment_if_needed(
                        processed["organization_name"],
                        processed["organization_type"],
                        processed["organization_country"]
                    )
            
        except Exception as e:
            # Log error but continue processing other opportunities
            print(f"Error processing opportunity: {e}")
            continue
    
    return processed_opportunities

def trigger_organization_enrichment_if_needed(org_name: str, org_type: str, org_country: str):
    """Trigger organization enrichment pipeline if organization doesn't exist"""
    
    # Check if organization exists in database
    if not organization_exists_in_db(org_name):
        # Trigger webhook or queue for organization enrichment
        enrichment_data = {
            "organization_name": org_name,
            "organization_type": org_type,
            "organization_country": org_country,
            "trigger_source": "funding_opportunity_processing",
            "triggered_at": datetime.utcnow().isoformat()
        }
        
        # This could be a webhook, queue message, or direct function call
        trigger_organization_enrichment_webhook(enrichment_data)

def organization_exists_in_db(org_name: str) -> bool:
    """Check if organization already exists in database"""
    # Database query implementation
    pass

def trigger_organization_enrichment_webhook(data: Dict):
    """Trigger webhook for organization enrichment"""
    # Webhook implementation
    pass
