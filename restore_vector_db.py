#!/usr/bin/env python3
"""
Vector Database Restoration Script
=================================

This script restores the Pinecone vector database by re-indexing all records
from Supabase using local embeddings (no OpenAI API key required).
"""

import os
import sys
import time
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np

# Load environment variables
load_dotenv()

def restore_vector_database():
    """Restore the vector database using local embeddings"""
    
    print("🔄 Starting vector database restoration...")
    
    # Import required libraries
    try:
        from supabase import create_client
        from pinecone import Pinecone
    except ImportError as e:
        print(f"❌ Missing required libraries: {e}")
        print("Please install: pip install supabase pinecone-client sentence-transformers")
        return False
    
    # Initialize clients
    try:
        client = create_client(os.getenv('SUPABASE_PROJECT_URL'), os.getenv('SUPABASE_API_KEY'))
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index('taifa-fiala')
        print("✅ Connected to Supabase and Pinecone")
    except Exception as e:
        print(f"❌ Failed to connect to databases: {e}")
        return False
    
    # Initialize local embedding model
    try:
        print("📥 Loading local embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast model
        print("✅ Local embedding model loaded")
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        print("Installing sentence-transformers...")
        os.system("pip install sentence-transformers")
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Local embedding model loaded after installation")
        except Exception as e2:
            print(f"❌ Still failed to load model: {e2}")
            return False
    
    # Get all records from Supabase
    try:
        print("📥 Fetching records from Supabase...")
        result = client.table('africa_intelligence_feed').select('*').execute()
        records = result.data
        print(f"Found {len(records)} records to index")
    except Exception as e:
        print(f"❌ Failed to fetch records: {e}")
        return False
    
    if not records:
        print("❌ No records found in Supabase")
        return False
    
    # Clear existing vectors (optional - comment out if you want to keep the 1 existing record)
    try:
        print("🗑️ Clearing existing vectors...")
        index.delete(delete_all=True)
        time.sleep(2)  # Wait for deletion to complete
        print("✅ Existing vectors cleared")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear existing vectors: {e}")
    
    # Process records in batches
    batch_size = 10
    total_indexed = 0
    failed_records = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        vectors_to_upsert = []
        
        print(f"🔄 Processing batch {i//batch_size + 1}/{(len(records) + batch_size - 1)//batch_size}")
        
        for record in batch:
            try:
                # Create text for embedding
                title = record.get('title', '') or ''
                description = record.get('description', '') or ''
                content = record.get('content', '') or ''
                
                # Combine text fields
                text_content = f"{title} {description} {content}".strip()
                
                if not text_content:
                    print(f"⚠️ Skipping record {record['id']} - no text content")
                    continue
                
                # Limit text length to prevent memory issues
                text_content = text_content[:2000]
                
                # Generate embedding using local model
                embedding = model.encode(text_content)
                
                # Convert to list and ensure correct dimension
                embedding_list = embedding.tolist()
                
                # Pad or truncate to 1024 dimensions to match Pinecone index
                if len(embedding_list) < 1024:
                    embedding_list.extend([0.0] * (1024 - len(embedding_list)))
                elif len(embedding_list) > 1024:
                    embedding_list = embedding_list[:1024]
                
                # Prepare vector for upsert
                vector_data = {
                    'id': f"record_{record['id']}",
                    'values': embedding_list,
                    'metadata': {
                        'title': title[:500] if title else '',
                        'description': description[:500] if description else '',
                        'url': record.get('url', '') or '',
                        'source': record.get('source', '') or '',
                        'created_at': str(record.get('created_at', ''))
                    }
                }
                vectors_to_upsert.append(vector_data)
                
            except Exception as e:
                print(f"❌ Error processing record {record['id']}: {e}")
                failed_records += 1
                continue
        
        # Upsert batch to Pinecone
        if vectors_to_upsert:
            try:
                index.upsert(vectors=vectors_to_upsert)
                total_indexed += len(vectors_to_upsert)
                print(f"✅ Indexed {len(vectors_to_upsert)} vectors (Total: {total_indexed})")
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error upserting batch: {e}")
                failed_records += len(vectors_to_upsert)
    
    # Wait for indexing to complete
    print("⏳ Waiting for indexing to complete...")
    time.sleep(5)
    
    # Verify the index
    try:
        stats = index.describe_index_stats()
        print(f"📊 Final index stats: {stats}")
        
        final_count = stats.get('total_vector_count', 0)
        if final_count > 1:
            print(f"🎉 SUCCESS! Vector database restored with {final_count} vectors")
            print(f"📈 Indexed: {total_indexed}, Failed: {failed_records}")
            return True
        else:
            print(f"❌ FAILED! Only {final_count} vectors in index")
            return False
            
    except Exception as e:
        print(f"❌ Error checking final stats: {e}")
        return False

def test_search():
    """Test the restored vector database with a sample search"""
    
    print("\n🔍 Testing vector search...")
    
    try:
        from pinecone import Pinecone
        from sentence_transformers import SentenceTransformer
        
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index('taifa-fiala')
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test query
        query = "AI funding opportunities in Africa"
        query_embedding = model.encode(query).tolist()
        
        # Pad to 1024 dimensions
        if len(query_embedding) < 1024:
            query_embedding.extend([0.0] * (1024 - len(query_embedding)))
        elif len(query_embedding) > 1024:
            query_embedding = query_embedding[:1024]
        
        # Search
        results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
        
        print(f"✅ Search successful! Found {len(results.matches)} results")
        for i, match in enumerate(results.matches[:3]):
            title = match.metadata.get('title', 'No title')
            score = match.score
            print(f"  {i+1}. {title} (score: {score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TAIFA-FIALA Vector Database Restoration")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['SUPABASE_PROJECT_URL', 'SUPABASE_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        sys.exit(1)
    
    # Restore vector database
    success = restore_vector_database()
    
    if success:
        # Test the restored database
        test_search()
        print("\n🎉 Vector database restoration complete!")
        print("Your semantic search functionality should now be working.")
    else:
        print("\n❌ Vector database restoration failed!")
        print("Please check the error messages above and try again.")
