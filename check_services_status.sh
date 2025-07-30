#!/bin/bash

# Check Status of TAIFA-FIALA Services

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

echo "=== TAIFA-FIALA Services Status ==="

# Function to check service status
check_service() {
    local service=$1
    local port=$2
    local endpoint=${3:-""}
    
    echo ""
    info "Checking $service..."
    
    # Check PID file
    pid_file="pids/${service}.pid"
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            success "✓ $service is running (PID: $pid)"
            
            # Check port binding
            if lsof -i :$port -p $pid > /dev/null 2>&1; then
                success "  └─ ✓ Bound to port $port"
                
                # Check HTTP endpoint if provided
                if [ -n "$endpoint" ]; then
                    if curl --silent --fail --max-time 5 "$endpoint" > /dev/null 2>&1; then
                        success "  └─ ✓ HTTP endpoint responding"
                    else
                        warning "  └─ ⚠ HTTP endpoint not responding"
                    fi
                fi
            else
                warning "  └─ ⚠ Not bound to port $port"
            fi
        else
            error "❌ $service PID file exists but process not running"
        fi
    else
        error "❌ $service not running (no PID file)"
        
        # Check if something else is using the port
        port_user=$(lsof -ti :$port 2>/dev/null)
        if [ -n "$port_user" ]; then
            warning "  └─ ⚠ Port $port is in use by PID: $port_user"
        fi
    fi
}

# Check each service
check_service "backend" "8030" "http://localhost:8030/health"
check_service "frontend" "3030" "http://localhost:3030"

# Overall port summary
echo ""
info "Port Summary:"
for port in 8030 3030 8501; do
    port_info=$(lsof -i :$port 2>/dev/null | grep LISTEN | head -1)
    if [ -n "$port_info" ]; then
        success "✓ Port $port: $port_info"
    else
        error "❌ Port $port: Not in use"
    fi
done

# Log file summary
echo ""
info "Recent Log Entries:"
for service in backend frontend; do
    log_file="logs/${service}.log"
    if [ -f "$log_file" ]; then
        echo ""
        info "$service log (last 3 lines):"
        tail -3 "$log_file" | sed 's/^/  /'
    else
        warning "No log file for $service"
    fi
done

echo ""
