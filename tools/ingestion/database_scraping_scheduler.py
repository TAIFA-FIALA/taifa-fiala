"""
Database Scraping Scheduler Service
Integrates scheduled database scraping with the existing daily scheduler
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import os

from scheduled_database_scraper import ScheduledDatabaseScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseScrapingScheduler:
    """Scheduler service for automated database scraping"""
    
    def __init__(self):
        self.scraper = ScheduledDatabaseScraper()
        self.is_running = False
        self.last_run_report = None
        
    def start_scheduler(self):
        """Start the database scraping scheduler"""
        logger.info("🚀 Starting Database Scraping Scheduler")
        
        # Schedule different frequencies for different checks
        schedule.every(1).hours.do(self._run_hourly_check)
        schedule.every(6).hours.do(self._run_six_hourly_check)
        schedule.every().day.at("06:00").do(self._run_daily_check)
        schedule.every().day.at("18:00").do(self._run_evening_check)
        
        self.is_running = True
        
        # Run initial check
        asyncio.run(self._run_initial_check())
        
        # Main scheduler loop
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                self.is_running = False
            except Exception as e:
                logger.error(f"❌ Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _run_initial_check(self):
        """Run initial check on startup"""
        logger.info("🔍 Running initial database check")
        return self._execute_scraping("initial")
    
    def _run_hourly_check(self):
        """Run hourly check for high-frequency databases"""
        logger.info("⏰ Running hourly database check")
        asyncio.run(self._execute_scraping("hourly"))
    
    def _run_six_hourly_check(self):
        """Run six-hourly check for medium-frequency databases"""
        logger.info("⏰ Running six-hourly database check")
        asyncio.run(self._execute_scraping("six_hourly"))
    
    def _run_daily_check(self):
        """Run daily morning check"""
        logger.info("🌅 Running daily morning database check")
        asyncio.run(self._execute_scraping("daily_morning"))
    
    def _run_evening_check(self):
        """Run evening check"""
        logger.info("🌆 Running evening database check")
        asyncio.run(self._execute_scraping("evening"))
    
    async def _execute_scraping(self, check_type: str):
        """Execute the database scraping"""
        try:
            logger.info(f"📡 Starting {check_type} database scraping")
            
            # Get status before scraping
            status_before = await self.scraper.get_scraping_status()
            
            # Run the scraping
            report = await self.scraper.run_scheduled_scraping()
            
            # Store the report
            self.last_run_report = {
                'check_type': check_type,
                'timestamp': datetime.now().isoformat(),
                'report': report,
                'status_before': status_before
            }
            
            # Log summary
            stats = report.get('statistics', {})
            logger.info(f"✅ {check_type} scraping complete:")
            logger.info(f"   📊 Total scraped: {stats.get('total_scraped', 0)}")
            logger.info(f"   ✨ New opportunities: {stats.get('new_opportunities', 0)}")
            logger.info(f"   🔄 Duplicates found: {stats.get('duplicates_found', 0)}")
            logger.info(f"   ❌ Errors: {stats.get('errors', 0)}")
            
            # Save report to file
            self._save_report_to_file(self.last_run_report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error in {check_type} scraping: {str(e)}")
            return None
    
    def _save_report_to_file(self, report: Dict[str, Any]):
        """Save scraping report to file"""
        try:
            reports_dir = "/Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/logs/database_scraping"
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_scraping_report_{timestamp}.json"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📝 Report saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving report: {str(e)}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'current_time': datetime.now().isoformat(),
            'last_run_report': self.last_run_report,
            'scheduled_jobs': [
                {
                    'interval': '1 hour',
                    'job': 'Hourly check for high-frequency databases',
                    'next_run': str(schedule.jobs[0].next_run) if schedule.jobs else None
                },
                {
                    'interval': '6 hours', 
                    'job': 'Six-hourly check for medium-frequency databases',
                    'next_run': str(schedule.jobs[1].next_run) if len(schedule.jobs) > 1 else None
                },
                {
                    'interval': 'Daily 06:00',
                    'job': 'Daily morning comprehensive check',
                    'next_run': str(schedule.jobs[2].next_run) if len(schedule.jobs) > 2 else None
                },
                {
                    'interval': 'Daily 18:00',
                    'job': 'Evening update check',
                    'next_run': str(schedule.jobs[3].next_run) if len(schedule.jobs) > 3 else None
                }
            ]
        }
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        logger.info("🛑 Stopping Database Scraping Scheduler")
        self.is_running = False
        schedule.clear()

# Integration with existing daily scheduler
def integrate_with_daily_scheduler():
    """Integration function for the existing daily scheduler"""
    
    async def run_database_scraping():
        """Function to be called by the existing daily scheduler"""
        scraper = ScheduledDatabaseScraper()
        
        try:
            logger.info("🔄 Daily database scraping initiated by daily scheduler")
            report = await scraper.run_scheduled_scraping()
            
            # Log results
            stats = report.get('statistics', {})
            logger.info(f"📊 Daily database scraping results:")
            logger.info(f"   New opportunities: {stats.get('new_opportunities', 0)}")
            logger.info(f"   Duplicates prevented: {stats.get('duplicates_found', 0)}")
            logger.info(f"   Databases scraped: {report.get('databases_configured', 0)}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error in daily database scraping: {str(e)}")
            return None
    
    return run_database_scraping

# Standalone scheduler service
def run_standalone_scheduler():
    """Run the database scraping scheduler as a standalone service"""
    scheduler = DatabaseScrapingScheduler()
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler service stopped")
    finally:
        scheduler.stop_scheduler()

if __name__ == "__main__":
    # Run as standalone service
    run_standalone_scheduler()
