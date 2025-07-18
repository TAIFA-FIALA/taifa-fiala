#!/bin/bash

# AI Africa Funding Tracker - Service Management Script
# Updated to align with the new project structure (FastAPI + Streamlit)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

echo -e "${GREEN}=== AI Africa Funding Tracker Service Management ===${NC}"

# Function to check if a service is running
check_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✓ $service_name: RUNNING (PID: $pid)${NC}"
            return 0
        else
            echo -e "${RED}✗ $service_name: NOT RUNNING (stale PID file)${NC}"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo -e "${RED}✗ $service_name: NOT RUNNING${NC}"
        return 1
    fi
}

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}Stopping $service_name...${NC}"
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}Force stopping $service_name...${NC}"
                kill -9 "$pid"
            fi
            rm -f "$pid_file"
            echo -e "${GREEN}✓ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}$service_name was not running${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}$service_name was not running${NC}"
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local command=$2
    local pid_file=$3
    local log_file=$4
    local working_dir=$5
    
    echo -e "${YELLOW}Starting $service_name...${NC}"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$log_file")"
    
    # Change to working directory if specified
    if [ ! -z "$working_dir" ]; then
        cd "$working_dir"
    fi
    
    # Start the service
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    
    # Return to script directory
    cd "$SCRIPT_DIR"
    
    sleep 3
    
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}✓ $service_name started (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}✗ $service_name failed to start${NC}"
        rm -f "$pid_file"
        return 1
    fi
}

# Parse command line arguments
ACTION=${1:-status}

case "$ACTION" in
    "status")
        echo -e "${BLUE}Checking service status...${NC}"
        check_service "Backend (FastAPI)" ".backend.pid"
        check_service "Streamlit Dashboard" ".streamlit.pid"
        ;;
    
    "start")
        echo -e "${BLUE}Starting services...${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "$VENV_PATH" ]; then
            echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
            exit 1
        fi
        
        # Check if required directories exist
        if [ ! -d "backend" ]; then
            echo -e "${RED}Error: Backend directory not found${NC}"
            exit 1
        fi
        
        if [ ! -d "frontend/streamlit_app" ]; then
            echo -e "${RED}Error: Streamlit app directory not found${NC}"
            exit 1
        fi
        
        # Start backend service
        start_service "Backend (FastAPI)" \
            "$VENV_PATH/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" \
            ".backend.pid" \
            "logs/backend.log" \
            "backend"
        
        # Start streamlit service
        start_service "Streamlit Dashboard" \
            "$VENV_PATH/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0" \
            ".streamlit.pid" \
            "logs/streamlit.log" \
            "frontend/streamlit_app"
        ;;
    
    "stop")
        echo -e "${BLUE}Stopping services...${NC}"
        stop_service "Backend (FastAPI)" ".backend.pid"
        stop_service "Streamlit Dashboard" ".streamlit.pid"
        
        # Kill any remaining processes
        pkill -f 'uvicorn.*app.main:app' 2>/dev/null || true
        pkill -f 'streamlit.*app.py' 2>/dev/null || true
        
        # Kill processes on our ports
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
        lsof -ti :8501 | xargs kill -9 2>/dev/null || true
        ;;
    
    "restart")
        echo -e "${BLUE}Restarting services...${NC}"
        
        # Stop services
        stop_service "Backend (FastAPI)" ".backend.pid"
        stop_service "Streamlit Dashboard" ".streamlit.pid"
        
        # Kill any remaining processes
        pkill -f 'uvicorn.*app.main:app' 2>/dev/null || true
        pkill -f 'streamlit.*app.py' 2>/dev/null || true
        
        # Kill processes on our ports
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
        lsof -ti :8501 | xargs kill -9 2>/dev/null || true
        
        sleep 3
        
        # Start services
        echo -e "${BLUE}Starting services...${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "$VENV_PATH" ]; then
            echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
            exit 1
        fi
        
        # Check if required directories exist
        if [ ! -d "backend" ]; then
            echo -e "${RED}Error: Backend directory not found${NC}"
            exit 1
        fi
        
        if [ ! -d "frontend/streamlit_app" ]; then
            echo -e "${RED}Error: Streamlit app directory not found${NC}"
            exit 1
        fi
        
        # Start backend service
        start_service "Backend (FastAPI)" \
            "$VENV_PATH/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" \
            ".backend.pid" \
            "logs/backend.log" \
            "backend"
        
        # Start streamlit service
        start_service "Streamlit Dashboard" \
            "$VENV_PATH/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0" \
            ".streamlit.pid" \
            "logs/streamlit.log" \
            "frontend/streamlit_app"
        ;;
    
    "logs")
        echo -e "${BLUE}Recent logs:${NC}"
        echo -e "${YELLOW}--- Backend (FastAPI) ---${NC}"
        tail -20 logs/backend.log 2>/dev/null || echo "No logs found"
        echo
        echo -e "${YELLOW}--- Streamlit Dashboard ---${NC}"
        tail -20 logs/streamlit.log 2>/dev/null || echo "No logs found"
        ;;
    
    "tail")
        echo -e "${BLUE}Following logs (Ctrl+C to exit)...${NC}"
        tail -f logs/*.log 2>/dev/null || echo "No logs found"
        ;;
    
    "health")
        echo -e "${BLUE}Checking service health...${NC}"
        
        # Check backend health
        if curl -s http://localhost:8000/docs > /dev/null; then
            echo -e "${GREEN}✓ Backend API: HEALTHY (http://localhost:8000)${NC}"
        else
            echo -e "${RED}✗ Backend API: UNHEALTHY${NC}"
        fi
        
        # Check streamlit health
        if curl -s http://localhost:8501 > /dev/null; then
            echo -e "${GREEN}✓ Streamlit Dashboard: HEALTHY (http://localhost:8501)${NC}"
        else
            echo -e "${RED}✗ Streamlit Dashboard: UNHEALTHY${NC}"
        fi
        ;;
    
    *)
        echo -e "${YELLOW}Usage: $0 {status|start|stop|restart|logs|tail|health}${NC}"
        echo
        echo "Commands:"
        echo -e "${BLUE}status${NC}   - Check service status"
        echo -e "${BLUE}start${NC}    - Start all services"
        echo -e "${BLUE}stop${NC}     - Stop all services"
        echo -e "${BLUE}restart${NC}  - Restart all services"
        echo -e "${BLUE}logs${NC}     - Show recent logs"
        echo -e "${BLUE}tail${NC}     - Follow logs in real-time"
        echo -e "${BLUE}health${NC}   - Check service health endpoints"
        echo
        echo "Service URLs:"
        echo -e "${BLUE}Backend API:${NC} http://localhost:8000"
        echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs"
        echo -e "${BLUE}Streamlit:${NC} http://localhost:8501"
        exit 1
        ;;
esac