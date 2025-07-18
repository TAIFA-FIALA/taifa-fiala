#!/bin/bash

# Quick Development Startup Script
# Simpler version for rapid development

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting AI Africa Funding Tracker Development Environment"
echo "============================================================"

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
lsof -ti :8501 | xargs kill -9 2>/dev/null || true

# Start Backend
echo "🔧 Starting Backend..."
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Frontend
echo "🎨 Starting Frontend..."
cd "$PROJECT_ROOT/frontend/nextjs"
npm install > /dev/null 2>&1
npm run dev &

# Start Streamlit
echo "📊 Starting Streamlit..."
cd "$PROJECT_ROOT/frontend/streamlit_app"
pip3 install -r requirements.txt > /dev/null 2>&1
streamlit run app.py --server.port 8501 &

echo ""
echo "✅ All services starting..."
echo "Frontend:   http://localhost:3000"
echo "Backend:    http://localhost:8000"
echo "Streamlit:  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $(jobs -p); exit 0' INT
wait