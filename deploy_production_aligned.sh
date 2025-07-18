#!/bin/bash

# AI Africa Funding Tracker - Production Deployment Script
# Updated to align with the new project structure (Backend FastAPI + Frontend Next.js + Streamlit)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these for your setup
PROD_SERVER="100.75.201.24"  # Your Mac-mini Tailscale IP
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/ai-africa-funding-tracker"
LOCAL_PATH="$(pwd)"

# Service management
PYTHON_ENV="python3"
VENV_PATH="$PROD_PATH/venv"

echo -e "${GREEN}=== AI Africa Funding Tracker Production Deployment ===${NC}"
echo -e "${BLUE}Backend: Mac-mini (FastAPI + Streamlit) | Frontend: Vercel (Next.js)${NC}"

# Verify we're in the correct directory
if [ ! -f "backend/app/main.py" ]; then
    echo -e "${RED}Error: AI Africa Funding Tracker project files not found. Please run this script from the project root.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Testing SSH connection to Mac-mini${NC}"

# Test SSH connection first
if ! ssh -o ConnectTimeout=10 $SSH_USER@$PROD_SERVER 'echo "SSH connection successful"' >/dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to Mac-mini server $PROD_SERVER${NC}"
    echo -e "${YELLOW}Please check your SSH configuration and Tailscale connection${NC}"
    exit 1
fi

echo -e "${GREEN}✓ SSH connection verified${NC}"

echo -e "${YELLOW}Step 2: Git safety checks${NC}"

# Check Git status
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    echo "Uncommitted files:"
    git status --porcelain
    echo
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deployment cancelled. Please commit or stash your changes.${NC}"
        exit 1
    fi
fi

# Get current branch and commit info
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)

echo -e "${BLUE}Deploying branch: ${CURRENT_BRANCH} (${CURRENT_COMMIT})${NC}"

# Create deployment tag
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEPLOY_TAG="production_${TIMESTAMP}_${CURRENT_COMMIT}"

echo -e "${YELLOW}Creating deployment tag: ${DEPLOY_TAG}${NC}"
git tag "$DEPLOY_TAG"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create deployment tag${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 3: Pre-deployment checks${NC}"

# Check if key files exist
if [ ! -f "backend/app/main.py" ]; then
    echo -e "${RED}Error: Backend FastAPI main.py not found${NC}"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}Error: Backend requirements.txt not found${NC}"
    exit 1
fi

if [ ! -f "frontend/streamlit_app/app.py" ]; then
    echo -e "${RED}Error: Streamlit app not found${NC}"
    exit 1
fi

# Check if environment file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}Error: Backend .env file not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project files ready${NC}"

echo -e "${YELLOW}Step 4: Creating backup on Mac-mini${NC}"

# Create backup of current production
BACKUP_DIR="${PROD_PATH}_backup_${TIMESTAMP}"
ssh $SSH_USER@$PROD_SERVER "
    if [ -d '$PROD_PATH' ]; then 
        echo 'Creating backup...'
        cp -r '$PROD_PATH' '$BACKUP_DIR'
        echo 'Backup created at $BACKUP_DIR'
    else
        echo 'No existing production directory found, skipping backup'
    fi
"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create backup${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backup completed${NC}"

echo -e "${YELLOW}Step 5: Cleaning Python cache and preparing files${NC}"

# Clean Python cache files locally
echo "Cleaning local Python cache files..."
find "$LOCAL_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$LOCAL_PATH" -name "*.pyc" -delete 2>/dev/null || true

# Create production directory if it doesn't exist
ssh $SSH_USER@$PROD_SERVER "mkdir -p '$PROD_PATH'"

echo -e "${GREEN}✓ Files prepared${NC}"

echo -e "${YELLOW}Step 6: Syncing backend files to Mac-mini${NC}"

# Sync files excluding frontend/nextjs and development artifacts
echo "Syncing backend and streamlit files..."
rsync -avz --delete --progress \
    --exclude '.git' \
    --exclude 'frontend/nextjs/' \
    --exclude 'node_modules' \
    --exclude '.next' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude 'logs/*' \
    --exclude '*.log' \
    --exclude '.DS_Store' \
    --exclude '.env.local' \
    --exclude '.env.development' \
    --exclude '.vercel' \
    --exclude 'deploy_production.sh' \
    --exclude 'deploy_production_aligned.sh' \
    --exclude 'start-dev.sh' \
    --exclude 'dev-quick-start.sh' \
    "$LOCAL_PATH/" "$SSH_USER@$PROD_SERVER:$PROD_PATH/"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to sync files to Mac-mini${NC}"
    # Clean up deployment tag
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Backend and Streamlit files synced successfully${NC}"

echo -e "${YELLOW}Step 7: Stopping existing services${NC}"

# Stop existing services
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Kill existing processes
    echo 'Stopping existing services...'
    pkill -f 'uvicorn.*app.main:app' || true
    pkill -f 'streamlit.*app.py' || true
    
    # Kill processes on our ports
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    lsof -ti :8501 | xargs kill -9 2>/dev/null || true
    
    # Wait for processes to stop
    sleep 3
    
    echo 'Existing services stopped'
"

echo -e "${GREEN}✓ Existing services stopped${NC}"

echo -e "${YELLOW}Step 8: Setting up Python environment${NC}"

# Setup Python environment and install dependencies
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Create virtual environment if it doesn't exist
    if [ ! -d 'venv' ]; then
        echo 'Creating Python virtual environment...'
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install requirements
    echo 'Installing Python dependencies...'
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install backend requirements
    pip install -r backend/requirements.txt
    
    # Install streamlit requirements
    pip install -r frontend/streamlit_app/requirements.txt
    
    echo 'Python environment ready'
"

SETUP_STATUS=$?

if [ $SETUP_STATUS -ne 0 ]; then
    echo -e "${RED}Error: Failed to setup Python environment${NC}"
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Python environment setup complete${NC}"

echo -e "${YELLOW}Step 9: Starting services${NC}"

# Start services
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Clean Python cache on server
    echo 'Cleaning Python cache on server...'
    find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    find . -name '*.pyc' -delete 2>/dev/null || true
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start services in background
    echo 'Starting services...'
    
    # Start FastAPI backend
    cd backend
    nohup ../venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    echo \$! > ../.backend.pid
    cd ..
    
    # Start Streamlit app
    cd frontend/streamlit_app
    nohup ../../venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../../logs/streamlit.log 2>&1 &
    echo \$! > ../../.streamlit.pid
    cd ../../
    
    echo 'Waiting for services to start...'
    sleep 10
    
    # Check if services are running
    echo 'Service status:'
    if kill -0 \$(cat .backend.pid 2>/dev/null) 2>/dev/null; then
        echo '✓ Backend service: RUNNING on port 8000'
    else
        echo '✗ Backend service: FAILED'
    fi
    
    if kill -0 \$(cat .streamlit.pid 2>/dev/null) 2>/dev/null; then
        echo '✓ Streamlit service: RUNNING on port 8501'
    else
        echo '✗ Streamlit service: FAILED'
    fi
"

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Services started successfully${NC}"
    
    # Final health check
    echo -e "${YELLOW}Checking service health...${NC}"
    sleep 5
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        echo 'Final service status:'
        
        # Check processes
        if kill -0 \$(cat .backend.pid 2>/dev/null) 2>/dev/null; then
            echo '✓ Backend: RUNNING (PID: '\$(cat .backend.pid)')'
        else
            echo '✗ Backend: NOT RUNNING'
        fi
        
        if kill -0 \$(cat .streamlit.pid 2>/dev/null) 2>/dev/null; then
            echo '✓ Streamlit: RUNNING (PID: '\$(cat .streamlit.pid)')'
        else
            echo '✗ Streamlit: NOT RUNNING'
        fi
        
        echo
        echo 'Recent logs:'
        echo '--- Backend ---'
        tail -5 logs/backend.log 2>/dev/null || echo 'No logs yet'
        echo '--- Streamlit ---'
        tail -5 logs/streamlit.log 2>/dev/null || echo 'No logs yet'
    "
    
    echo
    echo -e "${GREEN}=== Deployment Complete ===${NC}"
    echo -e "${BLUE}Deployment tag: ${DEPLOY_TAG}${NC}"
    echo -e "${BLUE}Branch deployed: ${CURRENT_BRANCH} (${CURRENT_COMMIT})${NC}"
    echo -e "${YELLOW}Backend (FastAPI) running on: http://${PROD_SERVER}:8000${NC}"
    echo -e "${YELLOW}Streamlit Dashboard running on: http://${PROD_SERVER}:8501${NC}"
    echo -e "${YELLOW}API Documentation: http://${PROD_SERVER}:8000/docs${NC}"
    echo -e "${YELLOW}Remember to deploy Next.js frontend to Vercel separately${NC}"
    echo
    echo "Useful commands:"
    echo -e "${BLUE}Check logs:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/*.log'"
    echo -e "${BLUE}Check status:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ps aux | grep -E \"(uvicorn|streamlit)\"'"
    echo -e "${BLUE}Restart services:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ./restart_services_aligned.sh'"
    
else
    echo -e "${RED}Error: Failed to start services${NC}"
    echo -e "${YELLOW}Attempting rollback to previous version...${NC}"
    
    ssh $SSH_USER@$PROD_SERVER "
        if [ -d '$BACKUP_DIR' ]; then
            echo 'Rolling back to previous version...'
            rm -rf '$PROD_PATH'
            mv '$BACKUP_DIR' '$PROD_PATH'
            echo 'Rollback completed'
        else
            echo 'No backup found for rollback'
        fi
    "
    
    ROLLBACK_STATUS=$?
    
    if [ $ROLLBACK_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Rollback successful${NC}"
    else
        echo -e "${RED}Error: Rollback failed. Manual intervention required.${NC}"
        echo -e "${YELLOW}Backup is available at: $BACKUP_DIR${NC}"
    fi
    
    # Remove deployment tag on failure
    echo -e "${YELLOW}Cleaning up deployment tag due to failure${NC}"
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    
    echo
    echo "Debug commands:"
    echo -e "${BLUE}Check logs:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && cat logs/*.log'"
    echo -e "${BLUE}Check processes:${NC} ssh $SSH_USER@$PROD_SERVER 'ps aux | grep -E \"(uvicorn|streamlit)\"'"
    
    exit 1
fi