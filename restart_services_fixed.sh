#!/bin/bash

# Restart Services with Fixed Port Configuration
# This script ensures both backend and frontend start with correct ports

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { printf "${BLUE}%s${NC}\n" "$1"; }
success() { printf "${GREEN}%s${NC}\n" "$1"; }
warning() { printf "${YELLOW}%s${NC}\n" "$1"; }
error() { printf "${RED}%s${NC}\n" "$1"; }

echo "=== TAIFA-FIALA Service Restart with Fixed Ports ==="

# Function to kill processes on a port
kill_port() {
    local port=$1
    local service_name=$2
    
    info "Checking port $port for $service_name..."
    local pids=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        warning "Killing existing processes on port $port: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Verify port is free
    local remaining=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$remaining" ]; then
        error "Failed to free port $port"
        return 1
    else
        success "Port $port is now free"
    fi
}

# Function to test endpoint
test_endpoint() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    info "Testing $service_name at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl --silent --fail --max-time 5 "$url" > /dev/null 2>&1; then
            success "✅ $service_name is responding"
            return 0
        fi
        
        if [ $attempt -eq 1 ]; then
            info "Waiting for $service_name to start..."
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "❌ $service_name failed to respond after $max_attempts attempts"
    return 1
}

# Step 1: Stop existing services
info "Step 1: Stopping existing services..."

# Kill processes on our target ports
kill_port 8030 "Backend"
kill_port 3030 "Frontend"
kill_port 8501 "Streamlit"

# Also kill any npm/node processes that might be running
info "Stopping any existing npm/node processes..."
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "next.*start" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 3

# Step 2: Ensure directories exist
info "Step 2: Ensuring directories exist..."
mkdir -p logs
mkdir -p pids

# Step 3: Start Backend (FastAPI on port 8030)
info "Step 3: Starting Backend on port 8030..."

cd backend
if [ ! -d "venv" ]; then
    info "Creating backend virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start backend with correct port
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../pids/backend.pid
cd ..

success "Backend started with PID $BACKEND_PID"

# Step 4: Start Frontend (Next.js on port 3030)
info "Step 4: Starting Frontend on port 3030..."

cd frontend/nextjs

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
    info "Installing frontend dependencies..."
    npm install
fi

# Build if needed
if [ ! -d ".next" ]; then
    info "Building frontend..."
    npm run build
fi

# Start frontend with correct port
PORT=3030 nohup npm start > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../pids/frontend.pid
cd ../..

success "Frontend started with PID $FRONTEND_PID"

# Step 5: Wait and test services
info "Step 5: Testing service health..."

# Test backend health
test_endpoint "http://localhost:8030/health" "Backend API"

# Test frontend
test_endpoint "http://localhost:3030" "Frontend"

# Step 6: Display status
echo ""
success "=== All Services Started Successfully ==="
info "Backend API: http://localhost:8030"
info "Frontend: http://localhost:3030"
info "API Docs: http://localhost:8030/docs"
echo ""
info "Log files:"
info "  Backend: logs/backend.log"
info "  Frontend: logs/frontend.log"
echo ""
info "PID files:"
info "  Backend: pids/backend.pid"
info "  Frontend: pids/frontend.pid"
echo ""
info "To stop services: ./stop_services.sh"
info "To check status: ./check_services_status.sh"
