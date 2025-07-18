# Development Environment Setup

This guide helps you quickly start all three services for the AI Africa Funding Tracker project.

## Services Overview

- **Backend (FastAPI)**: Runs on `http://localhost:8000`
- **Frontend (Next.js)**: Runs on `http://localhost:3000`
- **Streamlit Dashboard**: Runs on `http://localhost:8501`

## Quick Start

### Option 1: Full Development Script (Recommended)

```bash
# Start all services
./start-dev.sh

# Start specific service only
./start-dev.sh backend
./start-dev.sh frontend
./start-dev.sh streamlit
```

### Option 2: Quick Start Script

```bash
# Start all services with minimal output
./dev-quick-start.sh
```

## Manual Setup

### Backend (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Next.js)

```bash
cd frontend/nextjs
npm install
npm run dev
```

### Streamlit Dashboard

```bash
cd frontend/streamlit_app
pip3 install -r requirements.txt
streamlit run app.py --server.port 8501
```

## Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**

## Environment Variables

Make sure you have the following environment files:

- `backend/.env` - Backend configuration
- `frontend/nextjs/.env.local` - Frontend configuration (if needed)

## Stopping Services

Press `Ctrl+C` in the terminal where the script is running to stop all services.

## Troubleshooting

### Port Already in Use

If you get port errors, the scripts will automatically kill existing processes on ports 3000, 8000, and 8501.

### Python Virtual Environment Issues

If you have issues with Python dependencies, try:

```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node.js Module Issues

If you have issues with Node.js modules, try:

```bash
cd frontend/nextjs
rm -rf node_modules package-lock.json
npm install
```

## Development URLs

Once all services are running:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)

## Production Deployment

### Updated Production Scripts

The production deployment has been updated to align with the new project structure:

- **`deploy_production_aligned.sh`** - Updated deployment script for FastAPI + Streamlit
- **`restart_services_aligned.sh`** - Updated service management script

### Production Deployment Process

```bash
# Deploy to production (Mac-mini)
./deploy_production_aligned.sh

# Manage services on production
./restart_services_aligned.sh status
./restart_services_aligned.sh restart
./restart_services_aligned.sh logs
./restart_services_aligned.sh health
```

### Architecture Alignment

**Development vs Production:**
- **Development**: All services run locally (ports 3000, 8000, 8501)
- **Production**: Backend + Streamlit on Mac-mini, Next.js on Vercel

**Service Structure:**
- **Backend (FastAPI)**: `backend/app/main.py` → Port 8000
- **Frontend (Next.js)**: `frontend/nextjs/` → Port 3000 (dev) / Vercel (prod)
- **Streamlit Dashboard**: `frontend/streamlit_app/app.py` → Port 8501

## Next Steps

1. Check that all services are running by visiting the URLs above
2. Review the API documentation at `/docs`
3. Test the frontend functionality
4. Use the Streamlit dashboard for data visualization
5. For production deployment, use the aligned scripts mentioned above