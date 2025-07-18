#!/bin/bash

# TAIFA-FIALA Service Management Script
# This script manages the TAIFA-FIALA services on the Mac-mini

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

echo -e "${GREEN}=== TAIFA-FIALA Service Management ===${NC}"

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
    
    echo -e "${YELLOW}Starting $service_name...${NC}"
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$log_file")"
    
    # Start the service
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "$pid_file"
    
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
        check_service "Data Ingestion" ".data_ingestion.pid"
        check_service "Dashboard" ".dashboard.pid"
        ;;
    
    "start")
        echo -e "${BLUE}Starting services...${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "$VENV_PATH" ]; then
            echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
            exit 1
        fi
        
        # Start data ingestion service
        start_service "Data Ingestion" \
            "$VENV_PATH/bin/python tools/ingestion/start_data_ingestion.py" \
            ".data_ingestion.pid" \
            "logs/data_ingestion.log"
        
        # Start dashboard service
        start_service "Dashboard" \
            "$VENV_PATH/bin/streamlit run tools/dashboard/system_dashboard.py --server.port 8501 --server.address 0.0.0.0" \
            ".dashboard.pid" \
            "logs/dashboard.log"
        ;;
    
    "stop")
        echo -e "${BLUE}Stopping services...${NC}"
        stop_service "Data Ingestion" ".data_ingestion.pid"
        stop_service "Dashboard" ".dashboard.pid"
        
        # Kill any remaining processes
        pkill -f 'streamlit.*system_dashboard' 2>/dev/null || true
        pkill -f 'python.*start_data_ingestion' 2>/dev/null || true
        ;;
    
    "restart")
        echo -e "${BLUE}Restarting services...${NC}"
        
        # Stop services
        stop_service "Data Ingestion" ".data_ingestion.pid"
        stop_service "Dashboard" ".dashboard.pid"
        
        # Kill any remaining processes
        pkill -f 'streamlit.*system_dashboard' 2>/dev/null || true
        pkill -f 'python.*start_data_ingestion' 2>/dev/null || true
        
        sleep 3
        
        # Start services
        echo -e "${BLUE}Starting services...${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "$VENV_PATH" ]; then
            echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
            exit 1
        fi
        
        # Start data ingestion service
        start_service "Data Ingestion" \
            "$VENV_PATH/bin/python tools/ingestion/start_data_ingestion.py" \
            ".data_ingestion.pid" \
            "logs/data_ingestion.log"
        
        # Start dashboard service
        start_service "Dashboard" \
            "$VENV_PATH/bin/streamlit run tools/dashboard/system_dashboard.py --server.port 8501 --server.address 0.0.0.0" \
            ".dashboard.pid" \
            "logs/dashboard.log"
        ;;
    
    "logs")
        echo -e "${BLUE}Recent logs:${NC}"
        echo -e "${YELLOW}--- Data Ingestion ---${NC}"
        tail -20 logs/data_ingestion.log 2>/dev/null || echo "No logs found"
        echo
        echo -e "${YELLOW}--- Dashboard ---${NC}"
        tail -20 logs/dashboard.log 2>/dev/null || echo "No logs found"
        ;;
    
    "tail")
        echo -e "${BLUE}Following logs (Ctrl+C to exit)...${NC}"
        tail -f logs/*.log 2>/dev/null || echo "No logs found"
        ;;
    
    *)
        echo -e "${YELLOW}Usage: $0 {status|start|stop|restart|logs|tail}${NC}"
        echo
        echo "Commands:"
        echo -e "${BLUE}status${NC}   - Check service status"
        echo -e "${BLUE}start${NC}    - Start all services"
        echo -e "${BLUE}stop${NC}     - Stop all services"
        echo -e "${BLUE}restart${NC}  - Restart all services"
        echo -e "${BLUE}logs${NC}     - Show recent logs"
        echo -e "${BLUE}tail${NC}     - Follow logs in real-time"
        exit 1
        ;;
esac