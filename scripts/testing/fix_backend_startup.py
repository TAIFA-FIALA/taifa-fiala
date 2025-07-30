#!/usr/bin/env python3
"""
Backend Startup Fix
Creates a more robust version of main.py that won't crash on database errors
"""

import shutil
from pathlib import Path

def create_robust_main():
    """Create a more robust main.py that handles database errors gracefully"""
    
    backend_main = Path("backend/app/main.py")
    if not backend_main.exists():
        print("❌ Backend main.py not found")
        return False
    
    # Create backup
    backup_path = Path("backend/app/main.py.backup")
    shutil.copy2(backend_main, backup_path)
    print(f"✓ Created backup: {backup_path}")
    
    # Read current content
    with open(backend_main, 'r') as f:
        content = f.read()
    
    # Replace the startup event with a more robust version
    old_startup = '''@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        print("🔄 Attempting to create database tables...")
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database table creation failed: {e}")
        print("⚠️ Application will continue without database tables")
        # Log the error but don't crash the application
        import logging
        logging.error(f"Database initialization failed: {e}", exc_info=True)'''
    
    new_startup = '''@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        print("🔄 Attempting to create database tables...")
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database table creation failed: {e}")
        print("⚠️ Application will continue without database tables")
        # Log the error but don't crash the application
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        
        # Continue startup even if database fails
        print("✅ Application startup completed (database initialization skipped)")'''
    
    # Replace the content
    if old_startup in content:
        new_content = content.replace(old_startup, new_startup)
        
        with open(backend_main, 'w') as f:
            f.write(new_content)
        
        print("✅ Updated main.py with robust startup handling")
        return True
    else:
        print("⚠️ Could not find exact startup event to replace")
        print("The startup event may have been modified already")
        return False

def create_minimal_test_main():
    """Create a minimal test version of main.py for debugging"""
    
    minimal_main = Path("backend/app/main_minimal.py")
    
    minimal_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create minimal FastAPI application for testing
app = FastAPI(
    title="AI Africa Funding Tracker - Minimal Test",
    description="Minimal version for debugging",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Africa Funding Tracker API - Minimal Test",
        "version": "1.0.0-test",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "ai-africa-funding-tracker-minimal",
        "version": "1.0.0-test"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify functionality"""
    return {
        "test": "success",
        "message": "Backend is responding correctly"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8030,
        reload=False,
        log_level="info"
    )
'''
    
    with open(minimal_main, 'w') as f:
        f.write(minimal_content)
    
    print(f"✅ Created minimal test main: {minimal_main}")
    return True

def main():
    print("🔧 Backend Startup Fix Tool")
    print("=" * 40)
    
    # Create robust main.py
    robust_success = create_robust_main()
    
    # Create minimal test version
    minimal_success = create_minimal_test_main()
    
    print("\n" + "=" * 40)
    print("📋 Next Steps:")
    
    if robust_success:
        print("1. ✅ Robust main.py created - try redeploying")
        print("   The backend should now handle database errors gracefully")
    
    if minimal_success:
        print("2. ✅ Minimal test version created")
        print("   To test: cd backend && venv/bin/python -m uvicorn app.main_minimal:app --host 0.0.0.0 --port 8030")
    
    print("\n🔍 To diagnose the crash:")
    print("- Check backend logs: tail -f logs/backend.log")
    print("- Test minimal version first to isolate the issue")
    print("- If minimal works, the issue is in database/import initialization")

if __name__ == "__main__":
    main()