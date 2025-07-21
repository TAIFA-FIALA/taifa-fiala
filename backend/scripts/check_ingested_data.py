#!/usr/bin/env python3
"""
Script to verify the ingested data and enrichment status in the Supabase database.
"""
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Load environment variables
load_dotenv()

# Initialize Supabase client
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_API_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_API_KEY in environment variables")
    return create_client(url, key)

def get_recent_records(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent records from the database."""
    try:
        supabase = get_supabase_client()
        
        response = (
            supabase.table('africa_intelligence_feed')
            .select('*')
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
        )
        
        return response.data if hasattr(response, 'data') else []
    except Exception as e:
        print(f"Error fetching records: {e}")
        return []

def get_enrichment_status(record: Dict[str, Any]) -> str:
    """Determine the enrichment status of a record."""
    if not record:
        return "No record data"
        
    status = []
    
    # Check basic enrichment fields
    if record.get('enrichment_attempted'):
        if record.get('enrichment_success'):
            status.append(" Enrichment successful")
        else:
            status.append(" Enrichment failed")
    else:
        status.append(" Not yet enriched")
    
    # Check specific enrichment stages
    if record.get('crawl4ai_processed'):
        status.append(" Crawl4AI processed")
    if record.get('serper_processed'):
        status.append(" Serper.dev processed")
    
    # Check if we have key fields that should be enriched
    if record.get('funding_amount'):
        status.append(f" Funding: {record.get('funding_amount')}")
    if record.get('application_deadline'):
        status.append(f" Deadline: {record.get('application_deadline')}")
    
    return " | ".join(status) if status else "No enrichment data"

def format_record(record: Dict[str, Any]) -> str:
    """Format a single record for display."""
    if not record:
        return "No record data"
        
    output = []
    output.append(f" ID: {record.get('id')}")
    output.append(f" Title: {record.get('title')}")
    output.append(f"  Source: {record.get('source')}")
    output.append(f" Published: {record.get('published_date')}")
    output.append(f" Created: {record.get('created_at')}")
    
    # Enrichment status
    output.append(f"\n Enrichment Status:")
    output.append(f"   {get_enrichment_status(record)}")
    
    # Content preview
    content = record.get('content', '')
    content_preview = (content[:150] + '...') if len(content) > 150 else content
    output.append(f"\n Content Preview: {content_preview}")
    
    # URL
    url = record.get('url', '')
    if url:
        output.append(f"\n URL: {url}")
    
    return "\n".join(output)

def main():
    print(" Fetching recent records from the database...\n")
    
    # Get the 10 most recent records
    records = get_recent_records(limit=10)
    
    if not records:
        print(" No recent records found or error occurred.")
        return
    
    print(f" Found {len(records)} records. Here are the most recent ones:\n")
    
    for i, record in enumerate(records, 1):
        print(f"=== Record {i} ===")
        print(format_record(record))
        print("\n" + "-"*80 + "\n")
    
    print("\n To see more details about a specific record, run:")
    print("""python3 -c "
import json
from pprint import pprint
from scripts.check_ingested_data import get_recent_records
record = get_recent_records(1)[0]
print(f'Full record for {record.get("title")}:')
pprint(record)""
""")

if __name__ == "__main__":
    main()
