#!/bin/bash

# TAIFA-FIALA Production Deployment Script
# This script deploys the TAIFA-FIALA platform to the production server

set -e  # Exit on any error

# Configuration
PROD_SERVER="100.75.201.24"
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/taifa-fiala"
VENV_PATH="/Users/jforrest/production/taifa-fiala/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to sync code to production server
sync_code() {
    step "Step 1: Syncing Code to Production Server"
    
    info "Syncing codebase to $PROD_SERVER..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.env*' \
        --exclude='venv' \
        --exclude='backend/venv' \
        --exclude='.next' \
        ./ $SSH_USER@$PROD_SERVER:$PROD_PATH/
    
    if [ $? -eq 0 ]; then
        success "✓ Code sync completed."
    else
        error "Code sync failed."
        exit 1
    fi
}

# Function to setup environment
setup_environment() {
    step "Step 2: Setting Up Production Environment"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        
        # Stop existing services cleanly
        echo 'Stopping existing services...'
        pkill -f 'uvicorn.*main:app' || echo 'No FastAPI process found'
        pkill -f 'streamlit run' || echo 'No Streamlit process found'
        pkill -f 'next.*start' || echo 'No Next.js process found'
        
        # Clean up ports
        echo 'Cleaning up ports...'
        lsof -ti:8020 | xargs kill -9 2>/dev/null || echo 'Port 8020 already free'
        lsof -ti:8501 | xargs kill -9 2>/dev/null || echo 'Port 8501 already free'
        lsof -ti:3020 | xargs kill -9 2>/dev/null || echo 'Port 3020 already free'
        
        # Activate virtual environment
        source '$VENV_PATH/bin/activate'
        
        # Install/update Python dependencies
        echo 'Installing Python dependencies...'
        cd backend
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Ensure Streamlit is installed
        echo 'Installing Streamlit...'
        pip install streamlit
        
        # Build Next.js frontend
        echo 'Building Next.js frontend...'
        cd ../frontend/nextjs
        
        # Check for Node.js and npm
        if command -v node >/dev/null 2>&1; then
            echo 'Using system Node.js'
            NODE_CMD='node'
            NPM_CMD='npm'
        elif [ -f '/usr/local/opt/node@22/bin/node' ]; then
            echo 'Using Node.js v22 from Homebrew'
            export PATH='/usr/local/opt/node@22/bin:$PATH'
            NODE_CMD='/usr/local/opt/node@22/bin/node'
            NPM_CMD='/usr/local/opt/node@22/bin/npm'
        else
            echo 'Error: Node.js not found'
            exit 1
        fi
        
        # Install Node.js dependencies
        \$NPM_CMD install
        
        # Build the frontend
        \$NPM_CMD run build
        
        echo 'Environment setup completed successfully'
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Environment setup completed."
    else
        error "Environment setup failed."
        exit 1
    fi
}

# Function to start services
start_services() {
    step "Step 3: Starting Services"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        source '$VENV_PATH/bin/activate'
        
        # Create logs directory if it doesn't exist
        mkdir -p logs
        
        # Start FastAPI backend
        echo 'Starting FastAPI backend...'
        cd '$PROD_PATH'
        export PYTHONPATH='$PROD_PATH:\$PYTHONPATH'
        nohup '$VENV_PATH/bin/python' -m uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload > logs/backend.log 2>&1 &
        BACKEND_PID=\$!
        echo \"Backend started with PID: \$BACKEND_PID\"
        
        # Start Streamlit dashboard
        echo 'Starting Streamlit dashboard...'
        nohup '$VENV_PATH/bin/python' -m streamlit run run_dashboard.py --server.port 8501 --server.address 0.0.0.0 > logs/streamlit.log 2>&1 &
        STREAMLIT_PID=\$!
        echo \"Streamlit started with PID: \$STREAMLIT_PID\"
        
        # Start Next.js frontend
        echo 'Starting Next.js frontend...'
        cd frontend/nextjs
        
        # Check for npm and start frontend
        if command -v npm >/dev/null 2>&1; then
            echo 'Using system npm'
            nohup npm start -- --port 3020 > ../../logs/frontend.log 2>&1 &
            FRONTEND_PID=\$!
            echo \"Frontend started with PID: \$FRONTEND_PID\"
        elif [ -f '/usr/local/opt/node@22/bin/npm' ]; then
            echo 'Using Homebrew npm'
            export PATH='/usr/local/opt/node@22/bin:\$PATH'
            nohup /usr/local/opt/node@22/bin/npm start -- --port 3020 > ../../logs/frontend.log 2>&1 &
            FRONTEND_PID=\$!
            echo \"Frontend started with PID: \$FRONTEND_PID\"
        else
            echo '✗ Cannot start frontend: npm not found'
            echo 'Checked system PATH and /usr/local/opt/node@22/bin/'
            FRONTEND_PID=''
        fi
        
        # Wait for services to initialize
        echo 'Waiting for services to initialize...'
        sleep 10
        
        # Check if processes are still running
        echo 'Verifying service status...'
        if [ -n \"\$BACKEND_PID\" ] && kill -0 \$BACKEND_PID 2>/dev/null; then
            echo '✓ Backend process is running'
        else
            echo '✗ Backend process failed to start'
            echo 'Backend logs (last 20 lines):'
            tail -20 '$PROD_PATH/logs/backend.log' 2>/dev/null || echo 'No backend logs found'
        fi
        
        if [ -n \"\$STREAMLIT_PID\" ] && kill -0 \$STREAMLIT_PID 2>/dev/null; then
            echo '✓ Streamlit process is running'
        else
            echo '✗ Streamlit process failed to start'
            echo 'Streamlit logs (last 20 lines):'
            tail -20 '$PROD_PATH/logs/streamlit.log' 2>/dev/null || echo 'No streamlit logs found'
        fi
        
        if [ -n \"\$FRONTEND_PID\" ] && kill -0 \$FRONTEND_PID 2>/dev/null; then
            echo '✓ Frontend process is running'
        else
            echo '✗ Frontend process failed to start'
            echo 'Frontend logs (last 20 lines):'
            tail -20 '$PROD_PATH/logs/frontend.log' 2>/dev/null || echo 'No frontend logs found'
        fi
        
        # Show running processes
        echo 'Current service processes:'
        ps aux | grep -E '(uvicorn|streamlit|npm)' | grep -v grep || echo 'No matching processes found'
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Services started successfully."
    else
        error "Failed to start services."
        exit 1
    fi
}

# Function to perform health checks
health_check() {
    step "Step 4: Health Check"
    
    ssh $SSH_USER@$PROD_SERVER "
        echo 'Waiting for services to fully initialize...'
        sleep 5
        
        echo 'Performing health checks...'
        
        # Check process status
        echo 'Checking process status...'
        BACKEND_COUNT=\$(ps aux | grep -c 'uvicorn.*backend.main:app' | grep -v grep || echo 0)
        STREAMLIT_COUNT=\$(ps aux | grep -c 'streamlit run' | grep -v grep || echo 0)
        FRONTEND_COUNT=\$(ps aux | grep -c 'npm.*start' | grep -v grep || echo 0)
        
        echo \"Backend processes: \$BACKEND_COUNT\"
        echo \"Streamlit processes: \$STREAMLIT_COUNT\"
        echo \"Frontend processes: \$FRONTEND_COUNT\"
        
        # Test HTTP endpoints
        echo 'Testing HTTP endpoints...'
        
        echo 'Checking FastAPI backend health...'
        if curl -f http://localhost:8020/health >/dev/null 2>&1; then
            echo '✓ Backend health check passed'
        else
            echo '✗ Backend health check failed'
            echo 'Backend logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/backend.log' 2>/dev/null || echo 'No backend logs available'
        fi
        
        echo 'Checking Streamlit dashboard...'
        if curl -f http://localhost:8501 >/dev/null 2>&1; then
            echo '✓ Streamlit dashboard health check passed'
        else
            echo '✗ Streamlit dashboard health check failed'
            echo 'Streamlit logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/streamlit.log' 2>/dev/null || echo 'No streamlit logs available'
        fi
        
        echo 'Checking Next.js frontend...'
        if curl -f http://localhost:3020 >/dev/null 2>&1; then
            echo '✓ Frontend health check passed'
        else
            echo '✗ Frontend health check failed'
            echo 'Frontend logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/frontend.log' 2>/dev/null || echo 'No frontend logs available'
        fi
        
        # Check port status
        echo 'Port status:'
        if netstat -tlnp | grep ':8020' >/dev/null 2>&1; then
            echo '✓ Port 8020 is in use (service running)'
        else
            echo '✗ Port 8020 is not in use (service may be down)'
        fi
        
        if netstat -tlnp | grep ':8501' >/dev/null 2>&1; then
            echo '✓ Port 8501 is in use (service running)'
        else
            echo '✗ Port 8501 is not in use (service may be down)'
        fi
        
        if netstat -tlnp | grep ':3020' >/dev/null 2>&1; then
            echo '✓ Port 3020 is in use (service running)'
        else
            echo '✗ Port 3020 is not in use (service may be down)'
        fi
        
        # Service summary
        echo 'Service Summary:'
        ps aux | grep -E '(uvicorn|streamlit|npm)' | grep -v grep || echo 'No services running'
    "
    
    success "✓ Health check completed."
}

# Function to display deployment summary
deployment_summary() {
    step "Deployment Complete"
    
    # Get current git info
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    DEPLOYMENT_TAG="production_$(date +%Y%m%d_%H%M%S)_${CURRENT_COMMIT}"
    
    success "Deployment tag: $DEPLOYMENT_TAG"
    success "Branch deployed: $CURRENT_BRANCH $CURRENT_COMMIT"
    
    echo -e "\n${GREEN}Services should be running at:${NC}"
    echo "Backend FastAPI running on: http://$PROD_SERVER:8020"
    echo "Streamlit Dashboard running on: http://$PROD_SERVER:8501"
    echo "API Documentation: http://$PROD_SERVER:8020/docs"
    echo "Next.js frontend running on: http://$PROD_SERVER:3020"
    
    echo -e "\n${BLUE}Useful commands:${NC}"
    echo "Check logs: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/*.log'"
    echo "Check status: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ps aux | grep -E \"(uvicorn|streamlit)\"'"
    echo "Restart services: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ./deploy_production_fixed.sh'"
}

# Main deployment flow
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 TAIFA-FIALA Production Deployment            ║"
    echo "║                      (Fixed Version)                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    sync_code
    setup_environment
    start_services
    health_check
    deployment_summary
    
    success "🎉 Deployment completed successfully!"
}

# Error handling
trap 'error "Deployment failed at step: $BASH_COMMAND"; exit 1' ERR

# Run main deployment
main "$@"