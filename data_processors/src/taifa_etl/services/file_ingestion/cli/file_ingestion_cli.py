"""
CLI Interface for AI Africa Funding Tracker File Ingestion
========================================================

This module provides a command-line interface for the file ingestion pipeline,
allowing users to manually process files and monitor the ingestion process.
"""

import os
import sys
import argparse
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
sys.path.append(parent_dir)

from data_processors.src.taifa_etl.services.file_ingestion.watcher import FileIngestionService


class FileIngestionCLI:
    """
    Command-line interface for the file ingestion pipeline.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.service = FileIngestionService()
        self.logger = logging.getLogger(__name__)
        
    def run(self):
        """Run the CLI."""
        parser = argparse.ArgumentParser(
            description='AI Africa Funding Tracker File Ingestion CLI',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python file_ingestion_cli.py watch                   # Start watching the inbox directory
  python file_ingestion_cli.py add path/to/file.pdf    # Add a file to the inbox
  python file_ingestion_cli.py process path/to/file.pdf # Process a file directly
  python file_ingestion_cli.py status                  # Show processing status
  python file_ingestion_cli.py recent --days 7         # Show recently processed records
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to run')
        
        # Watch command
        watch_parser = subparsers.add_parser('watch', help='Start watching the inbox directory')
        
        # Add command
        add_parser = subparsers.add_parser('add', help='Add a file to the inbox')
        add_parser.add_argument('file_path', help='Path to the file to add')
        
        # Process command
        process_parser = subparsers.add_parser('process', help='Process a file directly')
        process_parser.add_argument('file_path', help='Path to the file to process')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show processing status')
        
        # Recent command
        recent_parser = subparsers.add_parser('recent', help='Show recently processed records')
        recent_parser.add_argument('--days', type=int, default=7, help='Number of days to look back')
        
        # Parse arguments
        args = parser.parse_args()
        
        # Execute command
        if args.command == 'watch':
            self.watch()
        elif args.command == 'add':
            self.add(args.file_path)
        elif args.command == 'process':
            asyncio.run(self.process(args.file_path))
        elif args.command == 'status':
            self.status()
        elif args.command == 'recent':
            asyncio.run(self.recent(args.days))
        else:
            parser.print_help()
    
    def watch(self):
        """Start watching the inbox directory."""
        print("🔍 Starting file watcher...")
        self.service.start_watching()
    
    def add(self, file_path: str):
        """
        Add a file to the inbox.
        
        Args:
            file_path: Path to the file to add
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        # Determine subfolder based on file type
        inbox_path = Path(self.service.config['paths']['inbox'])
        
        if file_path.suffix.lower() == '.csv':
            dest_folder = inbox_path / 'csvs'
        elif file_path.suffix.lower() == '.pdf':
            dest_folder = inbox_path / 'pdfs'
        elif file_path.suffix.lower() in ('.txt', '.html', '.json'):
            dest_folder = inbox_path / 'articles'
        else:
            dest_folder = inbox_path
        
        dest_folder.mkdir(exist_ok=True)
        dest_path = dest_folder / file_path.name
        
        try:
            shutil.copy(file_path, dest_path)
            print(f"✅ Added {file_path.name} to processing queue at {dest_path}")
        except Exception as e:
            print(f"❌ Error adding file: {e}")
    
    async def process(self, file_path: str):
        """
        Process a file directly.
        
        Args:
            file_path: Path to the file to process
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"🔍 Processing file: {file_path}")
        
        try:
            await self.service.process_file(file_path)
            print(f"✅ Successfully processed {file_path}")
        except Exception as e:
            print(f"❌ Error processing file: {e}")
    
    def status(self):
        """Show processing status."""
        folders = {
            'Inbox': Path(self.service.config['paths']['inbox']),
            'Processing': Path(self.service.config['paths']['processing']),
            'Completed': Path(self.service.config['paths']['completed']),
            'Failed': Path(self.service.config['paths']['failed'])
        }
        
        print("\n📊 Processing Status:")
        
        for name, folder in folders.items():
            if folder.exists():
                count = len(list(folder.glob('**/*.*')))
                print(f"  {name}: {count} files")
        
        # Show error log summary if available
        log_path = Path(self.service.config['paths']['logs']) / 'errors.log'
        if log_path.exists():
            with open(log_path, 'r') as f:
                error_count = len(f.readlines())
                print(f"  Errors: {error_count} logged errors")
        
        # Show duplicate log summary if available
        dup_log_path = Path(self.service.config['paths']['logs']) / 'duplicates.log'
        if dup_log_path.exists():
            with open(dup_log_path, 'r') as f:
                dup_count = len(f.readlines())
                print(f"  Duplicates: {dup_count} detected duplicates")
    
    async def recent(self, days: int):
        """
        Show recently processed records.
        
        Args:
            days: Number of days to look back
        """
        try:
            # Import database client
            from data_processors.db_inserter_enhanced import get_recent_transactions
            
            # Get records from the last N days
            records = await get_recent_transactions(days=days)
            
            print(f"\n📋 Recent funding records (last {days} days):")
            
            if not records:
                print("  No records found")
                return
            
            print(f"  Found {len(records)} records")
            
            # Group by source type
            source_types = {}
            for record in records:
                source_type = record.get('source_type', 'unknown')
                if source_type not in source_types:
                    source_types[source_type] = 0
                source_types[source_type] += 1
            
            print("\n  Records by source type:")
            for source_type, count in source_types.items():
                print(f"    {source_type}: {count} records")
            
            # Show most recent records
            print("\n  Most recent records:")
            for record in sorted(records, key=lambda r: r.get('created_at', ''), reverse=True)[:5]:
                print(f"    • {record.get('title', 'Untitled')} - {record.get('organization_name', 'Unknown')}")
                print(f"      Amount: {record.get('funding_amount', 'Unknown')}")
                print(f"      Date: {record.get('created_at', 'Unknown')}")
                print()
            
        except Exception as e:
            print(f"❌ Error retrieving recent records: {e}")


def main():
    """Main entry point for the CLI."""
    cli = FileIngestionCLI()
    cli.run()


if __name__ == "__main__":
    main()