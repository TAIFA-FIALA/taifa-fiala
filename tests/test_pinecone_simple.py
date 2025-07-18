#!/usr/bin/env python3
"""
Simple Pinecone connection test script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Pinecone connection...")

try:
    # Try different import methods
    try:
        from pinecone import Pinecone
        print("✅ Successfully imported Pinecone")
    except ImportError as e:
        print(f"❌ Failed to import Pinecone: {e}")
        try:
            import pinecone
            print("✅ Successfully imported pinecone module")
            if hasattr(pinecone, 'Pinecone'):
                Pinecone = pinecone.Pinecone
                print("✅ Found Pinecone class")
            else:
                print("❌ Pinecone class not found in module")
                print(f"Available attributes: {dir(pinecone)}")
                sys.exit(1)
        except ImportError as e2:
            print(f"❌ Failed to import pinecone module: {e2}")
            sys.exit(1)
    
    # Get environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    host = os.getenv("PINECONE_HOST")
    
    print(f"API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"Host: {'✅ Found' if host else '❌ Missing'}")
    
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        sys.exit(1)
    
    # Initialize Pinecone client
    print("Initializing Pinecone client...")
    pc = Pinecone(api_key=api_key)
    print("✅ Successfully created Pinecone client")
    
    # List indexes
    print("Listing indexes...")
    indexes = pc.list_indexes()
    print(f"✅ Successfully listed indexes: {indexes}")
    
    # Extract index name from host
    if host:
        print(f"Host URL: {host}")
        host_parts = host.replace("https://", "").split(".")
        if host_parts:
            index_name = host_parts[0]
            print(f"Detected index name: {index_name}")
            
            # Check if index exists
            if hasattr(indexes, 'names'):
                index_names = indexes.names()
                print(f"Available index names: {index_names}")
                
                # Use the first available index name instead of parsing from host
                if index_names:
                    actual_index_name = index_names[0]
                    print(f"✅ Using index '{actual_index_name}'")
                    
                    # Connect to index and get stats
                    print("Connecting to index...")
                    index = pc.Index(actual_index_name)
                    stats = index.describe_index_stats()
                    print(f"✅ Index stats: {stats}")
                    
                    print("🎉 Pinecone connection successful!")
                else:
                    print(f"❌ No indexes found")
            else:
                print(f"❌ Could not get index names from response")
    else:
        print("⚠️ No host URL provided, skipping index connection test")
        print("🎉 Pinecone client connection successful!")

except Exception as e:
    print(f"❌ Error testing Pinecone: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
