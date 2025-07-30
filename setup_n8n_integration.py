#!/usr/bin/env python3
"""
Complete Setup Script for TAIFA-FIALA n8n SQLite Integration
Initializes database, sets up FastAPI endpoints, and provides n8n configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_complete_integration():
    """Setup the complete n8n SQLite integration"""
    
    print("🚀 Setting up TAIFA-FIALA n8n SQLite Integration...")
    
    project_root = Path(__file__).parent
    
    # 1. Initialize SQLite database
    print("\n📊 Step 1: Initializing SQLite database...")
    try:
        setup_script = project_root / "data" / "setup_database.py"
        result = subprocess.run([sys.executable, str(setup_script)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database initialized successfully")
            print(result.stdout)
        else:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    # 2. Install Python dependencies
    print("\n📦 Step 2: Installing Python dependencies...")
    dependencies = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlite3"  # Built-in, but good to note
    ]
    
    try:
        for dep in dependencies:
            if dep != "sqlite3":  # Skip built-in module
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # 3. Create FastAPI integration file
    print("\n🔗 Step 3: Setting up FastAPI integration...")
    try:
        fastapi_integration = project_root / "backend" / "main_with_webhooks.py"
        with open(fastapi_integration, 'w') as f:
            f.write("""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import the webhook router
from api.webhooks import router as webhook_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TAIFA-FIALA API with n8n Integration",
    description="AI Funding Tracker with automated pipeline integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {
        "message": "TAIFA-FIALA API with n8n Integration",
        "status": "running",
        "endpoints": {
            "webhooks": "/api/v1/webhooks/",
            "health": "/api/v1/webhooks/health",
            "pipeline_stats": "/api/v1/webhooks/pipeline-stats"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "taifa-fiala-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")
        print("✅ FastAPI integration created")
    except Exception as e:
        print(f"❌ Error creating FastAPI integration: {e}")
        return False
    
    # 4. Create n8n configuration guide
    print("\n⚙️ Step 4: Creating n8n configuration guide...")
    try:
        n8n_guide = project_root / "n8n-workflows" / "N8N_SETUP_GUIDE.md"
        with open(n8n_guide, 'w') as f:
            f.write("""# n8n Integration Setup Guide for TAIFA-FIALA

## Overview
This guide helps you set up n8n to automatically collect funding opportunities and insert them into your TAIFA-FIALA SQLite database.

## Prerequisites
- n8n installed and running
- TAIFA-FIALA FastAPI server running on localhost:8000
- SQLite database initialized

## Setup Steps

### 1. Configure SQLite Credential in n8n
1. Go to n8n Settings > Credentials
2. Add new credential: "SQLite"
3. Name: "TAIFA SQLite Database"
4. Database file path: `/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/data/taifa_fiala.db`

### 2. Import Workflow
1. Copy the content from `funding-pipeline-sqlite.json`
2. In n8n, go to Workflows > Import from JSON
3. Paste the content and save

### 3. Configure Webhook URLs
Update these URLs in the workflow nodes to match your setup:
- Cache refresh: `http://localhost:8000/api/v1/webhooks/refresh-cache`
- Pipeline logging: `http://localhost:8000/api/v1/webhooks/pipeline-log`

### 4. Test the Integration

#### Option A: Using SQLite Node (Recommended)
The workflow uses direct SQLite insertion for maximum performance.

#### Option B: Using HTTP Webhook
Alternative approach using FastAPI webhooks:

```bash
# Test single opportunity insertion
curl -X POST http://localhost:8000/api/v1/webhooks/funding-opportunity \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Test AI Grant",
    "description": "Test funding opportunity",
    "organization": "Test Foundation",
    "amount_exact": 100000,
    "currency": "USD",
    "sector": "AI",
    "location": "Africa"
  }'
```

#### Option C: Using Python Script
Direct Python integration for complex data processing:

```python
# In n8n Python node:
import subprocess
import json

opportunity_data = {
    "title": $json.title,
    "organization": $json.organization,
    "description": $json.description,
    # ... other fields from your data
}

result = subprocess.run([
    "python3", 
    "/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/n8n-workflows/sqlite_direct_insert.py",
    json.dumps(opportunity_data)
], capture_output=True, text=True)

return json.loads(result.stdout)
```

## Monitoring and Maintenance

### Check Pipeline Stats
```bash
curl http://localhost:8000/api/v1/webhooks/pipeline-stats
```

### View Database Contents
```bash
sqlite3 /Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/data/taifa_fiala.db
.tables
SELECT COUNT(*) FROM funding_opportunities;
SELECT * FROM pipeline_logs ORDER BY created_at DESC LIMIT 10;
```

### Common Issues

1. **Database locked error**: Ensure no other processes are accessing the database
2. **Permission denied**: Check file permissions on the database file
3. **Connection refused**: Verify FastAPI server is running on port 8000

## Data Sources to Configure

Add these data sources to your n8n workflows:

1. **African Development Bank**: https://www.afdb.org/en/news-and-events/news
2. **Gates Foundation**: https://www.gatesfoundation.org/ideas/media-center/press-releases
3. **World Bank**: https://www.worldbank.org/en/news/all
4. **Google AI for Social Good**: https://ai.google/social-good/
5. **Mozilla Foundation**: https://foundation.mozilla.org/en/blog/

## Performance Tips

- Run workflows every 6 hours to avoid overwhelming sources
- Use bulk insertion for multiple opportunities
- Monitor execution logs for errors
- Set up alerts for failed pipeline runs

## Security Considerations

- Restrict API access to local network only
- Validate all incoming data
- Monitor for unusual activity
- Regular database backups
""")
        print("✅ n8n setup guide created")
    except Exception as e:
        print(f"❌ Error creating n8n guide: {e}")
        return False
    
    # 5. Create startup script
    print("\n🎬 Step 5: Creating startup script...")
    try:
        startup_script = project_root / "start_taifa_with_n8n.sh"
        with open(startup_script, 'w') as f:
            f.write("""#!/bin/bash
# TAIFA-FIALA Startup Script with n8n Integration

echo "🚀 Starting TAIFA-FIALA with n8n Integration..."

# Set project directory
PROJECT_DIR="/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker"
cd "$PROJECT_DIR"

# Check if database exists
if [ ! -f "data/taifa_fiala.db" ]; then
    echo "📊 Initializing database..."
    python3 data/setup_database.py
fi

# Start FastAPI server with webhook support
echo "🔗 Starting FastAPI server with n8n webhooks..."
cd backend
python3 main_with_webhooks.py &
FASTAPI_PID=$!

# Start Next.js frontend
echo "🎨 Starting Next.js frontend..."
cd ../frontend/nextjs
npm run dev &
NEXTJS_PID=$!

echo "✅ TAIFA-FIALA is running!"
echo "📊 FastAPI with webhooks: http://localhost:8000"
echo "🎨 Next.js frontend: http://localhost:3000"
echo "📈 Pipeline stats: http://localhost:8000/api/v1/webhooks/pipeline-stats"
echo ""
echo "To stop services:"
echo "kill $FASTAPI_PID $NEXTJS_PID"

# Wait for user input to stop
read -p "Press Enter to stop all services..."

# Kill background processes
kill $FASTAPI_PID $NEXTJS_PID
echo "🛑 Services stopped"
""")
        
        # Make executable
        os.chmod(startup_script, 0o755)
        print("✅ Startup script created and made executable")
    except Exception as e:
        print(f"❌ Error creating startup script: {e}")
        return False
    
    # 6. Final summary
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Start the services: ./start_taifa_with_n8n.sh")
    print("2. Import the n8n workflow from n8n-workflows/funding-pipeline-sqlite.json")
    print("3. Configure SQLite credentials in n8n")
    print("4. Test the pipeline with: curl http://localhost:8000/api/v1/webhooks/health")
    print("5. Check pipeline stats: curl http://localhost:8000/api/v1/webhooks/pipeline-stats")
    
    print("\n📁 Created Files:")
    print("- data/taifa_fiala.db (SQLite database)")
    print("- backend/database/sqlite_manager.py (Database manager)")
    print("- backend/api/webhooks.py (FastAPI webhook endpoints)")
    print("- backend/main_with_webhooks.py (FastAPI app with webhooks)")
    print("- n8n-workflows/funding-pipeline-sqlite.json (n8n workflow)")
    print("- n8n-workflows/sqlite_direct_insert.py (Direct Python integration)")
    print("- n8n-workflows/N8N_SETUP_GUIDE.md (Setup guide)")
    print("- start_taifa_with_n8n.sh (Startup script)")
    
    return True

if __name__ == "__main__":
    success = setup_complete_integration()
    if success:
        print("\n✅ TAIFA-FIALA n8n SQLite integration setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)