#!/bin/bash

# AI Africa Funding Tracker - Development Environment Startup Script
# This script starts all three services: Backend (FastAPI), Frontend (Next.js), and Streamlit

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend/nextjs"
STREAMLIT_DIR="$PROJECT_ROOT/frontend/streamlit_app"

echo -e "${BLUE}🚀 Starting AI Africa Funding Tracker Development Environment${NC}"
echo -e "${BLUE}=======================================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if port_in_use $1; then
        echo -e "${YELLOW}⚠️  Port $1 is in use. Killing existing process...${NC}"
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to start backend
start_backend() {
    echo -e "${GREEN}🔧 Starting Backend (FastAPI)...${NC}"
    
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # UV handles environment management automatically
    echo -e "${YELLOW}📦 UV will handle environment management...${NC}"
    
    # Install dependencies with UV
    echo -e "${YELLOW}📦 Installing Python dependencies with UV...${NC}"
    uv pip install -r requirements.txt
    
    # Kill any existing process on port 8000
    kill_port 8000
    
    # Start FastAPI with uvicorn using UV
    echo -e "${GREEN}🚀 Starting FastAPI server on http://localhost:8000${NC}"
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
}

# Function to start frontend
start_frontend() {
    echo -e "${GREEN}🔧 Starting Frontend (Next.js)...${NC}"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if Node.js is installed
    if ! command_exists node; then
        echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
        exit 1
    fi
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
    
    # Kill any existing process on port 3000
    kill_port 3000
    
    # Start Next.js development server
    echo -e "${GREEN}🚀 Starting Next.js server on http://localhost:3000${NC}"
    npm run dev &
    FRONTEND_PID=$!
    
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
}

# Function to start streamlit
start_streamlit() {
    echo -e "${GREEN}🔧 Starting Streamlit App...${NC}"
    
    if [ ! -d "$STREAMLIT_DIR" ]; then
        echo -e "${RED}❌ Streamlit directory not found: $STREAMLIT_DIR${NC}"
        exit 1
    fi
    
    cd "$STREAMLIT_DIR"
    
    # Check if Python is installed
    if ! command_exists python3; then
        echo -e "${RED}❌ Python3 is not installed. Please install Python3 first.${NC}"
        exit 1
    fi
    
    # Install streamlit dependencies with UV
    echo -e "${YELLOW}📦 Installing Streamlit dependencies with UV...${NC}"
    uv pip install -r requirements.txt
    
    # Kill any existing process on port 8501
    kill_port 8501
    
    # Start Streamlit with UV
    echo -e "${GREEN}🚀 Starting Streamlit server on http://localhost:8501${NC}"
    uv run streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
    STREAMLIT_PID=$!
    
    echo -e "${GREEN}✅ Streamlit started (PID: $STREAMLIT_PID)${NC}"
}

# Function to wait for services to be ready
wait_for_services() {
    local services_to_check="$1"
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    
    # Wait for backend
    if [[ "$services_to_check" == *"backend"* ]]; then
        echo -e "${YELLOW}  Checking backend...${NC}"
        timeout=30
        while ! curl -s --max-time 5 http://localhost:8000/docs > /dev/null 2>&1; do
            sleep 2
            timeout=$((timeout - 2))
            if [ $timeout -le 0 ]; then
                echo -e "${RED}❌ Backend failed to start within 30 seconds${NC}"
                break
            fi
        done
        if [ $timeout -gt 0 ]; then
            echo -e "${GREEN}✅ Backend is ready${NC}"
        fi
    fi
    
    # Wait for frontend
    if [[ "$services_to_check" == *"frontend"* ]]; then
        echo -e "${YELLOW}  Checking frontend...${NC}"
        timeout=30
        while ! curl -s --max-time 5 http://localhost:3000 > /dev/null 2>&1; do
            sleep 2
            timeout=$((timeout - 2))
            if [ $timeout -le 0 ]; then
                echo -e "${RED}❌ Frontend failed to start within 30 seconds${NC}"
                break
            fi
        done
        if [ $timeout -gt 0 ]; then
            echo -e "${GREEN}✅ Frontend is ready${NC}"
        fi
    fi
    
    # Wait for streamlit
    if [[ "$services_to_check" == *"streamlit"* ]]; then
        echo -e "${YELLOW}  Checking streamlit...${NC}"
        timeout=30
        while ! curl -s --max-time 5 http://localhost:8501 > /dev/null 2>&1; do
            sleep 2
            timeout=$((timeout - 2))
            if [ $timeout -le 0 ]; then
                echo -e "${RED}❌ Streamlit failed to start within 30 seconds${NC}"
                break
            fi
        done
        if [ $timeout -gt 0 ]; then
            echo -e "${GREEN}✅ Streamlit is ready${NC}"
        fi
    fi
}

# Function to display service URLs
display_urls() {
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}🎉 All services are running!${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}📱 Frontend (Next.js):     ${YELLOW}http://localhost:3000${NC}"
    echo -e "${GREEN}🔧 Backend (FastAPI):      ${YELLOW}http://localhost:8000${NC}"
    echo -e "${GREEN}📊 API Documentation:      ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "${GREEN}📊 Streamlit Dashboard:    ${YELLOW}http://localhost:8501${NC}"
    echo -e "${BLUE}=======================================================${NC}"
}

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    # Kill all background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Streamlit stopped${NC}"
    fi
    
    # Kill any remaining processes on our ports
    kill_port 8000
    kill_port 3000
    kill_port 8501
    
    echo -e "${GREEN}🏁 All services stopped successfully${NC}"
}

# Set up trap to handle Ctrl+C
trap cleanup EXIT INT TERM

# Check if specific service is requested
case "${1:-all}" in
    "backend")
        start_backend
        wait_for_services "backend"
        display_urls
        ;;
    "frontend")
        start_frontend
        wait_for_services "frontend"
        display_urls
        ;;
    "streamlit")
        start_streamlit
        wait_for_services "streamlit"
        display_urls
        ;;
    "all"|"")
        # Start all services
        start_backend
        sleep 5  # Give backend time to start
        start_frontend
        sleep 5  # Give frontend time to start
        start_streamlit
        
        # Wait for all services to be ready
        wait_for_services "backend frontend streamlit"
        
        # Display URLs
        display_urls
        ;;
    *)
        echo -e "${RED}❌ Invalid option. Use: all, backend, frontend, or streamlit${NC}"
        exit 1
        ;;
esac

# Keep the script running
echo -e "${YELLOW}💡 Press Ctrl+C to stop all services${NC}"
wait