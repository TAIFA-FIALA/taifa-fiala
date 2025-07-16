"""
Organization Enrichment Pipeline

A comprehensive pipeline for enriching organization profiles with cultural context,
impact metrics, and respectful showcase information for African AI funding organizations.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.organization import Organization
from app.models.validation import ProcessingJob
from app.core.logging import logger
from app.core.config import settings
from app.services.organization_mention_parser import OrganizationMentionParser


class OrganizationEnrichmentPipeline:
    """
    Multi-source enrichment pipeline for organization profiles with emphasis on
    cultural context and respectful representation of African funding organizations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.session = None
        self.data_sources = self._configure_data_sources()
    
    def _configure_data_sources(self) -> Dict:
        """Configure data sources for organization enrichment"""
        return {
            'company_registries': {
                'south_africa': 'https://cipc.co.za/index.php/contact-us/',
                'nigeria': 'https://www.cac.gov.ng/',
                'kenya': 'https://www.attorney-general.go.ke/',
                'ghana': 'https://www.registrargeneral.gov.gh/',
                'egypt': 'https://www.gafi.gov.eg/'
            },
            'academic_sources': {
                'african_journals': 'https://www.ajol.info/',
                'codesria': 'https://www.codesria.org/',
                'african_academy_sciences': 'https://www.aasciences.africa/',
                'university_world_news': 'https://www.universityworldnews.com/region.php?region=Africa'
            },
            'business_directories': {
                'africa_business_portal': 'https://www.africabusinessportal.com/',
                'african_development_bank': 'https://www.afdb.org/',
                'invest_africa': 'https://www.investafrica.com/'
            },
            'media_sources': {
                'techcabal': 'https://techcabal.com/',
                'disrupt_africa': 'https://disrupt-africa.com/',
                'ventures_africa': 'https://venturesafrica.com/',
                'african_business': 'https://african.business/'
            },
            'social_media': {
                'linkedin_company_api': 'https://api.linkedin.com/v2/companies',
                'twitter_api': 'https://api.twitter.com/2/users/by/username'
            }
        }
    
    async def enrich_organization(self, organization: Organization, force_refresh: bool = False) -> Dict:
        """
        Enrich a single organization with comprehensive data.
        
        Args:
            organization: Organization instance to enrich
            force_refresh: Whether to force refresh even if recently enriched
            
        Returns:
            Enrichment results dictionary
        """
        try:
            # Check if enrichment needed
            if not force_refresh and not organization.needs_enrichment:
                return {
                    'organization_id': organization.id,
                    'status': 'skipped',
                    'reason': 'recently_enriched',
                    'enrichment_completeness': organization.enrichment_completeness
                }
            
            # Update status
            organization.enrichment_status = 'in_progress'
            organization.last_enrichment_attempt = datetime.utcnow()
            self.db.commit()
            
            # Track enrichment job
            job = ProcessingJob(
                job_type='organization_enrichment',
                status='running',
                metadata=json.dumps({
                    'organization_id': organization.id,
                    'organization_name': organization.name,
                    'started_at': datetime.utcnow().isoformat()
                })
            )
            self.db.add(job)
            self.db.commit()
            
            # Start enrichment process
            enrichment_data = await self._gather_enrichment_data(organization)
            
            # Process and validate data
            processed_data = await self._process_enrichment_data(enrichment_data, organization)
            
            # Update organization with enriched data
            updated_org = await self._update_organization_with_enrichment(organization, processed_data)
            
            # Calculate final completeness score
            completeness_score = self._calculate_completeness_score(updated_org)
            
            # Update enrichment status
            updated_org.enrichment_completeness = completeness_score
            updated_org.enrichment_status = 'completed'
            updated_org.enrichment_sources = json.dumps(list(enrichment_data.keys()))
            
            # Update job status
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.metadata = json.dumps({
                'organization_id': organization.id,
                'organization_name': organization.name,
                'completeness_score': completeness_score,
                'data_sources_used': list(enrichment_data.keys()),
                'completed_at': datetime.utcnow().isoformat()
            })
            
            self.db.commit()
            
            logger.info(f"Successfully enriched organization {organization.name} "
                       f"(ID: {organization.id}) - completeness: {completeness_score}%")
            
            return {
                'organization_id': organization.id,
                'status': 'completed',
                'completeness_score': completeness_score,
                'data_sources_used': list(enrichment_data.keys()),
                'enrichment_summary': self._generate_enrichment_summary(processed_data)
            }
            
        except Exception as e:
            logger.error(f"Error enriching organization {organization.id}: {str(e)}")
            
            # Update status to failed
            organization.enrichment_status = 'failed'
            if 'job' in locals():
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                'organization_id': organization.id,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _gather_enrichment_data(self, organization: Organization) -> Dict:
        """Gather data from multiple sources for organization enrichment"""
        enrichment_data = {}
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Basic profile enrichment
            enrichment_data['basic_profile'] = await self._enrich_basic_profile(organization)
            
            # Cultural context enrichment
            enrichment_data['cultural_context'] = await self._enrich_cultural_context(organization)
            
            # Financial and operational context
            enrichment_data['financial_context'] = await self._enrich_financial_context(organization)
            
            # Impact metrics and stories
            enrichment_data['impact_metrics'] = await self._enrich_impact_metrics(organization)
            
            # Social media and online presence
            enrichment_data['online_presence'] = await self._enrich_online_presence(organization)
            
            # Leadership and team information
            enrichment_data['leadership'] = await self._enrich_leadership_info(organization)
            
            # Recognition and awards
            enrichment_data['recognition'] = await self._enrich_recognition_data(organization)
        
        return enrichment_data
    
    async def _enrich_basic_profile(self, organization: Organization) -> Dict:
        """Enrich basic organization profile information"""
        try:
            data = {
                'mission_statement': await self._search_mission_statement(organization),
                'vision_statement': await self._search_vision_statement(organization),
                'founding_year': await self._search_founding_year(organization),
                'headquarters_location': await self._search_headquarters(organization),
                'logo_url': await self._search_logo(organization),
                'official_website': await self._validate_website(organization.website)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching basic profile for {organization.name}: {str(e)}")
            return {}
    
    async def _enrich_cultural_context(self, organization: Organization) -> Dict:
        """Enrich cultural context and heritage information"""
        try:
            data = {
                'founding_story': await self._search_founding_story(organization),
                'cultural_significance': await self._analyze_cultural_significance(organization),
                'local_partnerships': await self._search_local_partnerships(organization),
                'community_connections': await self._search_community_connections(organization),
                'languages_supported': await self._identify_supported_languages(organization),
                'regional_focus': await self._analyze_regional_focus(organization)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching cultural context for {organization.name}: {str(e)}")
            return {}
    
    async def _enrich_financial_context(self, organization: Organization) -> Dict:
        """Enrich financial and operational context"""
        try:
            data = {
                'annual_budget_range': await self._estimate_budget_range(organization),
                'staff_size_range': await self._estimate_staff_size(organization),
                'funding_history': await self._search_funding_history(organization),
                'financial_transparency': await self._assess_financial_transparency(organization)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching financial context for {organization.name}: {str(e)}")
            return {}
    
    async def _enrich_impact_metrics(self, organization: Organization) -> Dict:
        """Enrich impact metrics and success stories"""
        try:
            data = {
                'beneficiaries_served': await self._estimate_beneficiaries(organization),
                'funding_distributed': await self._calculate_funding_distributed(organization),
                'success_stories': await self._gather_success_stories(organization),
                'impact_areas': await self._identify_impact_areas(organization),
                'sdg_alignment': await self._analyze_sdg_alignment(organization)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching impact metrics for {organization.name}: {str(e)}")
            return {}
    
    async def _enrich_online_presence(self, organization: Organization) -> Dict:
        """Enrich social media and online presence information"""
        try:
            data = {
                'linkedin_profile': await self._find_linkedin_profile(organization),
                'twitter_handle': await self._find_twitter_handle(organization),
                'facebook_page': await self._find_facebook_page(organization),
                'instagram_account': await self._find_instagram_account(organization),
                'media_mentions': await self._search_media_mentions(organization)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching online presence for {organization.name}: {str(e)}")
            return {}
    
    async def _enrich_leadership_info(self, organization: Organization) -> Dict:
        """Enrich leadership and team information"""
        try:
            data = {
                'leadership_team': await self._identify_leadership_team(organization),
                'board_members': await self._identify_board_members(organization),
                'key_personnel': await self._identify_key_personnel(organization),
                'diversity_metrics': await self._analyze_leadership_diversity(organization)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching leadership info for {organization.name}: {str(e)}")
            return {}
    
    async def _enrich_recognition_data(self, organization: Organization) -> Dict:
        """Enrich recognition and awards information"""
        try:
            data = {
                'awards_received': await self._search_awards(organization),
                'media_coverage': await self._search_media_coverage(organization),
                'industry_recognition': await self._search_industry_recognition(organization),
                'certifications': await self._search_certifications(organization)
            }
            
            return {k: v for k, v in data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error enriching recognition data for {organization.name}: {str(e)}")
            return {}
    
    async def _search_mission_statement(self, organization: Organization) -> Optional[str]:
        """Search for organization's mission statement"""
        if not organization.website:
            return None
            
        try:
            # Use web scraping to find mission statement
            search_terms = ['mission', 'about us', 'who we are', 'purpose']
            # Implementation would use web scraping or API calls
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Error searching mission statement for {organization.name}: {str(e)}")
            return None
    
    async def _search_founding_story(self, organization: Organization) -> Optional[str]:
        """Search for organization's founding story"""
        try:
            # Search news articles, press releases, and website content
            # Implementation would use web scraping, news APIs, or search engines
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Error searching founding story for {organization.name}: {str(e)}")
            return None
    
    async def _analyze_cultural_significance(self, organization: Organization) -> Optional[str]:
        """Analyze cultural significance and context"""
        try:
            # Analyze organization's role in African development context
            # Consider regional focus, cultural alignment, local impact
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Error analyzing cultural significance for {organization.name}: {str(e)}")
            return None
    
    async def _process_enrichment_data(self, enrichment_data: Dict, organization: Organization) -> Dict:
        """Process and validate enrichment data"""
        processed_data = {}
        
        for source, data in enrichment_data.items():
            if data:
                # Validate and clean data
                cleaned_data = self._clean_data(data)
                
                # Verify data quality
                if self._validate_data_quality(cleaned_data, source):
                    processed_data[source] = cleaned_data
                else:
                    logger.warning(f"Low quality data from {source} for {organization.name}")
        
        return processed_data
    
    def _clean_data(self, data: Dict) -> Dict:
        """Clean and standardize enrichment data"""
        cleaned = {}
        
        for key, value in data.items():
            if value is not None:
                # Clean strings
                if isinstance(value, str):
                    cleaned[key] = value.strip()
                # Clean lists
                elif isinstance(value, list):
                    cleaned[key] = [item.strip() if isinstance(item, str) else item for item in value]
                else:
                    cleaned[key] = value
        
        return cleaned
    
    def _validate_data_quality(self, data: Dict, source: str) -> bool:
        """Validate data quality for a specific source"""
        if not data:
            return False
        
        # Check for minimum required fields based on source
        required_fields = {
            'basic_profile': ['mission_statement', 'founding_year'],
            'cultural_context': ['founding_story', 'cultural_significance'],
            'financial_context': ['annual_budget_range'],
            'impact_metrics': ['beneficiaries_served', 'success_stories'],
            'online_presence': ['linkedin_profile', 'twitter_handle'],
            'leadership': ['leadership_team'],
            'recognition': ['awards_received']
        }
        
        if source in required_fields:
            return any(field in data for field in required_fields[source])
        
        return True
    
    async def _update_organization_with_enrichment(self, organization: Organization, processed_data: Dict) -> Organization:
        """Update organization with enriched data"""
        try:
            # Update basic profile
            if 'basic_profile' in processed_data:
                basic_data = processed_data['basic_profile']
                organization.mission_statement = basic_data.get('mission_statement', organization.mission_statement)
                organization.vision_statement = basic_data.get('vision_statement', organization.vision_statement)
                organization.established_year = basic_data.get('founding_year', organization.established_year)
                organization.logo_url = basic_data.get('logo_url', organization.logo_url)
                organization.website = basic_data.get('official_website', organization.website)
            
            # Update cultural context
            if 'cultural_context' in processed_data:
                cultural_data = processed_data['cultural_context']
                organization.founding_story = cultural_data.get('founding_story', organization.founding_story)
                organization.cultural_significance = cultural_data.get('cultural_significance', organization.cultural_significance)
                organization.local_partnerships = json.dumps(cultural_data.get('local_partnerships', []))
                organization.languages_supported = json.dumps(cultural_data.get('languages_supported', []))
            
            # Update financial context
            if 'financial_context' in processed_data:
                financial_data = processed_data['financial_context']
                organization.annual_budget_range = financial_data.get('annual_budget_range', organization.annual_budget_range)
                organization.staff_size_range = financial_data.get('staff_size_range', organization.staff_size_range)
            
            # Update impact metrics
            if 'impact_metrics' in processed_data:
                impact_data = processed_data['impact_metrics']
                organization.beneficiaries_count = impact_data.get('beneficiaries_served', organization.beneficiaries_count)
                organization.total_funding_distributed = impact_data.get('funding_distributed', organization.total_funding_distributed)
                organization.success_stories = json.dumps(impact_data.get('success_stories', []))
            
            # Update online presence
            if 'online_presence' in processed_data:
                online_data = processed_data['online_presence']
                organization.linkedin_url = online_data.get('linkedin_profile', organization.linkedin_url)
                organization.twitter_handle = online_data.get('twitter_handle', organization.twitter_handle)
                organization.facebook_url = online_data.get('facebook_page', organization.facebook_url)
                organization.instagram_url = online_data.get('instagram_account', organization.instagram_url)
            
            # Update leadership
            if 'leadership' in processed_data:
                leadership_data = processed_data['leadership']
                organization.leadership_team = json.dumps(leadership_data.get('leadership_team', []))
            
            # Update recognition
            if 'recognition' in processed_data:
                recognition_data = processed_data['recognition']
                organization.awards_recognition = json.dumps(recognition_data.get('awards_received', []))
                organization.notable_achievements = json.dumps(recognition_data.get('industry_recognition', []))
            
            self.db.commit()
            
            return organization
            
        except Exception as e:
            logger.error(f"Error updating organization with enrichment: {str(e)}")
            self.db.rollback()
            raise
    
    def _calculate_completeness_score(self, organization: Organization) -> int:
        """Calculate organization profile completeness score"""
        fields_to_check = [
            'name', 'type', 'country', 'website', 'description',
            'mission_statement', 'vision_statement', 'founding_story',
            'cultural_significance', 'local_partnerships', 'community_impact',
            'logo_url', 'leadership_team', 'notable_achievements',
            'awards_recognition', 'linkedin_url', 'twitter_handle',
            'annual_budget_range', 'staff_size_range', 'languages_supported',
            'beneficiaries_count', 'success_stories'
        ]
        
        completed_fields = 0
        
        for field in fields_to_check:
            value = getattr(organization, field, None)
            if value is not None and value != '' and value != '[]':
                completed_fields += 1
        
        return round((completed_fields / len(fields_to_check)) * 100)
    
    def _generate_enrichment_summary(self, processed_data: Dict) -> Dict:
        """Generate summary of enrichment results"""
        summary = {
            'data_sources_used': list(processed_data.keys()),
            'fields_enriched': [],
            'data_quality_scores': {}
        }
        
        for source, data in processed_data.items():
            summary['fields_enriched'].extend(data.keys())
            summary['data_quality_scores'][source] = len(data)
        
        summary['total_fields_enriched'] = len(summary['fields_enriched'])
        
        return summary
    
    async def batch_enrich_organizations(self, organization_ids: List[int] = None, 
                                       max_concurrent: int = 5) -> Dict:
        """
        Enrich multiple organizations in batch with concurrency control.
        
        Args:
            organization_ids: List of organization IDs to enrich, or None for all pending
            max_concurrent: Maximum number of concurrent enrichment processes
            
        Returns:
            Batch enrichment results
        """
        # Get organizations to enrich
        if organization_ids:
            organizations = self.db.query(Organization).filter(
                Organization.id.in_(organization_ids)
            ).all()
        else:
            organizations = self.db.query(Organization).filter(
                or_(
                    Organization.enrichment_status.in_(['pending', 'failed']),
                    Organization.enrichment_completeness < 70
                )
            ).all()
        
        results = {
            'total_organizations': len(organizations),
            'completed': 0,
            'failed': 0,
            'skipped': 0,
            'results': []
        }
        
        # Process organizations in batches with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def enrich_with_semaphore(org):
            async with semaphore:
                return await self.enrich_organization(org)
        
        # Execute enrichment tasks
        tasks = [enrich_with_semaphore(org) for org in organizations]
        enrichment_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in enrichment_results:
            if isinstance(result, Exception):
                results['failed'] += 1
                results['results'].append({
                    'status': 'failed',
                    'error': str(result)
                })
            else:
                results['results'].append(result)
                if result['status'] == 'completed':
                    results['completed'] += 1
                elif result['status'] == 'failed':
                    results['failed'] += 1
                else:
                    results['skipped'] += 1
        
        logger.info(f"Batch enrichment completed: {results['completed']} completed, "
                   f"{results['failed']} failed, {results['skipped']} skipped")
        
        return results
    
    # Placeholder methods for specific enrichment tasks
    # These would be implemented with actual web scraping, API calls, etc.
    
    async def _search_vision_statement(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _search_founding_year(self, organization: Organization) -> Optional[int]:
        return None
    
    async def _search_headquarters(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _search_logo(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _validate_website(self, website: str) -> Optional[str]:
        return website
    
    async def _search_local_partnerships(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _search_community_connections(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _identify_supported_languages(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _analyze_regional_focus(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _estimate_budget_range(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _estimate_staff_size(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _search_funding_history(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _assess_financial_transparency(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _estimate_beneficiaries(self, organization: Organization) -> Optional[int]:
        return None
    
    async def _calculate_funding_distributed(self, organization: Organization) -> Optional[float]:
        return None
    
    async def _gather_success_stories(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _identify_impact_areas(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _analyze_sdg_alignment(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _find_linkedin_profile(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _find_twitter_handle(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _find_facebook_page(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _find_instagram_account(self, organization: Organization) -> Optional[str]:
        return None
    
    async def _search_media_mentions(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _identify_leadership_team(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _identify_board_members(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _identify_key_personnel(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _analyze_leadership_diversity(self, organization: Organization) -> Optional[Dict]:
        return None
    
    async def _search_awards(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _search_media_coverage(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _search_industry_recognition(self, organization: Organization) -> Optional[List]:
        return None
    
    async def _search_certifications(self, organization: Organization) -> Optional[List]:
        return None