#!/usr/bin/env python3
"""
TAIFA 3-Method Data Importation System Test
Tests all three methods of data importation to ensure MVP is working
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class TAIFASystemTester:
    """Test all three data importation methods"""
    
    def __init__(self):
        self.test_results = {
            "method_1_user_submission": False,
            "method_2_admin_scraping": False,
            "method_3_automated_discovery": False,
            "backend_health": False,
            "frontend_health": False
        }
    
    async def run_full_test(self):
        """Run comprehensive test of all three methods"""
        print("🚀 Starting TAIFA 3-Method System Test...")
        print("=" * 60)
        
        # Test backend health
        await self.test_backend_health()
        
        # Test Method 1: User Submissions
        await self.test_method_1_user_submission()
        
        # Test Method 2: Admin Portal Scraping
        await self.test_method_2_admin_scraping()
        
        # Test Method 3: Automated Discovery
        await self.test_method_3_automated_discovery()
        
        # Test frontend integration
        await self.test_frontend_integration()
        
        # Report results
        self.print_test_report()
    
    async def test_backend_health(self):
        """Test backend API health"""
        print("\n🔍 Testing Backend Health...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test main health endpoint
                async with session.get(f"{BACKEND_URL}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Backend health: {data.get('status', 'unknown')}")
                        self.test_results["backend_health"] = True
                    else:
                        print(f"❌ Backend health check failed: {response.status}")
                
                # Test API endpoints health
                endpoints = [
                    "/api/v1/submissions/health",
                    "/api/v1/admin/scraping/health", 
                    "/api/v1/discovery/health"
                ]
                
                for endpoint in endpoints:
                    try:
                        async with session.get(f"{BACKEND_URL}{endpoint}") as response:
                            if response.status == 200:
                                data = await response.json()
                                service = data.get('service', endpoint.split('/')[-2])
                                print(f"✅ {service} service: healthy")
                            else:
                                print(f"❌ {endpoint}: {response.status}")
                    except Exception as e:
                        print(f"❌ {endpoint}: {e}")
                        
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
    
    async def test_method_1_user_submission(self):
        """Test Method 1: User submission through API"""
        print("\n📝 Testing Method 1: User Submissions...")
        
        # Sample submission data
        test_submission = {
            "title": "Test AI Health Grant Program",
            "organization": "Test Foundation",
            "description": "This is a test submission for AI health innovation in Africa. The program focuses on machine learning applications for healthcare in African countries, particularly Kenya, Nigeria, and Rwanda. Funding supports research and implementation of artificial intelligence solutions.",
            "url": "https://example.com/test-funding",
            "amount": 50000,
            "currency": "USD",
            "deadline": "2024-12-31",
            "contactEmail": "test@example.com"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/v1/submissions/create",
                    json=test_submission,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ User submission successful!")
                        print(f"   - Submission ID: {result.get('submission_id', 'N/A')}")
                        print(f"   - Validation Score: {result.get('validation_score', 'N/A')}")
                        print(f"   - Requires Review: {result.get('requires_review', 'N/A')}")
                        self.test_results["method_1_user_submission"] = True
                    else:
                        error_data = await response.text()
                        print(f"❌ User submission failed: {response.status}")
                        print(f"   Error: {error_data}")
                        
        except Exception as e:
            print(f"❌ Method 1 test failed: {e}")
    
    async def test_method_2_admin_scraping(self):
        """Test Method 2: Admin portal scraping"""
        print("\n🛠️ Testing Method 2: Admin Portal Scraping...")
        
        # Sample scraping job
        test_scraping_job = {
            "url": "https://www.gatesfoundation.org/ideas/articles/digital-financial-services-africa",
            "source_type": "foundation",
            "priority": "medium",
            "description": "Test scraping of Gates Foundation page"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/v1/admin/scraping/process-url",
                    json=test_scraping_job,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Admin scraping job created!")
                        print(f"   - Job ID: {result.get('job_id', 'N/A')}")
                        print(f"   - Status: {result.get('status', 'N/A')}")
                        print(f"   - Estimated completion: {result.get('estimated_completion', 'N/A')}")
                        
                        # Check job status after a delay
                        job_id = result.get('job_id')
                        if job_id:
                            await asyncio.sleep(5)  # Wait for processing
                            await self.check_scraping_job_status(session, job_id)
                        
                        self.test_results["method_2_admin_scraping"] = True
                    else:
                        error_data = await response.text()
                        print(f"❌ Admin scraping failed: {response.status}")
                        print(f"   Error: {error_data}")
                        
        except Exception as e:
            print(f"❌ Method 2 test failed: {e}")
    
    async def check_scraping_job_status(self, session: aiohttp.ClientSession, job_id: str):
        """Check the status of a scraping job"""
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/admin/scraping/jobs/{job_id}") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print(f"   - Job Status Update: {status_data.get('status', 'unknown')}")
                    if status_data.get('opportunities_found', 0) > 0:
                        print(f"   - Opportunities Found: {status_data['opportunities_found']}")
                else:
                    print(f"   - Status check failed: {response.status}")
        except Exception as e:
            print(f"   - Status check error: {e}")
    
    async def test_method_3_automated_discovery(self):
        """Test Method 3: Automated discovery"""
        print("\n🤖 Testing Method 3: Automated Discovery...")
        
        # Sample discovery job
        test_discovery_job = {
            "search_terms": ["AI grants Africa", "technology funding"],
            "search_type": "targeted",
            "priority": "high",
            "max_results": 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/api/v1/discovery/start-discovery",
                    json=test_discovery_job,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Automated discovery job created!")
                        print(f"   - Job ID: {result.get('job_id', 'N/A')}")
                        print(f"   - Search Type: {result.get('search_type', 'N/A')}")
                        print(f"   - Estimated completion: {result.get('estimated_completion', 'N/A')}")
                        
                        # Check job status after a delay
                        job_id = result.get('job_id')
                        if job_id:
                            await asyncio.sleep(5)  # Wait for processing
                            await self.check_discovery_job_status(session, job_id)
                        
                        self.test_results["method_3_automated_discovery"] = True
                    else:
                        error_data = await response.text()
                        print(f"❌ Automated discovery failed: {response.status}")
                        print(f"   Error: {error_data}")
                        
        except Exception as e:
            print(f"❌ Method 3 test failed: {e}")
    
    async def check_discovery_job_status(self, session: aiohttp.ClientSession, job_id: str):
        """Check the status of a discovery job"""
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/discovery/jobs/{job_id}") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print(f"   - Job Status Update: {status_data.get('status', 'unknown')}")
                    if status_data.get('opportunities_discovered', 0) > 0:
                        print(f"   - Opportunities Discovered: {status_data['opportunities_discovered']}")
                else:
                    print(f"   - Status check failed: {response.status}")
        except Exception as e:
            print(f"   - Status check error: {e}")
    
    async def test_frontend_integration(self):
        """Test frontend integration"""
        print("\n🖥️ Testing Frontend Integration...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test Next.js frontend
                async with session.get(f"{FRONTEND_URL}") as response:
                    if response.status == 200:
                        print("✅ Next.js frontend accessible")
                        self.test_results["frontend_health"] = True
                    else:
                        print(f"❌ Next.js frontend failed: {response.status}")
                
                # Test Next.js API route
                test_data = {
                    "title": "Frontend Test Grant",
                    "organization": "Test Org", 
                    "description": "Test submission through Next.js API route for AI funding in Africa",
                    "url": "https://example.com/test"
                }
                
                async with session.post(
                    f"{FRONTEND_URL}/api/submissions/create",
                    json=test_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Next.js API route working")
                        print(f"   - Response: {result.get('status', 'unknown')}")
                    else:
                        error_data = await response.text()
                        print(f"❌ Next.js API route failed: {response.status}")
                        print(f"   Error: {error_data}")
                        
        except Exception as e:
            print(f"❌ Frontend integration test failed: {e}")
    
    def print_test_report(self):
        """Print final test report"""
        print("\n" + "=" * 60)
        print("📊 TAIFA 3-Method System Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        print(f"Overall Status: {passed_tests}/{total_tests} tests passed")
        print()
        
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            test_display = test_name.replace("_", " ").title()
            print(f"{status} - {test_display}")
        
        print("\n" + "=" * 60)
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Your 3-method MVP is ready!")
            print("\nNext steps:")
            print("1. Access Streamlit admin portal at http://localhost:8501")
            print("2. Access Next.js frontend at http://localhost:3000")
            print("3. Submit test opportunities through both interfaces")
            print("4. Monitor data collection through the admin portal")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            print("\nTroubleshooting:")
            print("1. Ensure backend is running: docker-compose up backend")
            print("2. Ensure frontend is running: cd frontend/nextjs_dashboard && npm run dev")
            print("3. Check environment variables and database connections")
        
        print("\n🌍 TAIFA-FIALA: Democratizing AI funding access across Africa!")

async def main():
    """Main test execution"""
    tester = TAIFASystemTester()
    await tester.run_full_test()

if __name__ == "__main__":
    print("🚀 TAIFA 3-Method Data Importation System Test")
    print("Testing all three data collection methods...")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
