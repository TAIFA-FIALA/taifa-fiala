"""
Organization Mention Parser

Extracts organization mentions from funding opportunity descriptions and triggers 
enrichment pipeline for incomplete organizations.
"""
import re
import json
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.organization import Organization
from app.models.funding import FundingOpportunity
from app.core.logging import logger


class OrganizationMentionParser:
    """
    Parses funding opportunity descriptions to extract organization mentions
    and identify organizations that need enrichment.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.organization_patterns = self._compile_organization_patterns()
        self.known_organizations = self._load_known_organizations()
    
    def _compile_organization_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for identifying organization mentions"""
        patterns = [
            # Foundation patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:Foundation|Fund|Trust|Institute|Initiative))\b',
            # Government agency patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:Ministry|Department|Agency|Authority|Commission))\b',
            # University patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:University|College|Institute of Technology|School))\b',
            # Corporate patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:Corporation|Corp|Company|Ltd|Limited|Inc|Technologies|Tech))\b',
            # NGO patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:Organization|Organisation|NGO|NPO|Society|Association))\b',
            # Development organization patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:Development|Relief|Aid|International|Global|World))\b',
            # African organization patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:African|Africa|Continental|Regional|ECOWAS|SADC|EAC))\b',
            # Funding-specific patterns
            r'(?i)\b([A-Z][a-z\s&]+(?:Grant|Funding|Capital|Investment|Venture|Angels?))\b',
            # Acronym patterns (2-8 uppercase letters)
            r'\b([A-Z]{2,8})\b',
            # Quoted organization names
            r'"([^"]+(?:Foundation|Fund|Trust|Institute|Initiative|Organization|University|Corporation|Agency))"',
            r"'([^']+(?:Foundation|Fund|Trust|Institute|Initiative|Organization|University|Corporation|Agency))'"
        ]
        return [re.compile(pattern) for pattern in patterns]
    
    def _load_known_organizations(self) -> Dict[str, int]:
        """Load known organizations from database for quick lookup"""
        organizations = self.db.query(Organization).all()
        return {org.name.lower(): org.id for org in organizations}
    
    def extract_organization_mentions(self, text: str) -> List[Dict]:
        """
        Extract organization mentions from text.
        
        Args:
            text: Text to parse for organization mentions
            
        Returns:
            List of organization mention dictionaries
        """
        mentions = []
        seen_mentions = set()
        
        for pattern in self.organization_patterns:
            for match in pattern.finditer(text):
                mention = match.group(1).strip()
                
                # Skip if too short or already seen
                if len(mention) < 3 or mention.lower() in seen_mentions:
                    continue
                
                # Skip common false positives
                if self._is_false_positive(mention):
                    continue
                
                seen_mentions.add(mention.lower())
                
                # Check if organization exists in database
                existing_org = self._find_existing_organization(mention)
                
                mention_info = {
                    'mention': mention,
                    'start_position': match.start(),
                    'end_position': match.end(),
                    'context': self._extract_context(text, match.start(), match.end()),
                    'existing_organization_id': existing_org.id if existing_org else None,
                    'confidence_score': self._calculate_confidence(mention, text),
                    'organization_type': self._infer_organization_type(mention),
                    'extracted_at': datetime.utcnow().isoformat()
                }
                
                mentions.append(mention_info)
        
        return mentions
    
    def _is_false_positive(self, mention: str) -> bool:
        """Check if mention is likely a false positive"""
        false_positives = {
            'ai', 'africa', 'african', 'development', 'international', 'global',
            'world', 'research', 'technology', 'innovation', 'program', 'programme',
            'project', 'initiative', 'fund', 'grant', 'funding', 'support',
            'application', 'deadline', 'submission', 'requirements', 'criteria',
            'overview', 'summary', 'description', 'details', 'information',
            'contact', 'website', 'email', 'phone', 'address', 'location'
        }
        
        return (
            mention.lower() in false_positives or
            len(mention.split()) > 8 or  # Too long to be organization name
            mention.isdigit() or  # Numeric values
            mention.lower().startswith(('http', 'www', 'email', 'tel'))  # URLs/contacts
        )
    
    def _find_existing_organization(self, mention: str) -> Optional[Organization]:
        """Find existing organization by name or similar names"""
        # Exact match (case insensitive)
        exact_match = self.db.query(Organization).filter(
            Organization.name.ilike(mention)
        ).first()
        
        if exact_match:
            return exact_match
        
        # Fuzzy match (contains or similar)
        fuzzy_matches = self.db.query(Organization).filter(
            or_(
                Organization.name.ilike(f'%{mention}%'),
                Organization.name.ilike(f'{mention}%'),
                Organization.name.ilike(f'%{mention}')
            )
        ).all()
        
        # Return best match based on similarity
        if fuzzy_matches:
            return min(fuzzy_matches, key=lambda org: abs(len(org.name) - len(mention)))
        
        return None
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Extract surrounding context for organization mention"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        context = text[context_start:context_end]
        
        # Mark the mention within context
        mention_start = start - context_start
        mention_end = end - context_start
        
        return {
            'text': context,
            'mention_start': mention_start,
            'mention_end': mention_end
        }
    
    def _calculate_confidence(self, mention: str, full_text: str) -> float:
        """Calculate confidence score for organization mention"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for common organization indicators
        org_indicators = ['foundation', 'fund', 'trust', 'institute', 'university', 
                         'corporation', 'agency', 'ministry', 'department']
        
        for indicator in org_indicators:
            if indicator in mention.lower():
                confidence += 0.2
                break
        
        # Boost confidence for African context
        african_indicators = ['african', 'africa', 'continental', 'regional',
                            'ecowas', 'sadc', 'eac', 'au', 'nepad']
        
        for indicator in african_indicators:
            if indicator in mention.lower() or indicator in full_text.lower():
                confidence += 0.15
                break
        
        # Boost confidence for funding context
        funding_indicators = ['grant', 'funding', 'investment', 'capital', 'venture']
        
        for indicator in funding_indicators:
            if indicator in full_text.lower():
                confidence += 0.1
                break
        
        # Reduce confidence for very short mentions
        if len(mention) < 5:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _infer_organization_type(self, mention: str) -> str:
        """Infer organization type from mention"""
        mention_lower = mention.lower()
        
        type_indicators = {
            'foundation': ['foundation', 'fund', 'trust'],
            'government': ['ministry', 'department', 'agency', 'authority', 'commission'],
            'university': ['university', 'college', 'institute of technology', 'school'],
            'corporation': ['corporation', 'corp', 'company', 'ltd', 'limited', 'inc', 'technologies', 'tech'],
            'ngo': ['organization', 'organisation', 'ngo', 'npo', 'society', 'association'],
            'multilateral': ['world', 'international', 'global', 'development', 'relief', 'aid']
        }
        
        for org_type, indicators in type_indicators.items():
            if any(indicator in mention_lower for indicator in indicators):
                return org_type
        
        return 'unknown'
    
    def process_funding_opportunity(self, opportunity: FundingOpportunity) -> Dict:
        """
        Process a funding opportunity to extract organization mentions.
        
        Args:
            opportunity: FundingOpportunity instance
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Combine all text fields for parsing
            text_fields = [
                opportunity.title or '',
                opportunity.description or '',
                opportunity.eligibility_criteria or '',
                opportunity.application_process or '',
                opportunity.source_content or ''
            ]
            
            full_text = ' '.join(text_fields)
            
            # Extract mentions
            mentions = self.extract_organization_mentions(full_text)
            
            # Identify organizations needing enrichment
            organizations_for_enrichment = []
            
            for mention in mentions:
                if mention['existing_organization_id']:
                    org = self.db.query(Organization).get(mention['existing_organization_id'])
                    if org and org.needs_enrichment:
                        organizations_for_enrichment.append(org.id)
                else:
                    # Create new organization if confidence is high enough
                    if mention['confidence_score'] >= 0.7:
                        new_org = self._create_organization_from_mention(mention, opportunity)
                        if new_org:
                            organizations_for_enrichment.append(new_org.id)
            
            result = {
                'opportunity_id': opportunity.id,
                'mentions_found': len(mentions),
                'mentions': mentions,
                'organizations_for_enrichment': organizations_for_enrichment,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Processed opportunity {opportunity.id}: found {len(mentions)} mentions, "
                       f"{len(organizations_for_enrichment)} organizations need enrichment")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing funding opportunity {opportunity.id}: {str(e)}")
            return {
                'opportunity_id': opportunity.id,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def _create_organization_from_mention(self, mention: Dict, opportunity: FundingOpportunity) -> Optional[Organization]:
        """Create new organization from high-confidence mention"""
        try:
            # Determine role based on opportunity context
            role = 'provider' if 'provider' in mention['context']['text'].lower() else 'recipient'
            
            new_org = Organization(
                name=mention['mention'],
                type=mention['organization_type'],
                role=role,
                country=opportunity.country,
                region=opportunity.region,
                description=f"Organization discovered from funding opportunity: {opportunity.title}",
                enrichment_status='pending',
                enrichment_completeness=10,  # Basic info only
                source_type='auto_discovered',
                monitoring_status='pilot'
            )
            
            self.db.add(new_org)
            self.db.commit()
            
            logger.info(f"Created new organization: {new_org.name} (ID: {new_org.id})")
            
            return new_org
            
        except Exception as e:
            logger.error(f"Error creating organization from mention: {str(e)}")
            self.db.rollback()
            return None
    
    def get_organizations_needing_enrichment(self, limit: int = 50) -> List[Organization]:
        """Get organizations that need enrichment"""
        return self.db.query(Organization).filter(
            or_(
                Organization.enrichment_status.in_(['pending', 'failed']),
                Organization.enrichment_completeness < 70
            )
        ).limit(limit).all()
    
    def batch_process_opportunities(self, opportunity_ids: List[int] = None) -> Dict:
        """
        Process multiple funding opportunities in batch.
        
        Args:
            opportunity_ids: List of opportunity IDs to process, or None for all
            
        Returns:
            Batch processing results
        """
        if opportunity_ids:
            opportunities = self.db.query(FundingOpportunity).filter(
                FundingOpportunity.id.in_(opportunity_ids)
            ).all()
        else:
            # Process recent opportunities that haven't been processed for mentions
            opportunities = self.db.query(FundingOpportunity).filter(
                FundingOpportunity.created_at >= datetime.utcnow().replace(day=1)  # This month
            ).all()
        
        results = {
            'total_opportunities': len(opportunities),
            'processed': 0,
            'mentions_found': 0,
            'organizations_for_enrichment': set(),
            'errors': []
        }
        
        for opportunity in opportunities:
            try:
                result = self.process_funding_opportunity(opportunity)
                
                if 'error' not in result:
                    results['processed'] += 1
                    results['mentions_found'] += result['mentions_found']
                    results['organizations_for_enrichment'].update(result['organizations_for_enrichment'])
                else:
                    results['errors'].append(result)
                    
            except Exception as e:
                results['errors'].append({
                    'opportunity_id': opportunity.id,
                    'error': str(e)
                })
        
        results['organizations_for_enrichment'] = list(results['organizations_for_enrichment'])
        
        logger.info(f"Batch processed {results['processed']} opportunities, "
                   f"found {results['mentions_found']} mentions, "
                   f"{len(results['organizations_for_enrichment'])} organizations need enrichment")
        
        return results