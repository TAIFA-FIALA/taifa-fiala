#!/usr/bin/env python3
"""
TAIFA CrewAI Pipeline Test Suite
Comprehensive testing for the enhanced ETL pipeline
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import components to test
from data_processors.crews.enhanced_funding_crew import EnhancedAfricaIntelligenceItemProcessor
from data_processors.crews.organization_enrichment_crew import OrganizationEnrichmentPipeline
from data_processors.translation.translation_pipeline import TranslationPipelineService, create_translation_service
from data_processors.community.validation_service import CommunityValidationService, create_validation_service
from data_processors.crewai_pipeline_main import TaifaCrewAIPipeline, create_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CrewAITestSuite:
    """Comprehensive test suite for CrewAI components"""
    
    def __init__(self):
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "start_time": datetime.utcnow(),
            "details": {}
        }
    
    async def run_all_tests(self):
        """Run all test suites"""
        
        print("🧪 Starting TAIFA CrewAI Test Suite")
        print("=" * 50)
        
        # Test individual components
        await self.test_intelligence_item_processor()
        await self.test_organization_enrichment()
        await self.test_translation_pipeline()
        await self.test_community_validation()
        await self.test_integration_pipeline()
        
        # Generate test report
        self.generate_test_report()
    
    async def test_intelligence_item_processor(self):
        """Test the enhanced intelligence item processor"""
        
        print("\n🔍 Testing Enhanced Intelligence Item Processor...")
        
        try:
            # Create test data
            test_opportunity = {
                "title": "AI Research Grant for African Universities",
                "snippet": "The Gates Foundation announces $5M in funding for AI research projects at universities across Sub-Saharan Africa, focusing on healthcare applications.",
                "link": "https://www.gatesfoundation.org/ai-research-grant-2025",
                "source_type": "test"
            }
            
            # Initialize processor
            processor = EnhancedAfricaIntelligenceItemProcessor()
            
            # Process opportunity
            start_time = time.time()
            result = await processor.process_opportunity_enhanced(test_opportunity)
            processing_time = time.time() - start_time
            
            # Validate results
            assert result is not None, "Processing result should not be None"
            assert "title" in result, "Result should contain title"
            assert "overall_confidence" in result, "Result should contain confidence score"
            assert "review_status" in result, "Result should contain review status"
            
            # Check confidence scores
            confidence = result.get("overall_confidence", 0)
            assert 0 <= confidence <= 1, f"Confidence should be between 0 and 1, got {confidence}"
            
            self.record_test_result("funding_processor", True, {
                "processing_time": processing_time,
                "confidence_score": confidence,
                "review_status": result.get("review_status"),
                "conflicts_detected": len(result.get("processing_metadata", {}).get("conflicts_detected", {}))
            })
            
            print(f"✅ Funding processor test passed (confidence: {confidence:.2f}, time: {processing_time:.2f}s)")
            
        except Exception as e:
            self.record_test_result("funding_processor", False, {"error": str(e)})
            print(f"❌ Funding processor test failed: {e}")
    
    async def test_organization_enrichment(self):
        """Test organization enrichment pipeline"""
        
        print("\n🏢 Testing Organization Enrichment Pipeline...")
        
        try:
            # Initialize pipeline with mock token
            pipeline = OrganizationEnrichmentPipeline("mock_apify_token")
            
            # Test organization enrichment
            start_time = time.time()
            result = await pipeline.enrich_organization(
                org_name="Gates Foundation",
                org_type="foundation",
                org_country="USA",
                trigger_source="test"
            )
            processing_time = time.time() - start_time
            
            # Validate results
            assert result is not None, "Enrichment result should not be None"
            assert "organization_name" in result, "Result should contain organization name"
            assert "enrichment_status" in result, "Result should contain enrichment status"
            
            # Check status
            status = result.get("enrichment_status")
            assert status in ["completed", "failed", "locked"], f"Invalid status: {status}"
            
            self.record_test_result("organization_enrichment", True, {
                "processing_time": processing_time,
                "enrichment_status": status,
                "has_basic_info": "basic_info" in result,
                "has_enriched_data": "enriched_data" in result
            })
            
            print(f"✅ Organization enrichment test passed (status: {status}, time: {processing_time:.2f}s)")
            
        except Exception as e:
            self.record_test_result("organization_enrichment", False, {"error": str(e)})
            print(f"❌ Organization enrichment test failed: {e}")
    
    async def test_translation_pipeline(self):
        """Test translation pipeline"""
        
        print("\n🌐 Testing Translation Pipeline...")
        
        try:
            # Create mock provider configs
            provider_configs = {
                "azure_translator": {
                    "api_key": "mock_azure_key",
                    "region": "eastus"
                }
            }
            
            # Initialize translation service
            service = TranslationPipelineService(provider_configs)
            
            # Test translation request
            test_content = {
                "title": "AI Research Grant",
                "description": "This grant supports artificial intelligence research in Africa."
            }
            
            start_time = time.time()
            request_id = await service.translate_manual_submission(test_content)
            processing_time = time.time() - start_time
            
            # Validate results
            assert request_id is not None, "Request ID should not be None"
            assert isinstance(request_id, str), "Request ID should be a string"
            
            # Check queue status
            status = service.get_status()
            assert "queue_status" in status, "Status should contain queue information"
            
            self.record_test_result("translation_pipeline", True, {
                "processing_time": processing_time,
                "request_id": request_id,
                "queue_status": status["queue_status"]
            })
            
            print(f"✅ Translation pipeline test passed (request_id: {request_id[:12]}..., time: {processing_time:.2f}s)")
            
        except Exception as e:
            self.record_test_result("translation_pipeline", False, {"error": str(e)})
            print(f"❌ Translation pipeline test failed: {e}")
    
    async def test_community_validation(self):
        """Test community validation service"""
        
        print("\n👥 Testing Community Validation Service...")
        
        try:
            # Initialize validation service
            service = await create_validation_service()
            
            # Test newsletter preparation (will not send emails in test)
            start_time = time.time()
            batch_id = await service.prepare_daily_newsletter()
            processing_time = time.time() - start_time
            
            # Validate results (batch_id might be None if no opportunities)
            if batch_id:
                assert isinstance(batch_id, str), "Batch ID should be a string"
                assert batch_id.startswith("newsletter_"), "Batch ID should have correct prefix"
            
            # Test validation statistics
            stats = service.get_validation_statistics()
            assert "validators" in stats, "Stats should contain validator information"
            assert "validations" in stats, "Stats should contain validation information"
            
            self.record_test_result("community_validation", True, {
                "processing_time": processing_time,
                "batch_id": batch_id,
                "validator_count": stats["validators"]["total"],
                "active_validators": stats["validators"]["active"]
            })
            
            print(f"✅ Community validation test passed (batch_id: {batch_id}, time: {processing_time:.2f}s)")
            
        except Exception as e:
            self.record_test_result("community_validation", False, {"error": str(e)})
            print(f"❌ Community validation test failed: {e}")
    
    async def test_integration_pipeline(self):
        """Test the complete integration pipeline"""
        
        print("\n🔗 Testing Complete Integration Pipeline...")
        
        try:
            # Create test configuration
            test_config = {
                "apify_api_token": "mock_token",
                "translation_providers": {
                    "azure_translator": {
                        "api_key": "mock_key",
                        "region": "eastus"
                    }
                }
            }
            
            # Initialize pipeline
            pipeline = TaifaCrewAIPipeline(test_config)
            await pipeline.initialize()
            
            # Test pipeline status
            start_time = time.time()
            status = await pipeline.get_pipeline_status()
            processing_time = time.time() - start_time
            
            # Validate results
            assert status is not None, "Pipeline status should not be None"
            assert "pipeline" in status, "Status should contain pipeline info"
            assert "components" in status, "Status should contain component info"
            
            # Check component initialization
            components = status["components"]
            assert components["funding_processor"], "Funding processor should be initialized"
            assert components["organization_enricher"], "Organization enricher should be initialized"
            
            # Test manual submission processing
            test_submission = {
                "title": "Test Manual Submission",
                "description": "This is a test intelligence item submitted manually",
                "source_type": "manual_test"
            }
            
            manual_result = await pipeline.process_manual_submission(test_submission)
            assert manual_result is not None, "Manual submission result should not be None"
            
            # Cleanup
            await pipeline.shutdown()
            
            self.record_test_result("integration_pipeline", True, {
                "status_check_time": processing_time,
                "components_initialized": sum(components.values()),
                "manual_submission_processed": "error" not in manual_result
            })
            
            print(f"✅ Integration pipeline test passed (components: {sum(components.values())}/4, time: {processing_time:.2f}s)")
            
        except Exception as e:
            self.record_test_result("integration_pipeline", False, {"error": str(e)})
            print(f"❌ Integration pipeline test failed: {e}")
    
    def record_test_result(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Record test result"""
        
        self.test_results["tests_run"] += 1
        
        if passed:
            self.test_results["tests_passed"] += 1
        else:
            self.test_results["tests_failed"] += 1
            self.test_results["errors"].append({
                "test": test_name,
                "details": details
            })
        
        self.test_results["details"][test_name] = {
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        self.test_results["end_time"] = datetime.utcnow()
        self.test_results["total_time"] = (
            self.test_results["end_time"] - self.test_results["start_time"]
        ).total_seconds()
        
        print("\n" + "=" * 50)
        print("📊 TAIFA CrewAI Test Results")
        print("=" * 50)
        
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']} ✅")
        print(f"Tests Failed: {self.test_results['tests_failed']} ❌")
        print(f"Success Rate: {(self.test_results['tests_passed'] / max(self.test_results['tests_run'], 1)) * 100:.1f}%")
        print(f"Total Time: {self.test_results['total_time']:.2f} seconds")
        
        if self.test_results["tests_failed"] > 0:
            print("\n❌ Failed Tests:")
            for error in self.test_results["errors"]:
                print(f"  - {error['test']}: {error['details'].get('error', 'Unknown error')}")
        
        print("\n📋 Test Details:")
        for test_name, details in self.test_results["details"].items():
            status = "✅ PASS" if details["passed"] else "❌ FAIL"
            print(f"  {test_name}: {status}")
            
            if details["passed"] and "processing_time" in details["details"]:
                time_taken = details["details"]["processing_time"]
                print(f"    Processing time: {time_taken:.2f}s")
        
        # Save detailed results to file
        with open("tests/test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: tests/test_results.json")
        
        # Overall result
        if self.test_results["tests_failed"] == 0:
            print("\n🎉 All tests passed! CrewAI pipeline is ready for deployment.")
        else:
            print(f"\n⚠️  {self.test_results['tests_failed']} tests failed. Please review and fix issues before deployment.")

async def run_quick_test():
    """Run a quick smoke test of key components"""
    
    print("🚀 Running Quick CrewAI Smoke Test...")
    
    try:
        # Test 1: Basic funding processor initialization
        processor = EnhancedAfricaIntelligenceItemProcessor()
        print("✅ Funding processor initialized")
        
        # Test 2: Organization enrichment initialization
        enricher = OrganizationEnrichmentPipeline("mock_token")
        print("✅ Organization enricher initialized")
        
        # Test 3: Translation service initialization
        translation_service = TranslationPipelineService({})
        print("✅ Translation service initialized")
        
        # Test 4: Community validation initialization
        validation_service = await create_validation_service()
        print("✅ Community validation service initialized")
        
        print("\n🎉 Quick smoke test completed successfully!")
        print("All core components can be initialized without errors.")
        
    except Exception as e:
        print(f"\n❌ Quick smoke test failed: {e}")
        return False
    
    return True

async def run_performance_test():
    """Run performance benchmarks"""
    
    print("⚡ Running CrewAI Performance Tests...")
    
    # Test data
    test_opportunities = [
        {
            "title": f"Test Opportunity {i}",
            "snippet": f"This is test opportunity number {i} for performance testing",
            "link": f"https://example.com/opportunity-{i}",
            "source_type": "performance_test"
        }
        for i in range(10)
    ]
    
    try:
        processor = EnhancedAfricaIntelligenceItemProcessor()
        
        # Measure processing time for batch
        start_time = time.time()
        
        results = []
        for opportunity in test_opportunities:
            result = await processor.process_opportunity_enhanced(opportunity)
            results.append(result)
        
        total_time = time.time() - start_time
        avg_time = total_time / len(test_opportunities)
        
        print(f"📊 Performance Results:")
        print(f"  Total opportunities: {len(test_opportunities)}")
        print(f"  Total processing time: {total_time:.2f}s")
        print(f"  Average time per opportunity: {avg_time:.2f}s")
        print(f"  Throughput: {len(test_opportunities) / total_time:.1f} opportunities/second")
        
        # Check for any failures
        failures = [r for r in results if "error" in r]
        print(f"  Failures: {len(failures)}")
        
        if len(failures) == 0:
            print("✅ Performance test completed successfully!")
        else:
            print("⚠️ Some opportunities failed processing")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TAIFA CrewAI Test Suite")
    parser.add_argument("--mode", choices=["full", "quick", "performance"], 
                       default="quick", help="Test mode to run")
    parser.add_argument("--output", help="Output file for test results")
    
    args = parser.parse_args()
    
    # Ensure test directory exists
    os.makedirs("tests", exist_ok=True)
    
    if args.mode == "full":
        # Run comprehensive test suite
        test_suite = CrewAITestSuite()
        asyncio.run(test_suite.run_all_tests())
        
    elif args.mode == "quick":
        # Run quick smoke test
        success = asyncio.run(run_quick_test())
        exit(0 if success else 1)
        
    elif args.mode == "performance":
        # Run performance benchmarks
        asyncio.run(run_performance_test())
