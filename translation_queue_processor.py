"""
TAIFA-FIALA Translation Queue Processor
Automated translation workflow for funding opportunities
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collectors'))

from translation_service import TranslationService, ContentType

logger = logging.getLogger(__name__)

class TranslationQueueProcessor:
    """Processes translation queue with intelligent prioritization"""
    
    def __init__(self):
        self.translation_service = None
        self.db_connector = None
        self.is_running = False
        self.batch_size = 10
        self.processing_interval = 30  # seconds
        
    async def initialize(self):
        """Initialize the translation queue processor"""
        try:
            # Initialize translation service
            self.translation_service = TranslationService()
            await self.translation_service.initialize()
            
            # Get database connector from translation service
            self.db_connector = self.translation_service.db_connector
            
            logger.info("✅ Translation queue processor initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Translation queue processor initialization failed: {e}")
            return False
    
    async def start_processing(self):
        """Start the translation queue processing loop"""
        if self.is_running:
            logger.warning("Translation queue processor is already running")
            return
            
        logger.info("🚀 Starting translation queue processor...")
        self.is_running = True
        
        try:
            while self.is_running:
                await self._process_translation_batch()
                await asyncio.sleep(self.processing_interval)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal...")
            await self.stop_processing()
        except Exception as e:
            logger.error(f"Error in translation processing loop: {e}")
            await self.stop_processing()
    
    async def stop_processing(self):
        """Stop the translation queue processor"""
        logger.info("Stopping translation queue processor...")
        self.is_running = False
        
        if self.translation_service:
            await self.translation_service.close()
        
        logger.info("✅ Translation queue processor stopped")
    
    async def _process_translation_batch(self):
        """Process a batch of translations from the queue"""
        try:
            # Get pending translations ordered by priority
            async with self.db_connector.pool.acquire() as conn:
                pending_translations = await conn.fetch("""
                    SELECT id, source_table, source_id, source_field, target_language, priority
                    FROM translation_queue 
                    WHERE status = 'pending' 
                    AND attempts < max_attempts
                    AND scheduled_at <= NOW()
                    ORDER BY priority DESC, scheduled_at ASC
                    LIMIT $1
                """, self.batch_size)
            
            if not pending_translations:
                logger.debug("No pending translations in queue")
                return
            
            logger.info(f"📝 Processing {len(pending_translations)} translations...")
            
            # Process each translation
            for translation_req in pending_translations:
                await self._process_single_translation(translation_req)
                
                # Small delay between translations to respect API limits
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error processing translation batch: {e}")
    
    async def _process_single_translation(self, translation_req: Dict[str, Any]):
        """Process a single translation request"""
        req_id = translation_req['id']
        source_table = translation_req['source_table']
        source_id = translation_req['source_id']
        source_field = translation_req['source_field']
        target_language = translation_req['target_language']
        
        try:
            # Mark as processing
            await self._update_translation_status(req_id, 'processing')
            
            # Get the source text
            source_text = await self._get_source_text(source_table, source_id, source_field)
            if not source_text:
                await self._update_translation_status(req_id, 'failed', "Source text not found")
                return
            
            # Determine content type
            content_type = self._determine_content_type(source_field)
            
            # Detect source language
            source_language = await self._detect_source_language(source_table, source_id)
            
            # Skip if already in target language
            if source_language == target_language:
                await self._save_translation(source_table, source_id, source_field, target_language,
                                           source_text, source_text, "no_translation_needed", 1.0)
                await self._update_translation_status(req_id, 'completed')
                return
            
            # Perform translation
            translation_result = await self.translation_service.translate_text(
                source_text,
                target_language,
                source_language,
                content_type
            )
            
            # Save translation
            await self._save_translation(
                source_table, source_id, source_field, target_language,
                source_text, translation_result['translated_text'],
                translation_result['provider'], translation_result['confidence']
            )
            
            # Mark as completed
            await self._update_translation_status(req_id, 'completed')
            
            logger.info(f"✅ Translated {source_field} for {source_table}:{source_id} to {target_language}")
            
        except Exception as e:
            logger.error(f"Translation failed for {source_table}:{source_id}.{source_field}: {e}")
            
            # Update attempts and possibly mark as failed
            await self._handle_translation_error(req_id, str(e))
    
    async def _get_source_text(self, source_table: str, source_id: int, source_field: str) -> Optional[str]:
        """Get the source text to translate"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                query = f"SELECT {source_field} FROM {source_table} WHERE id = $1"
                result = await conn.fetchval(query, source_id)
                return result
        except Exception as e:
            logger.error(f"Error getting source text: {e}")
            return None
    
    async def _detect_source_language(self, source_table: str, source_id: int) -> str:
        """Detect the source language of content"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                # Check if language is already detected
                if source_table == 'funding_opportunities':
                    detected_lang = await conn.fetchval(
                        "SELECT detected_language FROM funding_opportunities WHERE id = $1", 
                        source_id
                    )
                    return detected_lang or 'en'
                
                # Default to English for other tables
                return 'en'
                
        except Exception as e:
            logger.error(f"Error detecting source language: {e}")
            return 'en'
    
    def _determine_content_type(self, source_field: str) -> ContentType:
        """Determine content type based on field name"""
        field_mapping = {
            'title': ContentType.TITLE,
            'description': ContentType.DESCRIPTION,
            'summary': ContentType.DESCRIPTION,
            'content': ContentType.DESCRIPTION,
            'requirements': ContentType.TECHNICAL,
            'eligibility': ContentType.LEGAL,
            'terms': ContentType.LEGAL,
            'application_process': ContentType.TECHNICAL
        }
        
        return field_mapping.get(source_field.lower(), ContentType.DESCRIPTION)
    
    async def _save_translation(self, source_table: str, source_id: int, source_field: str,
                              target_language: str, original_text: str, translated_text: str,
                              provider: str, confidence: float):
        """Save translation to database"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO translations (
                        source_table, source_id, source_field, target_language,
                        original_text, translated_text, translation_service, confidence_score
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (source_table, source_id, source_field, target_language)
                    DO UPDATE SET 
                        original_text = EXCLUDED.original_text,
                        translated_text = EXCLUDED.translated_text,
                        translation_service = EXCLUDED.translation_service,
                        confidence_score = EXCLUDED.confidence_score,
                        updated_at = CURRENT_TIMESTAMP
                """, source_table, source_id, source_field, target_language,
                    original_text, translated_text, provider, confidence)
                
        except Exception as e:
            logger.error(f"Error saving translation: {e}")
            raise
    
    async def _update_translation_status(self, req_id: int, status: str, error_message: Optional[str] = None):
        """Update translation request status"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                if status == 'processing':
                    await conn.execute("""
                        UPDATE translation_queue 
                        SET status = $1, started_at = CURRENT_TIMESTAMP, attempts = attempts + 1
                        WHERE id = $2
                    """, status, req_id)
                elif status == 'completed':
                    await conn.execute("""
                        UPDATE translation_queue 
                        SET status = $1, completed_at = CURRENT_TIMESTAMP
                        WHERE id = $2
                    """, status, req_id)
                elif status == 'failed':
                    await conn.execute("""
                        UPDATE translation_queue 
                        SET status = $1, error_message = $2, completed_at = CURRENT_TIMESTAMP
                        WHERE id = $3
                    """, status, error_message, req_id)
                    
        except Exception as e:
            logger.error(f"Error updating translation status: {e}")
    
    async def _handle_translation_error(self, req_id: int, error_message: str):
        """Handle translation error with retry logic"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                # Get current attempt count
                attempt_info = await conn.fetchrow("""
                    SELECT attempts, max_attempts FROM translation_queue WHERE id = $1
                """, req_id)
                
                if attempt_info['attempts'] >= attempt_info['max_attempts']:
                    # Max attempts reached, mark as failed
                    await self._update_translation_status(req_id, 'failed', error_message)
                else:
                    # Schedule retry with exponential backoff
                    retry_delay = min(300, 60 * (2 ** attempt_info['attempts']))  # Max 5 minutes
                    retry_time = datetime.utcnow() + timedelta(seconds=retry_delay)
                    
                    await conn.execute("""
                        UPDATE translation_queue 
                        SET status = 'pending', 
                            scheduled_at = $1,
                            error_message = $2
                        WHERE id = $3
                    """, retry_time, error_message, req_id)
                    
                    logger.info(f"Scheduled retry for translation {req_id} in {retry_delay} seconds")
                    
        except Exception as e:
            logger.error(f"Error handling translation error: {e}")
    
    async def queue_content_for_translation(self, source_table: str, source_id: int, 
                                          fields: List[str], target_languages: List[str],
                                          priority: int = 1):
        """Queue content for translation"""
        try:
            async with self.db_connector.pool.acquire() as conn:
                for field in fields:
                    for target_lang in target_languages:
                        await conn.execute("""
                            SELECT queue_for_translation($1, $2, $3, $4, $5)
                        """, source_table, source_id, field, target_lang, priority)
                        
            logger.info(f"Queued {len(fields)} fields × {len(target_languages)} languages for translation")
            
        except Exception as e:
            logger.error(f"Error queuing content for translation: {e}")

# Integration with data collection pipeline
async def auto_translate_new_opportunities():
    """Automatically queue new funding opportunities for translation"""
    processor = TranslationQueueProcessor()
    await processor.initialize()
    
    try:
        # Get recent opportunities that haven't been queued for translation
        async with processor.db_connector.pool.acquire() as conn:
            recent_opportunities = await conn.fetch("""
                SELECT fo.id, fo.title, fo.description
                FROM funding_opportunities fo
                LEFT JOIN translation_queue tq ON fo.id = tq.source_id 
                    AND tq.source_table = 'funding_opportunities'
                WHERE fo.discovered_date > NOW() - INTERVAL '24 hours'
                AND tq.id IS NULL
                LIMIT 50
            """)
            
        if recent_opportunities:
            logger.info(f"🔄 Auto-queuing {len(recent_opportunities)} recent opportunities for translation")
            
            for opp in recent_opportunities:
                await processor.queue_content_for_translation(
                    'funding_opportunities',
                    opp['id'],
                    ['title', 'description'],
                    ['fr'],  # Translate to French
                    priority=2  # Medium priority for auto-translation
                )
                
        logger.info("✅ Auto-translation queuing completed")
        
    finally:
        await processor.stop_processing()

# CLI interface
async def main():
    """Main entry point for translation queue processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TAIFA-FIALA Translation Queue Processor')
    parser.add_argument('--mode', choices=['process', 'auto-queue', 'test'], 
                       default='process', help='Operation mode')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='Translation batch size')
    parser.add_argument('--interval', type=int, default=30,
                       help='Processing interval in seconds')
    
    args = parser.parse_args()
    
    if args.mode == 'process':
        processor = TranslationQueueProcessor()
        processor.batch_size = args.batch_size
        processor.processing_interval = args.interval
        
        await processor.initialize()
        await processor.start_processing()
        
    elif args.mode == 'auto-queue':
        await auto_translate_new_opportunities()
        
    elif args.mode == 'test':
        # Test translation service
        from translation_service import test_translation_service
        await test_translation_service()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())