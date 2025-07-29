#!/bin/bash

# Deploy Production Host Script - Run services directly on macOS host
# This script runs all services natively on the production server
# Bypasses all Docker credential and keychain issues

set -e  # Exit on error

# Configuration
PROD_USER="jforrest"
PROD_SERVER="100.75.201.24"
PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"
DEV_WATCH_DIR="./data_ingestion_dev"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper Functions
info() { printf "${BLUE}%s${NC}\n" "$1"; }
success() { printf "${GREEN}%s${NC}\n" "$1"; }
warning() { printf "${YELLOW}%s${NC}\n" "$1"; }
error() { printf "${RED}%s${NC}\n" "$1"; }
step() { printf "\n${YELLOW}--- %s ---${NC}\n" "$1"; }

echo -e "${GREEN}=== AI Africa Funding Tracker Host-Based Deployment ===${NC}"
echo -e "${YELLOW}Deploying services directly on macOS host (no Docker)${NC}"

# Step 1: Verify prerequisites and sync files
step "Step 1: Syncing Files to Production Server"

# Copy files to production server (same as Docker deployment)
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '__pycache__' \
    --exclude 'venv' --exclude '.env' --exclude '.git' \
    ./ ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

# Copy the .env file separately
scp .env ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/
scp backend/.env ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/backend/ 2>/dev/null || true

success "✓ Files synced to production server"

# Step 2: Setup and start services on production server
step "Step 2: Setting up Host-Based Services"

ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    # Set up environment
    export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH
    
    # Unlock keychain directly (no Docker issues!)
    echo "Unlocking keychain for host-based deployment..."
    STORED_PASSWORD=$(security find-generic-password -a "$USER" -s "docker-deployment" -w 2>/dev/null || echo "")
    if [ -n "$STORED_PASSWORD" ]; then
        security unlock-keychain -p "$STORED_PASSWORD" "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null || true
        echo "✓ Keychain unlocked successfully"
    else
        echo "⚠ No stored keychain password found, continuing without unlock"
    fi
    
    # Stop any existing processes
    echo "Stopping existing services..."
    pkill -f "uvicorn.*taifa" 2>/dev/null || true
    pkill -f "streamlit.*run" 2>/dev/null || true
    pkill -f "next.*start" 2>/dev/null || true
    pkill -f "python.*file_watcher" 2>/dev/null || true
    sleep 3
    
    # Create Python virtual environment for backend
    echo "Setting up Python environment for backend..."
    cd backend
    /usr/local/bin/python3.12 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start backend service
    echo "Starting FastAPI backend..."
    nohup bash -c "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload" > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../pids/backend.pid
    echo "✓ Backend started (PID: $BACKEND_PID)"
    
    cd ..
    
    # Setup Streamlit
    echo "Setting up Streamlit dashboard..."
    cd frontend/streamlit_app
    /usr/local/bin/python3.12 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start Streamlit service
    echo "Starting Streamlit dashboard..."
    nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../../logs/streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > ../../pids/streamlit.pid
    echo "✓ Streamlit started (PID: $STREAMLIT_PID)"
    
    cd ../..
    
    # Setup Next.js frontend
    echo "Setting up Next.js frontend..."
    cd frontend/nextjs
    npm install
    npm run build
    
    # Start Next.js service
    echo "Starting Next.js frontend..."
    nohup bash -c "export PATH=/usr/local/bin:$PATH && PORT=3030 npm start" > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../../pids/frontend.pid
    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    
    cd ../..
    
    # Setup file watcher
    echo "Setting up file watcher..."
    cd data_processors
    /usr/local/bin/python3.12 -m venv venv 2>/dev/null || true
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start file watcher service
    echo "Starting file watcher..."
    export PYTHONPATH=/Users/jforrest/production/TAIFA-FIALA
    export DATA_INGESTION_PATH=/Users/jforrest/production/TAIFA-FIALA/data_ingestion
    nohup python file_watcher.py > ../logs/file_watcher.log 2>&1 &
    WATCHER_PID=$!
    echo $WATCHER_PID > ../pids/file_watcher.pid
    echo "✓ File watcher started (PID: $WATCHER_PID)"
    
    cd ..
    
    # Create directories for logs and PIDs
    mkdir -p logs pids
    
    echo "✓ All services started successfully"
    
    # Show running processes
    echo "Running services:"
    echo "Backend (PID: $(cat pids/backend.pid 2>/dev/null || echo 'N/A'))"
    echo "Streamlit (PID: $(cat pids/streamlit.pid 2>/dev/null || echo 'N/A'))"
    echo "Frontend (PID: $(cat pids/frontend.pid 2>/dev/null || echo 'N/A'))"
    echo "File Watcher (PID: $(cat pids/file_watcher.pid 2>/dev/null || echo 'N/A'))"
EOF

# Step 3: Health check
step "Step 3: Performing Health Check"
info "Waiting for services to initialize..."
sleep 15

info "Testing HTTP endpoints..."

# Test FastAPI backend
if curl --silent --fail --max-time 10 http://100.75.201.24:8030/health > /dev/null; then
    success "✓ Backend is healthy and responding"
else
    warning "⚠ Backend health check failed"
fi

# Test Streamlit dashboard
if curl --silent --fail --max-time 10 http://100.75.201.24:8501 > /dev/null; then
    success "✓ Streamlit dashboard is responding"
else
    warning "⚠ Streamlit dashboard health check failed"
fi

# Test Next.js frontend
if curl --silent --fail --max-time 10 http://100.75.201.24:3030 > /dev/null; then
    success "✓ Frontend is responding"
else
    warning "⚠ Frontend health check failed"
fi

# Step 4: Create management scripts
step "Step 4: Creating Management Scripts"

# Create restart script
ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    cat > restart_services_host.sh << 'RESTART_EOF'
#!/bin/bash

# AI Africa Funding Tracker - Host-Based Restart Script
cd $(dirname $0)

echo "Stopping services..."
[ -f pids/backend.pid ] && kill $(cat pids/backend.pid) 2>/dev/null || true
[ -f pids/streamlit.pid ] && kill $(cat pids/streamlit.pid) 2>/dev/null || true
[ -f pids/frontend.pid ] && kill $(cat pids/frontend.pid) 2>/dev/null || true
[ -f pids/file_watcher.pid ] && kill $(cat pids/file_watcher.pid) 2>/dev/null || true

sleep 5

echo "Starting services..."
# Backend
cd backend && source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
echo $! > ../pids/backend.pid
cd ..

# Streamlit
cd frontend/streamlit_app && source venv/bin/activate
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../../logs/streamlit.log 2>&1 &
echo $! > ../../pids/streamlit.pid
cd ../..

# Frontend
cd frontend/nextjs
nohup npm start > ../../logs/frontend.log 2>&1 &
echo $! > ../../pids/frontend.pid
cd ../..

# File watcher
cd data_processors && source venv/bin/activate
export PYTHONPATH=/Users/jforrest/production/TAIFA-FIALA
export DATA_INGESTION_PATH=/Users/jforrest/production/TAIFA-FIALA/data_ingestion
nohup python file_watcher.py > ../logs/file_watcher.log 2>&1 &
echo $! > ../pids/file_watcher.pid
cd ..

echo "✓ All services restarted"
RESTART_EOF

    chmod +x restart_services_host.sh
    
    # Create stop script
    cat > stop_services_host.sh << 'STOP_EOF'
#!/bin/bash

# AI Africa Funding Tracker - Host-Based Stop Script
cd $(dirname $0)

echo "Stopping all services..."
[ -f pids/backend.pid ] && kill $(cat pids/backend.pid) 2>/dev/null && echo "✓ Backend stopped"
[ -f pids/streamlit.pid ] && kill $(cat pids/streamlit.pid) 2>/dev/null && echo "✓ Streamlit stopped"
[ -f pids/frontend.pid ] && kill $(cat pids/frontend.pid) 2>/dev/null && echo "✓ Frontend stopped"
[ -f pids/file_watcher.pid ] && kill $(cat pids/file_watcher.pid) 2>/dev/null && echo "✓ File watcher stopped"

# Clean up PID files
rm -f pids/*.pid

echo "✓ All services stopped"
STOP_EOF

    chmod +x stop_services_host.sh
EOF

success "✓ Management scripts created"

echo
success "=== Host-Based Deployment Complete ==="
info "Deployment completed at: $(date)"
echo
warning "Services running on:"
warning "Backend FastAPI: http://100.75.201.24:8030"
warning "Streamlit Dashboard: http://100.75.201.24:8501"
warning "API Documentation: http://100.75.201.24:8030/docs"
warning "Next.js Frontend: http://100.75.201.24:3030"
echo
info "Management commands:"
echo "Restart services: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && ./restart_services_host.sh'"
echo "Stop services: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && ./stop_services_host.sh'"
echo "View logs: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && tail -f logs/<service>.log'"
echo "Check processes: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && cat pids/*.pid'"

echo
info "File Ingestion:"
echo "Local watch directory: ${DEV_WATCH_DIR}"
echo "Remote watch directory: ${PROD_DIR}/data_ingestion"
echo "To add files for processing:"
echo "1. Place files in ${DEV_WATCH_DIR}/inbox/"
echo "2. Files will be automatically synced to production"
echo "3. Check ${DEV_WATCH_DIR}/logs/ for processing logs"
