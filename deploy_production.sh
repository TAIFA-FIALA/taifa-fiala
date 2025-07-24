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
    
    # Verify .env files exist locally before sync
    info "Checking for .env files locally..."
    if [ -f "backend/.env" ]; then
        info "✓ Found backend/.env locally"
    else
        warning "⚠ backend/.env not found locally!"
    fi
    
    rsync -avz --progress \
        --exclude 'venv' \
        --exclude '.venv' \
        --exclude 'node_modules' \
        --exclude 'logs' \
        --exclude '.git' \
        --exclude '.idea' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --include 'backend/.env' \
        --include '*/.env' \
        --include '.env' \
        "$LOCAL_PATH/" "$SSH_USER@$PROD_SERVER:$PROD_PATH/" || cleanup_and_exit
    
    # Verify .env files were synced to remote
    info "Verifying .env files were synced to remote server..."
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        if [ -f 'backend/.env' ]; then
            echo '✓ backend/.env found on remote server'
            echo 'File size:' \$(wc -c < 'backend/.env') 'bytes'
        else
            echo '⚠ backend/.env NOT found on remote server!'
            echo 'Contents of backend directory:'
            ls -la backend/ || echo 'backend directory not found'
        fi
    "
    
    success "✓ Project files synced."
}

setup_environment() {
    step "Step 5: Setting Up Production Environment"
    ssh $SSH_USER@$PROD_SERVER "
        set -e
        cd '$PROD_PATH'
        
        # Set PATH to include common Docker installation locations
        export PATH=\"/usr/local/bin:/opt/homebrew/bin:\$PATH\"
        
        # Unlock keychain for Docker authentication (may require sudo)
        echo 'Unlocking keychain for Docker authentication...'
        sudo security -v unlock-keychain ~/Library/Keychains/login.keychain-db || {
            echo 'Keychain unlock failed. Trying without sudo...'
            security -v unlock-keychain ~/Library/Keychains/login.keychain-db || echo 'Keychain unlock failed, continuing anyway...'
        }
        
        # Ensure Docker daemon is running and accessible
        echo 'Checking Docker daemon status...'
        if ! docker info > /dev/null 2>&1; then
            echo 'ERROR: Docker daemon not accessible.'
            echo 'Please ensure Docker Desktop is running on the Mac-mini.'
            exit 1
        fi
        echo 'Docker daemon is accessible.'
        
        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            echo 'Docker not found. Please install Docker on the production server.'
            exit 1
        fi
        
        # Check if Docker Compose is available
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo 'Docker Compose not found. Please install Docker Compose on the production server.'
            exit 1
        fi
        
        # Stop any existing containers more aggressively
        echo 'Stopping existing containers...'
        
        # Try compose commands first
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || \
        docker compose -f docker-compose.prod.yml down 2>/dev/null || \
        echo 'No compose file or containers found, trying direct container cleanup...'
        
        # Stop and remove any taifa-fiala containers directly
        echo 'Cleaning up any remaining taifa-fiala containers...'
        CONTAINERS=\$(docker ps -aq --filter name=taifa-fiala)
        if [ ! -z "$CONTAINERS" ]; then
            echo 'Found containers to clean up:'
            docker ps -a --filter name=taifa-fiala
            docker stop $CONTAINERS 2>/dev/null || echo 'Some containers already stopped'
            docker rm $CONTAINERS 2>/dev/null || echo 'Some containers already removed'
        else
            echo 'No taifa-fiala containers found'
        fi
        
        # Targeted port cleanup - only target our specific ports
        echo 'Performing targeted port cleanup for ports 3020 and 8020...'
        
        # Function to identify and stop containers using specific ports
        cleanup_port() {
            local port=\$1
            echo \"Checking port \$port...\"
            
            if lsof -i:\$port >/dev/null 2>&1; then
                echo \"Port \$port is in use:\"
                lsof -i:\$port
                
                # Check if it's a Docker container
                PORT_PROCESSES=\$(lsof -ti:\$port)
                for pid in \$PORT_PROCESSES; do
                    # Get process info
                    PROCESS_INFO=\$(ps -p \$pid -o comm= 2>/dev/null || echo \"unknown\")
                    
                    # If it's a Docker container, try to identify and stop it gracefully
                    if echo \"\$PROCESS_INFO\" | grep -q docker; then
                        echo \"Found Docker process \$pid using port \$port\"
                        
                        # Try to find the container ID from the process
                        CONTAINER_ID=\$(docker ps --format \"table {{.ID}}\\t{{.Ports}}\" | grep \":\$port-\" | awk '{print \$1}' | head -1)
                        
                        if [ ! -z \"\$CONTAINER_ID\" ]; then
                            echo \"Stopping container \$CONTAINER_ID using port \$port\"
                            docker stop \$CONTAINER_ID 2>/dev/null || echo \"Failed to stop container gracefully\"
                            docker rm \$CONTAINER_ID 2>/dev/null || echo \"Failed to remove container\"
                        else
                            echo \"Could not identify container, killing process \$pid\"
                            kill -9 \$pid 2>/dev/null || echo \"Failed to kill process \$pid\"
                        fi
                    else
                        echo \"Non-Docker process \$pid (\$PROCESS_INFO) using port \$port, killing it\"
                        kill -9 \$pid 2>/dev/null || echo \"Failed to kill process \$pid\"
                    fi
                done
                
                sleep 2
                
                # Verify port is now free
                if lsof -i:\$port >/dev/null 2>&1; then
                    echo \"WARNING: Port \$port is still in use after cleanup attempt\"
                    lsof -i:\$port
                    return 1
                else
                    echo \"✓ Port \$port is now available\"
                    return 0
                fi
            else
                echo \"✓ Port \$port is already available\"
                return 0
            fi
        }
        
        # Clean up our target ports
        cleanup_port 3020
        PORT_3020_STATUS=\$?
        
        cleanup_port 8020
        PORT_8020_STATUS=\$?
        
        # Only fail if we absolutely cannot free the ports
        if [ \$PORT_3020_STATUS -ne 0 ] || [ \$PORT_8020_STATUS -ne 0 ]; then
            echo 'ERROR: Could not free required ports for deployment'
            echo 'You may need to manually stop conflicting services'
            exit 1
        fi
        
        echo 'All required ports are now available for deployment'
        
        # Build and start containers (backend and frontend)
        echo 'Building and starting Docker containers (backend and frontend)...'
        docker-compose -f docker-compose.prod.yml up -d --build || docker compose -f docker-compose.prod.yml up -d --build
        
        # Wait for services to be ready
        echo 'Waiting for services to be ready...'
        sleep 15
        
        # Verify migration system inside container
        echo 'Verifying migration system...'
        docker-compose exec -T backend python migration_helper.py --compare || docker compose exec -T backend python migration_helper.py --compare || echo 'Migration verification completed with warnings'
        
    " || cleanup_and_exit
    success "✓ Environment setup completed."
}

run_migrations() {
    step "Step 3: Running Local Database Migrations"
    info "Running migrations locally to ensure SQLite DB is up-to-date before deployment..."
    
    cd backend
    
    echo 'Checking local migration status...'
    poetry run alembic current
    
    echo 'Checking for pending migrations...'
    if poetry run alembic check 2>&1 | grep -q 'New upgrade operations detected'; then
        echo 'Pending migrations detected, generating new migration...'
        poetry run python migration_helper.py --update-migration || echo 'Migration helper completed with warnings'
    fi
    
    echo 'Running local Alembic migrations...'
    poetry run alembic upgrade head
    
    echo 'Final local migration status:'
    poetry run alembic current
    
    cd ..
    
    success "✓ Local database migrations completed."
}

start_services() {
    step "Step 7: Starting Services"
    ssh $SSH_USER@$PROD_SERVER "
        set -e
        cd '$PROD_PATH'
        
        # Set PATH to include common Docker installation locations
        export PATH=\"/usr/local/bin:/opt/homebrew/bin:\$PATH\"
        
        # Ensure containers are running (they should already be from setup_environment)
        echo 'Ensuring all containers are running...'
        docker-compose -f docker-compose.prod.yml up -d || docker compose -f docker-compose.prod.yml up -d
        
        # Wait for services to be ready
        echo 'Waiting for services to initialize...'
        sleep 15
        
        # Show container status
        echo 'Container status:'
        docker-compose -f docker-compose.prod.yml ps || docker compose -f docker-compose.prod.yml ps
        
    " || cleanup_and_exit
    success "✓ Services started successfully."
}

health_check() {
    step "Step 8: Performing Health Checks"
    info "Waiting for services to initialize..."
    sleep 30
    info "Checking service health..."

    ssh $SSH_USER@$PROD_SERVER "
        echo 'Checking Docker container status...'
        $DOCKER_COMPOSE_CMD ps

        echo 'Checking Next.js frontend...'
        curl --silent --fail http://localhost:3020 > /dev/null && echo -e '${GREEN}✓ Frontend is healthy.${NC}' || echo -e '${RED}✗ Frontend health check failed.${NC}'
        
        echo 'Checking FastAPI backend...'
        curl --silent --fail http://localhost:8000/health > /dev/null && echo -e '${GREEN}✓ Backend is healthy.${NC}' || echo -e '${RED}✗ Backend health check failed.${NC}'


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
    run_migrations
    backup_production
    sync_files
    setup_environment
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
