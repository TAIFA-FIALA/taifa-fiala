#!/bin/bash

# Backend Log Monitor for Production Server
# Usage: ./monitor_backend_logs.sh [command]
# Commands: tail, errors, access, health, full, clear

set -e

PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"
BACKEND_LOG="$PROD_DIR/logs/backend.log"
ACCESS_LOG="$PROD_DIR/logs/backend_access.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { printf "${BLUE}%s${NC}\n" "$1"; }
success() { printf "${GREEN}%s${NC}\n" "$1"; }
warning() { printf "${YELLOW}%s${NC}\n" "$1"; }
error() { printf "${RED}%s${NC}\n" "$1"; }

show_usage() {
    echo "Backend Log Monitor - Production Diagnostics"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  tail     - Follow backend logs in real-time (default)"
    echo "  errors   - Show only error messages from logs"
    echo "  access   - Show HTTP access logs"
    echo "  health   - Show health check related logs"
    echo "  startup  - Show startup and initialization logs"
    echo "  full     - Show complete backend log"
    echo "  clear    - Clear all backend logs"
    echo "  status   - Show backend process status and port info"
    echo ""
    echo "Examples:"
    echo "  $0 tail     # Follow logs in real-time"
    echo "  $0 errors   # Show only errors"
    echo "  $0 health   # Show health endpoint activity"
}

check_logs_exist() {
    if [ ! -f "$BACKEND_LOG" ]; then
        warning "⚠ Backend log not found at: $BACKEND_LOG"
        return 1
    fi
    return 0
}

show_backend_status() {
    info "=== Backend Process Status ==="
    
    # Check if backend process is running
    if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
        success "✅ Backend process is running"
        ps aux | grep "uvicorn.*app.main:app" | grep -v grep
    else
        error "❌ Backend process is not running"
    fi
    
    echo ""
    info "=== Port 8030 Status ==="
    if lsof -i :8030 > /dev/null 2>&1; then
        lsof -i :8030
    else
        warning "⚠ No process listening on port 8030"
    fi
    
    echo ""
    info "=== Recent Backend Log (last 10 lines) ==="
    if [ -f "$BACKEND_LOG" ]; then
        tail -10 "$BACKEND_LOG"
    else
        warning "⚠ Backend log file not found"
    fi
}

# Main command handling
case "${1:-tail}" in
    "tail"|"follow")
        info "📋 Following backend logs in real-time (Ctrl+C to stop)..."
        if check_logs_exist; then
            tail -f "$BACKEND_LOG"
        fi
        ;;
        
    "errors"|"error")
        info "🚨 Showing error messages from backend logs..."
        if check_logs_exist; then
            grep -i "error\|exception\|traceback\|failed\|❌" "$BACKEND_LOG" | tail -20
        fi
        ;;
        
    "access")
        info "🌐 Showing HTTP access logs..."
        if [ -f "$ACCESS_LOG" ]; then
            tail -20 "$ACCESS_LOG"
        else
            warning "⚠ Access log not found at: $ACCESS_LOG"
            info "Showing access-related entries from main log..."
            grep -i "GET\|POST\|PUT\|DELETE\|http" "$BACKEND_LOG" | tail -20
        fi
        ;;
        
    "health")
        info "❤️ Showing health check related logs..."
        if check_logs_exist; then
            grep -i "health\|/health\|startup\|ready" "$BACKEND_LOG" | tail -20
        fi
        ;;
        
    "startup")
        info "🚀 Showing startup and initialization logs..."
        if check_logs_exist; then
            grep -i "started\|startup\|uvicorn\|application\|database\|pinecone\|supabase" "$BACKEND_LOG" | tail -30
        fi
        ;;
        
    "full")
        info "📄 Showing complete backend log..."
        if check_logs_exist; then
            cat "$BACKEND_LOG"
        fi
        ;;
        
    "clear")
        warning "🗑️ Clearing all backend logs..."
        read -p "Are you sure you want to clear all backend logs? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            > "$BACKEND_LOG"
            [ -f "$ACCESS_LOG" ] && > "$ACCESS_LOG"
            success "✅ Backend logs cleared"
        else
            info "Operation cancelled"
        fi
        ;;
        
    "status")
        show_backend_status
        ;;
        
    "help"|"-h"|"--help")
        show_usage
        ;;
        
    *)
        error "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
