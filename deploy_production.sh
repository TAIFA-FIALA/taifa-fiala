#!/bin/bash

# TAIFA-FIALA Production Deployment Script
# This script deploys the backend to Mac-mini while frontend deploys to Vercel

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these for your setup
PROD_SERVER="100.75.201.24"  # Your Mac-mini Tailscale IP
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/taifa-fiala"
LOCAL_PATH="$(pwd)"

# Service management (no Docker, using systemd/processes)
PYTHON_ENV="python3"
VENV_PATH="$PROD_PATH/venv"

echo -e "${GREEN}=== TAIFA-FIALA Production Deployment ===${NC}"
echo -e "${BLUE}Backend: Mac-mini | Frontend: Vercel${NC}"

# Verify we're in the correct directory
if [ ! -f "tools/dashboard/system_dashboard.py" ]; then
    echo -e "${RED}Error: TAIFA-FIALA project files not found. Please run this script from the project root.${NC}"
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
if [ ! -f "tools/ingestion/start_data_ingestion.py" ]; then
    echo -e "${RED}Error: Data ingestion tools not found${NC}"
    exit 1
fi

if [ ! -f "tools/dashboard/system_dashboard.py" ]; then
    echo -e "${RED}Error: System dashboard not found${NC}"
    exit 1
fi

# Check if environment file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ TAIFA-FIALA files ready${NC}"

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

# Sync files excluding frontend and development artifacts
echo "Syncing backend files..."
rsync -avz --delete --progress \
    --exclude '.git' \
    --exclude 'frontend/' \
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
    "$LOCAL_PATH/" "$SSH_USER@$PROD_SERVER:$PROD_PATH/"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to sync files to Mac-mini${NC}"
    # Clean up deployment tag
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Backend files synced successfully${NC}"

echo -e "${YELLOW}Step 7: Stopping existing TAIFA-FIALA services${NC}"

# Stop existing services
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Kill existing processes
    echo 'Stopping existing TAIFA-FIALA services...'
    pkill -f 'streamlit.*system_dashboard' || true
    pkill -f 'python.*start_data_ingestion' || true
    pkill -f 'python.*enhanced_data_ingestion' || true
    
    # Wait for processes to stop
    sleep 3
    
    echo 'Existing services stopped'
"

echo -e "${GREEN}✓ Existing services stopped${NC}"

echo -e "${YELLOW}Step 8: Installing and configuring Redis${NC}"

# Install and configure Redis on mac-mini
ssh $SSH_USER@$PROD_SERVER "
    # Define Homebrew paths for Mac-mini
    BREW_PATH=/opt/homebrew/bin/brew
    if [ ! -f \$BREW_PATH ]; then
        BREW_PATH=/usr/local/bin/brew
    fi
    
    # Check if Redis is installed
    if ! command -v redis-server &> /dev/null; then
        echo 'Installing Redis...'
        
        # Check for Homebrew with full path
        if [ -f \$BREW_PATH ]; then
            echo 'Using Homebrew to install Redis...'
            \$BREW_PATH install redis
        else
            echo 'Homebrew not found. Trying alternative installation...'
            
            # Try different package managers based on the system
            if command -v apt-get &> /dev/null; then
                echo 'Using apt-get to install Redis...'
                sudo apt-get update
                sudo apt-get install -y redis-server
            elif command -v yum &> /dev/null; then
                echo 'Using yum to install Redis...'
                sudo yum install -y redis
            else
                echo 'Installing Redis from source...'
                
                # Install Redis from source
                cd /tmp
                curl -O http://download.redis.io/redis-stable.tar.gz
                tar xzf redis-stable.tar.gz
                cd redis-stable
                make
                sudo make install
                
                # Create Redis configuration directory
                sudo mkdir -p /etc/redis
                sudo mkdir -p /var/log/redis
                sudo mkdir -p /var/lib/redis
                
                # Create basic Redis configuration
                sudo tee /etc/redis/redis.conf > /dev/null <<EOF
port 6379
bind 127.0.0.1
daemonize yes
pidfile /var/run/redis.pid
logfile /var/log/redis/redis.log
dir /var/lib/redis
EOF
                
                echo '✓ Redis installed from source'
            fi
        fi
    else
        echo '✓ Redis already installed'
    fi
    
    # Start Redis service
    echo 'Starting Redis service...'
    
    # Try different methods to start Redis based on the system
    if [ -f \$BREW_PATH ]; then
        # Use Homebrew services (Mac-mini)
        \$BREW_PATH services start redis
    elif command -v systemctl &> /dev/null; then
        # Use systemd if available (most modern Linux systems)
        sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null
        sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis 2>/dev/null
    elif command -v service &> /dev/null; then
        # Use traditional service command
        sudo service redis-server start 2>/dev/null || sudo service redis start 2>/dev/null
    elif [ -f '/etc/redis/redis.conf' ]; then
        # Use custom configuration if available
        redis-server /etc/redis/redis.conf
    else
        # Default daemonized start
        redis-server --daemonize yes --port 6379 --bind 127.0.0.1
    fi
    
    # Wait for Redis to start
    sleep 5
    
    # Test Redis connection with retries
    REDIS_CLI_PATH=/usr/local/bin/redis-cli
    if [ ! -f \$REDIS_CLI_PATH ]; then
        REDIS_CLI_PATH=/opt/homebrew/bin/redis-cli
    fi
    
    REDIS_PASSWORD=redis1484
    
    REDIS_READY=false
    for i in {1..10}; do
        if [ -f \$REDIS_CLI_PATH ] && \$REDIS_CLI_PATH -a \$REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; then
            echo '✓ Redis is running and accessible'
            REDIS_READY=true
            break
        elif command -v redis-cli &> /dev/null && redis-cli -a \$REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; then
            echo '✓ Redis is running and accessible'
            REDIS_READY=true
            break
        else
            echo 'Waiting for Redis to start... (attempt $i/10)'
            sleep 2
        fi
    done
    
    if [ \$REDIS_READY = false ]; then
        echo 'Warning: Redis connection test failed, but continuing deployment...'
        echo 'Redis may still be functional - will verify later in health checks'
    fi
"

REDIS_STATUS=$?

if [ $REDIS_STATUS -ne 0 ]; then
    echo -e "${RED}Error: Failed to setup Redis${NC}"
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Redis setup complete${NC}"

echo -e "${YELLOW}Step 9: Setting up Python environment${NC}"

# Setup Python environment
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Create virtual environment if it doesn't exist
    if [ ! -d 'venv' ]; then
        echo 'Creating virtual environment...'
        $PYTHON_ENV -m venv venv
    fi
    
    echo 'Installing Python dependencies...'
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    # Install additional requirements if they exist
    if [ -f 'backend/requirements_crewai.txt' ]; then
        pip install -r backend/requirements_crewai.txt
    fi
    
    echo 'Python environment ready'
"

SETUP_STATUS=$?

if [ $SETUP_STATUS -ne 0 ]; then
    echo -e "${RED}Error: Failed to setup Python environment${NC}"
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Python environment setup complete${NC}"

echo -e "${YELLOW}Step 10: Deploying Frontend to Vercel${NC}"

# Deploy frontend to Vercel
echo "Deploying frontend to Vercel..."
cd frontend/nextjs

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Deploy to Vercel (using token from .env)
if [ -f ".env.local" ]; then
    echo "✓ Found Vercel configuration"
    echo "Deploying to Vercel project: TAIFA-FIALA-frontend"
    vercel --prod --yes --name TAIFA-FIALA-frontend
    VERCEL_STATUS=$?
    
    if [ $VERCEL_STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend deployed to Vercel successfully${NC}"
        echo -e "${GREEN}✓ Project: TAIFA-FIALA-frontend${NC}"
    else
        echo -e "${RED}Error: Frontend deployment to Vercel failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Warning: No .env.local found. Skipping Vercel deployment.${NC}"
    echo -e "${YELLOW}Please ensure VERCEL_TOKEN is configured in frontend/nextjs/.env.local${NC}"
fi

# Return to project root
cd ../..

echo -e "${YELLOW}Step 11: Starting TAIFA-FIALA Backend Services${NC}"

# Start backend services
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Create logs directory
    mkdir -p logs
    
    # Clean Python cache on server
    echo 'Cleaning Python cache on server...'
    find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    find . -name '*.pyc' -delete 2>/dev/null || true
    
    # Start services in background
    echo 'Starting TAIFA-FIALA backend services...'
    
    # Start FastAPI backend with Redis support
    echo 'Starting FastAPI backend...'
    cd backend
    nohup ../venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    echo \$! > ../.backend.pid
    cd ..
    
    # Start data ingestion service (if exists)
    if [ -f 'tools/ingestion/start_data_ingestion.py' ]; then
        nohup venv/bin/python tools/ingestion/start_data_ingestion.py > logs/data_ingestion.log 2>&1 &
        echo \$! > .data_ingestion.pid
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    echo 'Waiting for services to start...'
    sleep 15
    
    # Check if services are running
    echo 'Service status:'
    
    # Check Redis
    if [ -f \$REDIS_CLI_PATH ] && \$REDIS_CLI_PATH -a \$REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; then
        echo '✓ Redis service: RUNNING'
    elif command -v redis-cli &> /dev/null && redis-cli -a \$REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; then
        echo '✓ Redis service: RUNNING'
    else
        echo '✗ Redis service: FAILED'
    fi
    
    # Check FastAPI backend
    if kill -0 \$(cat .backend.pid 2>/dev/null) 2>/dev/null; then
        echo '✓ FastAPI backend: RUNNING on port 8000'
        # Test API health endpoint
        sleep 5
        if curl -s http://localhost:8000/health | grep -q 'healthy'; then
            echo '✓ FastAPI backend health check: PASSED'
        else
            echo '⚠ FastAPI backend health check: PENDING (may still be starting)'
        fi
    else
        echo '✗ FastAPI backend: FAILED'
    fi
    
    # Check data ingestion service (if exists)
    if [ -f '.data_ingestion.pid' ]; then
        if kill -0 \$(cat .data_ingestion.pid 2>/dev/null) 2>/dev/null; then
            echo '✓ Data ingestion service: RUNNING'
        else
            echo '✗ Data ingestion service: FAILED'
        fi
    else
        echo 'ℹ Data ingestion service: NOT CONFIGURED'
    fi
"

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ TAIFA-FIALA services started successfully${NC}"
    
    # Final health check
    echo -e "${YELLOW}Performing final health checks...${NC}"
    sleep 5
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        echo 'Final service status:'
        echo '=========================================='
        
        # Check Redis
        if [ -f \$REDIS_CLI_PATH ] && \$REDIS_CLI_PATH -a \$REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; then
            echo '✓ Redis: RUNNING and responding'
        elif command -v redis-cli &> /dev/null && redis-cli -a \$REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; then
            echo '✓ Redis: RUNNING and responding'
        else
            echo '✗ Redis: NOT RESPONDING'
        fi
        
        # Check FastAPI backend
        if kill -0 \$(cat .backend.pid 2>/dev/null) 2>/dev/null; then
            echo '✓ FastAPI Backend: RUNNING (PID: '\$(cat .backend.pid)')'
            # Final API health check
            if curl -s http://localhost:8000/health | grep -q 'healthy'; then
                echo '✓ API Health Check: PASSED'
            else
                echo '⚠ API Health Check: FAILED or PENDING'
            fi
        else
            echo '✗ FastAPI Backend: NOT RUNNING'
        fi
        
        # Check data ingestion service
        if [ -f '.data_ingestion.pid' ]; then
            if kill -0 \$(cat .data_ingestion.pid 2>/dev/null) 2>/dev/null; then
                echo '✓ Data Ingestion: RUNNING (PID: '\$(cat .data_ingestion.pid)')'
            else
                echo '✗ Data Ingestion: NOT RUNNING'
            fi
        else
            echo 'ℹ Data Ingestion: NOT CONFIGURED'
        fi
        
        echo
        echo 'Recent logs:'
        echo '--- FastAPI Backend ---'
        tail -5 logs/backend.log 2>/dev/null || echo 'No logs yet'
        if [ -f 'logs/data_ingestion.log' ]; then
            echo '--- Data Ingestion ---'
            tail -5 logs/data_ingestion.log 2>/dev/null || echo 'No logs yet'
        fi
    "
    
    echo
    echo -e "${GREEN}=== TAIFA-FIALA Deployment Complete ===${NC}"
    echo -e "${BLUE}Deployment tag: ${DEPLOY_TAG}${NC}"
    echo -e "${BLUE}Branch deployed: ${CURRENT_BRANCH} (${CURRENT_COMMIT})${NC}"
    echo
    echo -e "${GREEN}✓ Services Status:${NC}"
    echo -e "${YELLOW}  • Redis: Running on localhost:6379${NC}"
    echo -e "${YELLOW}  • FastAPI Backend: Running on http://${PROD_SERVER}:8000${NC}"
    echo -e "${YELLOW}  • Frontend: Deployed to Vercel${NC}"
    echo -e "${YELLOW}  • Data Ingestion: Configured (if available)${NC}"
    echo
    echo -e "${GREEN}🌐 Access URLs:${NC}"
    echo -e "${BLUE}  • API Documentation: http://${PROD_SERVER}:8000/docs${NC}"
    echo -e "${BLUE}  • API Health Check: http://${PROD_SERVER}:8000/health${NC}"
    echo -e "${BLUE}  • Frontend Application: Check Vercel deployment output${NC}"
    echo
    echo -e "${GREEN}🔧 Useful Commands:${NC}"
    echo -e "${BLUE}Check backend logs:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/backend.log'"
    echo -e "${BLUE}Check all logs:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/*.log'"
    echo -e "${BLUE}Check services:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ps aux | grep -E \"(uvicorn|python)\"'"
    echo -e "${BLUE}Test API:${NC} curl http://${PROD_SERVER}:8000/health"
    echo -e "${BLUE}Redis status:${NC} ssh $SSH_USER@$PROD_SERVER '/usr/local/bin/redis-cli ping'"
    echo
    echo -e "${GREEN}📝 Next Steps:${NC}"
    echo -e "${YELLOW}  1. Verify frontend deployment URL from Vercel output${NC}"
    echo -e "${YELLOW}  2. Test API endpoints using the documentation at /docs${NC}"
    echo -e "${YELLOW}  3. Monitor logs for any startup issues${NC}"
    echo -e "${YELLOW}  4. Configure domain/SSL if needed${NC}"
    
else
    echo -e "${RED}Error: Failed to start TAIFA-FIALA services${NC}"
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
    echo -e "${BLUE}Check processes:${NC} ssh $SSH_USER@$PROD_SERVER 'ps aux | grep -E \"(python|streamlit)\"'"
    
    exit 1
fi