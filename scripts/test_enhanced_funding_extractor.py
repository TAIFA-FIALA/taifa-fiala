#!/usr/bin/env python3
"""
Test Enhanced Funding Extractor
Tests the enhanced_funding_extractor.py module directly without complex dependencies

This script tests:
1. Enhanced funding pattern recognition (total pool, exact amount, range)
2. Target audience extraction
3. AI subsector identification
4. Deadline and process information extraction
5. Focus indicators (gender, youth, collaboration)

Usage:
    python scripts/test_enhanced_funding_extractor.py
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the enhanced funding extractor
from backend.app.services.etl.enhanced_funding_extractor import EnhancedFundingExtractor, EnhancedETLPipeline

def test_enhanced_funding_extractor():
    """Test the enhanced funding extractor with comprehensive test cases"""
    
    print("🧪 Testing Enhanced Funding Extractor")
    print("=" * 60)
    
    extractor = EnhancedFundingExtractor()
    pipeline = EnhancedETLPipeline()
    
    # Test cases covering all three funding patterns and enhanced fields
    test_cases = [
        {
            'name': 'Total Pool Pattern - Basic',
            'text': 'The African Innovation Fund announces $5 million total funding to support 10-15 AI startups across the continent.',
            'expected_funding_type': 'total_pool',
            'expected_fields': ['total_funding_pool', 'estimated_project_count', 'currency']
        },
        {
            'name': 'Total Pool Pattern - Complex',
            'text': 'Gates Foundation launches $10M initiative supporting African AI startups. The fund will support up to 20 projects focusing on healthcare AI solutions.',
            'expected_funding_type': 'total_pool',
            'expected_fields': ['total_funding_pool', 'estimated_project_count', 'ai_subsectors']
        },
        {
            'name': 'Exact Amount Pattern - Basic',
            'text': 'Each selected project will receive exactly $50,000 to develop AI solutions for healthcare challenges.',
            'expected_funding_type': 'per_project_exact',
            'expected_fields': ['exact_amount_per_project', 'ai_subsectors']
        },
        {
            'name': 'Exact Amount Pattern - Complex',
            'text': 'Mozilla Foundation offers grants of $75,000 each for women-led AI projects focusing on digital privacy and inclusion in African communities.',
            'expected_funding_type': 'per_project_exact',
            'expected_fields': ['exact_amount_per_project', 'gender_focused', 'target_audience']
        },
        {
            'name': 'Range Pattern - Basic',
            'text': 'Grants ranging from $25,000 to $100,000 are available for women-led AI ventures focusing on fintech and edtech.',
            'expected_funding_type': 'per_project_range',
            'expected_fields': ['min_amount_per_project', 'max_amount_per_project', 'gender_focused', 'ai_subsectors']
        },
        {
            'name': 'Range Pattern - Complex',
            'text': 'USAID AI Innovation Challenge offers funding between $50,000 and $200,000 for startups and researchers developing AI solutions for agriculture and climate change. Applications due March 15, 2024. Women entrepreneurs encouraged to apply.',
            'expected_funding_type': 'per_project_range',
            'expected_fields': ['min_amount_per_project', 'max_amount_per_project', 'target_audience', 'ai_subsectors', 'deadline_info', 'gender_focused']
        },
        {
            'name': 'Comprehensive Pattern',
            'text': 'The World Bank Digital Africa Initiative announces $500M total funding to support 100-150 AI and digital transformation projects. Each project receives between €75,000 and €250,000. Priority given to women-led startups and young entrepreneurs. Applications due December 31, 2024. Focus areas include fintech, healthcare, education, and agriculture.',
            'expected_funding_type': 'total_pool',  # Should detect total pool first
            'expected_fields': ['total_funding_pool', 'estimated_project_count', 'currency', 'gender_focused', 'youth_focused', 'target_audience', 'ai_subsectors', 'deadline_info']
        },
        {
            'name': 'Youth and Collaboration Focus',
            'text': 'Microsoft AI for Good Lab launches program for young researchers under 30. Collaborative projects between universities and startups receive up to $150,000. Focus on machine learning and computer vision applications.',
            'expected_funding_type': 'per_project_range',
            'expected_fields': ['max_amount_per_project', 'youth_focused', 'collaboration_required', 'target_audience', 'ai_subsectors']
        }
    ]
    
    # Track test results
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    test_details = []
    
    for test_case in test_cases:
        total_tests += 1
        print(f"\n🔍 Test: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        
        try:
            # Extract funding information
            result = extractor.extract_funding_info(test_case['text'])
            
            # Check funding type
            funding_type = result.get('funding_type')
            funding_type_correct = funding_type == test_case['expected_funding_type']
            
            # Check expected fields
            fields_found = []
            fields_missing = []
            
            for field in test_case['expected_fields']:
                if field in ['gender_focused', 'youth_focused', 'collaboration_required']:
                    # Check focus indicators
                    if result.get('focus_indicators', {}).get(field):
                        fields_found.append(field)
                    else:
                        fields_missing.append(field)
                elif field in ['target_audience', 'ai_subsectors']:
                    # Check list fields
                    if result.get(field) and len(result[field]) > 0:
                        fields_found.append(field)
                    else:
                        fields_missing.append(field)
                elif field == 'deadline_info':
                    # Check deadline info
                    if result.get('deadline_info') and len(result['deadline_info']) > 0:
                        fields_found.append(field)
                    else:
                        fields_missing.append(field)
                elif field == 'estimated_project_count':
                    # Check project count (either estimated_count or count_range)
                    if (result.get('estimated_project_count') is not None or 
                        result.get('project_count_range') is not None):
                        fields_found.append(field)
                    else:
                        fields_missing.append(field)
                else:
                    # Check regular fields
                    if result.get(field) is not None:
                        fields_found.append(field)
                    else:
                        fields_missing.append(field)
            
            # Calculate success rate
            expected_field_count = len(test_case['expected_fields'])
            found_field_count = len(fields_found)
            field_success_rate = found_field_count / expected_field_count if expected_field_count > 0 else 1.0
            
            # Test passes if funding type is correct and at least 70% of fields are found
            test_passed = funding_type_correct and field_success_rate >= 0.7
            
            if test_passed:
                passed_tests += 1
                print(f"✅ PASSED")
            else:
                failed_tests += 1
                print(f"❌ FAILED")
            
            print(f"   Funding Type: {funding_type} (expected: {test_case['expected_funding_type']}) {'✓' if funding_type_correct else '✗'}")
            print(f"   Fields Found: {found_field_count}/{expected_field_count} ({field_success_rate:.1%})")
            print(f"   Found: {fields_found}")
            if fields_missing:
                print(f"   Missing: {fields_missing}")
            
            # Show key extracted data
            key_data = {}
            if result.get('total_funding_pool'):
                key_data['total_pool'] = f"{result['currency']} {result['total_funding_pool']:,.0f}"
            if result.get('exact_amount_per_project'):
                key_data['exact_amount'] = f"{result['currency']} {result['exact_amount_per_project']:,.0f}"
            if result.get('min_amount_per_project') and result.get('max_amount_per_project'):
                key_data['range'] = f"{result['currency']} {result['min_amount_per_project']:,.0f} - {result['max_amount_per_project']:,.0f}"
            if result.get('target_audience'):
                key_data['audience'] = result['target_audience']
            if result.get('ai_subsectors'):
                key_data['subsectors'] = result['ai_subsectors']
            
            if key_data:
                print(f"   Key Data: {key_data}")
            
            test_details.append({
                'name': test_case['name'],
                'passed': test_passed,
                'funding_type_correct': funding_type_correct,
                'field_success_rate': field_success_rate,
                'fields_found': fields_found,
                'fields_missing': fields_missing,
                'key_data': key_data
            })
            
        except Exception as e:
            failed_tests += 1
            print(f"❌ FAILED - Exception: {str(e)}")
            test_details.append({
                'name': test_case['name'],
                'passed': False,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("🧪 ENHANCED FUNDING EXTRACTOR TEST SUMMARY")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ FAILED TESTS:")
        for test in test_details:
            if not test['passed']:
                print(f"   • {test['name']}")
                if 'error' in test:
                    print(f"     Error: {test['error']}")
                elif 'field_success_rate' in test:
                    print(f"     Field Success: {test['field_success_rate']:.1%}, Missing: {test.get('fields_missing', [])}")
    
    # Overall assessment
    if success_rate >= 90:
        print(f"\n🎉 EXCELLENT: Enhanced funding extractor is working excellently!")
    elif success_rate >= 75:
        print(f"\n👍 GOOD: Enhanced funding extractor is working well with minor issues.")
    elif success_rate >= 50:
        print(f"\n⚠️  FAIR: Enhanced funding extractor has some issues that need attention.")
    else:
        print(f"\n🚨 POOR: Enhanced funding extractor has significant issues that need immediate attention.")
    
    print("=" * 60)
    
    return success_rate >= 75


def test_rss_processing():
    """Test RSS item processing with enhanced extraction"""
    
    print("\n🔄 Testing RSS Processing with Enhanced Extraction")
    print("=" * 60)
    
    pipeline = EnhancedETLPipeline()
    
    # Test RSS items
    test_rss_items = [
        {
            'title': 'Gates Foundation Announces $5M AI for Africa Initiative',
            'description': 'The Gates Foundation is launching a new $5 million initiative to support AI startups across Africa, with grants ranging from $50,000 to $200,000 per project. Applications due December 31, 2024.',
            'link': 'https://gatesfoundation.org/ai-africa-initiative'
        },
        {
            'title': 'African Development Bank Launches Tech Innovation Fund',
            'description': 'The AfDB announces a $10 million fund to support technology innovation across Africa, with particular focus on AI and fintech solutions. Each project receives exactly $75,000.',
            'link': 'https://afdb.org/tech-innovation-fund'
        },
        {
            'title': 'Mozilla Foundation AI Grant Program for Women',
            'description': 'Mozilla Foundation offers grants up to $100,000 for AI projects led by women that promote digital inclusion and privacy in African communities.',
            'link': 'https://mozilla.org/ai-grants-women'
        }
    ]
    
    processed_items = []
    
    for i, rss_item in enumerate(test_rss_items, 1):
        print(f"\n📰 Processing RSS Item {i}: {rss_item['title']}")
        
        try:
            processed_item = pipeline.process_rss_item(rss_item)
            processed_items.append(processed_item)
            
            # Show key processed fields
            print(f"   ✅ Processed successfully")
            print(f"   Funding Type: {processed_item.get('funding_type', 'N/A')}")
            print(f"   Currency: {processed_item.get('currency', 'N/A')}")
            
            if processed_item.get('total_funding_pool'):
                print(f"   Total Pool: {processed_item['currency']} {processed_item['total_funding_pool']:,.0f}")
            if processed_item.get('exact_amount_per_project'):
                print(f"   Exact Amount: {processed_item['currency']} {processed_item['exact_amount_per_project']:,.0f}")
            if processed_item.get('min_amount_per_project') and processed_item.get('max_amount_per_project'):
                print(f"   Range: {processed_item['currency']} {processed_item['min_amount_per_project']:,.0f} - {processed_item['max_amount_per_project']:,.0f}")
            
            if processed_item.get('target_audience'):
                print(f"   Target Audience: {processed_item['target_audience']}")
            if processed_item.get('ai_subsectors'):
                print(f"   AI Subsectors: {processed_item['ai_subsectors']}")
            if processed_item.get('gender_focused'):
                print(f"   Gender Focused: {processed_item['gender_focused']}")
            
        except Exception as e:
            print(f"   ❌ Processing failed: {str(e)}")
    
    print(f"\n📊 RSS Processing Summary:")
    print(f"   Items Processed: {len(processed_items)}/{len(test_rss_items)}")
    print(f"   Success Rate: {len(processed_items)/len(test_rss_items)*100:.1f}%")
    
    return len(processed_items) == len(test_rss_items)


def main():
    """Main test execution"""
    print("🚀 Starting Enhanced Funding Extractor Tests")
    print("=" * 60)
    
    # Test 1: Enhanced funding extractor
    extractor_success = test_enhanced_funding_extractor()
    
    # Test 2: RSS processing
    rss_success = test_rss_processing()
    
    # Overall results
    print("\n🏁 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Enhanced Funding Extractor: {'✅ PASSED' if extractor_success else '❌ FAILED'}")
    print(f"RSS Processing: {'✅ PASSED' if rss_success else '❌ FAILED'}")
    
    overall_success = extractor_success and rss_success
    print(f"\nOverall Status: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n✨ The enhanced funding extractor is working correctly and ready for integration!")
    else:
        print("\n🔧 Some issues were found that may need attention before full deployment.")
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
