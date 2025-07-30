#!/usr/bin/env python3
"""
Direct SQLite Integration Script for n8n
Alternative to webhook approach - can be called directly from n8n Python node
"""

import sqlite3
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from database.sqlite_manager import db_manager

def insert_funding_opportunity_direct(data):
    """
    Direct SQLite insertion for n8n Python node
    Usage in n8n Python node:
    
    import subprocess
    import json
    
    # Prepare data
    opportunity_data = {
        "title": "AI Innovation Grant",
        "organization": "Example Foundation",
        # ... other fields
    }
    
    # Call this script
    result = subprocess.run([
        "python3", 
        "/path/to/sqlite_direct_insert.py", 
        json.dumps(opportunity_data)
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)
    """
    
    try:
        # Insert using the database manager
        opportunity_id = db_manager.insert_funding_opportunity(data)
        
        # Log execution
        log_id = db_manager.log_pipeline_execution(
            source_name=data.get('source_type', 'n8n_direct'),
            execution_id=f"direct_{int(datetime.now().timestamp())}",
            status="success",
            records_processed=1,
            records_inserted=1,
            execution_time=0.1
        )
        
        return {
            "status": "success",
            "opportunity_id": opportunity_id,
            "log_id": log_id,
            "message": f"Successfully inserted: {data.get('title', 'Unknown')}"
        }
        
    except Exception as e:
        # Log error
        try:
            log_id = db_manager.log_pipeline_execution(
                source_name=data.get('source_type', 'n8n_direct'),
                execution_id=f"direct_error_{int(datetime.now().timestamp())}",
                status="error",
                records_processed=1,
                records_inserted=0,
                error_message=str(e),
                execution_time=0.1
            )
        except:
            log_id = None
        
        return {
            "status": "error",
            "error": str(e),
            "log_id": log_id,
            "message": f"Failed to insert: {data.get('title', 'Unknown')}"
        }

def bulk_insert_funding_opportunities(opportunities_list):
    """
    Bulk insert multiple opportunities
    """
    results = []
    successful_inserts = 0
    
    for opportunity_data in opportunities_list:
        result = insert_funding_opportunity_direct(opportunity_data)
        results.append(result)
        
        if result["status"] == "success":
            successful_inserts += 1
    
    # Log bulk execution
    try:
        bulk_log_id = db_manager.log_pipeline_execution(
            source_name="n8n_bulk_direct",
            execution_id=f"bulk_{int(datetime.now().timestamp())}",
            status="success" if successful_inserts > 0 else "error",
            records_processed=len(opportunities_list),
            records_inserted=successful_inserts,
            error_message=None if successful_inserts > 0 else "No records inserted",
            execution_time=0.5
        )
    except Exception as e:
        bulk_log_id = None
    
    return {
        "status": "completed",
        "total_processed": len(opportunities_list),
        "successful_inserts": successful_inserts,
        "failed_inserts": len(opportunities_list) - successful_inserts,
        "bulk_log_id": bulk_log_id,
        "individual_results": results
    }

def get_database_stats():
    """
    Get current database statistics for monitoring
    """
    try:
        stats = db_manager.get_pipeline_stats()
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    """
    Command line interface for n8n integration
    
    Usage:
    python sqlite_direct_insert.py '{"title": "Grant", "organization": "Org"}'
    python sqlite_direct_insert.py --bulk '[{"title": "Grant1"}, {"title": "Grant2"}]'
    python sqlite_direct_insert.py --stats
    """
    
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "error": "No data provided",
            "usage": "python sqlite_direct_insert.py '{\"title\": \"Grant\", \"organization\": \"Org\"}'"
        }))
        sys.exit(1)
    
    try:
        if sys.argv[1] == "--stats":
            result = get_database_stats()
        elif sys.argv[1] == "--bulk":
            if len(sys.argv) < 3:
                raise ValueError("Bulk mode requires data argument")
            opportunities_data = json.loads(sys.argv[2])
            result = bulk_insert_funding_opportunities(opportunities_data)
        else:
            # Single opportunity insert
            opportunity_data = json.loads(sys.argv[1])
            result = insert_funding_opportunity_direct(opportunity_data)
        
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "status": "error",
            "error": f"Invalid JSON data: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }))
        sys.exit(1)