#!/usr/bin/env python3
"""
Backend Startup Test Script
Tests if the backend can start properly without the full deployment
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def test_backend_startup():
    """Test if backend can start locally"""
    print("=== Backend Startup Test ===")
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    # Check if virtual environment exists
    venv_python = Path("venv/bin/python")
    if not venv_python.exists():
        print("❌ Backend virtual environment not found")
        return False
    
    print("✓ Virtual environment found")
    
    # Test basic imports
    print("\n=== Testing Imports ===")
    import_tests = [
        "import fastapi; print('✓ FastAPI imported')",
        "import uvicorn; print('✓ Uvicorn imported')",
        "from app.core.config import settings; print('✓ Config imported')",
        "from app.main import app; print('✓ Main app imported')"
    ]
    
    for test in import_tests:
        try:
            result = subprocess.run([str(venv_python), "-c", test], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"❌ Import failed: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ Import test timed out")
            return False
        except Exception as e:
            print(f"❌ Import test error: {e}")
            return False
    
    # Test database connection
    print("\n=== Testing Database Connection ===")
    db_test = """
try:
    from app.core.config import settings
    print(f'Database URL: {settings.DATABASE_URL}')
    
    from app.core.database import create_tables
    import asyncio
    asyncio.run(create_tables())
    print('✓ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    import traceback
    traceback.print_exc()
"""
    
    try:
        result = subprocess.run([str(venv_python), "-c", db_test], 
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"❌ Database test error: {e}")
    
    # Test FastAPI app creation
    print("\n=== Testing FastAPI App Startup ===")
    app_test = """
try:
    from app.main import app
    print('✓ FastAPI app created successfully')
    print(f'App title: {app.title}')
    print(f'Routes count: {len(app.routes)}')
except Exception as e:
    print(f'❌ FastAPI app creation failed: {e}')
    import traceback
    traceback.print_exc()
"""
    
    try:
        result = subprocess.run([str(venv_python), "-c", app_test], 
                              capture_output=True, text=True, timeout=15)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"❌ App test error: {e}")
    
    # Test uvicorn startup (brief test)
    print("\n=== Testing Uvicorn Startup (5 second test) ===")
    try:
        # Start uvicorn in background
        process = subprocess.Popen([
            str(venv_python), "-m", "uvicorn", 
            "app.main:app", "--host", "127.0.0.1", "--port", "8031"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ Uvicorn started successfully")
            
            # Test health endpoint
            try:
                import requests
                response = requests.get("http://127.0.0.1:8031/health", timeout=3)
                print(f"✓ Health endpoint responded: {response.status_code}")
                print(f"Response: {response.text}")
            except Exception as e:
                print(f"❌ Health endpoint test failed: {e}")
            
            # Stop the process
            process.terminate()
            process.wait(timeout=5)
            print("✓ Uvicorn stopped cleanly")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Uvicorn failed to start")
            print(f"Stdout: {stdout.decode()}")
            print(f"Stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Uvicorn test error: {e}")
        if 'process' in locals():
            try:
                process.terminate()
            except:
                pass
        return False

if __name__ == "__main__":
    success = test_backend_startup()
    sys.exit(0 if success else 1)