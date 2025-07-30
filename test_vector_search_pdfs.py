#!/usr/bin/env python3
"""
Test Vector Search for PDF Ingestions
Test if manually ingested PDFs are being vectorized and searchable
"""

import asyncio
import sys
from pathlib import Path
import requests
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_vector_search_for_pdfs():
    """Test if our recently ingested PDFs are searchable via vector search"""
    
    print("🔍 Testing Vector Search for PDF Ingestions")
    print("=" * 60)
    
    # Test queries based on the PDFs we just ingested
    test_queries = [
        {
            "query": "African Development Bank Ghana Rwanda Zambia AI customer management",
            "expected_content": "African Development Bank",
            "description": "Should find the ADB HTML document we ingested"
        },
        {
            "query": "Google 37 million investment Africa AI",
            "expected_content": "Google",
            "description": "Should find the Google AI investment PDF"
        },
        {
            "query": "AI artificial intelligence funding Africa startup",
            "expected_content": "AI",
            "description": "General AI funding search"
        },
        {
            "query": "machine learning technology investment",
            "expected_content": "investment",
            "description": "Semantic search for ML/tech funding"
        }
    ]
    
    base_url = "http://localhost:8030/api/v1/intelligent-search"
    
    print(f"🌐 Testing endpoint: {base_url}/opportunities")
    print()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"📋 Test {i}: {test_case['description']}")
        print(f"🔍 Query: '{test_case['query']}'")
        
        try:
            # Test the intelligent search endpoint
            response = requests.get(f"{base_url}/opportunities", params={
                "q": test_case["query"],
                "min_relevance": 0.3,  # Lower threshold to catch more results
                "max_results": 10
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                metadata = data.get("search_metadata", {})
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Results found: {len(results)}")
                print(f"🔧 Search strategy: {metadata.get('search_strategy', 'unknown')}")
                print(f"🎯 Vector enhancement used: {metadata.get('vector_enhancement_used', False)}")
                
                if results:
                    print(f"📄 Sample results:")
                    for j, result in enumerate(results[:3]):  # Show first 3 results
                        title = result.get('title', 'No title')[:80]
                        score = result.get('composite_score', result.get('relevance_score', 0))
                        source = result.get('source_url', result.get('source_type', 'unknown'))
                        
                        print(f"  {j+1}. {title}... (score: {score:.3f})")
                        print(f"     Source: {source}")
                        
                        # Check if expected content is found
                        content_found = (
                            test_case["expected_content"].lower() in title.lower() or
                            test_case["expected_content"].lower() in result.get('description', '').lower()
                        )
                        
                        if content_found:
                            print(f"     ✅ Expected content '{test_case['expected_content']}' found!")
                        
                else:
                    print("⚠️ No results found")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the backend running on port 8030?")
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
        print()
    
    # Test if we can check vector database directly
    print("🔍 Testing Direct Vector Database Access")
    print("-" * 40)
    
    try:
        # Try to import and test vector services
        from app.services.funding_intelligence.vector_intelligence import FundingIntelligenceVectorDB
        
        vector_db = FundingIntelligenceVectorDB()
        
        if hasattr(vector_db, 'index') and vector_db.index:
            # Get index stats
            stats = vector_db.index.describe_index_stats()
            print(f"📊 Vector Database Stats:")
            print(f"  • Total vectors: {stats.total_vector_count}")
            print(f"  • Dimension: {stats.dimension}")
            print(f"  • Index fullness: {stats.index_fullness}")
            
            if stats.total_vector_count > 0:
                print("✅ Vector database has content!")
            else:
                print("⚠️ Vector database appears to be empty")
        else:
            print("⚠️ Could not access vector database index")
            
    except ImportError as e:
        print(f"⚠️ Could not import vector services: {e}")
    except Exception as e:
        print(f"❌ Error accessing vector database: {e}")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 60)
    
    print("1. If search results are found:")
    print("   ✅ Vector search is working with existing data")
    print("   ✅ PDF ingestion pipeline may already be connected")
    
    print("\n2. If no results or low relevance:")
    print("   🔧 Need to connect PDF ingestion to vector pipeline")
    print("   🔧 May need to trigger manual vectorization of recent ingestions")
    
    print("\n3. If vector database is empty:")
    print("   🚀 Need to populate vector database with existing data")
    print("   🔧 Consider running batch vectorization process")

def main():
    """Main entry point"""
    try:
        asyncio.run(test_vector_search_for_pdfs())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
