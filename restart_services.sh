#!/bin/bash

# AI Africa Funding Tracker - Service Restart Script
# This script restarts all services on the production server

# --- Colors ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Helper Functions ---
info() { printf "${BLUE}%s${NC}\n" "$1"; }
success() { printf "${GREEN}%s${NC}\n" "$1"; }
warning() { printf "${YELLOW}%s${NC}\n" "$1"; }
error() { printf "${RED}%s${NC}\n" "$1"; }

# --- Configuration ---
VENV_PATH="./venv"
DATA_INGESTION_PATH="./data_ingestion"

# Check if Docker is available
if command -v docker >/dev/null 2>&1 && [ -f "docker-compose.watcher.yml" ]; then
    DOCKER_AVAILABLE=true
else
    DOCKER_AVAILABLE=false
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Stop all running services
info "Stopping all running services..."

# Stop traditional services
pkill -f 'uvicorn.*main:app' || echo "No FastAPI process found"
pkill -f 'streamlit run' || echo "No Streamlit process found"
pkill -f 'next.*start' || echo "No Next.js process found"
pkill -f 'file_ingestion_cli watch' || echo "No file watcher process found"

# Stop Docker services if available
if [ "$DOCKER_AVAILABLE" = true ]; then
    info "Stopping Docker containers..."
    docker-compose -f docker-compose.watcher.yml down || echo "No Docker Compose services to stop"
fi

# Wait for processes to stop gracefully
sleep 3

# Ask user which deployment method to use
echo "Choose deployment method:"
echo "1) Traditional deployment (FastAPI, Streamlit, Next.js as separate processes)"
echo "2) Docker-based deployment (includes file watcher service)"
read -p "Enter your choice (1 or 2): " deployment_choice

if [ "$deployment_choice" == "2" ] && [ "$DOCKER_AVAILABLE" = true ]; then
    # Docker-based deployment
    info "Starting services with Docker Compose..."
    docker-compose -f docker-compose.watcher.yml up -d
    
    # Check if services are running
    info "Docker services status:"
    docker-compose -f docker-compose.watcher.yml ps
else
    # Traditional deployment
    info "Starting services traditionally..."
    
    # Activate virtual environment if it exists
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
    else
        warning "Virtual environment not found at $VENV_PATH"
        warning "Using system Python instead"
    fi
    
    # Start FastAPI backend
    info "Starting FastAPI backend..."
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    
    # Start Streamlit dashboard
    info "Starting Streamlit dashboard..."
    nohup python -m streamlit run run_dashboard.py --server.port 8501 --server.address 0.0.0.0 > logs/streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    echo "Streamlit started with PID: $STREAMLIT_PID"
    
    # Start Next.js frontend
    info "Starting Next.js frontend..."
    cd frontend/nextjs
    
    # Check for Node.js and npm availability
    if command -v npm >/dev/null 2>&1; then
        echo "Using system npm"
        nohup npm start -- --port 3020 > ../../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo "Frontend started with PID: $FRONTEND_PID"
    else
        error "Cannot start frontend: npm not found"
        FRONTEND_PID=""
    fi
    
    # Return to project root
    cd ../..
    
    # Start file watcher service
    info "Starting file watcher service..."
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    export DATA_INGESTION_PATH="$DATA_INGESTION_PATH"
    nohup python -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli watch > logs/file_watcher.log 2>&1 &
    WATCHER_PID=$!
    echo "File watcher started with PID: $WATCHER_PID"
fi

# Wait for services to initialize
info "Waiting for services to initialize..."
sleep 10

# Show running processes
info "Current service processes:"
ps aux | grep -E '(uvicorn|streamlit|node.*next|file_ingestion)' | grep -v grep || echo "No matching processes found"

if [ "$DOCKER_AVAILABLE" = true ]; then
    info "Docker containers:"
    docker ps
fi

success "Services restarted successfully!"
info "Check logs in the logs/ directory for any issues."