#!/usr/bin/env python3
import subprocess
import requests
import os

print("=== Simple Service Status Check ===")

# Check if we're in the right directory
print(f"Current directory: {os.getcwd()}")

# Check for running processes
print("\n--- Process Check ---")
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    # Look for frontend processes
    frontend_processes = [line for line in lines if 'npm' in line or ('node' in line and 'next' in line)]
    if frontend_processes:
        print("Frontend processes found:")
        for proc in frontend_processes[:3]:  # Show first 3
            print(f"  {proc}")
    else:
        print("❌ No frontend processes found")
    
    # Look for backend processes  
    backend_processes = [line for line in lines if 'uvicorn' in line or 'fastapi' in line]
    if backend_processes:
        print("Backend processes found:")
        for proc in backend_processes[:3]:  # Show first 3
            print(f"  {proc}")
    else:
        print("❌ No backend processes found")
        
except Exception as e:
    print(f"Error checking processes: {e}")

# Check ports
print("\n--- Port Check ---")
for port in [3030, 8030]:
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✓ Port {port} is in use")
        else:
            print(f"❌ Port {port} is not in use")
    except Exception as e:
        print(f"Error checking port {port}: {e}")

# Quick endpoint test
print("\n--- Endpoint Test ---")
for name, url in [("Frontend", "http://localhost:3030"), ("Backend", "http://localhost:8030/health")]:
    try:
        response = requests.get(url, timeout=3)
        print(f"✓ {name}: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused")
    except Exception as e:
        print(f"❌ {name}: {str(e)}")

# Check if frontend directory exists and has dependencies
print("\n--- Frontend Directory Check ---")
frontend_dir = "frontend/nextjs"
if os.path.exists(frontend_dir):
    print(f"✓ Frontend directory exists: {frontend_dir}")
    if os.path.exists(f"{frontend_dir}/node_modules"):
        print("✓ node_modules exists")
    else:
        print("❌ node_modules missing - need to run npm install")
    if os.path.exists(f"{frontend_dir}/package.json"):
        print("✓ package.json exists")
    else:
        print("❌ package.json missing")
else:
    print(f"❌ Frontend directory not found: {frontend_dir}")