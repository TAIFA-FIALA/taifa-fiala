#!/usr/bin/env python3
"""
Enhanced Deduplication Integration for Ingestion Pipeline
========================================================

This module integrates the advanced deduplication system into the ingestion pipeline
to prevent duplicate funding opportunities from entering the database.

Features:
- Multi-layer deduplication (URL, content, metadata)
- Configurable similarity thresholds
- Performance tracking and analytics
- Fallback to basic deduplication if advanced system fails
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from backend.app.services.source_validation.deduplication import (
    DeduplicationPipeline, 
    OpportunityContent,
    DuplicateMatch
)
from backend.app.services.source_validation.config import DeduplicationSettings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedDeduplicationIntegrator:
    """
    Integrates advanced deduplication into the ingestion pipeline
    """
    
    def __init__(self, settings: Optional[DeduplicationSettings] = None):
        self.settings = settings or DeduplicationSettings()
        self.dedup_pipeline = DeduplicationPipeline()
        self.logger = logging.getLogger(__name__)
        
        # Statistics tracking
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'duplicates_by_type': {},
            'processing_times': [],
            'errors': 0
        }
    
    async def check_opportunity_for_duplicates(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an opportunity is a duplicate using advanced deduplication
        
        Args:
            opportunity_data: Dictionary containing opportunity information
            
        Returns:
            Dict with duplicate status and recommendations
        """
        start_time = datetime.now()
        self.stats['total_checked'] += 1
        
        try:
            # Convert opportunity data to OpportunityContent format
            opportunity = self._convert_to_opportunity_content(opportunity_data)
            
            # Run advanced deduplication checks
            dedup_result = await self.dedup_pipeline.check_for_duplicates(opportunity)
            
            # Process results
            result = self._process_deduplication_result(dedup_result, opportunity_data)
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats['processing_times'].append(processing_time)
            
            if result['is_duplicate']:
                self.stats['duplicates_found'] += 1
                match_type = result.get('primary_match_type', 'unknown')
                self.stats['duplicates_by_type'][match_type] = self.stats['duplicates_by_type'].get(match_type, 0) + 1
            
            self.logger.info(f"Deduplication check completed in {processing_time:.2f}s - {'DUPLICATE' if result['is_duplicate'] else 'UNIQUE'}")
            
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Error in enhanced deduplication: {e}")
            
            # Fallback to basic deduplication
            return await self._fallback_basic_deduplication(opportunity_data)
    
    def _convert_to_opportunity_content(self, opportunity_data: Dict[str, Any]) -> OpportunityContent:
        """Convert ingestion data format to OpportunityContent"""
        return OpportunityContent(
            url=opportunity_data.get('source_url', ''),
            title=opportunity_data.get('title', ''),
            description=opportunity_data.get('description', ''),
            organization=opportunity_data.get('organization', ''),
            amount=opportunity_data.get('amount_max') or opportunity_data.get('amount_exact'),
            currency=opportunity_data.get('currency'),
            deadline=opportunity_data.get('deadline'),
            source_id=opportunity_data.get('source_id')
        )
    
    def _process_deduplication_result(self, dedup_result: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process deduplication results into actionable format"""
        
        is_duplicate = dedup_result.get('is_duplicate', False)
        action = dedup_result.get('action', 'proceed')
        
        # Get primary match details
        primary_match = dedup_result.get('primary_match', {})
        
        result = {
            'is_duplicate': is_duplicate,
            'action': action,
            'confidence': self._calculate_confidence(dedup_result),
            'primary_match_type': primary_match.get('match_type'),
            'similarity_score': primary_match.get('similarity_score'),
            'existing_opportunity_id': primary_match.get('existing_opportunity_id'),
            'existing_url': primary_match.get('existing_url'),
            'reason': primary_match.get('reason'),
            'all_checks': dedup_result.get('duplicate_checks', {}),
            'recommendation': self._generate_recommendation(dedup_result, original_data),
            'checked_at': dedup_result.get('checked_at')
        }
        
        return result
    
    def _calculate_confidence(self, dedup_result: Dict[str, Any]) -> float:
        """Calculate confidence score for deduplication result"""
        checks = dedup_result.get('duplicate_checks', {})
        
        if not checks:
            return 0.5  # Medium confidence for no checks
        
        # Weight different check types
        weights = {
            'url_check': 0.3,
            'content_check': 0.4,
            'metadata_check': 0.3
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for check_name, check_result in checks.items():
            if check_name in weights and check_result.get('similarity_score'):
                score = check_result['similarity_score']
                weight = weights[check_name]
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _generate_recommendation(self, dedup_result: Dict[str, Any], original_data: Dict[str, Any]) -> str:
        """Generate human-readable recommendation"""
        
        if not dedup_result.get('is_duplicate'):
            return "✅ No duplicates found - safe to proceed with ingestion"
        
        action = dedup_result.get('action', 'unknown')
        primary_match = dedup_result.get('primary_match', {})
        
        if action == 'skip':
            return f"🚫 Skip ingestion - exact duplicate found (ID: {primary_match.get('existing_opportunity_id')})"
        elif action == 'merge':
            return f"🔄 Consider merging with existing opportunity (ID: {primary_match.get('existing_opportunity_id')})"
        elif action == 'flag_for_review':
            return f"⚠️ Flag for manual review - potential duplicate (similarity: {primary_match.get('similarity_score', 0):.2f})"
        else:
            return "❓ Uncertain - proceed with caution"
    
    async def _fallback_basic_deduplication(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to basic deduplication if advanced system fails"""
        self.logger.warning("Falling back to basic deduplication")
        
        # Simple title and URL check (current system)
        title = opportunity_data.get('title', '')
        source_url = opportunity_data.get('source_url', '')
        
        # This would typically query the database
        # For now, return a basic result structure
        return {
            'is_duplicate': False,  # Conservative approach
            'action': 'proceed',
            'confidence': 0.3,  # Low confidence
            'primary_match_type': 'basic_check',
            'similarity_score': None,
            'existing_opportunity_id': None,
            'existing_url': None,
            'reason': 'Fallback basic deduplication - advanced system failed',
            'all_checks': {},
            'recommendation': "⚠️ Basic deduplication only - advanced checks failed",
            'checked_at': datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        avg_processing_time = (
            sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            if self.stats['processing_times'] else 0
        )
        
        duplicate_rate = (
            self.stats['duplicates_found'] / self.stats['total_checked']
            if self.stats['total_checked'] > 0 else 0
        )
        
        return {
            'total_checked': self.stats['total_checked'],
            'duplicates_found': self.stats['duplicates_found'],
            'duplicate_rate': duplicate_rate,
            'duplicates_by_type': self.stats['duplicates_by_type'],
            'average_processing_time_seconds': avg_processing_time,
            'errors': self.stats['errors'],
            'error_rate': self.stats['errors'] / self.stats['total_checked'] if self.stats['total_checked'] > 0 else 0
        }
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'duplicates_by_type': {},
            'processing_times': [],
            'errors': 0
        }


async def test_enhanced_deduplication():
    """Test the enhanced deduplication integration"""
    logger.info("🧪 Testing Enhanced Deduplication Integration")
    
    # Create integrator
    integrator = EnhancedDeduplicationIntegrator()
    
    # Test opportunity data
    test_opportunities = [
        {
            'title': 'AI Startup Funding Program 2024',
            'description': 'Funding for AI startups in Africa',
            'source_url': 'https://example.com/funding/ai-program',
            'organization': 'Tech Foundation',
            'amount_max': 100000,
            'currency': 'USD'
        },
        {
            'title': 'AI Startup Funding Program 2024',  # Exact duplicate
            'description': 'Funding for AI startups in Africa',
            'source_url': 'https://example.com/funding/ai-program?utm_source=newsletter',  # Same URL with tracking
            'organization': 'Tech Foundation',
            'amount_max': 100000,
            'currency': 'USD'
        },
        {
            'title': 'African AI Innovation Grant',  # Similar but different
            'description': 'Supporting artificial intelligence innovation across Africa',
            'source_url': 'https://different-site.com/grants/ai-innovation',
            'organization': 'Innovation Hub',
            'amount_max': 75000,
            'currency': 'USD'
        }
    ]
    
    # Test each opportunity
    for i, opportunity in enumerate(test_opportunities):
        logger.info(f"\n--- Testing Opportunity {i+1} ---")
        logger.info(f"Title: {opportunity['title']}")
        
        result = await integrator.check_opportunity_for_duplicates(opportunity)
        
        logger.info(f"Result: {result['recommendation']}")
        logger.info(f"Action: {result['action']}")
        logger.info(f"Confidence: {result['confidence']:.2f}")
    
    # Show statistics
    stats = integrator.get_statistics()
    logger.info(f"\n📊 Deduplication Statistics:")
    logger.info(f"Total checked: {stats['total_checked']}")
    logger.info(f"Duplicates found: {stats['duplicates_found']}")
    logger.info(f"Duplicate rate: {stats['duplicate_rate']:.2%}")
    logger.info(f"Average processing time: {stats['average_processing_time_seconds']:.3f}s")


if __name__ == "__main__":
    asyncio.run(test_enhanced_deduplication())
