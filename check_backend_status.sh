#!/bin/bash

# Backend Status Check Script
# Run this on the production server to diagnose backend health issues

echo "=== Backend Health Diagnostic ==="
echo "Timestamp: $(date)"
echo

# Check if backend process is running
echo "=== Process Status ==="
BACKEND_PID=$(cat pids/backend.pid 2>/dev/null || echo "N/A")
echo "Backend PID from file: $BACKEND_PID"

if [ "$BACKEND_PID" != "N/A" ]; then
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "✓ Backend process is running (PID: $BACKEND_PID)"
    else
        echo "❌ Backend process is not running (stale PID file)"
    fi
else
    echo "❌ No backend PID file found"
fi

# Check for uvicorn processes
echo
echo "=== Uvicorn Processes ==="
ps aux | grep uvicorn | grep -v grep || echo "No uvicorn processes found"

# Check port 8030
echo
echo "=== Port 8030 Status ==="
if command -v lsof >/dev/null 2>&1; then
    lsof -i :8030 || echo "Port 8030 is not in use"
else
    netstat -an | grep 8030 || echo "Port 8030 is not in use"
fi

# Check backend logs
echo
echo "=== Recent Backend Logs ==="
if [ -f "logs/backend.log" ]; then
    echo "Last 10 lines of backend.log:"
    tail -10 logs/backend.log
else
    echo "❌ Backend log file not found"
fi

# Test health endpoint
echo
echo "=== Health Endpoint Test ==="
if command -v curl >/dev/null 2>&1; then
    echo "Testing http://localhost:8030/health..."
    curl -s --max-time 5 http://localhost:8030/health || echo "❌ Health endpoint not responding"
    
    echo
    echo "Testing http://localhost:8030/..."
    curl -s --max-time 5 http://localhost:8030/ || echo "❌ Root endpoint not responding"
else
    echo "curl not available for endpoint testing"
fi

# Check virtual environment
echo
echo "=== Virtual Environment ==="
if [ -d "backend/venv" ]; then
    echo "✓ Backend virtual environment exists"
    if [ -f "backend/venv/bin/python" ]; then
        echo "Python version: $(backend/venv/bin/python --version)"
    fi
else
    echo "❌ Backend virtual environment not found"
fi

# Check if we can import FastAPI
echo
echo "=== FastAPI Import Test ==="
cd backend 2>/dev/null || echo "❌ Cannot change to backend directory"
if [ -f "venv/bin/python" ]; then
    venv/bin/python -c "import fastapi; print('✓ FastAPI import successful')" 2>/dev/null || echo "❌ FastAPI import failed"
    venv/bin/python -c "from app.main import app; print('✓ App import successful')" 2>/dev/null || echo "❌ App import failed"
else
    echo "❌ Python executable not found in venv"
fi

echo
echo "=== Diagnostic Complete ==="