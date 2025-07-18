#!/usr/bin/env python3
"""
TAIFA-FIALA Daily Collection Scheduler
Runs the SERPER collection process daily to keep the database fresh
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Import the actual collection modules
import sys
sys.path.append(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='📅 %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyCollectionScheduler:
    """Schedules and manages daily intelligence item collection"""
    
    def __init__(self):
        load_dotenv()
        self.serper_api_key = os.getenv("SERPER_DEV_API_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        
        # Collection settings
        self.collection_time = "06:00"  # 6 AM local time
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes between retries
        
    async def run_daily_collection(self):
        """Execute the daily collection process"""
        logger.info("🚀 Starting daily intelligence item collection")
        
        start_time = datetime.now()
        
        try:
            # Import and run the collection pipeline
            from data_collectors.serper_search.collector import SerperSearchCollector
            
            collector = SerperSearchCollector(self.serper_api_key)
            opportunities = await collector.start_collection()
            
            # Store opportunities in database
            stored_count = await self._store_opportunities(opportunities)
            
            # Send summary notification
            await self._send_collection_summary(stored_count, start_time)
            
            logger.info(f"✅ Daily collection completed: {stored_count} new opportunities")
            
        except Exception as e:
            logger.error(f"❌ Daily collection failed: {e}")
            await self._send_error_notification(str(e))
    
    async def _store_opportunities(self, opportunities):
        """Store opportunities in database with deduplication"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        stored_count = 0
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            for opp in opportunities:
                # Check for duplicates
                cursor.execute(
                    "SELECT id FROM africa_intelligence_feed WHERE source_url = %s OR title = %s",
                    (opp.get('source_url'), opp.get('title'))
                )
                
                if cursor.fetchone():
                    continue  # Skip duplicates
                
                # Insert new opportunity
                insert_query = """
                INSERT INTO africa_intelligence_feed (
                    title, description, source_url, status, 
                    geographical_scope, created_at, last_checked
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    opp.get('title'),
                    opp.get('description'),
                    opp.get('source_url'),
                    'active',
                    'Africa',
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                stored_count += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database storage error: {e}")
        
        return stored_count
    
    async def _send_collection_summary(self, count, start_time):
        """Send summary of collection results"""
        duration = datetime.now() - start_time
        
        summary = {
            "collection_date": datetime.now().isoformat(),
            "new_opportunities": count,
            "duration_minutes": duration.total_seconds() / 60,
            "status": "success"
        }
        
        logger.info(f"📊 Collection Summary: {summary}")
        
        # Send to n8n/Notion if configured
        if self.n8n_webhook_url:
            await self._send_webhook_notification(summary)
    
    async def _send_error_notification(self, error_message):
        """Send error notification"""
        error_data = {
            "collection_date": datetime.now().isoformat(),
            "status": "error",
            "error_message": error_message
        }
        
        if self.n8n_webhook_url:
            await self._send_webhook_notification(error_data)
    
    async def _send_webhook_notification(self, data):
        """Send notification via webhook"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.n8n_webhook_url, json=data) as response:
                    if response.status == 200:
                        logger.info("✅ Notification sent successfully")
                    else:
                        logger.warning(f"⚠️ Notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Webhook notification error: {e}")
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        logger.info(f"🕐 Scheduling daily collection at {self.collection_time}")
        
        # Schedule daily collection
        schedule.every().day.at(self.collection_time).do(
            lambda: asyncio.run(self.run_daily_collection())
        )
        
        # Schedule weekly cleanup (remove old expired opportunities)
        schedule.every().sunday.at("02:00").do(
            lambda: asyncio.run(self.cleanup_expired_opportunities())
        )
        
        logger.info("✅ Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler stopped")
    
    async def cleanup_expired_opportunities(self):
        """Clean up expired opportunities weekly"""
        logger.info("🧹 Running weekly cleanup of expired opportunities")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Mark opportunities as expired if deadline has passed
            cursor.execute("""
                UPDATE africa_intelligence_feed 
                SET status = 'expired' 
                WHERE deadline < NOW() AND status = 'active'
            """)
            
            expired_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Marked {expired_count} opportunities as expired")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Main function to run the scheduler"""
    scheduler = DailyCollectionScheduler()
    
    # Check prerequisites
    if not scheduler.serper_api_key:
        logger.error("❌ SERPER_DEV_API_KEY not found in environment")
        return
    
    if not scheduler.database_url:
        logger.error("❌ DATABASE_URL not found in environment")
        return
    
    logger.info("🎯 TAIFA Daily Collection Scheduler")
    logger.info("=" * 50)
    logger.info(f"Collection time: {scheduler.collection_time} daily")
    logger.info("Cleanup time: 02:00 Sundays")
    logger.info("=" * 50)
    
    # Start the scheduler
    scheduler.start_scheduler()

if __name__ == "__main__":
    main()
