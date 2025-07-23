#!/usr/bin/env python3
"""
Standalone Deduplication Test
============================

This module tests our deduplication strategies without complex backend dependencies.
It demonstrates the different levels of deduplication we can implement.
"""

import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from dataclasses import dataclass

# For fuzzy string matching
try:
    from fuzzywuzzy import fuzz
    FUZZ_AVAILABLE = True
except ImportError:
    FUZZ_AVAILABLE = False
    print("⚠️ fuzzywuzzy not available - installing...")

# For semantic similarity (optional)
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("⚠️ sentence-transformers not available - semantic similarity disabled")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FundingAnnouncement:
    """Simplified funding announcement structure for testing"""
    title: str
    description: str
    source_url: str
    organization: str = ""
    amount: Optional[float] = None
    currency: str = "USD"
    deadline: Optional[str] = None


class URLNormalizer:
    """Normalizes URLs for consistent comparison"""
    
    def __init__(self):
        self.params_to_remove = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
            'fbclid', 'gclid', 'ref', 'source', 'campaign_id', '_ga', 'mc_cid'
        }
    
    def normalize(self, url: str) -> str:
        """Normalize URL by removing tracking parameters"""
        try:
            parsed = urlparse(url.lower().strip())
            
            # Remove tracking parameters
            query_params = parse_qs(parsed.query)
            cleaned_params = {k: v for k, v in query_params.items() 
                            if k not in self.params_to_remove}
            
            # Rebuild query string
            cleaned_query = urlencode(cleaned_params, doseq=True) if cleaned_params else ''
            
            # Remove fragment and rebuild URL
            normalized = urlunparse((
                parsed.scheme or 'https',
                parsed.netloc,
                parsed.path.rstrip('/') if parsed.path != '/' else '/',
                parsed.params,
                cleaned_query,
                ''  # Remove fragment
            ))
            
            return normalized
            
        except Exception:
            return url.lower().strip()


class ContentHasher:
    """Generates consistent hashes for content comparison"""
    
    def hash(self, title: str, description: str, organization: str = "") -> str:
        """Generate hash from normalized content fields"""
        # Normalize text (lowercase, strip whitespace)
        normalized_title = ' '.join(title.lower().strip().split())
        normalized_desc = ' '.join(description.lower().strip().split())
        normalized_org = ' '.join(organization.lower().strip().split())
        
        # Combine and hash
        combined = f"{normalized_title}|{normalized_desc}|{normalized_org}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()


class DeduplicationTester:
    """Tests different deduplication strategies"""
    
    def __init__(self):
        self.url_normalizer = URLNormalizer()
        self.content_hasher = ContentHasher()
        self.existing_opportunities = []  # Simulated database
        
        # Initialize semantic similarity if available
        self.semantic_model = None
        if SEMANTIC_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Semantic similarity model loaded")
            except Exception as e:
                logger.warning(f"Could not load semantic model: {e}")
    
    def add_existing_opportunity(self, opportunity: FundingAnnouncement):
        """Add an opportunity to our simulated database"""
        self.existing_opportunities.append(opportunity)
    
    def check_url_duplicate(self, new_url: str) -> Dict[str, Any]:
        """Check for URL-based duplicates"""
        normalized_new = self.url_normalizer.normalize(new_url)
        
        for existing in self.existing_opportunities:
            normalized_existing = self.url_normalizer.normalize(existing.source_url)
            
            # Exact match
            if normalized_new == normalized_existing:
                return {
                    'is_duplicate': True,
                    'match_type': 'exact_url',
                    'similarity_score': 1.0,
                    'existing_opportunity': existing,
                    'reason': 'Exact URL match after normalization'
                }
            
            # Similar URL check
            if FUZZ_AVAILABLE:
                similarity = fuzz.ratio(normalized_new, normalized_existing) / 100.0
                if similarity > 0.8:  # 80% similarity threshold
                    return {
                        'is_duplicate': True,
                        'match_type': 'similar_url',
                        'similarity_score': similarity,
                        'existing_opportunity': existing,
                        'reason': f'Similar URL (similarity: {similarity:.2f})'
                    }
        
        return {'is_duplicate': False, 'match_type': 'no_url_match'}
    
    def check_content_duplicate(self, opportunity: FundingAnnouncement) -> Dict[str, Any]:
        """Check for content-based duplicates"""
        new_hash = self.content_hasher.hash(
            opportunity.title, 
            opportunity.description, 
            opportunity.organization
        )
        
        for existing in self.existing_opportunities:
            existing_hash = self.content_hasher.hash(
                existing.title,
                existing.description,
                existing.organization
            )
            
            # Exact content match
            if new_hash == existing_hash:
                return {
                    'is_duplicate': True,
                    'match_type': 'exact_content',
                    'similarity_score': 1.0,
                    'existing_opportunity': existing,
                    'reason': 'Exact content hash match'
                }
        
        # Fuzzy title matching
        if FUZZ_AVAILABLE:
            for existing in self.existing_opportunities:
                title_similarity = fuzz.ratio(opportunity.title, existing.title) / 100.0
                if title_similarity > 0.85:  # 85% title similarity threshold
                    return {
                        'is_duplicate': True,
                        'match_type': 'similar_title',
                        'similarity_score': title_similarity,
                        'existing_opportunity': existing,
                        'reason': f'Similar title (similarity: {title_similarity:.2f})'
                    }
        
        return {'is_duplicate': False, 'match_type': 'no_content_match'}
    
    def check_semantic_duplicate(self, opportunity: FundingAnnouncement) -> Dict[str, Any]:
        """Check for semantic duplicates using embeddings"""
        if not self.semantic_model:
            return {'is_duplicate': False, 'match_type': 'no_semantic_check'}
        
        try:
            # Create embedding for new opportunity
            new_text = f"{opportunity.title} {opportunity.description}"
            new_embedding = self.semantic_model.encode([new_text])[0]
            
            for existing in self.existing_opportunities:
                existing_text = f"{existing.title} {existing.description}"
                existing_embedding = self.semantic_model.encode([existing_text])[0]
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(new_embedding, existing_embedding)
                
                if similarity > 0.9:  # 90% semantic similarity threshold
                    return {
                        'is_duplicate': True,
                        'match_type': 'semantic_similarity',
                        'similarity_score': similarity,
                        'existing_opportunity': existing,
                        'reason': f'Semantic similarity (score: {similarity:.2f})'
                    }
            
            return {'is_duplicate': False, 'match_type': 'no_semantic_match'}
            
        except Exception as e:
            logger.warning(f"Semantic similarity check failed: {e}")
            return {'is_duplicate': False, 'match_type': 'semantic_error'}
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        
        # Convert to numpy arrays if needed
        if not isinstance(vec1, np.ndarray):
            vec1 = np.array(vec1)
        if not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def check_metadata_duplicate(self, opportunity: FundingAnnouncement) -> Dict[str, Any]:
        """Check for metadata-based duplicates"""
        if not opportunity.organization:
            return {'is_duplicate': False, 'match_type': 'no_metadata_check'}
        
        for existing in self.existing_opportunities:
            # Check organization + amount combination
            if (opportunity.organization.lower() == existing.organization.lower() and
                opportunity.amount and existing.amount and
                abs(opportunity.amount - existing.amount) / max(opportunity.amount, existing.amount) < 0.1):  # 10% tolerance
                
                return {
                    'is_duplicate': True,
                    'match_type': 'metadata_similarity',
                    'similarity_score': 0.95,
                    'existing_opportunity': existing,
                    'reason': f'Same organization and similar amount'
                }
        
        return {'is_duplicate': False, 'match_type': 'no_metadata_match'}
    
    def comprehensive_duplicate_check(self, opportunity: FundingAnnouncement) -> Dict[str, Any]:
        """Run all deduplication checks"""
        logger.info(f"🔍 Checking for duplicates: {opportunity.title[:50]}...")
        
        # Run all checks
        url_result = self.check_url_duplicate(opportunity.source_url)
        content_result = self.check_content_duplicate(opportunity)
        semantic_result = self.check_semantic_duplicate(opportunity)
        metadata_result = self.check_metadata_duplicate(opportunity)
        
        # Determine overall result
        all_checks = {
            'url_check': url_result,
            'content_check': content_result,
            'semantic_check': semantic_result,
            'metadata_check': metadata_result
        }
        
        # Find the strongest match
        duplicate_checks = [check for check in all_checks.values() if check.get('is_duplicate')]
        
        if duplicate_checks:
            # Get the check with highest similarity score
            primary_match = max(duplicate_checks, key=lambda x: x.get('similarity_score', 0))
            
            return {
                'is_duplicate': True,
                'action': self._determine_action(primary_match),
                'primary_match': primary_match,
                'all_checks': all_checks,
                'confidence': primary_match.get('similarity_score', 0.5),
                'recommendation': self._generate_recommendation(primary_match)
            }
        else:
            return {
                'is_duplicate': False,
                'action': 'proceed',
                'primary_match': None,
                'all_checks': all_checks,
                'confidence': 1.0,
                'recommendation': '✅ No duplicates found - safe to proceed'
            }
    
    def _determine_action(self, match: Dict[str, Any]) -> str:
        """Determine what action to take based on match type and score"""
        match_type = match.get('match_type', '')
        score = match.get('similarity_score', 0)
        
        if match_type in ['exact_url', 'exact_content'] or score >= 0.95:
            return 'skip'
        elif score >= 0.85:
            return 'flag_for_review'
        else:
            return 'proceed_with_caution'
    
    def _generate_recommendation(self, match: Dict[str, Any]) -> str:
        """Generate human-readable recommendation"""
        action = self._determine_action(match)
        match_type = match.get('match_type', '')
        score = match.get('similarity_score', 0)
        
        if action == 'skip':
            return f"🚫 Skip ingestion - {match_type} detected (score: {score:.2f})"
        elif action == 'flag_for_review':
            return f"⚠️ Flag for review - potential duplicate {match_type} (score: {score:.2f})"
        else:
            return f"⚡ Proceed with caution - weak {match_type} signal (score: {score:.2f})"


async def test_deduplication_strategies():
    """Test our deduplication strategies with sample data"""
    logger.info("🧪 Testing Deduplication Strategies")
    
    # Create tester
    tester = DeduplicationTester()
    
    # Add some existing opportunities to our "database"
    existing_opportunities = [
        FundingAnnouncement(
            title="AI Innovation Grant 2024",
            description="Funding for AI startups in Africa",
            source_url="https://techfoundation.org/grants/ai-innovation",
            organization="Tech Foundation",
            amount=100000
        ),
        FundingAnnouncement(
            title="African Tech Accelerator Program",
            description="Supporting technology entrepreneurs across Africa",
            source_url="https://accelerator.africa/program",
            organization="African Accelerator",
            amount=50000
        ),
        FundingAnnouncement(
            title="Startup Funding Initiative",
            description="Early-stage funding for innovative startups",
            source_url="https://startup-fund.com/apply",
            organization="Startup Fund",
            amount=75000
        )
    ]
    
    for opp in existing_opportunities:
        tester.add_existing_opportunity(opp)
    
    logger.info(f"📊 Added {len(existing_opportunities)} existing opportunities to test database")
    
    # Test cases
    test_cases = [
        # Case 1: Exact duplicate (same URL)
        FundingAnnouncement(
            title="AI Innovation Grant 2024",
            description="Funding for AI startups in Africa",
            source_url="https://techfoundation.org/grants/ai-innovation",
            organization="Tech Foundation",
            amount=100000
        ),
        
        # Case 2: Same URL with tracking parameters
        FundingAnnouncement(
            title="AI Innovation Grant 2024",
            description="Funding for AI startups in Africa",
            source_url="https://techfoundation.org/grants/ai-innovation?utm_source=newsletter&utm_campaign=funding",
            organization="Tech Foundation",
            amount=100000
        ),
        
        # Case 3: Similar title, different URL
        FundingAnnouncement(
            title="AI Innovation Grant Program 2024",
            description="Funding for artificial intelligence startups in Africa",
            source_url="https://different-site.com/ai-grants",
            organization="Tech Foundation",
            amount=100000
        ),
        
        # Case 4: Completely different opportunity
        FundingAnnouncement(
            title="Blockchain Development Fund",
            description="Supporting blockchain innovation in emerging markets",
            source_url="https://blockchain-fund.org/apply",
            organization="Blockchain Foundation",
            amount=200000
        ),
        
        # Case 5: Same organization, similar amount
        FundingAnnouncement(
            title="Advanced AI Research Grant",
            description="Research funding for advanced AI projects",
            source_url="https://research-grants.org/ai",
            organization="Tech Foundation",
            amount=95000  # Similar to existing 100k
        )
    ]
    
    # Test each case
    results = []
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n--- Test Case {i}: {test_case.title[:40]}... ---")
        
        result = tester.comprehensive_duplicate_check(test_case)
        results.append(result)
        
        logger.info(f"Result: {result['recommendation']}")
        logger.info(f"Action: {result['action']}")
        logger.info(f"Confidence: {result['confidence']:.2f}")
        
        if result['is_duplicate']:
            primary = result['primary_match']
            logger.info(f"Match Type: {primary['match_type']}")
            logger.info(f"Similarity: {primary.get('similarity_score', 'N/A')}")
            logger.info(f"Existing: {primary['existing_opportunity'].title[:40]}...")
    
    # Summary statistics
    duplicates_found = sum(1 for r in results if r['is_duplicate'])
    logger.info(f"\n📈 Summary:")
    logger.info(f"Total tests: {len(test_cases)}")
    logger.info(f"Duplicates found: {duplicates_found}")
    logger.info(f"Duplicate rate: {duplicates_found/len(test_cases):.1%}")
    
    # Show capabilities
    capabilities = []
    if FUZZ_AVAILABLE:
        capabilities.append("✅ Fuzzy string matching")
    else:
        capabilities.append("❌ Fuzzy string matching (install fuzzywuzzy)")
    
    if SEMANTIC_AVAILABLE and tester.semantic_model:
        capabilities.append("✅ Semantic similarity")
    else:
        capabilities.append("❌ Semantic similarity (install sentence-transformers)")
    
    logger.info(f"\n🔧 Deduplication Capabilities:")
    for cap in capabilities:
        logger.info(f"  {cap}")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_deduplication_strategies())
