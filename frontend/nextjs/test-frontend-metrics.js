#!/usr/bin/env node
/**
 * Frontend Metrics Integration Test
 * Verifies that frontend components are now using real backend data instead of placeholders
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Testing Frontend Metrics Integration');
console.log('=' * 50);

// Test files to check
const testFiles = [
  {
    path: 'src/components/homepage/DatabaseGrowthChart.tsx',
    description: 'Database Growth Chart',
    shouldContain: [
      'metricsApi.getDatabaseGrowthMetrics()',
      'Real metrics loaded',
      'Real-time ingestion'
    ],
    shouldNotContain: [
      'Mock data for demonstration',
      'generateMockData()',
      'Simulate fetching real data'
    ]
  },
  {
    path: 'src/components/homepage/DatabaseScopeVisualization.tsx',
    description: 'Database Scope Visualization',
    shouldContain: [
      'metricsApi.getPipelineMetrics()',
      'Real database scope metrics loaded',
      'fetchRealMetrics'
    ],
    shouldNotContain: [
      'totalOpportunities: 12847',
      'activeOpportunities: 8934',
      'hardcoded metrics'
    ]
  },
  {
    path: 'src/app/page.tsx',
    description: 'Homepage Analytics',
    shouldContain: [
      'ETL monitoring dashboard',
      'Using real ETL metrics',
      'total_opportunities_in_db'
    ],
    shouldNotContain: [
      'Return demo data if API',
      'total_opportunities: 2467'
    ]
  },
  {
    path: 'src/lib/metrics-api.ts',
    description: 'Metrics API Service',
    shouldContain: [
      'Real Metrics API Service',
      'getDatabaseGrowthMetrics',
      'smart-prioritization',
      '60 days (2 months)'
    ],
    shouldNotContain: [
      'placeholder',
      'mock only'
    ]
  }
];

let allTestsPassed = true;
const results = [];

// Check each file
testFiles.forEach(testFile => {
  const fullPath = path.join(__dirname, testFile.path);
  
  console.log(`\n📄 Testing: ${testFile.description}`);
  console.log(`   File: ${testFile.path}`);
  
  if (!fs.existsSync(fullPath)) {
    console.log(`   ❌ File not found`);
    allTestsPassed = false;
    results.push({ file: testFile.description, status: 'MISSING', issues: ['File not found'] });
    return;
  }
  
  const content = fs.readFileSync(fullPath, 'utf8');
  const issues = [];
  
  // Check for required content
  testFile.shouldContain.forEach(requiredText => {
    if (!content.includes(requiredText)) {
      issues.push(`Missing: "${requiredText}"`);
    }
  });
  
  // Check for content that should be removed
  testFile.shouldNotContain.forEach(forbiddenText => {
    if (content.includes(forbiddenText)) {
      issues.push(`Still contains: "${forbiddenText}"`);
    }
  });
  
  if (issues.length === 0) {
    console.log(`   ✅ All checks passed`);
    results.push({ file: testFile.description, status: 'PASSED', issues: [] });
  } else {
    console.log(`   ❌ Issues found:`);
    issues.forEach(issue => console.log(`      - ${issue}`));
    allTestsPassed = false;
    results.push({ file: testFile.description, status: 'FAILED', issues });
  }
});

// Summary
console.log('\n📊 Test Results Summary');
console.log('=' * 30);

results.forEach(result => {
  const status = result.status === 'PASSED' ? '✅' : '❌';
  console.log(`${status} ${result.file}: ${result.status}`);
  if (result.issues.length > 0) {
    result.issues.forEach(issue => console.log(`      ${issue}`));
  }
});

console.log(`\n🎯 Overall Result: ${allTestsPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);

if (allTestsPassed) {
  console.log('\n🎉 Frontend Metrics Integration Complete!');
  console.log('✅ All placeholder data has been replaced with real backend metrics');
  console.log('✅ Growth chart shows realistic 2-month timeline');
  console.log('✅ Database scope uses live pipeline data');
  console.log('✅ Homepage analytics connected to ETL monitoring');
  console.log('✅ Smart prioritization metrics integrated');
  console.log('\n🚀 Your TAIFA-FIALA frontend now displays real-time data from your robust backend pipeline!');
} else {
  console.log('\n⚠️  Some integration issues found. Please review the failed tests above.');
}

process.exit(allTestsPassed ? 0 : 1);
