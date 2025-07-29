#!/usr/bin/env python3
"""
Backend Health Diagnostic Script
Helps diagnose why the backend health check is failing
"""

import requests
import subprocess
import sys
import time
from pathlib import Path

def check_process_status():
    """Check if backend process is actually running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        backend_processes = [line for line in result.stdout.split('\n') if 'uvicorn' in line and 'app.main:app' in line]
        
        print("=== Backend Process Status ===")
        if backend_processes:
            for process in backend_processes:
                print(f"✓ Found backend process: {process}")
        else:
            print("❌ No backend processes found")
        
        return len(backend_processes) > 0
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def check_port_binding():
    """Check if port 8030 is being used"""
    try:
        result = subprocess.run(['lsof', '-i', ':8030'], capture_output=True, text=True)
        print("\n=== Port 8030 Status ===")
        if result.stdout:
            print("✓ Port 8030 is in use:")
            print(result.stdout)
        else:
            print("❌ Port 8030 is not in use")
        
        return bool(result.stdout)
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def check_backend_logs():
    """Check backend logs for errors"""
    log_file = Path("logs/backend.log")
    print(f"\n=== Backend Logs ===")
    
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Show last 20 lines
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                for line in recent_lines:
                    print(line.strip())
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    else:
        print("❌ Backend log file not found")

def test_health_endpoints():
    """Test various backend endpoints"""
    endpoints = [
        "http://100.75.201.24:8030/health",
        "http://100.75.201.24:8030/",
        "http://localhost:8030/health",
        "http://localhost:8030/",
        "http://127.0.0.1:8030/health",
        "http://127.0.0.1:8030/"
    ]
    
    print(f"\n=== Testing Backend Endpoints ===")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✓ {endpoint}: {response.status_code} - {response.text[:100]}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: Timeout")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

def check_database_connection():
    """Check if database connection is working"""
    print(f"\n=== Database Connection Test ===")
    try:
        # Try to import and test database connection
        sys.path.append('backend')
        from app.core.database import get_db
        from app.core.config import settings
        
        print(f"Database URL configured: {bool(settings.DATABASE_URL)}")
        print(f"Supabase configured: {bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)}")
        
    except ImportError as e:
        print(f"❌ Cannot import database modules: {e}")
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")

def main():
    print("🔍 Backend Health Diagnostic Tool")
    print("=" * 50)
    
    # Run all diagnostic checks
    process_running = check_process_status()
    port_bound = check_port_binding()
    
    check_backend_logs()
    test_health_endpoints()
    check_database_connection()
    
    print(f"\n=== Summary ===")
    print(f"Process running: {'✓' if process_running else '❌'}")
    print(f"Port bound: {'✓' if port_bound else '❌'}")
    
    if process_running and not port_bound:
        print("\n🔍 Process is running but port is not bound - likely startup error")
        print("💡 Check backend logs for database or configuration issues")
    elif not process_running:
        print("\n🔍 Process is not running - check deployment script")
    elif process_running and port_bound:
        print("\n🔍 Process and port look good - might be a network/firewall issue")

if __name__ == "__main__":
    main()