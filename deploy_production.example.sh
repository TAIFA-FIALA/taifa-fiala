#!/bin/bash

# StockSight Production Deployment Script
# This script prepares and deploys the application to the Mac-mini production server

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these if needed
PROD_SERVER="100.75.201.24"  # Tailscale IP
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/stocksight-beta"
LOCAL_PATH="$(pwd)"

# Docker paths on production server
DOCKER_COMPOSE="/usr/local/bin/docker compose"
DOCKER="/usr/local/bin/docker"

echo -e "${GREEN}=== StockSight Production Deployment ===${NC}"

# Verify we're in the correct directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}Error: docker-compose.prod.yml not found. Please run this script from the project root.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Testing SSH connection to production server${NC}"

# Test SSH connection first
if ! ssh -o ConnectTimeout=10 $SSH_USER@$PROD_SERVER 'echo "SSH connection successful"' >/dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to production server $PROD_SERVER${NC}"
    echo -e "${YELLOW}Please check your SSH configuration and server availability${NC}"
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

# Check if production startup script exists
if [ ! -f "backend/start_prod.sh" ]; then
    echo -e "${RED}Error: backend/start_prod.sh not found${NC}"
    exit 1
fi

# Check if production environment file exists
if [ ! -f "backend/.env.prod" ]; then
    echo -e "${RED}Error: backend/.env.prod not found${NC}"
    exit 1
fi

# Check if backend/start_prod.sh is executable
if [ ! -x "backend/start_prod.sh" ]; then
    echo -e "${YELLOW}Making backend/start_prod.sh executable${NC}"
    chmod +x backend/start_prod.sh
fi

echo -e "${GREEN}✓ Production files ready${NC}"

echo -e "${YELLOW}Step 4: Creating backup on production server${NC}"

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

echo -e "${YELLOW}Step 6: Syncing files to production server${NC}"

# Sync files excluding development artifacts
echo "Syncing files..."
rsync -avz --delete --progress \
    --exclude '.git' \
    --exclude 'node_modules' \
    --exclude '.next' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude 'logs/*' \
    --exclude '*.log' \
    --exclude '.DS_Store' \
    --exclude '.redis_tunnel.pid' \
    --exclude '.uvicorn.pid' \
    --exclude '.env' \
    --exclude '.env.local' \
    --exclude '.env.development' \
    "$LOCAL_PATH/" "$SSH_USER@$PROD_SERVER:$PROD_PATH/"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to sync files to production server${NC}"
    # Clean up deployment tag
    git tag -d "$DEPLOY_TAG" 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Files synced successfully${NC}"

echo -e "${YELLOW}Step 7: Stopping existing services${NC}"

# Stop existing services first
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Fix Docker credentials issue for SSH sessions
    if [ -f ~/.docker/config.json ] && grep -q '\"credsStore\"' ~/.docker/config.json; then
        echo 'Fixing Docker credentials configuration...'
        cp ~/.docker/config.json ~/.docker/config.json.backup 2>/dev/null || true
        echo '{\"auths\":{},\"currentContext\":\"desktop-linux\"}' > ~/.docker/config.json
    fi
    
    if [ -f docker-compose.prod.yml ]; then
        echo 'Stopping existing services...'
        /usr/local/bin/docker compose -f docker-compose.prod.yml down || true
    fi
    echo 'Cleaning up Docker resources...'
    /usr/local/bin/docker system prune -af || true
"

echo -e "${GREEN}✓ Existing services stopped${NC}"

echo -e "${YELLOW}Step 8: Starting production services${NC}"

# SSH into production server and start services
echo "Starting production services..."
ssh $SSH_USER@$PROD_SERVER "
    cd '$PROD_PATH'
    
    # Clean Python cache on server
    echo 'Cleaning Python cache on server...'
    find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    find . -name '*.pyc' -delete 2>/dev/null || true
    
    # Ensure start_prod.sh is executable
    chmod +x backend/start_prod.sh
    
    # Start services
    echo 'Building and starting production services...'
    /usr/local/bin/docker compose -f docker-compose.prod.yml up -d --build --force-recreate
    
    echo 'Waiting for services to start...'
    sleep 15
    
    # Check service status
    echo 'Service status:'
    /usr/local/bin/docker compose -f docker-compose.prod.yml ps
"

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Production services started successfully${NC}"
    
    # Wait a bit more and check health
    echo -e "${YELLOW}Checking service health...${NC}"
    sleep 5
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        echo 'Final service status:'
        /usr/local/bin/docker compose -f docker-compose.prod.yml ps
        echo
        echo 'Recent logs:'
        /usr/local/bin/docker compose -f docker-compose.prod.yml logs --tail=10
    "
    
    echo
    echo -e "${GREEN}=== Deployment Complete ===${NC}"
    echo -e "${BLUE}Deployment tag: ${DEPLOY_TAG}${NC}"
    echo -e "${BLUE}Branch deployed: ${CURRENT_BRANCH} (${CURRENT_COMMIT})${NC}"
    echo -e "${YELLOW}Application should be available at: https://stocksight.drjforrest.com${NC}"
    echo
    echo "Useful commands:"
    echo -e "${BLUE}Check logs:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && /usr/local/bin/docker compose -f docker-compose.prod.yml logs -f'"
    echo -e "${BLUE}Check status:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && /usr/local/bin/docker compose -f docker-compose.prod.yml ps'"
    echo -e "${BLUE}Restart services:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && /usr/local/bin/docker compose -f docker-compose.prod.yml restart'"
    
else
    echo -e "${RED}Error: Failed to start production services${NC}"
    echo -e "${YELLOW}Attempting rollback to previous version...${NC}"
    
    ssh $SSH_USER@$PROD_SERVER "
        if [ -d '$BACKUP_DIR' ]; then
            echo 'Rolling back to previous version...'
            rm -rf '$PROD_PATH'
            mv '$BACKUP_DIR' '$PROD_PATH'
            cd '$PROD_PATH'
            /usr/local/bin/docker compose -f docker-compose.prod.yml up -d
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
    echo -e "${BLUE}Check logs:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && /usr/local/bin/docker compose -f docker-compose.prod.yml logs'"
    echo -e "${BLUE}Check service status:${NC} ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && /usr/local/bin/docker compose -f docker-compose.prod.yml ps'"
    
    exit 1
fi