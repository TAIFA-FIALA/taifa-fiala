# AI Africa Funding Tracker

A comprehensive platform to track research and implementation funding for artificial intelligence initiatives in Africa, with automated data collection, analysis, and public accessibility.

## Project Overview

This project addresses the lack of centralized tracking for AI funding opportunities across Africa. It automatically monitors multiple sources, classifies opportunities, and provides accessible dashboards for researchers, organizations, and policymakers.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Tailscale connection to mac-mini-local)
- **Caching**: Redis
- **Frontend**: Streamlit (primary) + Next.js (enhanced dashboards)
- **Data Collection**: RSS monitors, web scrapers, webhook integrations
- **Deployment**: Docker containers

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for Next.js dashboard)
- Access to PostgreSQL database at 100.75.201.24

### Quick Start

1. **Clone and setup environment**:
   ```bash
   cd ~/dev/devprojects/ai-africa-funding-tracker
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start development services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the applications**:
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Streamlit App: http://localhost:8501
   - Next.js Dashboard: http://localhost:3000

### Database Setup

The project connects to a PostgreSQL database on mac-mini-local via Tailscale (100.75.201.24). 

Initial database setup:
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Optional: Load sample data
docker-compose exec backend python scripts/load_sample_data.py
```

## Project Structure

```
ai-africa-funding-tracker/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   └── alembic/            # Database migrations
├── frontend/
│   ├── streamlit_app/      # Primary Streamlit interface
│   └── nextjs_dashboard/   # Enhanced Next.js dashboards
├── data_collectors/        # Automated data collection
│   ├── rss_monitors/       # RSS feed monitoring
│   ├── scrapers/           # Web scraping modules
│   └── parsers/            # Data parsing and classification
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── tests/                  # Test suite
```

## Data Sources (Phase 1)

Currently monitoring:
- Llama Impact Accelerator Program
- Milken-Motsepe Innovation Prize
- Grand Challenges Africa (Science for Africa Foundation)
- AI4D Africa (IDRC)
- European Commission AI initiatives

## Development Workflow

1. **Feature development**: Create feature branches from main
2. **Testing**: Run tests locally before pushing
3. **Deployment**: Use `./scripts/deploy_production.sh` for production deployment to mac-mini-local

## Production Deployment

```bash
# Deploy to mac-mini-local via SSH
./scripts/deploy_production.sh
```

## Contributing

This project is currently in private development (Phase 1). Contributors will be welcomed in Phase 2 once core functionality is stable.

## License

MIT License (to be applied when project goes public)

## Contact

For questions about this project, please reach out to the development team.
