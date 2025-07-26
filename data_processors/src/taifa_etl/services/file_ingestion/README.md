# AI Africa Funding Tracker - File Ingestion Pipeline

This module implements a file ingestion pipeline for the AI Africa Funding Tracker, allowing for the extraction of funding data from various file types (PDF, CSV, text, HTML) and URLs.

## Overview

The file ingestion pipeline is designed to work in parallel with the existing RSS-based ingestion system. It provides a way to manually ingest funding data from files and URLs, with the following features:

- **File Watching**: Monitors a directory for new files and processes them automatically
- **Multiple File Types**: Supports PDF, CSV, text, HTML, and JSON files
- **URL Processing**: Extracts funding data from URLs
- **Deduplication**: Prevents duplicate entries from being added to the database
- **Database Integration**: Integrates with the existing database
- **Vector Database Integration**: Indexes data in Pinecone for semantic search
- **CLI Interface**: Provides a command-line interface for manual processing

## Directory Structure

```
data_ingestion/
├── inbox/              # Drop files here
│   ├── pdfs/
│   ├── csvs/
│   ├── articles/       # HTML or text files
│   └── urls.txt        # List of URLs to process
├── processing/         # Files being processed
├── completed/          # Processed files (archived)
├── failed/             # Files that failed processing
└── logs/               # Processing logs
```

## Usage

### CLI Interface

The file ingestion pipeline provides a command-line interface for manual processing:

```bash
# Start watching the inbox directory
python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli watch

# Add a file to the inbox
python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli add path/to/file.pdf

# Process a file directly
python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli process path/to/file.pdf

# Show processing status
python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli status

# Show recently processed records
python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli recent --days 7
```

### Watch Folder

The simplest way to use the file ingestion pipeline is to drop files into the watch folder:

1. Start the watcher:
   ```bash
   python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli watch
   ```

2. Drop files into the appropriate subfolder:
   - PDFs: `data_ingestion/inbox/pdfs/`
   - CSVs: `data_ingestion/inbox/csvs/`
   - Text/HTML: `data_ingestion/inbox/articles/`

3. Add URLs to `data_ingestion/inbox/urls.txt` (one per line)

The watcher will automatically process new files and add the extracted data to the database.

## Components

### File Watcher

The file watcher monitors the inbox directory for new files and processes them using the appropriate processor based on the file type.

### File Processors

- **PDF Processor**: Extracts funding data from PDF files using PyPDF2 and a language model
- **CSV Processor**: Extracts funding data from CSV files using pandas with intelligent column detection
- **Text Processor**: Extracts funding data from text and HTML files
- **URL Processor**: Extracts funding data from URLs

### Deduplication

The deduplication system prevents duplicate entries from being added to the database by:

1. Generating a content hash for each record
2. Checking for exact hash matches in the database
3. Using fuzzy matching for records that don't have an exact match

### Database Integration

The database integration system inserts extracted records into the database, handling:

1. Record preparation
2. Field mapping
3. Data validation

### Vector Database Integration

The vector database integration system indexes extracted records in Pinecone for semantic search, enabling:

1. Semantic search of funding data
2. Organization relationship discovery
3. Funding trend analysis

## Configuration

The file ingestion pipeline can be configured by modifying the configuration in `watcher.py`:

```python
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
```

## Requirements

- Python 3.8+
- PyPDF2
- pandas
- BeautifulSoup4
- aiohttp
- watchdog
- fuzzywuzzy
- chardet
- anthropic (optional, for enhanced extraction)

## Integration with Existing System

The file ingestion pipeline is designed to work in parallel with the existing RSS-based ingestion system. It uses the same database schema and deduplication logic, ensuring that data from both sources is consistent and deduplicated.

## Logging

The file ingestion pipeline logs all activity to the following files:

- `data_ingestion/logs/errors.log`: Errors encountered during processing
- `data_ingestion/logs/duplicates.log`: Duplicate records detected during processing

## Future Improvements

- Add support for more file types (e.g., Excel, Word)
- Improve extraction accuracy with better language models
- Add a web interface for manual processing
- Implement batch processing for large files
- Add support for more languages