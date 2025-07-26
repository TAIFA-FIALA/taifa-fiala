"""
File Watcher Service for AI Africa Funding Tracker
=================================================

This module implements a file watcher service that monitors a directory for new files,
processes them using appropriate processors, and integrates the extracted data
with the existing database after deduplication.
"""

import os
import time
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InboxWatcher(FileSystemEventHandler):
    """
    Watchdog event handler that monitors a directory for new files
    and processes them using appropriate processors.
    """
    
    def __init__(self, processor_service):
        """
        Initialize the watcher with a processor service.
        
        Args:
            processor_service: Service that processes files based on their type
        """
        self.processor_service = processor_service
        self.processing_queue = []
        self.logger = logging.getLogger(__name__)
        
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: The file system event
        """
        if not event.is_directory:
            # Wait a moment to ensure file is fully written
            time.sleep(0.5)
            self.logger.info(f"New file detected: {event.src_path}")
            self.processing_queue.append(event.src_path)
            
    def on_modified(self, event):
        """
        Handle file modification events.
        
        Args:
            event: The file system event
        """
        if not event.is_directory and event.src_path.endswith('.csv'):
            # Handle CSV updates specifically
            if event.src_path not in self.processing_queue:
                self.logger.info(f"Modified CSV file detected: {event.src_path}")
                self.processing_queue.append(event.src_path)


class FileIngestionService:
    """
    Service that manages the file ingestion pipeline, including:
    - Watching directories for new files
    - Processing files based on their type
    - Deduplicating extracted data
    - Inserting data into the database
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the file ingestion service.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Create directory structure if it doesn't exist
        self._create_directory_structure()
        
        # Initialize the watcher
        self.watcher = InboxWatcher(self)
        self.observer = None
        
        # Import processors and other services here to avoid circular imports
        from .processors.pdf_processor import PDFProcessor
        from .processors.csv_processor import CSVProcessor
        from .processors.text_processor import TextProcessor
        from .deduplication.deduplicator import FundingDeduplicator
        
        # Initialize processors
        self.processors = {
            '.pdf': PDFProcessor(),
            '.csv': CSVProcessor(),
            '.txt': TextProcessor(),
            '.html': TextProcessor(),
            '.json': TextProcessor()
        }
        
        # Initialize deduplicator
        self.deduplicator = FundingDeduplicator()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a file or use default values.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration values
        """
        default_config = {
            'paths': {
                'inbox': './data_ingestion/inbox',
                'processing': './data_ingestion/processing',
                'completed': './data_ingestion/completed',
                'failed': './data_ingestion/failed',
                'logs': './data_ingestion/logs'
            },
            'processing': {
                'batch_size': 10,
                'parallel_workers': 4,
                'timeout_seconds': 300,
                'retry_attempts': 3
            },
            'deduplication': {
                'similarity_threshold': 85,
                'check_window_days': 90
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    for section, values in default_config.items():
                        if section not in config:
                            config[section] = values
                        else:
                            for key, value in values.items():
                                if key not in config[section]:
                                    config[section][key] = value
                    return config
            except Exception as e:
                self.logger.error(f"Error loading config from {config_path}: {e}")
                return default_config
        else:
            return default_config
            
    def _create_directory_structure(self):
        """Create the necessary directory structure for file ingestion."""
        for path_name, path in self.config['paths'].items():
            os.makedirs(path, exist_ok=True)
            
        # Create subdirectories in inbox
        inbox_path = self.config['paths']['inbox']
        for subdir in ['pdfs', 'csvs', 'articles', 'urls']:
            os.makedirs(os.path.join(inbox_path, subdir), exist_ok=True)
            
        self.logger.info("Directory structure created successfully")
        
    def start_watching(self):
        """Start watching the inbox directory for new files."""
        self.logger.info(f"Starting to watch {self.config['paths']['inbox']} for new files")
        
        self.observer = Observer()
        self.observer.schedule(
            self.watcher, 
            self.config['paths']['inbox'], 
            recursive=True
        )
        self.observer.start()
        
        try:
            while True:
                # Process queued files
                if self.watcher.processing_queue:
                    file_path = self.watcher.processing_queue.pop(0)
                    asyncio.run(self.process_file(file_path))
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
        
    async def process_file(self, file_path: str):
        """
        Process a single file based on its type.
        
        Args:
            file_path: Path to the file to process
        """
        file_path = Path(file_path)
        
        # Skip if file doesn't exist (might have been moved)
        if not file_path.exists():
            self.logger.warning(f"File {file_path} no longer exists, skipping")
            return
            
        self.logger.info(f"Processing file: {file_path.name}")
        
        # Move to processing folder
        processing_file = Path(self.config['paths']['processing']) / file_path.name
        shutil.move(str(file_path), str(processing_file))
        
        try:
            # Determine file type and process
            suffix = processing_file.suffix.lower()
            
            if suffix in self.processors:
                extracted_data = await self.processors[suffix].process(processing_file)
            else:
                # Try to process as text
                self.logger.warning(f"Unknown file type: {suffix}, trying text processor")
                extracted_data = await self.processors['.txt'].process(processing_file)
            
            # Add metadata
            for record in extracted_data['records']:
                record['source_file'] = file_path.name
                record['processed_at'] = datetime.now().isoformat()
                record['file_hash'] = self._calculate_file_hash(processing_file)
            
            # Deduplicate
            unique_records, duplicate_records = await self.deduplicator.check_duplicates(
                extracted_data['records']
            )
            
            self.logger.info(f"Extracted {len(extracted_data['records'])} records, "
                            f"{len(unique_records)} unique, {len(duplicate_records)} duplicates")
            
            # Send to database
            if unique_records:
                await self._send_to_database(unique_records)
            
            # Move to completed
            completed_file = Path(self.config['paths']['completed']) / file_path.name
            shutil.move(str(processing_file), str(completed_file))
            
            self.logger.info(f"Completed processing: {file_path.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to process {file_path.name}: {str(e)}")
            
            # Move to failed folder
            failed_file = Path(self.config['paths']['failed']) / file_path.name
            shutil.move(str(processing_file), str(failed_file))
            
            # Log the error
            self._log_error(file_path.name, str(e))
            
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate a hash for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hash string
        """
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def _log_error(self, file_name: str, error_message: str):
        """
        Log an error to the error log file.
        
        Args:
            file_name: Name of the file that caused the error
            error_message: Error message
        """
        log_path = Path(self.config['paths']['logs']) / 'errors.log'
        timestamp = datetime.now().isoformat()
        
        with open(log_path, 'a') as f:
            f.write(f"{timestamp} - {file_name} - {error_message}\n")
            
    async def _send_to_database(self, records: List[Dict[str, Any]]):
        """
        Send records to the database.
        
        Args:
            records: List of records to insert
        """
        from data_processors.db_inserter_enhanced import insert_enhanced_africa_intelligence_feed
        
        try:
            await insert_enhanced_africa_intelligence_feed(records)
            self.logger.info(f"Successfully inserted {len(records)} records into the database")
        except Exception as e:
            self.logger.error(f"Error inserting records into database: {e}")
            
    async def process_urls_file(self, urls_file_path: str):
        """
        Process a file containing URLs.
        
        Args:
            urls_file_path: Path to the file containing URLs
        """
        try:
            with open(urls_file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
            self.logger.info(f"Processing {len(urls)} URLs from {urls_file_path}")
            
            # Process URLs in parallel with rate limiting
            from .processors.url_processor import URLProcessor
            url_processor = URLProcessor()
            
            results = await url_processor.process_batch(urls)
            
            # Deduplicate
            unique_records, duplicate_records = await self.deduplicator.check_duplicates(
                results['records']
            )
            
            # Send to database
            if unique_records:
                await self._send_to_database(unique_records)
                
            self.logger.info(f"Completed processing URLs from {urls_file_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing URLs file {urls_file_path}: {e}")


def main():
    """Main entry point for the file ingestion service."""
    service = FileIngestionService()
    service.start_watching()


if __name__ == "__main__":
    main()