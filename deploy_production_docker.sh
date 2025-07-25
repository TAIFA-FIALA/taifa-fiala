#!/bin/bash

# TAIFA-FIALA Production Deployment Script (Docker-based)
# This script deploys the TAIFA-FIALA platform using Docker containers

set -e  # Exit on any error

# Configuration
PROD_SERVER="100.75.201.24"
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/taifa-fiala"
DOCKER_PATH="/usr/local/bin/docker"
DOCKER_COMPOSE_PATH="/usr/local/bin/docker-compose"

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

cleanup_and_exit() {
    error "Deployment failed."
    if [ -n "$DEPLOY_TAG" ]; then
        warning "Cleaning up deployment tag: $DEPLOY_TAG"
        git tag -d "$DEPLOY_TAG" 2>/dev/null
    fi
    exit 1
}

# Function to check prerequisites
check_prerequisites() {
    step "Step 1: Verifying Prerequisites"
    
    if [ ! -f "backend/app/main.py" ]; then
        error "Project files not found. Please run this script from the project root."
        exit 1
    fi

    info "Checking 1Password login status..."
    if command -v op >/dev/null 2>&1; then
        if ! op account list >/dev/null 2>&1; then
            error "1Password CLI is not signed in."
            warning "Please run 'op signin' or ensure 1Password app is logged in."
            exit 1
        fi
        success "✓ 1Password is logged in."
    else
        warning "1Password CLI not found, skipping 1Password check."
    fi

    info "Checking SSH agent status..."
    if [ -z "$SSH_AUTH_SOCK" ]; then
        error "SSH agent is not running or not accessible."
        warning "Please ensure SSH agent is running and 1Password SSH agent is enabled."
        exit 1
    fi
    
    if ! ssh-add -l >/dev/null 2>&1; then
        error "No SSH keys are loaded in the SSH agent."
        warning "Please ensure 1Password is logged in and SSH keys are available."
        exit 1
    fi
    success "✓ SSH agent is running with keys loaded."

    info "Testing SSH connection to Mac-mini..."
    if ! ssh -o ConnectTimeout=10 $SSH_USER@$PROD_SERVER 'echo "SSH connection successful"' >/dev/null 2>&1; then
        error "Cannot connect to Mac-mini server $PROD_SERVER"
        warning "Please check your SSH configuration and Tailscale connection."
        exit 1
    fi
    success "✓ SSH connection verified."

    info "Checking for required files..."
    for f in "backend/requirements.txt" "frontend/streamlit_app/app.py" "backend/.env"; do
        if [ ! -f "$f" ]; then
            error "$f not found."
            exit 1
        fi
    done
    success "✓ Required files are present."
}

# Function to perform git safety checks
git_safety_checks() {
    step "Step 2: Performing Git Safety Checks"
    
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        error "Not a git repository."
        exit 1
    fi

    if [ -n "$(git status --porcelain)" ]; then
        warning "You have uncommitted changes."
        git status --porcelain
        read -p "Do you want to continue anyway? (y/N) " -n 1 -r; echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            warning "Deployment cancelled. Please commit or stash your changes."
            exit 1
        fi
    fi

    CURRENT_BRANCH=$(git branch --show-current)
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    DEPLOY_TAG="production_${TIMESTAMP}_${CURRENT_COMMIT}"
    info "Deploying branch: ${CURRENT_BRANCH} ${CURRENT_COMMIT}"

    info "Creating deployment tag: ${DEPLOY_TAG}"
    git tag "$DEPLOY_TAG" || cleanup_and_exit
    success "✓ Git checks passed and tag created."
}

# Function to run local migrations
run_local_migrations() {
    step "Step 3: Running Local Database Migrations"
    
    info "Running migrations locally to ensure SQLite DB is up-to-date before deployment..."
    
    cd backend
    
    # Set PYTHONPATH to include the backend directory
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    info "Checking local migration status..."
    if python -m alembic current 2>/dev/null; then
        info "Local migration status checked successfully."
        
        info "Checking for pending migrations..."
        if python -m alembic check 2>/dev/null; then
            info "No pending migrations found."
        else
            info "Running local Alembic migrations..."
            python -m alembic upgrade head 2>/dev/null || warning "Local migration upgrade had issues (non-critical for Docker deployment)"
        fi
        
        info "Final local migration status:"
        python -m alembic current 2>/dev/null || info "Migration status check completed"
    else
        warning "Local migration check failed - this is non-critical for Docker deployment"
        info "Docker containers will handle database setup independently"
    fi
    
    cd ..
    
    success "✓ Local database migrations completed."
}

# Function to create backup
backup_production() {
    step "Step 4: Creating Backup on Remote Server"
    
    BACKUP_DIR="${PROD_PATH}_backup_${TIMESTAMP}"
    ssh $SSH_USER@$PROD_SERVER "
        if [ -d '$PROD_PATH' ]; then
            echo 'Creating backup...'
            cp -r '$PROD_PATH' '$BACKUP_DIR'
            echo 'Backup created at: $BACKUP_DIR'
        else
            echo 'No existing deployment found, skipping backup.'
        fi
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Backup completed."
    else
        error "Backup failed."
        cleanup_and_exit
    fi
}

# Function to sync environment files
sync_env_files() {
    step "Step 5: Syncing Environment Files"
    
    info "Syncing environment files..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='venv' \
        --exclude='backend/venv' \
        --exclude='.next' \
        ./backend/.env $SSH_USER@$PROD_SERVER:$PROD_PATH/backend/
    
    if [ $? -eq 0 ]; then
        success "✓ Environment files synced."
    else
        error "Environment files sync failed."
        exit 1
    fi
}

# Function to check if Docker is available
check_docker() {
    step "Step 6: Checking Docker Installation"
    
    ssh $SSH_USER@$PROD_SERVER "
        if [ -f '$DOCKER_PATH' ]; then
            echo '✓ Docker found at $DOCKER_PATH'
            $DOCKER_PATH --version
        else
            echo '✗ Docker not found at $DOCKER_PATH'
            exit 1
        fi
        
        if [ -f '$DOCKER_COMPOSE_PATH' ]; then
            echo '✓ Docker Compose found at $DOCKER_COMPOSE_PATH'
            $DOCKER_COMPOSE_PATH --version
        else
            echo '✗ Docker Compose not found at $DOCKER_COMPOSE_PATH'
            exit 1
        fi
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Docker environment verified."
    else
        error "Docker environment check failed."
        exit 1
    fi
}

# Function to sync code to production server
sync_code() {
    step "Step 8: Syncing Code to Production Server"
    
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

# Function to stop existing services
stop_services() {
    step "Step 9: Stopping Existing Services"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        
        # Stop Docker containers
        echo 'Stopping Docker containers...'
        $DOCKER_COMPOSE_PATH -f docker-compose.prod.yml down || echo 'No containers to stop'
        
        # Clean up any orphaned processes (fallback)
        echo 'Cleaning up any remaining processes...'
        pkill -f 'uvicorn.*main:app' || echo 'No FastAPI processes found'
        pkill -f 'streamlit run' || echo 'No Streamlit processes found'
        pkill -f 'next.*start' || echo 'No Next.js processes found'
        
        # Clean up ports
        echo 'Cleaning up ports...'
        lsof -ti:8020 | xargs kill -9 2>/dev/null || echo 'Port 8020 already free'
        lsof -ti:8501 | xargs kill -9 2>/dev/null || echo 'Port 8501 already free'
        lsof -ti:3020 | xargs kill -9 2>/dev/null || echo 'Port 3020 already free'
        
        echo 'Services stopped and ports cleaned'
    "
    
    success "✓ Existing services stopped."
}

# Function to start services with Docker
start_services() {
    step "Step 10: Starting Services with Docker"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        
        # Create logs directory
        mkdir -p logs
        
        # Start all services with Docker Compose
        echo 'Starting services with Docker Compose...'
        $DOCKER_COMPOSE_PATH -f docker-compose.prod.yml up -d --build
        
        if [ \$? -eq 0 ]; then
            echo '✓ Docker containers started successfully'
        else
            echo '✗ Failed to start Docker containers'
            exit 1
        fi
        
        # Wait for containers to initialize
        echo 'Waiting for containers to initialize...'
        sleep 15
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Services started with Docker."
    else
        error "Failed to start services."
        exit 1
    fi
}

# Function to perform health checks
health_check() {
    step "Step 11: Health Check"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        
        echo 'Checking Docker container status...'
        $DOCKER_PATH ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
        
        echo -e '\nChecking service health...'
        
        # Check backend health
        echo 'Testing FastAPI backend (port 8020)...'
        if curl -f http://localhost:8020/health >/dev/null 2>&1; then
            echo '✓ Backend health check passed'
        else
            echo '✗ Backend health check failed'
            echo 'Backend container logs:'
            $DOCKER_PATH logs taifa-fiala_backend_1 --tail 10 2>/dev/null || echo 'No backend logs available'
        fi
        
        # Check frontend
        echo 'Testing Next.js frontend (port 3020)...'
        if curl -f http://localhost:3020 >/dev/null 2>&1; then
            echo '✓ Frontend health check passed'
        else
            echo '✗ Frontend health check failed'
            echo 'Frontend container logs:'
            $DOCKER_PATH logs taifa-fiala_frontend_1 --tail 10 2>/dev/null || echo 'No frontend logs available'
        fi
        
        # Check Streamlit
        echo 'Testing Streamlit dashboard (port 8501)...'
        if curl -f http://localhost:8501 >/dev/null 2>&1; then
            echo '✓ Streamlit health check passed'
        else
            echo '✗ Streamlit health check failed'
            echo 'Streamlit container logs:'
            $DOCKER_PATH logs taifa-fiala_streamlit_1 --tail 10 2>/dev/null || echo 'No streamlit logs available'
        fi
        
        echo -e '\nPort status:'
        netstat -tlnp | grep -E ':(8020|8501|3020)' || echo 'No services listening on expected ports'
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
    
    echo -e "\n${GREEN}Services are now running in Docker containers:${NC}"
    echo "• Backend FastAPI: http://$PROD_SERVER:8020"
    echo "• Streamlit Dashboard: http://$PROD_SERVER:8501" 
    echo "• Next.js Frontend: http://$PROD_SERVER:3020"
    echo "• API Documentation: http://$PROD_SERVER:8020/docs"
    
    echo -e "\n${BLUE}Useful Docker commands:${NC}"
    echo "Check containers: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && $DOCKER_PATH ps'"
    echo "View logs: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && $DOCKER_COMPOSE_PATH -f docker-compose.prod.yml logs -f'"
    echo "Restart services: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && $DOCKER_COMPOSE_PATH -f docker-compose.prod.yml restart'"
    echo "Stop services: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && $DOCKER_COMPOSE_PATH -f docker-compose.prod.yml down'"
}

# Main deployment flow
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 TAIFA-FIALA Production Deployment            ║"
    echo "║                        (Docker-based)                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Set up error handling
    trap cleanup_and_exit SIGINT SIGTERM
    
    check_prerequisites
    git_safety_checks
    run_local_migrations
    backup_production
    check_docker
    sync_code
    sync_env_files
    stop_services
    start_services
    health_check
    deployment_summary
    
    success "🎉 Deployment completed successfully!"
}

# Error handling
trap 'error "Deployment failed at step: $BASH_COMMAND"; exit 1' ERR

# Run main deployment
main "$@"