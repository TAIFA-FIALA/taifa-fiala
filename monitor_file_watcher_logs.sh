#!/bin/bash

# File Watcher Log Monitor for Production Server
# Usage: ./monitor_file_watcher_logs.sh [command]
# Commands: tail, errors, files, startup, full, clear, status

set -e

PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"
WATCHER_LOG="$PROD_DIR/logs/file_watcher.log"
DATA_INGESTION_PATH="$PROD_DIR/data_ingestion"

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
    echo "File Watcher Log Monitor - Production Diagnostics"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  tail     - Follow file watcher logs in real-time (default)"
    echo "  errors   - Show only error messages from logs"
    echo "  files    - Show file processing activity"
    echo "  startup  - Show startup and initialization logs"
    echo "  full     - Show complete file watcher log"
    echo "  clear    - Clear file watcher logs"
    echo "  status   - Show file watcher process status and directory info"
    echo "  dirs     - Show data ingestion directory structure"
    echo ""
    echo "Examples:"
    echo "  $0 tail     # Follow logs in real-time"
    echo "  $0 errors   # Show only errors"
    echo "  $0 files    # Show file processing activity"
    echo "  $0 dirs     # Show inbox/processed/failed directories"
}

check_logs_exist() {
    if [ ! -f "$WATCHER_LOG" ]; then
        warning "⚠ File watcher log not found at: $WATCHER_LOG"
        return 1
    fi
    return 0
}

show_watcher_status() {
    info "=== File Watcher Process Status ==="
    
    # Check if file watcher process is running
    if pgrep -f "watcher.py" > /dev/null; then
        success "✅ File watcher process is running"
        ps aux | grep "watcher.py" | grep -v grep
    else
        error "❌ File watcher process is not running"
    fi
    
    echo ""
    info "=== Data Ingestion Directory Status ==="
    if [ -d "$DATA_INGESTION_PATH" ]; then
        success "✅ Data ingestion directory exists: $DATA_INGESTION_PATH"
        
        # Show directory structure
        for dir in inbox processed failed; do
            full_path="$DATA_INGESTION_PATH/$dir"
            if [ -d "$full_path" ]; then
                file_count=$(find "$full_path" -type f 2>/dev/null | wc -l)
                success "  📁 $dir: $file_count files"
            else
                warning "  ⚠ $dir directory missing"
            fi
        done
    else
        error "❌ Data ingestion directory not found: $DATA_INGESTION_PATH"
    fi
    
    echo ""
    info "=== Environment Variables ==="
    echo "PYTHONPATH: ${PYTHONPATH:-'Not set'}"
    echo "DATA_INGESTION_PATH: ${DATA_INGESTION_PATH:-'Not set'}"
    
    echo ""
    info "=== Recent File Watcher Log (last 10 lines) ==="
    if [ -f "$WATCHER_LOG" ]; then
        tail -10 "$WATCHER_LOG"
    else
        warning "⚠ File watcher log file not found"
    fi
}

show_directory_structure() {
    info "=== Data Ingestion Directory Structure ==="
    
    if [ -d "$DATA_INGESTION_PATH" ]; then
        echo "📁 $DATA_INGESTION_PATH"
        
        for dir in inbox processed failed; do
            full_path="$DATA_INGESTION_PATH/$dir"
            if [ -d "$full_path" ]; then
                file_count=$(find "$full_path" -type f 2>/dev/null | wc -l)
                echo "  📁 $dir/ ($file_count files)"
                
                # Show recent files (max 5)
                if [ $file_count -gt 0 ]; then
                    find "$full_path" -type f -exec ls -la {} + 2>/dev/null | head -5 | while read line; do
                        echo "    📄 $line"
                    done
                    if [ $file_count -gt 5 ]; then
                        echo "    ... and $((file_count - 5)) more files"
                    fi
                fi
            else
                echo "  ❌ $dir/ (missing)"
            fi
        done
    else
        error "❌ Data ingestion directory not found: $DATA_INGESTION_PATH"
    fi
}

# Main command handling
case "${1:-tail}" in
    "tail"|"follow")
        info "📋 Following file watcher logs in real-time (Ctrl+C to stop)..."
        if check_logs_exist; then
            tail -f "$WATCHER_LOG"
        fi
        ;;
        
    "errors"|"error")
        info "🚨 Showing error messages from file watcher logs..."
        if check_logs_exist; then
            grep -i "error\|exception\|traceback\|failed\|❌" "$WATCHER_LOG" | tail -20
        fi
        ;;
        
    "files"|"processing")
        info "📄 Showing file processing activity..."
        if check_logs_exist; then
            grep -i "processing\|processed\|file\|inbox\|moved\|📄\|📁" "$WATCHER_LOG" | tail -20
        fi
        ;;
        
    "startup")
        info "🚀 Showing startup and initialization logs..."
        if check_logs_exist; then
            grep -i "startup\|started\|watcher\|monitoring\|python\|environment\|===" "$WATCHER_LOG" | tail -30
        fi
        ;;
        
    "full")
        info "📄 Showing complete file watcher log..."
        if check_logs_exist; then
            cat "$WATCHER_LOG"
        fi
        ;;
        
    "clear")
        warning "🗑️ Clearing file watcher logs..."
        read -p "Are you sure you want to clear file watcher logs? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            > "$WATCHER_LOG"
            success "✅ File watcher logs cleared"
        else
            info "Operation cancelled"
        fi
        ;;
        
    "status")
        show_watcher_status
        ;;
        
    "dirs"|"directories")
        show_directory_structure
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
