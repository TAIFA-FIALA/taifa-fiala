"""
External Source Indexing Methods
================================

Specialized indexing methods for external data sources like Crawl4AI and RSS feeds,
with enhanced support for grant/investment type distinctions and organization roles.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from .indexing_service import VectorIndexingService
from .pinecone_config import VectorIndexType
from ..etl_architecture import ETLTask, ProcessingResult, PipelineStage, Priority

logger = logging.getLogger(__name__)

async def _index_crawl4ai_result(self, task: ETLTask) -> ProcessingResult:
    """Process and index results from Crawl4AI extraction"""
    crawl_result = task.payload.get('data', {})
    opportunities = crawl_result.get('opportunities', [])
    url = crawl_result.get('url', '')
    
    if not opportunities:
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error=f"No opportunities found in Crawl4AI result: {url}"
        )
        
    try:
        success_count = 0
        failed_ids = []
        
        for opportunity in opportunities:
            # Generate a unique ID for the opportunity
            source_id = opportunity.get('source_id', '')
            vector_id = f"crawl4ai_{source_id}_{datetime.now().timestamp()}"
            
            # Extract content for embedding
            title = opportunity.get('title', 'No title')
            description = opportunity.get('description', 'No description')
            link = opportunity.get('link', url)
            
            # Get extracted data if available
            extracted_data = opportunity.get('extracted_data', {})
            
            # Create rich content for embedding with funding type distinctions
            content_parts = [
                f"Title: {title}",
                f"Description: {description}",
                f"Source: {link}"
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
            
            # Add funding details
            funding_amount = extracted_data.get('funding_amount')
            if funding_amount:
                content_parts.append(f"Funding Amount: {funding_amount}")
            
            deadline = extracted_data.get('deadline')
            if deadline:
                content_parts.append(f"Deadline: {deadline}")
                
            # Add funding type/category information
            funding_type = extracted_data.get('funding_type')
            if funding_type:
                content_parts.append(f"Funding Type: {funding_type}")
            
            # Add grant-specific details if applicable
            is_grant = extracted_data.get('is_grant')
            if is_grant:
                content_parts.append("Funding Category: Grant")
                
                grant_props = extracted_data.get('grant_properties', {})
                if grant_props:
                    duration = grant_props.get('duration_months')
                    if duration:
                        content_parts.append(f"Grant Duration: {duration} months")
                        
                    renewable = grant_props.get('renewable')
                    if renewable is not None:
                        content_parts.append(f"Renewable: {'Yes' if renewable else 'No'}")
                        
                    reporting = grant_props.get('reporting_requirements')
                    if reporting:
                        content_parts.append(f"Reporting Requirements: {reporting}")
            
            # Add investment-specific details if applicable
            is_investment = extracted_data.get('is_investment')
            if is_investment:
                content_parts.append("Funding Category: Investment")
                
                investment_props = extracted_data.get('investment_properties', {})
                if investment_props:
                    equity = investment_props.get('equity_percentage')
                    if equity:
                        content_parts.append(f"Equity Percentage: {equity}%")
                        
                    valuation = investment_props.get('valuation_cap')
                    if valuation:
                        content_parts.append(f"Valuation Cap: {valuation}")
                        
                    interest = investment_props.get('interest_rate')
                    if interest:
                        content_parts.append(f"Interest Rate: {interest}%")
            
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
            
            # Prepare metadata with organization roles and funding type distinctions
            metadata = {
                'title': title[:100],
                'source_type': 'crawl4ai',
                'source_id': source_id,
                'url': link,
                'confidence_score': str(opportunity.get('confidence_score', 0.7)),
                'requires_review': opportunity.get('requires_review', True),
                'extraction_method': 'crawl4ai',
                'content_type': 'funding_opportunity'
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
            
            # Add funding type/category
            if funding_type:
                metadata['funding_category'] = funding_type
                
            # Add grant-specific properties if applicable
            if is_grant:
                metadata['is_grant'] = True
                
                grant_props = extracted_data.get('grant_properties', {})
                if grant_props:
                    if 'duration_months' in grant_props:
                        metadata['grant_duration_months'] = str(grant_props.get('duration_months'))
                    if 'renewable' in grant_props:
                        metadata['grant_renewable'] = str(grant_props.get('renewable')).lower()
                    if 'reporting_requirements' in grant_props:
                        metadata['grant_reporting'] = str(grant_props.get('reporting_requirements'))
            
            # Add investment-specific properties if applicable
            if is_investment:
                metadata['is_investment'] = True
                
                investment_props = extracted_data.get('investment_properties', {})
                if investment_props:
                    if 'equity_percentage' in investment_props:
                        metadata['equity_percentage'] = str(investment_props.get('equity_percentage'))
                    if 'valuation_cap' in investment_props:
                        metadata['valuation_cap'] = str(investment_props.get('valuation_cap'))
                    if 'interest_rate' in investment_props:
                        metadata['interest_rate'] = str(investment_props.get('interest_rate'))
            
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
                self.logger.error(f"Failed to index Crawl4AI opportunity {source_id}: {e}")
                failed_ids.append(source_id)
        
        self.logger.info(f"Indexed {success_count}/{len(opportunities)} Crawl4AI opportunities from {url}")
        
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
                'url': url
            }
        )
    except Exception as e:
        self.logger.error(f"Crawl4AI indexing error: {e}")
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error=f"Failed to index Crawl4AI results: {e}"
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
            
            # Create rich content for embedding with organization roles and funding type distinctions
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
            
            # Add funding details
            funding_amount = extracted_data.get('funding_amount')
            if funding_amount:
                content_parts.append(f"Funding Amount: {funding_amount}")
            
            deadline = extracted_data.get('deadline')
            if deadline:
                content_parts.append(f"Deadline: {deadline}")
                
            # Add funding type/category information
            funding_type = extracted_data.get('funding_type')
            if funding_type:
                content_parts.append(f"Funding Type: {funding_type}")
            
            # Add grant-specific details if applicable
            is_grant = extracted_data.get('is_grant')
            if is_grant:
                content_parts.append("Funding Category: Grant")
                
                grant_props = extracted_data.get('grant_properties', {})
                if grant_props:
                    duration = grant_props.get('duration_months')
                    if duration:
                        content_parts.append(f"Grant Duration: {duration} months")
                        
                    renewable = grant_props.get('renewable')
                    if renewable is not None:
                        content_parts.append(f"Renewable: {'Yes' if renewable else 'No'}")
                        
                    reporting = grant_props.get('reporting_requirements')
                    if reporting:
                        content_parts.append(f"Reporting Requirements: {reporting}")
            
            # Add investment-specific details if applicable
            is_investment = extracted_data.get('is_investment')
            if is_investment:
                content_parts.append("Funding Category: Investment")
                
                investment_props = extracted_data.get('investment_properties', {})
                if investment_props:
                    equity = investment_props.get('equity_percentage')
                    if equity:
                        content_parts.append(f"Equity Percentage: {equity}%")
                        
                    valuation = investment_props.get('valuation_cap')
                    if valuation:
                        content_parts.append(f"Valuation Cap: {valuation}")
                        
                    interest = investment_props.get('interest_rate')
                    if interest:
                        content_parts.append(f"Interest Rate: {interest}%")
            
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
                'content_type': 'funding_opportunity',
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
            
            # Add funding type/category
            if funding_type:
                metadata['funding_category'] = funding_type
                
            # Add grant-specific properties if applicable
            if is_grant:
                metadata['is_grant'] = True
                
                grant_props = extracted_data.get('grant_properties', {})
                if grant_props:
                    if 'duration_months' in grant_props:
                        metadata['grant_duration_months'] = str(grant_props.get('duration_months'))
                    if 'renewable' in grant_props:
                        metadata['grant_renewable'] = str(grant_props.get('renewable')).lower()
                    if 'reporting_requirements' in grant_props:
                        metadata['grant_reporting'] = str(grant_props.get('reporting_requirements'))
            
            # Add investment-specific properties if applicable
            if is_investment:
                metadata['is_investment'] = True
                
                investment_props = extracted_data.get('investment_properties', {})
                if investment_props:
                    if 'equity_percentage' in investment_props:
                        metadata['equity_percentage'] = str(investment_props.get('equity_percentage'))
                    if 'valuation_cap' in investment_props:
                        metadata['valuation_cap'] = str(investment_props.get('valuation_cap'))
                    if 'interest_rate' in investment_props:
                        metadata['interest_rate'] = str(investment_props.get('interest_rate'))
                    if 'expected_roi' in investment_props:
                        metadata['expected_roi'] = str(investment_props.get('expected_roi'))
            
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
            }
        )
    except Exception as e:
        self.logger.error(f"RSS indexing error: {e}")
        return ProcessingResult(
            task_id=task.id,
            stage=PipelineStage.INDEXING,
            success=False,
            error=f"Failed to index RSS feed results: {e}"
        )

# Add methods to VectorIndexingService class
VectorIndexingService._index_crawl4ai_result = _index_crawl4ai_result
VectorIndexingService._index_rss_feed_result = _index_rss_feed_result
