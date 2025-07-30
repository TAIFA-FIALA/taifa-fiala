#!/bin/bash

# Combined Service Monitor for Production Server
# Usage: ./monitor_services.sh [service] [command]
# Services: backend, watcher, all
# Commands: tail, errors, status, clear

set -e

PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"

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
    echo "Combined Service Monitor - Production Diagnostics"
    echo "Usage: $0 [service] [command]"
    echo ""
    echo "Services:"
    echo "  backend   - Monitor backend/uvicorn logs"
    echo "  watcher   - Monitor file watcher logs"
    echo "  all       - Monitor all services (default)"
    echo ""
    echo "Commands:"
    echo "  tail      - Follow logs in real-time (default)"
    echo "  errors    - Show only error messages"
    echo "  status    - Show service status and health"
    echo "  clear     - Clear service logs"
    echo ""
    echo "Examples:"
    echo "  $0                    # Show status of all services"
    echo "  $0 all tail          # Follow all service logs"
    echo "  $0 backend errors    # Show backend errors only"
    echo "  $0 watcher status    # Show file watcher status"
}

show_all_status() {
    info "=== AI Africa Funding Tracker - Service Status ==="
    echo ""
    
    # Backend Status
    info "🔧 Backend Service (Port 8030)"
    if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
        success "  ✅ Running"
        # Test health endpoint
        if curl -s --max-time 5 http://localhost:8030/health > /dev/null 2>&1; then
            success "  ✅ Health check: OK"
        else
            warning "  ⚠ Health check: Failed"
        fi
    else
        error "  ❌ Not running"
    fi
    
    # Streamlit Status
    info "📊 Streamlit Dashboard (Port 8501)"
    if pgrep -f "streamlit.*run" > /dev/null; then
        success "  ✅ Running"
    else
        error "  ❌ Not running"
    fi
    
    # Frontend Status
    info "🌐 Frontend Service (Port 3030)"
    if lsof -i :3030 > /dev/null 2>&1; then
        success "  ✅ Running"
    else
        error "  ❌ Not running"
    fi
    
    # File Watcher Status
    info "👁 File Watcher Service"
    if pgrep -f "watcher.py" > /dev/null; then
        success "  ✅ Running"
    else
        error "  ❌ Not running"
    fi
    
    # Directory Status
    echo ""
    info "📁 Data Ingestion Directories"
    DATA_INGESTION_PATH="$PROD_DIR/data_ingestion"
    if [ -d "$DATA_INGESTION_PATH" ]; then
        for dir in inbox processed failed; do
            full_path="$DATA_INGESTION_PATH/$dir"
            if [ -d "$full_path" ]; then
                file_count=$(find "$full_path" -type f 2>/dev/null | wc -l)
                success "  📁 $dir: $file_count files"
            else
                warning "  ⚠ $dir: missing"
            fi
        done
    else
        error "  ❌ Data ingestion directory not found"
    fi
    
    # Recent log activity
    echo ""
    info "📋 Recent Log Activity (last 5 minutes)"
    
    # Backend logs
    if [ -f "$PROD_DIR/logs/backend.log" ]; then
        recent_backend=$(find "$PROD_DIR/logs/backend.log" -mmin -5 2>/dev/null)
        if [ -n "$recent_backend" ]; then
            success "  📝 Backend: Active"
        else
            warning "  📝 Backend: No recent activity"
        fi
    fi
    
    # File watcher logs
    if [ -f "$PROD_DIR/logs/file_watcher.log" ]; then
        recent_watcher=$(find "$PROD_DIR/logs/file_watcher.log" -mmin -5 2>/dev/null)
        if [ -n "$recent_watcher" ]; then
            success "  📝 File Watcher: Active"
        else
            warning "  📝 File Watcher: No recent activity"
        fi
    fi
}

tail_all_logs() {
    info "📋 Following all service logs in real-time (Ctrl+C to stop)..."
    echo "Backend logs will be prefixed with [BACKEND]"
    echo "File Watcher logs will be prefixed with [WATCHER]"
    echo ""
    
    # Use multitail if available, otherwise fall back to tail
    if command -v multitail > /dev/null 2>&1; then
        multitail -l "tail -f $PROD_DIR/logs/backend.log" -l "tail -f $PROD_DIR/logs/file_watcher.log"
    else
        # Fallback: tail both files with prefixes
        (tail -f "$PROD_DIR/logs/backend.log" 2>/dev/null | sed 's/^/[BACKEND] /' &
         tail -f "$PROD_DIR/logs/file_watcher.log" 2>/dev/null | sed 's/^/[WATCHER] /' &
         wait)
    fi
}

show_all_errors() {
    info "🚨 Showing errors from all services..."
    echo ""
    
    info "Backend Errors:"
    if [ -f "$PROD_DIR/logs/backend.log" ]; then
        grep -i "error\|exception\|traceback\|failed\|❌" "$PROD_DIR/logs/backend.log" | tail -10 | sed 's/^/  /'
    else
        warning "  No backend log found"
    fi
    
    echo ""
    info "File Watcher Errors:"
    if [ -f "$PROD_DIR/logs/file_watcher.log" ]; then
        grep -i "error\|exception\|traceback\|failed\|❌" "$PROD_DIR/logs/file_watcher.log" | tail -10 | sed 's/^/  /'
    else
        warning "  No file watcher log found"
    fi
}

clear_all_logs() {
    warning "🗑️ Clearing all service logs..."
    read -p "Are you sure you want to clear ALL service logs? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        > "$PROD_DIR/logs/backend.log" 2>/dev/null || true
        > "$PROD_DIR/logs/backend_access.log" 2>/dev/null || true
        > "$PROD_DIR/logs/file_watcher.log" 2>/dev/null || true
        > "$PROD_DIR/logs/streamlit.log" 2>/dev/null || true
        > "$PROD_DIR/logs/frontend.log" 2>/dev/null || true
        success "✅ All service logs cleared"
    else
        info "Operation cancelled"
    fi
}

# Parse arguments
SERVICE="${1:-all}"
COMMAND="${2:-status}"

# Handle service-specific commands
case "$SERVICE" in
    "backend")
        case "$COMMAND" in
            "tail") exec ./monitor_backend_logs.sh tail ;;
            "errors") exec ./monitor_backend_logs.sh errors ;;
            "status") exec ./monitor_backend_logs.sh status ;;
            "clear") exec ./monitor_backend_logs.sh clear ;;
            *) exec ./monitor_backend_logs.sh "$COMMAND" ;;
        esac
        ;;
        
    "watcher")
        case "$COMMAND" in
            "tail") exec ./monitor_file_watcher_logs.sh tail ;;
            "errors") exec ./monitor_file_watcher_logs.sh errors ;;
            "status") exec ./monitor_file_watcher_logs.sh status ;;
            "clear") exec ./monitor_file_watcher_logs.sh clear ;;
            *) exec ./monitor_file_watcher_logs.sh "$COMMAND" ;;
        esac
        ;;
        
    "all")
        case "$COMMAND" in
            "tail") tail_all_logs ;;
            "errors") show_all_errors ;;
            "status") show_all_status ;;
            "clear") clear_all_logs ;;
            *) show_all_status ;;
        esac
        ;;
        
    "help"|"-h"|"--help")
        show_usage
        ;;
        
    *)
        error "❌ Unknown service: $SERVICE"
        echo ""
        show_usage
        exit 1
        ;;
esac
