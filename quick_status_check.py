#!/usr/bin/env python3
import subprocess
import requests

print("=== Quick Status Check ===")

# Check processes
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    print("\n--- Frontend Processes ---")
    frontend_found = False
    for line in lines:
        if any(term in line.lower() for term in ['npm start', 'next start', 'node.*next']):
            print(f"✓ {line}")
            frontend_found = True
    if not frontend_found:
        print("❌ No frontend processes found")
    
    print("\n--- Backend Processes ---")
    backend_found = False
    for line in lines:
        if any(term in line.lower() for term in ['uvicorn', 'fastapi', 'python.*main.py']):
            print(f"✓ {line}")
            backend_found = True
    if not backend_found:
        print("❌ No backend processes found")
        
except Exception as e:
    print(f"Error checking processes: {e}")

# Check ports
print("\n--- Port Status ---")
for port in [3030, 8030]:
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
        if result.stdout:
            print(f"✓ Port {port} in use")
        else:
            print(f"❌ Port {port} not in use")
    except:
        print(f"❌ Could not check port {port}")

# Test endpoints
print("\n--- Endpoint Tests ---")
endpoints = [
    ("Frontend", "http://localhost:3030"),
    ("Backend", "http://localhost:8030/health")
]

for name, url in endpoints:
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ {name}: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused")
    except Exception as e:
        print(f"❌ {name}: {str(e)}")