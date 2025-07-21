#!/bin/bash

# AI Africa Funding Tracker - Production Deployment Script
# Refactored for improved readability, maintainability, and robustness.

# --- Configuration ---
PROD_SERVER="100.75.201.24"
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/TAIFA-FIALA"
LOCAL_PATH="$(pwd)"
VENV_PATH="$PROD_PATH/venv"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# --- Colors ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Globals ---
CURRENT_BRANCH=""
CURRENT_COMMIT=""
DEPLOY_TAG=""
BACKUP_DIR=""

# --- Helper Functions ---
info() { printf "${BLUE}%s${NC}\n" "$1"; }
success() { printf "${GREEN}%s${NC}\n" "$1"; }
warning() { printf "${YELLOW}%s${NC}\n" "$1"; }
error() { printf "${RED}%s${NC}\n" "$1"; }
step() { printf "\n${YELLOW}--- %s ---${NC}\n" "$1"; }

cleanup_and_exit() {
    error "Deployment failed."
    if [ -n "$DEPLOY_TAG" ]; then
        warning "Cleaning up deployment tag: $DEPLOY_TAG"
        git tag -d "$DEPLOY_TAG" 2>/dev/null
    fi
    exit 1
}

# --- Deployment Functions ---

check_prerequisites() {
    step "Step 1: Verifying Prerequisites"
    if [ ! -f "backend/app/main.py" ]; then
        error "Project files not found. Please run this script from the project root."
        exit 1
    fi

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

backup_production() {
    step "Step 3: Creating Backup on Remote Server"
    BACKUP_DIR="${PROD_PATH}_backup_${TIMESTAMP}"
    ssh $SSH_USER@$PROD_SERVER "
        if [ -d '$PROD_PATH' ]; then
            echo 'Creating backup...'
            cp -r '$PROD_PATH' '$BACKUP_DIR' && echo 'Backup created at $BACKUP_DIR'
        else
            echo 'No existing production directory found, skipping backup.'
        fi
    " || cleanup_and_exit
    success "✓ Backup completed."
}

sync_files() {
    step "Step 4: Syncing Project Files"
    info "Syncing project files to production server..."
    rsync -avz --progress \
        --exclude 'venv' \
        --exclude '.venv' \
        --exclude 'node_modules' \
        --exclude 'logs' \
        --exclude '.git' \
        --exclude '.idea' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        "$LOCAL_PATH/" "$SSH_USER@$PROD_SERVER:$PROD_PATH/" || cleanup_and_exit
    success "✓ Project files synced."
}

setup_environment() {
    step "Step 5: Setting Up Production Environment"
    ssh $SSH_USER@$PROD_SERVER "
        set -e
        cd '$PROD_PATH'
        
        # Create virtual environment if it doesn't exist
        if [ ! -d 'venv' ]; then
            echo 'Creating Python virtual environment...'
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        echo 'Installing Python dependencies...'
        cd backend
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Verify migration system
        echo 'Verifying migration system...'
        python migration_helper.py --compare
        
        cd ..
    " || cleanup_and_exit
    success "✓ Environment setup completed."
}

run_migrations() {
    step "Step 6: Running Database Migrations"
    ssh $SSH_USER@$PROD_SERVER "
        set -e
        cd '$PROD_PATH'
        if [ -f .env ]; then
            export \$(grep -v '^#' .env | xargs)
        fi
        cd backend
        source ../venv/bin/activate
        
        echo 'Checking migration status...'
        alembic current
        
        echo 'Checking for pending migrations...'
        if alembic check 2>&1 | grep -q 'New upgrade operations detected'; then
            echo 'Pending migrations detected, generating new migration...'
            python migration_helper.py --update-migration || echo 'Migration helper completed with warnings'
        fi
        
        echo 'Running Alembic migrations...'
        alembic upgrade head
        
        echo 'Final migration status:'
        alembic current
    " || cleanup_and_exit
    success "✓ Database migrations completed."
}

start_services() {
    step "Step 7: Starting Services with Docker-Compose"
    ssh $SSH_USER@$PROD_SERVER "
        set -e
        cd '$PROD_PATH'
        
        # Find docker-compose command
        DOCKER_COMPOSE_CMD=''
        if command -v docker-compose >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD='docker-compose'
        elif command -v /usr/local/bin/docker-compose >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD='/usr/local/bin/docker-compose'
        elif docker compose version >/dev/null 2>&1; then
            DOCKER_COMPOSE_CMD='docker compose'
        else
            echo 'Error: docker-compose not found'
            exit 1
        fi
        
        echo \"Using Docker Compose command: \$DOCKER_COMPOSE_CMD\"
        echo 'Stopping existing services...'
        \$DOCKER_COMPOSE_CMD down --remove-orphans
        echo 'Building services with no cache...'
        \$DOCKER_COMPOSE_CMD build --no-cache
        echo 'Starting services...'
        \$DOCKER_COMPOSE_CMD up -d
    " || {
        warning "Service startup failed."
        cleanup_and_exit
    }
    success "✓ Services started."
}

health_check() {
    step "Step 8: Performing Health Checks"
    info "Waiting for services to initialize..."
    sleep 15
    info "Checking service health..."

    ssh $SSH_USER@$PROD_SERVER "
        echo 'Checking Docker container status...'
        docker ps

        echo 'Checking Next.js frontend...'
        curl --silent --fail http://localhost:3020 > /dev/null && echo -e '${GREEN}✓ Frontend is healthy.${NC}' || echo -e '${RED}✗ Frontend health check failed.${NC}'
        
        echo 'Checking FastAPI backend...'
        curl --silent --fail http://localhost:8000/health > /dev/null && echo -e '${GREEN}✓ Backend is healthy.${NC}' || echo -e '${RED}✗ Backend health check failed.${NC}'

        echo 'Checking Streamlit app...'
        curl --silent --fail http://localhost:8501 > /dev/null && echo -e '${GREEN}✓ Streamlit is healthy.${NC}' || echo -e '${RED}✗ Streamlit health check failed.${NC}'
    "
}

rollback_deployment() {
    step "Attempting Rollback"
    ssh $SSH_USER@$PROD_SERVER "
        if [ -d '$BACKUP_DIR' ]; then
            echo 'Rolling back to previous version...'
            rm -rf '$PROD_PATH'
            mv '$BACKUP_DIR' '$PROD_PATH'
            echo 'Rollback completed. You may need to restart services manually.'
        else
            echo 'No backup found for rollback.'
        fi
    "
    if [ $? -eq 0 ]; then
        success "✓ Rollback successful."
    else
        error "Rollback failed. Manual intervention required."
        warning "Backup is available at: $BACKUP_DIR"
    fi
}

main() {
    info "=== AI Africa Funding Tracker Production Deployment ==="

    trap cleanup_and_exit SIGINT SIGTERM

    check_prerequisites
    git_safety_checks
    backup_production
    sync_files
    setup_environment
    # run_migrations
    start_services
    health_check

    echo
    success "=== Deployment Complete ==="
    info "Deployment tag: ${DEPLOY_TAG}"
    info "Branch deployed: ${CURRENT_BRANCH} ${CURRENT_COMMIT}"
    warning "Backend FastAPI running on: http://${PROD_SERVER}:8000"
    warning "Streamlit Dashboard running on: http://${PROD_SERVER}:8501"
    warning "API Documentation: http://${PROD_SERVER}:8000/docs"
    warning "Next.js frontend running on: http://${PROD_SERVER}:3020"
    echo
    info "Useful commands:"
    echo "Check logs: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/*.log'"
    echo "Check status: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ps aux | grep -E \"(uvicorn|streamlit)\"'"
    echo "Restart services: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ./restart_services_aligned.sh'"
}

main "$@"
