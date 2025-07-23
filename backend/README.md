# TAIFA-FIALA Backend

AI Africa Funding Tracker - Comprehensive platform to track AI intelligence feed in Africa.

## Features

- **ETL Pipeline**: Intelligent data ingestion with rate limiting and caching
- **Balance Monitoring**: Real-time monitoring of LLM provider account balances
- **Notification System**: Multi-channel alerting for system events and low balances
- **Smart LLM Routing**: Cost-optimized routing between DeepSeek and OpenAI
- **Vector Search**: Semantic search capabilities with Pinecone integration
- **Admin Dashboard**: Comprehensive monitoring and management interface

## Quick Start

### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Start the server
poetry run start-server

# Run tests
poetry run test-systems
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_service_role_key
SUPABASE_PUBLISHABLE_KEY=your_anon_key

# LLM Providers
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
GEMINI_API_KEY=your_gemini_key

# External APIs
SERPER_API_KEY=your_serper_key

# Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_app_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/taifa-alerts

# Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env

# SMTP Server
SMTP_SERVER=your_smtp_server
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
```

## Architecture

- **FastAPI**: Modern, fast web framework
- **Supabase**: PostgreSQL database with real-time capabilities
- **Pinecone**: Vector database for semantic search
- **Celery**: Asynchronous task processing
- **Redis**: Caching and session storage
- **LiteLLM**: Unified LLM provider interface

## Development

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy .

# Run tests
poetry run pytest
```
