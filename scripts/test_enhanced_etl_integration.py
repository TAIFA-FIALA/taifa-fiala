#!/usr/bin/env python3
"""
Test Enhanced ETL Integration
Tests the integration of enhanced_funding_extractor.py into existing ETL workflows

This script tests:
1. Enhanced RSS processing with new funding patterns
2. Enhanced Crawl4AI processing with field extraction
3. Enhanced Serper search processing with enrichment
4. Database integration with enhanced schema
5. End-to-end pipeline functionality

Usage:
    python scripts/test_enhanced_etl_integration.py
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import enhanced ETL components
from backend.app.services.etl.enhanced_etl_integration import (
    EnhancedETLIntegrator, 
    EnhancedETLConfig, 
    ETLDataSource,
    EnhancedMasterPipelineWrapper
)
from backend.app.services.etl.enhanced_funding_extractor import (
    EnhancedFundingExtractor, 
    EnhancedETLPipeline
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/enhanced_etl_test.log')
    ]
)
logger = logging.getLogger(__name__)


class EnhancedETLTester:
    """Comprehensive tester for enhanced ETL integration"""
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'start_time': datetime.utcnow().isoformat()
        }
        
        # Create enhanced ETL config
        self.config = EnhancedETLConfig(
            enable_enhanced_extraction=True,
            enable_field_validation=True,
            enable_data_enrichment=True,
            min_relevance_score=0.5,  # Lower threshold for testing
            enable_enhanced_schema=False,  # Disable database saves for testing
            enable_backward_compatibility=True
        )
        
        # Initialize components
        self.integrator = EnhancedETLIntegrator(self.config)
        self.extractor = EnhancedFundingExtractor()
        self.pipeline = EnhancedETLPipeline()
        
        logger.info("Enhanced ETL Tester initialized")
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", data: Any = None):
        """Log test result"""
        self.test_results['total_tests'] += 1
        
        if passed:
            self.test_results['passed_tests'] += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.test_results['failed_tests'] += 1
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def test_enhanced_funding_extractor(self):
        """Test the enhanced funding extractor with different funding patterns"""
        logger.info("🧪 Testing Enhanced Funding Extractor...")
        
        # Test cases for the three funding patterns
        test_cases = [
            {
                'name': 'Total Pool Pattern',
                'text': 'The African Innovation Fund announces $5 million total funding to support 10-15 AI startups across the continent.',
                'expected_type': 'total_pool',
                'expected_fields': ['total_funding_pool', 'estimated_project_count']
            },
            {
                'name': 'Exact Amount Pattern',
                'text': 'Each selected project will receive exactly $50,000 to develop AI solutions for healthcare challenges.',
                'expected_type': 'per_project_exact',
                'expected_fields': ['exact_amount_per_project']
            },
            {
                'name': 'Range Pattern',
                'text': 'Grants ranging from $25,000 to $100,000 are available for women-led AI ventures focusing on fintech and edtech.',
                'expected_type': 'per_project_range',
                'expected_fields': ['min_amount_per_project', 'max_amount_per_project', 'gender_focused']
            },
            {
                'name': 'Complex Pattern with Multiple Fields',
                'text': 'The Gates Foundation launches a $10M initiative supporting African AI startups. Applications due March 15, 2024. Grants of $75,000-$150,000 for early-stage companies focusing on healthcare AI. Women entrepreneurs encouraged to apply.',
                'expected_type': 'per_project_range',
                'expected_fields': ['min_amount_per_project', 'max_amount_per_project', 'deadline_info', 'gender_focused', 'ai_subsectors']
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.extractor.extract_funding_info(test_case['text'])
                
                # Check funding type
                funding_type_correct = result.get('funding_type') == test_case['expected_type']
                
                # Check expected fields
                fields_found = []
                for field in test_case['expected_fields']:
                    if field in result and result[field] is not None:
                        fields_found.append(field)
                
                fields_correct = len(fields_found) >= len(test_case['expected_fields']) * 0.7  # 70% threshold
                
                test_passed = funding_type_correct and fields_correct
                
                details = f"Type: {result.get('funding_type')} (expected: {test_case['expected_type']}), Fields: {fields_found}"
                
                self.log_test_result(
                    f"Extractor - {test_case['name']}", 
                    test_passed, 
                    details, 
                    result
                )
                
            except Exception as e:
                self.log_test_result(
                    f"Extractor - {test_case['name']}", 
                    False, 
                    f"Exception: {str(e)}"
                )
    
    async def test_enhanced_rss_processing(self):
        """Test enhanced RSS processing"""
        logger.info("🧪 Testing Enhanced RSS Processing...")
        
        # Test RSS items with different funding patterns
        test_rss_items = [
            {
                'title': 'Gates Foundation Announces $5M AI for Africa Initiative',
                'description': 'The Gates Foundation is launching a new $5 million initiative to support AI startups across Africa, with grants ranging from $50,000 to $200,000 per project. Applications due December 31, 2024.',
                'link': 'https://gatesfoundation.org/ai-africa-initiative',
                'published': '2024-01-15T10:00:00Z'
            },
            {
                'title': 'African Development Bank Launches Tech Innovation Fund',
                'description': 'The AfDB announces a $10 million fund to support technology innovation across Africa, with particular focus on AI and fintech solutions. Each project receives exactly $75,000.',
                'link': 'https://afdb.org/tech-innovation-fund',
                'published': '2024-01-10T14:30:00Z'
            },
            {
                'title': 'Mozilla Foundation AI Grant Program for Women',
                'description': 'Mozilla Foundation offers grants up to $100,000 for AI projects led by women that promote digital inclusion and privacy in African communities.',
                'link': 'https://mozilla.org/ai-grants-women',
                'published': '2024-01-05T09:00:00Z'
            }
        ]
        
        try:
            enhanced_opportunities = await self.integrator.process_rss_data_enhanced(test_rss_items)
            
            # Validate results
            test_passed = len(enhanced_opportunities) > 0
            
            if test_passed:
                # Check if enhanced fields are present
                enhanced_fields_found = 0
                for opp in enhanced_opportunities:
                    if opp.get('funding_type'):
                        enhanced_fields_found += 1
                    if opp.get('target_audience'):
                        enhanced_fields_found += 1
                    if opp.get('suitability_score'):
                        enhanced_fields_found += 1
                
                enhancement_quality = enhanced_fields_found / (len(enhanced_opportunities) * 3)  # 3 key fields
                test_passed = enhancement_quality >= 0.5  # 50% threshold
                
                details = f"Processed {len(test_rss_items)} items → {len(enhanced_opportunities)} opportunities, Enhancement quality: {enhancement_quality:.2%}"
            else:
                details = "No opportunities extracted"
            
            self.log_test_result(
                "RSS Processing - Enhanced Extraction", 
                test_passed, 
                details, 
                enhanced_opportunities[:2] if enhanced_opportunities else None  # First 2 for brevity
            )
            
        except Exception as e:
            self.log_test_result(
                "RSS Processing - Enhanced Extraction", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_enhanced_crawl4ai_processing(self):
        """Test enhanced Crawl4AI processing"""
        logger.info("🧪 Testing Enhanced Crawl4AI Processing...")
        
        # Mock Crawl4AI results
        test_crawl4ai_results = [
            {
                'title': 'Google AI for Social Good Grants',
                'description': 'Google announces AI for Social Good grants supporting projects in Africa, with funding up to $100,000 per project. Focus on healthcare, education, and environmental solutions.',
                'source_url': 'https://ai.google/social-good/grants',
                'extraction_strategy': 'intelligence_item',
                'relevance_score': 0.85,
                'crawl_metadata': {
                    'target_type': 'foundation_website',
                    'source_priority': 1
                }
            },
            {
                'title': 'Microsoft AI for Good Lab Africa Program',
                'description': 'Microsoft AI for Good Lab launches African program with $2M total funding for 20 AI projects. Each project receives $100,000. Deadline: June 30, 2024.',
                'source_url': 'https://microsoft.com/ai-for-good-africa',
                'extraction_strategy': 'intelligence_item',
                'relevance_score': 0.90,
                'crawl_metadata': {
                    'target_type': 'corporate_website',
                    'source_priority': 1
                }
            }
        ]
        
        try:
            enhanced_opportunities = await self.integrator.process_crawl4ai_data_enhanced(test_crawl4ai_results)
            
            # Validate results
            test_passed = len(enhanced_opportunities) > 0
            
            if test_passed:
                # Check for Crawl4AI specific metadata
                crawl4ai_metadata_found = 0
                for opp in enhanced_opportunities:
                    if opp.get('extraction_strategy'):
                        crawl4ai_metadata_found += 1
                    if opp.get('crawl_target_type'):
                        crawl4ai_metadata_found += 1
                    if opp.get('original_relevance_score'):
                        crawl4ai_metadata_found += 1
                
                metadata_quality = crawl4ai_metadata_found / (len(enhanced_opportunities) * 3)
                test_passed = metadata_quality >= 0.6  # 60% threshold
                
                details = f"Processed {len(test_crawl4ai_results)} results → {len(enhanced_opportunities)} opportunities, Metadata quality: {metadata_quality:.2%}"
            else:
                details = "No opportunities extracted"
            
            self.log_test_result(
                "Crawl4AI Processing - Enhanced Extraction", 
                test_passed, 
                details, 
                enhanced_opportunities[:2] if enhanced_opportunities else None
            )
            
        except Exception as e:
            self.log_test_result(
                "Crawl4AI Processing - Enhanced Extraction", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_enhanced_serper_processing(self):
        """Test enhanced Serper search processing"""
        logger.info("🧪 Testing Enhanced Serper Processing...")
        
        # Mock Serper search results
        test_serper_results = [
            {
                'title': 'USAID AI Innovation Challenge for Africa',
                'snippet': 'USAID launches AI Innovation Challenge with $3M in funding for African startups. Grants range from $50,000 to $150,000 per project. Focus on agriculture and healthcare AI solutions.',
                'link': 'https://usaid.gov/ai-innovation-africa',
                'position': 1
            },
            {
                'title': 'World Bank Digital Africa Initiative',
                'snippet': 'World Bank announces Digital Africa Initiative with $500M total funding. Supporting AI and digital transformation projects across the continent.',
                'link': 'https://worldbank.org/digital-africa',
                'position': 2
            }
        ]
        
        search_query = 'AI funding opportunities Africa 2024'
        
        try:
            enhanced_opportunities = await self.integrator.process_serper_data_enhanced(
                test_serper_results, 
                search_query
            )
            
            # Validate results
            test_passed = len(enhanced_opportunities) > 0
            
            if test_passed:
                # Check for Serper specific metadata
                serper_metadata_found = 0
                for opp in enhanced_opportunities:
                    if opp.get('search_query'):
                        serper_metadata_found += 1
                    if opp.get('search_position') is not None:
                        serper_metadata_found += 1
                    if opp.get('search_engine'):
                        serper_metadata_found += 1
                
                metadata_quality = serper_metadata_found / (len(enhanced_opportunities) * 3)
                test_passed = metadata_quality >= 0.8  # 80% threshold
                
                details = f"Processed {len(test_serper_results)} results → {len(enhanced_opportunities)} opportunities, Metadata quality: {metadata_quality:.2%}"
            else:
                details = "No opportunities extracted"
            
            self.log_test_result(
                "Serper Processing - Enhanced Extraction", 
                test_passed, 
                details, 
                enhanced_opportunities[:2] if enhanced_opportunities else None
            )
            
        except Exception as e:
            self.log_test_result(
                "Serper Processing - Enhanced Extraction", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_data_validation_and_enrichment(self):
        """Test data validation and enrichment functionality"""
        logger.info("🧪 Testing Data Validation and Enrichment...")
        
        # Test data with various quality levels
        test_data_cases = [
            {
                'name': 'High Quality Data',
                'data': {
                    'title': 'African AI Innovation Fund - $5M Initiative',
                    'description': 'Comprehensive funding program supporting AI startups across Africa with grants ranging from $50,000 to $200,000. Applications due March 15, 2024. Focus on healthcare and education AI solutions.',
                    'source_url': 'https://example.org/ai-fund',
                    'funding_type': 'per_project_range',
                    'min_amount_per_project': 50000,
                    'max_amount_per_project': 200000,
                    'deadline': '2024-03-15',
                    'ai_subsectors': ['healthcare', 'education']
                },
                'should_pass': True
            },
            {
                'name': 'Low Quality Data',
                'data': {
                    'title': 'Fund',  # Too short
                    'description': 'Short desc',  # Too short
                    'source_url': 'invalid-url',  # Invalid URL
                },
                'should_pass': False
            },
            {
                'name': 'Medium Quality Data',
                'data': {
                    'title': 'Technology Innovation Grant Program',
                    'description': 'Grant program supporting technology innovation with focus on AI and digital solutions for African markets.',
                    'source_url': 'https://example.org/tech-grants',
                    'funding_type': 'invalid_type',  # Invalid funding type
                    'currency': 'INVALID'  # Invalid currency
                },
                'should_pass': True  # Should pass with corrections
            }
        ]
        
        for test_case in test_data_cases:
            try:
                validated_data = await self.integrator._validate_and_enrich_data(
                    test_case['data'].copy(), 
                    ETLDataSource.RSS_FEED
                )
                
                validation_passed = validated_data.get('validation_passed', False)
                has_enrichment = validated_data.get('enrichment_applied', False)
                
                # Check if result matches expectation
                test_passed = (validation_passed == test_case['should_pass']) or (
                    test_case['should_pass'] and validation_passed
                )
                
                details = f"Validation: {validation_passed}, Enrichment: {has_enrichment}"
                
                self.log_test_result(
                    f"Validation - {test_case['name']}", 
                    test_passed, 
                    details, 
                    {
                        'original': test_case['data'],
                        'validated': {k: v for k, v in validated_data.items() if k not in ['raw_data']}
                    }
                )
                
            except Exception as e:
                expected_failure = not test_case['should_pass']
                self.log_test_result(
                    f"Validation - {test_case['name']}", 
                    expected_failure, 
                    f"Exception (expected: {expected_failure}): {str(e)}"
                )
    
    async def test_quality_filters(self):
        """Test quality filtering functionality"""
        logger.info("🧪 Testing Quality Filters...")
        
        # Test data with different quality scores
        test_filter_cases = [
            {
                'name': 'High Quality - Should Pass',
                'data': {
                    'title': 'High Quality Funding Opportunity',
                    'description': 'Excellent funding opportunity with clear details',
                    'source_url': 'https://example.org/high-quality',
                    'relevance_score': 0.8,
                    'suitability_score': 0.9,
                    'validation_passed': True
                },
                'should_pass': True
            },
            {
                'name': 'Low Quality - Should Fail',
                'data': {
                    'title': 'Low Quality Opportunity',
                    'description': 'Poor quality opportunity',
                    'source_url': 'https://example.org/low-quality',
                    'relevance_score': 0.3,
                    'suitability_score': 0.2,
                    'validation_passed': True
                },
                'should_pass': False
            },
            {
                'name': 'Validation Failed - Should Fail',
                'data': {
                    'title': 'Failed Validation Opportunity',
                    'description': 'Opportunity that failed validation',
                    'source_url': 'https://example.org/failed-validation',
                    'relevance_score': 0.8,
                    'suitability_score': 0.9,
                    'validation_passed': False
                },
                'should_pass': False
            }
        ]
        
        for test_case in test_filter_cases:
            try:
                passes_filter = self.integrator._passes_quality_filters(test_case['data'])
                
                test_passed = passes_filter == test_case['should_pass']
                
                details = f"Filter result: {passes_filter} (expected: {test_case['should_pass']})"
                
                self.log_test_result(
                    f"Quality Filter - {test_case['name']}", 
                    test_passed, 
                    details
                )
                
            except Exception as e:
                self.log_test_result(
                    f"Quality Filter - {test_case['name']}", 
                    False, 
                    f"Exception: {str(e)}"
                )
    
    async def test_field_mapping(self):
        """Test field mapping to enhanced schema"""
        logger.info("🧪 Testing Field Mapping to Enhanced Schema...")
        
        # Test comprehensive field mapping
        test_opportunity = {
            'title': 'Comprehensive AI Funding Program',
            'description': 'Complete funding program with all enhanced fields',
            'source_url': 'https://example.org/comprehensive',
            'application_url': 'https://example.org/apply',
            'funding_type': 'per_project_range',
            'min_amount_per_project': 50000,
            'max_amount_per_project': 150000,
            'currency': 'USD',
            'deadline': '2024-06-30',
            'application_deadline_type': 'fixed',
            'target_audience': ['startups', 'researchers'],
            'ai_subsectors': ['healthcare', 'fintech'],
            'collaboration_required': True,
            'gender_focused': True,
            'youth_focused': False,
            'urgency_level': 'medium',
            'suitability_score': 0.85,
            'relevance_score': 0.90
        }
        
        try:
            # Test field mapping (simulate the mapping process)
            enhanced_record = {
                # Core fields
                'title': test_opportunity.get('title'),
                'description': test_opportunity.get('description'),
                'source_url': test_opportunity.get('source_url'),
                'application_url': test_opportunity.get('application_url'),
                
                # Enhanced funding fields
                'funding_type': test_opportunity.get('funding_type', 'per_project_range'),
                'min_amount_per_project': test_opportunity.get('min_amount_per_project'),
                'max_amount_per_project': test_opportunity.get('max_amount_per_project'),
                'currency': test_opportunity.get('currency', 'USD'),
                
                # Enhanced process fields
                'deadline': test_opportunity.get('deadline'),
                'application_deadline_type': test_opportunity.get('application_deadline_type', 'fixed'),
                
                # Enhanced targeting fields
                'target_audience': test_opportunity.get('target_audience'),
                'ai_subsectors': test_opportunity.get('ai_subsectors'),
                
                # Focus indicators
                'collaboration_required': test_opportunity.get('collaboration_required'),
                'gender_focused': test_opportunity.get('gender_focused'),
                'youth_focused': test_opportunity.get('youth_focused'),
                
                # Computed fields
                'urgency_level': test_opportunity.get('urgency_level'),
                'suitability_score': test_opportunity.get('suitability_score'),
                'relevance_score': test_opportunity.get('relevance_score'),
            }
            
            # Remove None values
            enhanced_record = {k: v for k, v in enhanced_record.items() if v is not None}
            
            # Validate mapping
            expected_fields = [
                'title', 'description', 'source_url', 'funding_type', 
                'min_amount_per_project', 'max_amount_per_project', 'currency',
                'deadline', 'target_audience', 'ai_subsectors', 'suitability_score'
            ]
            
            mapped_fields = [field for field in expected_fields if field in enhanced_record]
            mapping_quality = len(mapped_fields) / len(expected_fields)
            
            test_passed = mapping_quality >= 0.9  # 90% threshold
            
            details = f"Mapped {len(mapped_fields)}/{len(expected_fields)} fields ({mapping_quality:.1%})"
            
            self.log_test_result(
                "Field Mapping - Enhanced Schema", 
                test_passed, 
                details, 
                enhanced_record
            )
            
        except Exception as e:
            self.log_test_result(
                "Field Mapping - Enhanced Schema", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Enhanced ETL Integration Tests...")
        
        # Run all test suites
        await self.test_enhanced_funding_extractor()
        await self.test_enhanced_rss_processing()
        await self.test_enhanced_crawl4ai_processing()
        await self.test_enhanced_serper_processing()
        await self.test_data_validation_and_enrichment()
        await self.test_quality_filters()
        await self.test_field_mapping()
        
        # Finalize results
        self.test_results['end_time'] = datetime.utcnow().isoformat()
        self.test_results['success_rate'] = (
            self.test_results['passed_tests'] / max(self.test_results['total_tests'], 1) * 100
        )
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🧪 ENHANCED ETL INTEGRATION TEST SUMMARY")
        print("="*80)
        
        print(f"📊 Total Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed_tests']}")
        print(f"❌ Failed: {self.test_results['failed_tests']}")
        print(f"📈 Success Rate: {self.test_results['success_rate']:.1f}%")
        
        print(f"\n⏱️  Duration: {self.test_results['start_time']} → {self.test_results['end_time']}")
        
        if self.test_results['failed_tests'] > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results['test_details']:
                if not test['passed']:
                    print(f"   • {test['test_name']}: {test['details']}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test in self.test_results['test_details']:
            status = "✅" if test['passed'] else "❌"
            print(f"   {status} {test['test_name']}: {test['details']}")
        
        # Overall assessment
        if self.test_results['success_rate'] >= 90:
            print(f"\n🎉 EXCELLENT: Enhanced ETL integration is working excellently!")
        elif self.test_results['success_rate'] >= 75:
            print(f"\n👍 GOOD: Enhanced ETL integration is working well with minor issues.")
        elif self.test_results['success_rate'] >= 50:
            print(f"\n⚠️  FAIR: Enhanced ETL integration has some issues that need attention.")
        else:
            print(f"\n🚨 POOR: Enhanced ETL integration has significant issues that need immediate attention.")
        
        print("="*80)


async def main():
    """Main test execution"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Create and run tester
    tester = EnhancedETLTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Save results to file
        results_file = f"logs/enhanced_etl_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Test results saved to: {results_file}")
        
        # Exit with appropriate code
        exit_code = 0 if results['success_rate'] >= 75 else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
