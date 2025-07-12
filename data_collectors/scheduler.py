#!/usr/bin/env python3
"""
Production Data Collection Scheduler for Railway
Includes health check endpoint and proper logging
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from threading import Thread
import uvicorn

# Import the daily scheduler
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from daily_scheduler import DailyCollectionScheduler

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='🚄 %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/railway_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app for health checks
app = FastAPI(title="TAIFA Data Collection Service")

# Global scheduler instance
scheduler_instance = None
last_collection_time = None
collection_status = "initializing"

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TAIFA Data Collection Service",
        "status": collection_status,
        "last_collection": last_collection_time.isoformat() if last_collection_time else None,
        "next_collection": "06:00 daily",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    global collection_status, last_collection_time
    
    # Check if scheduler is running
    is_healthy = collection_status in ["running", "completed"]
    
    # Check if collection ran recently (within last 25 hours)
    recent_collection = False
    if last_collection_time:
        hours_since_collection = (datetime.now() - last_collection_time).total_seconds() / 3600
        recent_collection = hours_since_collection < 25
    
    status_code = 200 if is_healthy else 503
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "scheduler_status": collection_status,
        "last_collection": last_collection_time.isoformat() if last_collection_time else None,
        "recent_collection": recent_collection,
        "uptime": "running"
    }

@app.get("/status")
async def detailed_status():
    """Detailed status for monitoring"""
    return {
        "service": "TAIFA Data Collection",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "scheduler_status": collection_status,
        "last_collection": last_collection_time.isoformat() if last_collection_time else None,
        "database_url": "configured" if os.getenv("DATABASE_URL") else "missing",
        "serper_api": "configured" if os.getenv("SERPER_DEV_API_KEY") else "missing",
        "collection_schedule": "06:00 daily UTC"
    }

def run_scheduled_collection():
    """Wrapper for the collection process"""
    global collection_status, last_collection_time
    
    logger.info("🚀 Starting scheduled collection")
    collection_status = "running"
    
    try:
        # Run the collection
        asyncio.run(scheduler_instance.run_daily_collection())
        
        # Update status
        collection_status = "completed"
        last_collection_time = datetime.now()
        
        logger.info("✅ Scheduled collection completed successfully")
        
    except Exception as e:
        collection_status = "error"
        logger.error(f"❌ Collection failed: {e}")

def start_scheduler():
    """Start the collection scheduler"""
    global scheduler_instance, collection_status
    
    logger.info("🕐 Starting TAIFA collection scheduler for Railway")
    
    # Initialize scheduler
    scheduler_instance = DailyCollectionScheduler()
    
    # Schedule daily collection at 6 AM UTC
    schedule.every().day.at("06:00").do(run_scheduled_collection)
    
    # Schedule weekly cleanup on Sundays at 2 AM UTC  
    schedule.every().sunday.at("02:00").do(
        lambda: asyncio.run(scheduler_instance.cleanup_expired_opportunities())
    )
    
    collection_status = "scheduled"
    logger.info("✅ Scheduler configured: 06:00 daily, cleanup Sundays 02:00")
    
    # Run scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("⏹️ Scheduler stopped by interrupt")
        collection_status = "stopped"
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")
        collection_status = "error"

def start_health_server():
    """Start the health check server"""
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🏥 Starting health check server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

def main():
    """Main function for Railway deployment"""
    load_dotenv()
    
    logger.info("🚄 TAIFA Data Collection Service starting on Railway")
    
    # Check environment
    if not os.getenv("DATABASE_URL"):
        logger.error("❌ DATABASE_URL not configured")
        return
    
    if not os.getenv("SERPER_DEV_API_KEY"):
        logger.warning("⚠️ SERPER_DEV_API_KEY not configured")
    
    # Start health server in a separate thread
    health_thread = Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Give health server time to start
    time.sleep(2)
    
    # Start the main scheduler
    start_scheduler()

if __name__ == "__main__":
    main()
