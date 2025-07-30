#!/bin/bash

# Stop All TAIFA-FIALA Services

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { printf "${BLUE}%s${NC}\n" "$1"; }
success() { printf "${GREEN}%s${NC}\n" "$1"; }
warning() { printf "${YELLOW}%s${NC}\n" "$1"; }

echo "=== Stopping TAIFA-FIALA Services ==="

# Stop services by PID files
for service in backend frontend; do
    pid_file="pids/${service}.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            info "Stopping $service (PID: $pid)..."
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                warning "Force killing $service..."
                kill -9 "$pid"
            fi
            success "$service stopped"
        else
            warning "$service PID file exists but process not running"
        fi
        rm -f "$pid_file"
    else
        info "No PID file for $service"
    fi
done

# Kill any remaining processes on our ports
for port in 8030 3030 8501; do
    pids=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        warning "Killing remaining processes on port $port: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
    fi
done

# Kill any npm/node/uvicorn processes
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "next.*start" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

success "All services stopped"
