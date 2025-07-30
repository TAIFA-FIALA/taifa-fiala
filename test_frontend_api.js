#!/usr/bin/env node

/**
 * Test script to verify frontend API integration works correctly
 * Tests both local development and production API configurations
 */

const API_BASE_URL_DEV = 'http://localhost:8030';
const API_BASE_URL_PROD = 'https://taifa-fiala.net';

async function testApiEndpoint(baseUrl, endpoint, description) {
  console.log(`\n🧪 Testing ${description}...`);
  console.log(`   URL: ${baseUrl}${endpoint}`);
  
  try {
    const response = await fetch(`${baseUrl}${endpoint}`);
    
    if (response.ok) {
      const data = await response.text();
      console.log(`   ✅ SUCCESS: ${response.status} ${response.statusText}`);
      
      // Try to parse as JSON for better output
      try {
        const jsonData = JSON.parse(data);
        console.log(`   📊 Response: ${JSON.stringify(jsonData, null, 2).substring(0, 200)}...`);
      } catch {
        console.log(`   📊 Response: ${data.substring(0, 100)}...`);
      }
    } else {
      console.log(`   ❌ FAILED: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
  }
}

async function runTests() {
  console.log('🚀 TAIFA-FIALA Frontend API Integration Test\n');
  console.log('=' * 50);
  
  // Test development endpoints (direct backend connection)
  console.log('\n📍 DEVELOPMENT ENVIRONMENT TESTS');
  await testApiEndpoint(API_BASE_URL_DEV, '/health', 'Backend Health Check (Dev)');
  await testApiEndpoint(API_BASE_URL_DEV, '/api/v1/organizations/', 'Organizations API (Dev)');
  await testApiEndpoint(API_BASE_URL_DEV, '/api/v1/intelligent-search/opportunities?q=AI&max_results=5', 'Intelligent Search API (Dev)');
  
  // Test production endpoints (through Next.js proxy)
  console.log('\n📍 PRODUCTION ENVIRONMENT TESTS');
  await testApiEndpoint(API_BASE_URL_PROD, '/health', 'Backend Health Check (Prod via Proxy)');
  await testApiEndpoint(API_BASE_URL_PROD, '/api/v1/organizations/', 'Organizations API (Prod via Proxy)');
  await testApiEndpoint(API_BASE_URL_PROD, '/api/v1/intelligent-search/opportunities?q=AI&max_results=5', 'Intelligent Search API (Prod via Proxy)');
  
  console.log('\n🎯 Test Summary:');
  console.log('   - Development should work if backend is running on localhost:8030');
  console.log('   - Production should work after Next.js frontend is redeployed with proxy config');
  console.log('   - If production fails, redeploy frontend with new next.config.ts');
}

// Run the tests
runTests().catch(console.error);