#!/usr/bin/env python3
"""
Frontend Health Diagnostic Script
Helps diagnose why the frontend health check is failing
"""

import requests
import subprocess
import sys
import time
from pathlib import Path

def check_process_status():
    """Check if frontend process is actually running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        frontend_processes = [line for line in result.stdout.split('\n') 
                            if ('npm' in line and 'start' in line) or 
                               ('node' in line and 'next' in line) or
                               ('next' in line)]
        
        print("=== Frontend Process Status ===")
        if frontend_processes:
            for process in frontend_processes:
                print(f"✓ Found frontend process: {process}")
        else:
            print("❌ No frontend processes found")
        
        return len(frontend_processes) > 0
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def check_port_binding():
    """Check if port 3030 is being used"""
    try:
        result = subprocess.run(['lsof', '-i', ':3030'], capture_output=True, text=True)
        print("\n=== Port 3030 Status ===")
        if result.stdout:
            print("✓ Port 3030 is in use:")
            print(result.stdout)
        else:
            print("❌ Port 3030 is not in use")
        
        return bool(result.stdout)
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def check_frontend_logs():
    """Check frontend logs for errors"""
    log_file = Path("logs/frontend.log")
    print(f"\n=== Frontend Logs ===")
    
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
        print("❌ Frontend log file not found")

def test_frontend_endpoints():
    """Test various frontend endpoints"""
    endpoints = [
        "http://100.75.201.24:3030",
        "http://localhost:3030",
        "http://127.0.0.1:3030"
    ]
    
    print(f"\n=== Testing Frontend Endpoints ===")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"✓ {endpoint}: {response.status_code} - Content length: {len(response.text)}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: Timeout")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

def check_frontend_directory():
    """Check if frontend directory and files exist"""
    print(f"\n=== Frontend Directory Check ===")
    
    frontend_dir = Path("frontend/nextjs")
    if frontend_dir.exists():
        print(f"✓ Frontend directory exists: {frontend_dir}")
        
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            print("✓ package.json exists")
        else:
            print("❌ package.json not found")
            
        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            print("✓ node_modules exists")
        else:
            print("❌ node_modules not found - run npm install")
            
        next_config = frontend_dir / "next.config.js"
        if next_config.exists():
            print("✓ next.config.js exists")
        else:
            print("⚠ next.config.js not found (may be optional)")
    else:
        print(f"❌ Frontend directory not found: {frontend_dir}")

def check_pids():
    """Check PID files"""
    print(f"\n=== PID Files ===")
    
    pids_dir = Path("pids")
    if pids_dir.exists():
        frontend_pid = pids_dir / "frontend.pid"
        if frontend_pid.exists():
            try:
                with open(frontend_pid, 'r') as f:
                    pid = f.read().strip()
                    print(f"Frontend PID from file: {pid}")
                    
                    # Check if process is actually running
                    try:
                        subprocess.run(['kill', '-0', pid], check=True, capture_output=True)
                        print(f"✓ Process {pid} is running")
                    except subprocess.CalledProcessError:
                        print(f"❌ Process {pid} is not running (stale PID file)")
            except Exception as e:
                print(f"❌ Error reading PID file: {e}")
        else:
            print("❌ Frontend PID file not found")
    else:
        print("❌ PID directory not found")

def main():
    print("🔍 Frontend Health Diagnostic Tool")
    print("=" * 50)
    
    # Run all diagnostic checks
    process_running = check_process_status()
    port_bound = check_port_binding()
    
    check_frontend_logs()
    test_frontend_endpoints()
    check_frontend_directory()
    check_pids()
    
    print(f"\n=== Summary ===")
    print(f"Process running: {'✓' if process_running else '❌'}")
    print(f"Port bound: {'✓' if port_bound else '❌'}")
    
    if not process_running and not port_bound:
        print("\n🔍 Frontend is not running")
        print("💡 Try starting with: cd frontend/nextjs && PORT=3030 npm start")
    elif process_running and not port_bound:
        print("\n🔍 Process is running but port is not bound - likely startup error")
        print("💡 Check frontend logs for errors")
    elif not process_running and port_bound:
        print("\n🔍 Port is bound but no recognizable process - might be another service")
    elif process_running and port_bound:
        print("\n🔍 Process and port look good - might be a network/response issue")

if __name__ == "__main__":
    main()