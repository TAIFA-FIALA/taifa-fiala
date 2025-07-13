"""
TAIFA CrewAI ETL Integration Pipeline
Main orchestrator for the complete intelligent funding discovery system
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import schedule
import time
from pathlib import Path
import os

# Import all our CrewAI components
from data_processors.crews.enhanced_funding_crew import (
    EnhancedFundingOpportunityProcessor, 
    process_serper_results_enhanced
)
from data_processors.crews.organization_enrichment_crew import (
    OrganizationEnrichmentPipeline,
    trigger_organization_enrichment_webhook
)
from data_processors.translation.translation_pipeline import (
    TranslationPipelineService,
    create_translation_service
)
from data_processors.community.validation_service import (
    CommunityValidationService,
    create_validation_service,
    daily_newsletter_job,
    auto_publication_check_job
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/taifa_crewai_pipeline.log'),
        logging.StreamHandler()
    ]
)

class TaifaCrewAIPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize components
        self.funding_processor = None
        self.organization_enricher = None
        self.translation_service = None
        self.validation_service = None
        
        # Pipeline statistics
        self.stats = {
            "opportunities_processed": 0,
            "opportunities_approved": 0,
            "opportunities_rejected": 0,
            "organizations_enriched": 0,
            "translations_completed": 0,
            "community_validations": 0,
            "pipeline_runs": 0,
            "last_run": None,
            "errors": []
        }
    
    async def initialize(self):
        """Initialize all pipeline components"""
        
        try:
            logging.info("Initializing TAIFA CrewAI Pipeline...")
            
            # Initialize funding opportunity processor
            self.funding_processor = EnhancedFundingOpportunityProcessor()
            logging.info("✅ Funding opportunity processor initialized")
            
            # Initialize organization enrichment pipeline
            apify_token = self.config.get("apify_api_token", "your_apify_token")
            self.organization_enricher = OrganizationEnrichmentPipeline(apify_token)
            logging.info("✅ Organization enrichment pipeline initialized")
            
            # Initialize translation service
            self.translation_service = await create_translation_service()
            logging.info("✅ Translation service initialized")
            
            # Initialize community validation service
            self.validation_service = await create_validation_service()
            logging.info("✅ Community validation service initialized")
            
            # Start background services
            await self._start_background_services()
            
            logging.info("🚀 TAIFA CrewAI Pipeline fully initialized!")
            
        except Exception as e:
            logging.error(f"❌ Pipeline initialization failed: {e}")
            raise
    
    async def _start_background_services(self):
        """Start background services"""
        
        # Start translation queue processing
        if self.translation_service:
            asyncio.create_task(self.translation_service.start_processing())
            logging.info("🔄 Translation queue processor started")
        
        # Schedule periodic tasks
        self._schedule_periodic_tasks()
        logging.info("⏰ Periodic tasks scheduled")
    
    def _schedule_periodic_tasks(self):
        """Schedule periodic background tasks"""
        
        # Daily newsletter at 9:00 AM UTC
        schedule.every().day.at("09:00").do(self._run_daily_newsletter_job)
        
        # Auto-publication check every hour
        schedule.every().hour.do(self._run_auto_publication_check)
        
        # Performance monitoring every 6 hours
        schedule.every(6).hours.do(self._run_performance_monitoring)
        
        # Organization knowledge base update every 12 hours
        schedule.every(12).hours.do(self._update_organization_knowledge)
        
        # Start scheduler in background
        asyncio.create_task(self._run_scheduler())
    
    async def _run_scheduler(self):
        """Run the background scheduler"""
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    def _run_daily_newsletter_job(self):
        """Wrapper for daily newsletter job"""
        asyncio.create_task(daily_newsletter_job())
    
    def _run_auto_publication_check(self):
        """Wrapper for auto-publication check"""
        asyncio.create_task(auto_publication_check_job())
    
    def _run_performance_monitoring(self):
        """Wrapper for performance monitoring"""
        asyncio.create_task(self._monitor_performance())
    
    def _update_organization_knowledge(self):
        """Wrapper for organization knowledge update"""
        asyncio.create_task(self._update_org_knowledge_base())
    
    async def process_serper_batch(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of SERPER search results through the complete pipeline"""
        
        batch_start_time = datetime.utcnow()
        batch_id = f"batch_{int(time.time())}"
        
        logging.info(f"🔄 Starting batch processing: {batch_id} ({len(search_results)} results)")
        
        try:
            # Step 1: Enhanced CrewAI processing with conflict resolution
            processed_opportunities, rejected_opportunities = await process_serper_results_enhanced(search_results)
            
            logging.info(f"📊 Processing results: {len(processed_opportunities)} approved, {len(rejected_opportunities)} rejected")
            
            # Step 2: Trigger organization enrichment for new organizations
            enrichment_tasks = []
            for opportunity in processed_opportunities:
                org_name = opportunity.get("organization_name")
                if org_name and not await self._organization_exists(org_name):
                    enrichment_task = self._enrich_organization_async(
                        org_name,
                        opportunity.get("organization_type"),
                        opportunity.get("organization_country"),
                        f"batch_{batch_id}"
                    )
                    enrichment_tasks.append(enrichment_task)
            
            # Run organization enrichment in parallel
            if enrichment_tasks:
                enrichment_results = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
                successful_enrichments = [r for r in enrichment_results if not isinstance(r, Exception)]
                logging.info(f"🏢 Organization enrichment: {len(successful_enrichments)} completed")
            
            # Step 3: Queue translations for approved opportunities
            translation_requests = []
            for opportunity in processed_opportunities:
                if opportunity.get("review_status") in ["auto_approved", "community_review_queue"]:
                    translation_id = await self.translation_service.translate_funding_opportunity(
                        opportunity.get("content_id", opportunity["id"])
                    )
                    translation_requests.append(translation_id)
            
            logging.info(f"🌐 Translation requests: {len(translation_requests)} queued")
            
            # Step 4: Store all results in database
            stored_opportunities = await self._store_batch_results(
                batch_id, processed_opportunities, rejected_opportunities
            )
            
            # Step 5: Update pipeline statistics
            self._update_pipeline_stats(processed_opportunities, rejected_opportunities, enrichment_tasks, translation_requests)
            
            # Step 6: Prepare batch summary
            batch_summary = {
                "batch_id": batch_id,
                "processing_time_seconds": (datetime.utcnow() - batch_start_time).total_seconds(),
                "input_count": len(search_results),
                "processed_count": len(processed_opportunities),
                "rejected_count": len(rejected_opportunities),
                "organizations_enriched": len(enrichment_tasks),
                "translations_queued": len(translation_requests),
                "stored_opportunities": len(stored_opportunities),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logging.info(f"✅ Batch processing completed: {batch_id}")
            return batch_summary
            
        except Exception as e:
            logging.error(f"❌ Batch processing failed: {batch_id} - {e}")
            self.stats["errors"].append({
                "batch_id": batch_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            raise
    
    async def _organization_exists(self, org_name: str) -> bool:
        """Check if organization already exists in database"""
        try:
            # This would query your organizations table
            # For now, return False to trigger enrichment
            return False
        except Exception as e:
            logging.error(f"Error checking organization existence: {e}")
            return False
    
    async def _enrich_organization_async(self, org_name: str, org_type: str = None, 
                                       org_country: str = None, trigger_source: str = "pipeline") -> Dict[str, Any]:
        """Asynchronously enrich organization"""
        try:
            result = await self.organization_enricher.enrich_organization(
                org_name=org_name,
                org_type=org_type,
                org_country=org_country,
                trigger_source=trigger_source
            )
            return result
        except Exception as e:
            logging.error(f"Organization enrichment failed for {org_name}: {e}")
            return {"error": str(e), "organization_name": org_name}
    
    async def _store_batch_results(self, batch_id: str, processed_opportunities: List[Dict], 
                                 rejected_opportunities: List[Dict]) -> List[int]:
        """Store batch processing results in database"""
        
        stored_ids = []
        
        try:
            # Store approved/review opportunities
            for opportunity in processed_opportunities:
                # This would insert into funding_opportunities table
                stored_id = await self._store_funding_opportunity(opportunity, batch_id)
                if stored_id:
                    stored_ids.append(stored_id)
            
            # Store rejected opportunities in learning database
            for rejected in rejected_opportunities:
                await self._store_rejected_opportunity(rejected, batch_id)
            
            logging.info(f"💾 Stored {len(stored_ids)} opportunities for batch {batch_id}")
            
        except Exception as e:
            logging.error(f"Error storing batch results: {e}")
        
        return stored_ids
    
    async def _store_funding_opportunity(self, opportunity: Dict, batch_id: str) -> Optional[int]:
        """Store individual funding opportunity"""
        try:
            # This would insert into your funding_opportunities table
            # For now, return mock ID
            return hash(opportunity.get("title", "")) % 10000
        except Exception as e:
            logging.error(f"Error storing opportunity: {e}")
            return None
    
    async def _store_rejected_opportunity(self, rejected: Dict, batch_id: str):
        """Store rejected opportunity in learning database"""
        try:
            # This would insert into rejected_opportunities table
            pass
        except Exception as e:
            logging.error(f"Error storing rejected opportunity: {e}")
    
    def _update_pipeline_stats(self, processed: List[Dict], rejected: List[Dict], 
                             enrichments: List, translations: List):
        """Update pipeline statistics"""
        
        self.stats["opportunities_processed"] += len(processed)
        self.stats["opportunities_rejected"] += len(rejected)
        self.stats["organizations_enriched"] += len(enrichments)
        self.stats["translations_completed"] += len(translations)
        self.stats["pipeline_runs"] += 1
        self.stats["last_run"] = datetime.utcnow().isoformat()
        
        # Count approved vs community review
        auto_approved = len([o for o in processed if o.get("review_status") == "auto_approved"])
        self.stats["opportunities_approved"] += auto_approved
    
    async def _monitor_performance(self):
        """Monitor pipeline performance and agent accuracy"""
        
        try:
            logging.info("📈 Running performance monitoring...")
            
            # Get agent performance metrics
            agent_metrics = await self._calculate_agent_performance()
            
            # Get pipeline health metrics
            pipeline_health = self._calculate_pipeline_health()
            
            # Log performance summary
            self._log_performance_summary(agent_metrics, pipeline_health)
            
            # Store metrics in database
            await self._store_performance_metrics(agent_metrics, pipeline_health)
            
        except Exception as e:
            logging.error(f"Performance monitoring failed: {e}")
    
    async def _calculate_agent_performance(self) -> Dict[str, Any]:
        """Calculate agent performance metrics"""
        
        # This would query your agent_processing_logs and conflict_resolutions tables
        # For now, return mock metrics
        return {
            "parser_agent": {"accuracy": 0.89, "avg_confidence": 0.85, "processing_time_ms": 1200},
            "relevancy_agent": {"accuracy": 0.92, "avg_confidence": 0.88, "processing_time_ms": 800},
            "summarizer_agent": {"accuracy": 0.94, "avg_confidence": 0.91, "processing_time_ms": 1500},
            "extractor_agent": {"accuracy": 0.87, "avg_confidence": 0.82, "processing_time_ms": 1000}
        }
    
    def _calculate_pipeline_health(self) -> Dict[str, Any]:
        """Calculate overall pipeline health"""
        
        total_processed = self.stats["opportunities_processed"]
        total_approved = self.stats["opportunities_approved"]
        total_rejected = self.stats["opportunities_rejected"]
        
        approval_rate = total_approved / max(total_processed, 1)
        rejection_rate = total_rejected / max(total_processed, 1)
        
        return {
            "approval_rate": approval_rate,
            "rejection_rate": rejection_rate,
            "processing_throughput": total_processed / max(self.stats["pipeline_runs"], 1),
            "error_rate": len(self.stats["errors"]) / max(self.stats["pipeline_runs"], 1),
            "uptime_hours": (datetime.utcnow() - datetime.fromisoformat(self.stats.get("last_run", datetime.utcnow().isoformat()))).total_seconds() / 3600
        }
    
    def _log_performance_summary(self, agent_metrics: Dict, pipeline_health: Dict):
        """Log performance summary"""
        
        logging.info("📊 PERFORMANCE SUMMARY:")
        logging.info(f"   Pipeline Health:")
        logging.info(f"     - Approval Rate: {pipeline_health['approval_rate']:.2%}")
        logging.info(f"     - Rejection Rate: {pipeline_health['rejection_rate']:.2%}")
        logging.info(f"     - Error Rate: {pipeline_health['error_rate']:.2%}")
        logging.info(f"     - Processing Throughput: {pipeline_health['processing_throughput']:.1f} opps/run")
        
        logging.info(f"   Agent Performance:")
        for agent, metrics in agent_metrics.items():
            logging.info(f"     - {agent}: {metrics['accuracy']:.2%} accuracy, {metrics['avg_confidence']:.2f} confidence")
    
    async def _store_performance_metrics(self, agent_metrics: Dict, pipeline_health: Dict):
        """Store performance metrics in database"""
        try:
            # This would insert into agent_performance_metrics table
            pass
        except Exception as e:
            logging.error(f"Error storing performance metrics: {e}")
    
    async def _update_org_knowledge_base(self):
        """Update organization knowledge base for agent improvement"""
        
        try:
            logging.info("🧠 Updating organization knowledge base...")
            
            # This would trigger the OrganizationKnowledgeBase update
            # which refreshes agent prompts with new organization examples
            
            if self.funding_processor and hasattr(self.funding_processor, 'org_knowledge'):
                await self.funding_processor.org_knowledge.update_if_needed()
                logging.info("✅ Organization knowledge base updated")
        
        except Exception as e:
            logging.error(f"Error updating organization knowledge base: {e}")
    
    async def process_manual_submission(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process manually submitted funding opportunity"""
        
        try:
            logging.info(f"📝 Processing manual submission: {submission_data.get('title', 'Unknown')}")
            
            # Process through enhanced CrewAI pipeline
            processed = await self.funding_processor.process_opportunity_enhanced(submission_data)
            
            # High priority translation for manual submissions
            if processed.get("review_status") != "rejection_database":
                translation_id = await self.translation_service.translate_manual_submission(
                    content={
                        "title": processed.get("title", ""),
                        "description": processed.get("description", "")
                    },
                    priority="high"
                )
                processed["translation_request_id"] = translation_id
            
            # Store result
            opportunity_id = await self._store_funding_opportunity(processed, "manual_submission")
            processed["stored_id"] = opportunity_id
            
            logging.info(f"✅ Manual submission processed: {opportunity_id}")
            return processed
            
        except Exception as e:
            logging.error(f"❌ Manual submission processing failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        
        # Get component statuses
        translation_status = self.translation_service.get_status() if self.translation_service else {}
        validation_stats = self.validation_service.get_validation_statistics() if self.validation_service else {}
        
        return {
            "pipeline": {
                "is_running": self.is_running,
                "stats": self.stats,
                "last_update": datetime.utcnow().isoformat()
            },
            "translation_service": translation_status,
            "community_validation": validation_stats,
            "components": {
                "funding_processor": self.funding_processor is not None,
                "organization_enricher": self.organization_enricher is not None,
                "translation_service": self.translation_service is not None,
                "validation_service": self.validation_service is not None
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown the pipeline"""
        
        logging.info("🛑 Shutting down TAIFA CrewAI Pipeline...")
        
        self.is_running = False
        
        # Stop translation service
        if self.translation_service:
            await self.translation_service.stop_processing()
        
        # Save final statistics
        await self._save_final_stats()
        
        logging.info("✅ Pipeline shutdown complete")
    
    async def _save_final_stats(self):
        """Save final pipeline statistics"""
        try:
            # This would save stats to database or file
            with open("logs/pipeline_final_stats.json", "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving final stats: {e}")

# Main execution functions

async def create_pipeline(config_path: str = "config/crewai_config.json") -> TaifaCrewAIPipeline:
    """Create and initialize the pipeline"""
    
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Use default configuration
        config = {
            "apify_api_token": os.getenv("APIFY_API_TOKEN", "your_apify_token"),
            "translation_providers": {
                "azure_translator": {
                    "api_key": os.getenv("AZURE_TRANSLATOR_KEY", "your_azure_key"),
                    "region": os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
                },
                "deepl": {
                    "api_key": os.getenv("DEEPL_API_KEY", "your_deepl_key")
                },
                "openai_gpt4": {
                    "api_key": os.getenv("OPENAI_API_KEY", "your_openai_key")
                }
            },
            "community_validation": {
                "review_window_hours": 24,
                "smtp_server": "smtp.gmail.com",
                "email_user": os.getenv("SMTP_USER", "noreply@taifa-africa.com"),
                "email_password": os.getenv("SMTP_PASSWORD", "your_password")
            }
        }
    
    # Create and initialize pipeline
    pipeline = TaifaCrewAIPipeline(config)
    await pipeline.initialize()
    
    return pipeline

async def run_pipeline_daemon():
    """Run the pipeline as a daemon service"""
    
    pipeline = await create_pipeline()
    pipeline.is_running = True
    
    logging.info("🚀 TAIFA CrewAI Pipeline daemon started")
    
    try:
        # Keep running until shutdown
        while pipeline.is_running:
            await asyncio.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logging.info("Received shutdown signal")
    finally:
        await pipeline.shutdown()

async def process_serper_batch_standalone(search_results: List[Dict]) -> Dict[str, Any]:
    """Standalone function to process SERPER batch"""
    
    pipeline = await create_pipeline()
    try:
        result = await pipeline.process_serper_batch(search_results)
        return result
    finally:
        await pipeline.shutdown()

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TAIFA CrewAI ETL Pipeline")
    parser.add_argument("--mode", choices=["daemon", "batch", "status", "test"], 
                       default="daemon", help="Pipeline operation mode")
    parser.add_argument("--config", default="config/crewai_config.json",
                       help="Configuration file path")
    parser.add_argument("--input", help="Input file for batch processing")
    
    args = parser.parse_args()
    
    if args.mode == "daemon":
        asyncio.run(run_pipeline_daemon())
        
    elif args.mode == "batch":
        if not args.input:
            print("Error: --input required for batch mode")
            exit(1)
            
        # Load input data
        with open(args.input, 'r') as f:
            search_results = json.load(f)
        
        # Process batch
        result = asyncio.run(process_serper_batch_standalone(search_results))
        print(json.dumps(result, indent=2))
        
    elif args.mode == "status":
        async def get_status():
            pipeline = await create_pipeline()
            status = await pipeline.get_pipeline_status()
            print(json.dumps(status, indent=2))
            await pipeline.shutdown()
        
        asyncio.run(get_status())
        
    elif args.mode == "test":
        # Test mode with sample data
        sample_data = [
            {
                "title": "Test AI Grant",
                "snippet": "AI research funding for African universities",
                "link": "https://example.com/grant",
                "source_type": "test"
            }
        ]
        
        result = asyncio.run(process_serper_batch_standalone(sample_data))
        print("Test result:", json.dumps(result, indent=2))
