# TAIFA-FIALA Tools Directory

This directory contains organized tools and scripts for the TAIFA-FIALA AI Africa Funding Intelligence System.

## Directory Structure

### 📊 `dashboard/`
- `system_dashboard.py` - Comprehensive Streamlit dashboard for monitoring system status, data collection metrics, and search capabilities

### 🔄 `ingestion/`
- `start_data_ingestion.py` - Basic data ingestion pipeline starter
- `enhanced_data_ingestion.py` - Advanced data ingestion with RSS feeds and queue integration
- `intelligent_serper_system.py` - Smart search system for targeted data collection
- `scraping_queue_processor.py` - Queue-based web scraping system

### 🧪 `demo/`
- `pinecone_search_demo.py` - Demonstration of Pinecone vector search capabilities

### 🔧 `migration/`
- `update_code_references.py` - Migration script for updating code references across the codebase

## Quick Start

### Launch the System Dashboard
```bash
python run_dashboard.py
```

### Start Data Ingestion
```bash
python run_ingestion.py
```

### Run Individual Tools
```bash
# Dashboard
python tools/dashboard/system_dashboard.py

# Data Ingestion
python tools/ingestion/start_data_ingestion.py

# Enhanced Ingestion (with queue system)
python tools/ingestion/enhanced_data_ingestion.py

# Pinecone Search Demo
python tools/demo/pinecone_search_demo.py
```

## Integration Notes

All tools are designed to work together as part of the TAIFA-FIALA system:

1. **Dashboard** provides real-time monitoring and visualization
2. **Ingestion tools** collect and process data from various sources
3. **Demo tools** showcase system capabilities
4. **Migration tools** help maintain and update the system

The tools maintain their original functionality while being better organized for maintainability and scalability.