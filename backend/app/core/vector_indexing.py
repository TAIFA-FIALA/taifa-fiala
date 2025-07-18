"""
Vector Indexing Integration for ETL Pipeline
============================================

This module integrates Pinecone vector database indexing into the ETL pipeline,
specifically focusing on processing data from the Crawl4AI module and other opportunity sources.
It leverages Microsoft's multilingual-e5-large embedding model for enhanced multilingual support.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from pinecone import Pinecone, ServerlessSpec


from .etl_architecture import ETLTask, PipelineStage, Priority, ProcessingResult
from .vector_db_config import PineconeConfig, VectorIndexType, default_config
from ..models.funding import AfricaIntelligenceItem
from ..models.organization import Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VectorIndexingService:
    """Service for indexing ETL pipeline data in Pinecone vector database"""
    
    def __init__(self, config: PineconeConfig = default_config):
        self.config = config
        self.pinecone_client = None
        self.index = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize connection to Pinecone"""
        if self.initialized:
            return True
            
        if not self.config.api_key:
            self.logger.error("Pinecone API key not provided")
            return False
            
        try:
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(api_key=self.config.api_key)
            
            # Check if index exists
            index_list = self.pinecone_client.list_indexes()
            if self.config.index_name not in index_list.names():
                self.logger.error(f"Index {self.config.index_name} does not exist")
                return False
                
            # Connect to the index
            self.index = self.pinecone_client.Index(self.config.index_name)
            self.initialized = True
            self.logger.info(f"Connected to index: {self.config.index_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            return False
    
    async def process_indexing_task(self, task: ETLTask) -> ProcessingResult:
        """Process an indexing task from the ETL pipeline"""
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return ProcessingResult(
                    task_id=task.id,
                    stage=PipelineStage.INDEXING,
                    success=False,
                    error="Failed to initialize vector indexing service"
                )
        
        try:
            payload = task.payload
            data_type = payload.get('data_type')
            
            if data_type == 'intelligence_item':
                return await self._index_intelligence_item(task)
            elif data_type == 'organization':
                return await self._index_organization(task)
            elif data_type == 'crawl4ai_result':
                return await self._index_crawl4ai_result(task)
            elif data_type == 'rss_feed_result':
                return await self._index_rss_feed_result(task)
            else:
                return ProcessingResult(
                    task_id=task.id,
                    stage=PipelineStage.INDEXING,
                    success=False,
                    error=f"Unsupported data type for indexing: {data_type}"
                )
        
        except Exception as e:
            self.logger.error(f"Error in vector indexing: {e}")
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
    
    async def _index_intelligence_item(self, task: ETLTask) -> ProcessingResult:
        """Index a intelligence item in the vector database"""
        opportunity_data = task.payload.get('opportunity')
        
        if not opportunity_data:
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error="No opportunity data provided"
            )
            
        try:
            # Generate a unique ID for the opportunity
            opportunity_id = opportunity_data.get('id')
            vector_id = f"opportunity_{opportunity_id}"
            
            # Prepare content for vector embedding
            content = self._prepare_opportunity_content(opportunity_data)
            
            # Prepare metadata with equity-aware fields
            metadata = self._prepare_opportunity_metadata(opportunity_data)
            
            # Upsert with text field for hosted embedding
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "metadata": metadata
                }],
                namespace=VectorIndexType.OPPORTUNITIES.value,
                use_hosted_model=True,  # Use Microsoft's multilingual-e5-large model
                host_text=content  # Text to embed
            )
            
            self.logger.info(f"Indexed opportunity {opportunity_id} successfully")
            
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=True,
                data={
                    'vector_id': vector_id,
                    'namespace': VectorIndexType.OPPORTUNITIES.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to index opportunity: {e}")
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
    
    async def _index_organization(self, task: ETLTask) -> ProcessingResult:
        """Index an organization in the vector database"""
        organization_data = task.payload.get('organization')
        
        if not organization_data:
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error="No organization data provided"
            )
            
        try:
            # Generate a unique ID for the organization
            organization_id = organization_data.get('id')
            vector_id = f"organization_{organization_id}"
            
            # Prepare content for vector embedding
            content = self._prepare_organization_content(organization_data)
            
            # Prepare metadata with organization-specific fields
            metadata = {
                'organization_id': organization_id,
                'name': organization_data.get('name', ''),
                'role': organization_data.get('role', ''),
                'provider_type': organization_data.get('provider_type', ''),
                'recipient_type': organization_data.get('recipient_type', ''),
                'startup_stage': organization_data.get('startup_stage', ''),
                'country_code': organization_data.get('country_code', ''),
                'region': organization_data.get('region', '')
            }
            
            # Upsert with text field for hosted embedding
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "metadata": metadata
                }],
                namespace=VectorIndexType.ORGANIZATIONS.value,
                use_hosted_model=True,
                host_text=content
            )
            
            self.logger.info(f"Indexed organization {organization_id} successfully")
            
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=True,
                data={
                    'vector_id': vector_id,
                    'namespace': VectorIndexType.ORGANIZATIONS.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to index organization: {e}")
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
    
    async def _index_rss_feed_result(self, task: ETLTask) -> ProcessingResult:
        """Process and index RSS feed results with streamlined validation"""
        rss_result = task.payload.get('data', {})
        opportunities = rss_result.get('opportunities', [])
        feed_url = rss_result.get('feed_url')
        feed_id = rss_result.get('feed_id')
        
        if not opportunities:
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=f"No opportunities found in RSS feed result: {feed_url}"
            )
            
        try:
            success_count = 0
            failed_ids = []
            
            for opportunity in opportunities:
                # Generate a unique ID for the opportunity
                source_id = opportunity.get('source_id') or feed_id
                vector_id = f"rss_{source_id}_{datetime.now().timestamp()}"
                
                # Extract content for embedding with minimal processing (trusted source)
                title = opportunity.get('title', 'No title')
                description = opportunity.get('description', 'No description')
                link = opportunity.get('link', '')
                published_date = opportunity.get('published_date', '')
                
                # Get extracted data if available
                extracted_data = opportunity.get('extracted_data', {})
                
                # Create rich content for embedding
                content_parts = [
                    f"Title: {title}",
                    f"Description: {description}",
                    f"Source: {link}",
                    f"Published: {published_date}",
                    f"Feed: {feed_url}",
                ]
                
                # Add organization information if available
                provider_org = extracted_data.get('provider_organization_name')
                if provider_org:
                    content_parts.append(f"Provider Organization: {provider_org}")
                    
                    provider_type = extracted_data.get('provider_type')
                    if provider_type:
                        content_parts.append(f"Provider Type: {provider_type}")
                
                recipient_org = extracted_data.get('recipient_organization_name')
                if recipient_org:
                    content_parts.append(f"Recipient Organization: {recipient_org}")
                    
                    recipient_type = extracted_data.get('recipient_type')
                    if recipient_type:
                        content_parts.append(f"Recipient Type: {recipient_type}")
                        
                    startup_stage = extracted_data.get('startup_stage')
                    if startup_stage:
                        content_parts.append(f"Startup Stage: {startup_stage}")
                
                # Add funding details if available
                funding_amount = extracted_data.get('funding_amount')
                if funding_amount:
                    content_parts.append(f"Funding Amount: {funding_amount}")
                
                deadline = extracted_data.get('deadline')
                if deadline:
                    content_parts.append(f"Deadline: {deadline}")
                
                # Add geographic and domain focus
                geo_focus = extracted_data.get('geographic_focus')
                if geo_focus:
                    if isinstance(geo_focus, list):
                        geo_focus_str = ", ".join(geo_focus)
                    else:
                        geo_focus_str = str(geo_focus)
                    content_parts.append(f"Geographic Focus: {geo_focus_str}")
                
                ai_focus = extracted_data.get('ai_focus')
                if ai_focus:
                    if isinstance(ai_focus, list):
                        ai_focus_str = ", ".join(ai_focus)
                    else:
                        ai_focus_str = str(ai_focus)
                    content_parts.append(f"AI Focus: {ai_focus_str}")
                
                content = "\n".join(content_parts)
                
                # Prepare metadata - for RSS, we set higher confidence and require less review
                metadata = {
                    'title': title[:100],
                    'source_type': 'rss',
                    'source_id': source_id,
                    'feed_id': feed_id,
                    'link': link,
                    'confidence_score': str(opportunity.get('confidence_score', 0.85)),  # Higher default confidence for RSS
                    'requires_review': False,  # Trusted sources need less review
                    'extraction_method': 'rss_feed',
                    'content_type': 'intelligence_item',
                    'published_date': published_date
                }
                
                # Add organization role information if available
                if 'provider_organization_id' in extracted_data:
                    metadata['provider_organization_id'] = str(extracted_data['provider_organization_id'])
                    
                if 'provider_type' in extracted_data:
                    metadata['provider_type'] = extracted_data['provider_type']  # granting_agency, venture_capital, etc.
                    
                if 'recipient_organization_id' in extracted_data:
                    metadata['recipient_organization_id'] = str(extracted_data['recipient_organization_id'])
                    
                if 'recipient_type' in extracted_data:
                    metadata['recipient_type'] = extracted_data['recipient_type']  # grantee, startup, etc.
                    
                # Add startup stage if applicable
                if 'startup_stage' in extracted_data:
                    metadata['startup_stage'] = extracted_data['startup_stage']
                
                # Add funding category if available
                funding_type = extracted_data.get('funding_type')
                if funding_type:
                    metadata['funding_category'] = funding_type
                
                # Add geographic focus
                if geo_focus:
                    if isinstance(geo_focus, list):
                        metadata['geographic_scopes'] = ",".join(geo_focus)
                    else:
                        metadata['geographic_scopes'] = str(geo_focus)
                
                # Add AI domains
                if ai_focus:
                    if isinstance(ai_focus, list):
                        metadata['ai_domains'] = ",".join(ai_focus)
                    else:
                        metadata['ai_domains'] = str(ai_focus)
                
                try:
                    # Upsert with text field for hosted embedding
                    self.index.upsert(
                        vectors=[{
                            "id": vector_id,
                            "metadata": metadata
                        }],
                        namespace=VectorIndexType.OPPORTUNITIES.value,
                        use_hosted_model=True,
                        host_text=content
                    )
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to index RSS opportunity {source_id}: {e}")
                    failed_ids.append(source_id)
            
            self.logger.info(f"Indexed {success_count}/{len(opportunities)} RSS feed opportunities from {feed_url}")
            
            # Return results
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=success_count > 0,
                data={
                    'indexed_count': success_count,
                    'total_count': len(opportunities),
                    'failed_ids': failed_ids,
                    'namespace': VectorIndexType.OPPORTUNITIES.value,
                    'feed_url': feed_url
                },
                error=f"Failed to index {len(failed_ids)} opportunities" if failed_ids else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process RSS feed results from {feed_url}: {e}")
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
    
    async def _index_crawl4ai_result(self, task: ETLTask) -> ProcessingResult:
        """Process and index crawl4ai extraction results"""
        crawl_result = task.payload.get('data', {})
        opportunities = crawl_result.get('opportunities', [])
        
        if not opportunities:
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error="No opportunities found in crawl4ai result"
            )
            
        try:
            success_count = 0
            failed_ids = []
            
            for opportunity in opportunities:
                # Generate a temp ID if not available
                opportunity_id = opportunity.get('source_id') or f"temp_{datetime.now().timestamp()}"
                vector_id = f"crawl4ai_{opportunity_id}"
                
                # Extract content for embedding
                extracted_data = opportunity.get('extracted_data', {})
                
                # Create rich content for embedding
                content_parts = [
                    f"Title: {opportunity.get('title', 'No title')}",
                    f"Description: {opportunity.get('description', 'No description')}",
                    f"Source: {opportunity.get('link', 'Unknown source')}",
                ]
                
                # Add funding details if available
                funding_amount = extracted_data.get('funding_amount')
                if funding_amount:
                    content_parts.append(f"Funding Amount: {funding_amount}")
                
                deadline = extracted_data.get('deadline')
                if deadline:
                    content_parts.append(f"Deadline: {deadline}")
                
                # Add geographic and domain focus
                geo_focus = extracted_data.get('geographic_focus', [])
                if geo_focus:
                    if isinstance(geo_focus, list):
                        geo_focus_str = ", ".join(geo_focus)
                    else:
                        geo_focus_str = str(geo_focus)
                    content_parts.append(f"Geographic Focus: {geo_focus_str}")
                
                ai_focus = extracted_data.get('ai_focus', [])
                if ai_focus:
                    if isinstance(ai_focus, list):
                        ai_focus_str = ", ".join(ai_focus)
                    else:
                        ai_focus_str = str(ai_focus)
                    content_parts.append(f"AI Focus: {ai_focus_str}")
                
                # Add application details
                app_details = extracted_data.get('application_details')
                if app_details:
                    content_parts.append(f"Application Details: {app_details}")
                
                content = "\n".join(content_parts)
                
                # Prepare metadata
                metadata = {
                    'title': opportunity.get('title', '')[:100],
                    'source_type': opportunity.get('source_type', 'crawl4ai'),
                    'source_id': opportunity_id,
                    'link': opportunity.get('link', ''),
                    'confidence_score': str(opportunity.get('confidence_score', 0)),
                    'requires_review': opportunity.get('requires_review', True),
                    'extraction_method': opportunity.get('extraction_method', 'crawl4ai'),
                    'content_type': 'intelligence_item',
                }
                
                # Add funding category if available
                funding_type = extracted_data.get('funding_type')
                if funding_type:
                    metadata['funding_category'] = funding_type
                
                # Add geographic focus
                if geo_focus:
                    if isinstance(geo_focus, list):
                        metadata['geographic_scopes'] = ",".join(geo_focus)
                    else:
                        metadata['geographic_scopes'] = str(geo_focus)
                
                # Add AI domains
                if ai_focus:
                    if isinstance(ai_focus, list):
                        metadata['ai_domains'] = ",".join(ai_focus)
                    else:
                        metadata['ai_domains'] = str(ai_focus)
                
                # Add equity-aware indicators if available
                for indicator in ["underserved_focus", "women_focus", "youth_focus"]:
                    if indicator in extracted_data:
                        metadata[indicator] = bool(extracted_data[indicator])
                
                try:
                    # Upsert with text field for hosted embedding
                    self.index.upsert(
                        vectors=[{
                            "id": vector_id,
                            "metadata": metadata
                        }],
                        namespace=VectorIndexType.OPPORTUNITIES.value,
                        use_hosted_model=True,
                        host_text=content
                    )
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to index crawl4ai opportunity {opportunity_id}: {e}")
                    failed_ids.append(opportunity_id)
            
            self.logger.info(f"Indexed {success_count}/{len(opportunities)} crawl4ai opportunities")
            
            # Return results
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=success_count > 0,
                data={
                    'indexed_count': success_count,
                    'total_count': len(opportunities),
                    'failed_ids': failed_ids,
                    'namespace': VectorIndexType.OPPORTUNITIES.value
                },
                error=f"Failed to index {len(failed_ids)} opportunities" if failed_ids else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process crawl4ai results: {e}")
            return ProcessingResult(
                task_id=task.id,
                stage=PipelineStage.INDEXING,
                success=False,
                error=str(e)
            )
    
    def _prepare_opportunity_content(self, opportunity_data: Dict[str, Any]) -> str:
        """Prepare opportunity content for embedding with multilingual support"""
        content_parts = [
            f"Title: {opportunity_data.get('title', 'No title')}",
            f"Description: {opportunity_data.get('description', 'No description')}"
        ]
        
        # Add organization if available
        organization_name = opportunity_data.get('organization_name')
        if organization_name:
            content_parts.append(f"Organization: {organization_name}")
        
        # Add funding details
        funding_amount = opportunity_data.get('funding_amount')
        if funding_amount:
            content_parts.append(f"Amount: {funding_amount}")
            
        currency = opportunity_data.get('currency')
        if currency:
            content_parts.append(f"Currency: {currency}")
            
        funding_type = opportunity_data.get('funding_category')
        if funding_type:
            content_parts.append(f"Type: {funding_type}")
            
        deadline = opportunity_data.get('deadline')
        if deadline:
            content_parts.append(f"Deadline: {deadline}")
            
        status = opportunity_data.get('status')
        if status:
            content_parts.append(f"Status: {status}")
        
        # Add geographic and domain information
        geographic_scopes = opportunity_data.get('geographic_scope_names')
        if geographic_scopes:
            if isinstance(geographic_scopes, list):
                content_parts.append(f"Geographic Scope: {', '.join(geographic_scopes)}")
            else:
                content_parts.append(f"Geographic Scope: {geographic_scopes}")
        
        ai_domains = opportunity_data.get('ai_domain_names')
        if ai_domains:
            if isinstance(ai_domains, list):
                content_parts.append(f"AI Domains: {', '.join(ai_domains)}")
            else:
                content_parts.append(f"AI Domains: {ai_domains}")
        
        # Add equity-awareness indicators
        for indicator in ["underserved_focus", "women_focus", "youth_focus"]:
            if opportunity_data.get(indicator):
                content_parts.append(f"{indicator.replace('_', ' ').title()}: Yes")
        
        # Add grant-specific information
        if opportunity_data.get('is_grant'):
            grant_props = opportunity_data.get('grant_properties', {}) or {}
            if grant_props:
                duration = grant_props.get('duration_months')
                if duration:
                    content_parts.append(f"Grant Duration: {duration} months")
                
                renewable = grant_props.get('renewable')
                if renewable is not None:
                    content_parts.append(f"Renewable: {'Yes' if renewable else 'No'}")
                
                reporting = grant_props.get('reporting_requirements')
                if reporting:
                    content_parts.append(f"Reporting Required: {reporting}")
        
        # Add investment-specific information
        if opportunity_data.get('is_investment'):
            investment_props = opportunity_data.get('investment_properties', {}) or {}
            if investment_props:
                equity = investment_props.get('equity_percentage')
                if equity:
                    content_parts.append(f"Equity Required: {equity}%")
                
                roi = investment_props.get('expected_roi')
                if roi:
                    content_parts.append(f"Expected ROI: {roi}%")
                
                valuation = investment_props.get('valuation_cap')
                if valuation:
                    content_parts.append(f"Valuation Cap: {valuation}")
                
                interest = investment_props.get('interest_rate')
                if interest:
                    content_parts.append(f"Interest Rate: {interest}%")
        
        return "\n".join(content_parts)
    
    def _prepare_opportunity_metadata(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for opportunity with enhanced equity-aware fields"""
        metadata = {
            'opportunity_id': str(opportunity_data.get('id', '')),
            'title': opportunity_data.get('title', '')[:100],  # Truncate long titles
            'organization_name': opportunity_data.get('organization_name', '')[:100],
            'funding_amount': str(opportunity_data.get('funding_amount', '')),
            'currency': opportunity_data.get('currency', 'USD'),
            'status': opportunity_data.get('status', 'unknown'),
            'content_type': 'intelligence_item',
        }
        
        # Add organization role information
        if 'provider_organization_id' in opportunity_data:
            metadata['provider_organization_id'] = str(opportunity_data['provider_organization_id'])
            
        if 'provider_organization_name' in opportunity_data:
            metadata['provider_organization_name'] = opportunity_data['provider_organization_name'][:100]
        
        provider_type = opportunity_data.get('provider_type')
        if provider_type:
            metadata['provider_type'] = provider_type  # granting_agency, venture_capital, etc.
        
        if 'recipient_organization_id' in opportunity_data:
            metadata['recipient_organization_id'] = str(opportunity_data['recipient_organization_id'])
            
        if 'recipient_organization_name' in opportunity_data:
            metadata['recipient_organization_name'] = opportunity_data['recipient_organization_name'][:100]
            
        recipient_type = opportunity_data.get('recipient_type')
        if recipient_type:
            metadata['recipient_type'] = recipient_type  # grantee, startup, etc.
            
        startup_stage = opportunity_data.get('startup_stage')
        if startup_stage:
            metadata['startup_stage'] = startup_stage
        
        # Add deadline if available
        deadline = opportunity_data.get('deadline')
        if deadline:
            try:
                if isinstance(deadline, datetime):
                    metadata['deadline'] = deadline.isoformat()
                else:
                    metadata['deadline'] = str(deadline)
            except Exception:
                metadata['deadline'] = str(deadline)
        
        # Add funding type information
        funding_category = opportunity_data.get('funding_category')
        if funding_category:
            metadata['funding_category'] = funding_category
            
        if opportunity_data.get('is_grant') is not None:
            metadata['is_grant'] = opportunity_data.get('is_grant')
            
            # Add grant-specific properties if it's a grant
            if opportunity_data.get('is_grant'):
                grant_props = opportunity_data.get('grant_properties', {}) or {}
                if grant_props:
                    if 'duration_months' in grant_props:
                        metadata['grant_duration_months'] = str(grant_props.get('duration_months'))
                    if 'renewable' in grant_props:
                        metadata['grant_renewable'] = bool(grant_props.get('renewable'))
                    if 'reporting_requirements' in grant_props:
                        metadata['grant_reporting'] = grant_props.get('reporting_requirements')
            
        if opportunity_data.get('is_investment') is not None:
            metadata['is_investment'] = opportunity_data.get('is_investment')
            
            # Add investment-specific properties if it's an investment
            if opportunity_data.get('is_investment'):
                investment_props = opportunity_data.get('investment_properties', {}) or {}
                if investment_props:
                    if 'equity_percentage' in investment_props:
                        metadata['equity_percentage'] = str(investment_props.get('equity_percentage'))
                    if 'valuation_cap' in investment_props:
                        metadata['valuation_cap'] = str(investment_props.get('valuation_cap'))
                    if 'interest_rate' in investment_props:
                        metadata['interest_rate'] = str(investment_props.get('interest_rate'))
                    if 'expected_roi' in investment_props:
                        metadata['expected_roi'] = str(investment_props.get('expected_roi'))
            
        # Add geographic and domain information as strings (Pinecone requirement)
        geographic_scopes = opportunity_data.get('geographic_scope_names')
        if geographic_scopes:
            if isinstance(geographic_scopes, list):
                metadata['geographic_scopes'] = ",".join(geographic_scopes)
            else:
                metadata['geographic_scopes'] = str(geographic_scopes)
            
        ai_domains = opportunity_data.get('ai_domain_names')
        if ai_domains:
            if isinstance(ai_domains, list):
                metadata['ai_domains'] = ",".join(ai_domains)
            else:
                metadata['ai_domains'] = str(ai_domains)
            
        # Add equity-awareness indicators
        for indicator in ["underserved_focus", "women_focus", "youth_focus"]:
            if indicator in opportunity_data:
                metadata[indicator] = bool(opportunity_data[indicator])
                
        # Add organization relationships if available
        if 'provider_organization_id' in opportunity_data:
            metadata['provider_organization_id'] = str(opportunity_data['provider_organization_id'])
            
        if 'recipient_organization_id' in opportunity_data:
            metadata['recipient_organization_id'] = str(opportunity_data['recipient_organization_id'])
            
        # Add funding stage if available
        if 'funding_stage' in opportunity_data:
            metadata['funding_stage'] = opportunity_data['funding_stage']
            
        return metadata
        
    def _prepare_organization_content(self, organization_data: Dict[str, Any]) -> str:
        """Prepare organization content for embedding"""
        content_parts = [
            f"Name: {organization_data.get('name', 'No name')}",
            f"Description: {organization_data.get('description', 'No description')}"
        ]
        
        # Add role information
        role = organization_data.get('role')
        if role:
            content_parts.append(f"Role: {role}")  # provider, recipient, both
            
        # Add provider-specific information
        provider_type = organization_data.get('provider_type')
        if provider_type:
            content_parts.append(f"Provider Type: {provider_type}")  # granting_agency, venture_capital, etc.
            
        # Add recipient-specific information
        recipient_type = organization_data.get('recipient_type')
        if recipient_type:
            content_parts.append(f"Recipient Type: {recipient_type}")  # grantee, startup, etc.
            
        # Add startup stage if available
        startup_stage = organization_data.get('startup_stage')
        if startup_stage:
            content_parts.append(f"Startup Stage: {startup_stage}")
            
        # Add geographic information
        country_name = organization_data.get('country_name')
        if country_name:
            content_parts.append(f"Country: {country_name}")
            
        region = organization_data.get('region')
        if region:
            content_parts.append(f"Region: {region}")
            
        return "\n".join(content_parts)

# Create a singleton instance
vector_indexing_service = VectorIndexingService()

# Function to integrate with the ETL pipeline
async def add_to_indexing_queue(data: Dict[str, Any], data_type: str, priority: Priority = Priority.MEDIUM):
    """Add data to the vector indexing queue"""
    from .etl_architecture import ETLTask, PipelineStage
    
    task_id = f"idx_{data_type}_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,
        created_at=datetime.now(),
        payload={
            'data_type': data_type,
            data_type: data
        }
    )
    
    # Here you would typically add to your queue
    # For direct processing (no queue):
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result

# Specialized function to integrate with crawl4ai results
async def index_crawl4ai_results(crawl_results: Dict[str, Any], priority: Priority = Priority.MEDIUM):
    """Index crawl4ai results directly"""
    task_id = f"idx_crawl4ai_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,
        created_at=datetime.now(),
        payload={
            'data_type': 'crawl4ai_result',
            'data': crawl_results
        }
    )
    
    # Initialize if needed
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Process directly
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result

# Specialized function for RSS feed results
async def index_rss_feed_results(rss_results: Dict[str, Any], priority: Priority = Priority.HIGH):
    """Index RSS feed results directly with streamlined validation
    
    Since RSS feeds come from known funders, we apply minimal validation and higher priority.
    """
    task_id = f"idx_rss_{datetime.now().timestamp()}"
    
    indexing_task = ETLTask(
        id=task_id,
        stage=PipelineStage.INDEXING,
        priority=priority,  # Higher priority for trusted sources
        created_at=datetime.now(),
        payload={
            'data_type': 'rss_feed_result',
            'data': rss_results
        }
    )
    
    # Initialize if needed
    if not vector_indexing_service.initialized:
        await vector_indexing_service.initialize()
    
    # Process directly
    result = await vector_indexing_service.process_indexing_task(indexing_task)
    return result
