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
        cd '$PROD_PATH'
        
        # Stop existing services cleanly
        echo 'Stopping existing services...'
        pkill -f 'uvicorn.*main:app' || echo 'No FastAPI process found'
        pkill -f 'streamlit run' || echo 'No Streamlit process found'
        pkill -f 'next.*start' || echo 'No Next.js process found'
        
        # Wait for processes to stop gracefully
        sleep 3
        
        # Verify ports are available
        echo 'Checking port availability...'
        for port in 8020 8501 3020; do
            if lsof -i:\$port >/dev/null 2>&1; then
                echo \"WARNING: Port \$port still in use, attempting to free it...\"
                PID=\$(lsof -ti:\$port)
                if [ -n \"\$PID\" ]; then
                    echo \"Killing process \$PID on port \$port\"
                    kill -9 \$PID 2>/dev/null || echo \"Failed to kill process \$PID\"
                    sleep 2
                fi
                
                # Final check
                if lsof -i:\$port >/dev/null 2>&1; then
                    echo \"ERROR: Port \$port is still in use after cleanup\"
                    lsof -i:\$port
                    exit 1
                else
                    echo \"✓ Port \$port is now available\"
                fi
            else
                echo \"✓ Port \$port is available\"
            fi
        done
        
        # Set up Python virtual environment
        echo 'Setting up Python virtual environment...'
        if [ ! -d '$VENV_PATH' ]; then
            python3 -m venv '$VENV_PATH'
        fi
        
        source '$VENV_PATH/bin/activate'
        
        # Install/update Python dependencies
        echo 'Installing Python dependencies...'
        cd backend
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Build Next.js frontend
        echo 'Building Next.js frontend...'
        cd ../frontend/nextjs
        
        # Install Node.js dependencies
        npm install
        
        # Build the frontend
        npm run build
        
        echo 'Environment setup completed successfully'
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Environment setup completed."
    else
        error "Environment setup failed."
        rollback_deployment
        exit 1
    fi
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
    step "Step 6: Starting Services"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        source '$VENV_PATH/bin/activate'
        
        # Create logs directory if it doesn't exist
        mkdir -p logs
        
        # Start FastAPI backend
        echo 'Starting FastAPI backend...'
        cd backend
        nohup uvicorn main:app --host 0.0.0.0 --port 8020 --reload > ../logs/backend.log 2>&1 &
        BACKEND_PID=\$!
        echo \"Backend started with PID: \$BACKEND_PID\"
        
        # Start Streamlit dashboard
        echo 'Starting Streamlit dashboard...'
        nohup streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0 > ../logs/streamlit.log 2>&1 &
        STREAMLIT_PID=\$!
        echo \"Streamlit started with PID: \$STREAMLIT_PID\"
        
        # Start Next.js frontend
        echo 'Starting Next.js frontend...'
        cd ../frontend/nextjs
        nohup npm start -- --port 3020 > ../../logs/frontend.log 2>&1 &
        FRONTEND_PID=\$!
        echo \"Frontend started with PID: \$FRONTEND_PID\"
        
        # Wait for services to initialize
        echo 'Waiting for services to initialize...'
        sleep 10
        
        # Check if processes are still running
        echo 'Verifying service status...'
        if kill -0 \$BACKEND_PID 2>/dev/null; then
            echo '✓ Backend process is running'
        else
            echo '✗ Backend process failed to start'
            tail -20 ../logs/backend.log
        fi
        
        if kill -0 \$STREAMLIT_PID 2>/dev/null; then
            echo '✓ Streamlit process is running'
        else
            echo '✗ Streamlit process failed to start'
            tail -20 ../logs/streamlit.log
        fi
        
        if kill -0 \$FRONTEND_PID 2>/dev/null; then
            echo '✓ Frontend process is running'
        else
            echo '✗ Frontend process failed to start'
            tail -20 ../../logs/frontend.log
        fi
        
        # Show running processes
        echo 'Current service processes:'
        ps aux | grep -E '(uvicorn|streamlit|node.*next)' | grep -v grep || echo 'No matching processes found'
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Services started successfully."
    else
        error "Failed to start services."
        rollback_deployment
        exit 1
    fi
}

health_check() {
    step "Step 7: Health Check"
    
    info "Waiting for services to fully initialize..."
    sleep 15
    
    ssh $SSH_USER@$PROD_SERVER "
        echo 'Performing health checks...'
        
        # Check if processes are running
        echo 'Checking process status...'
        BACKEND_RUNNING=\$(ps aux | grep -v grep | grep 'uvicorn.*main:app' | wc -l)
        STREAMLIT_RUNNING=\$(ps aux | grep -v grep | grep 'streamlit run' | wc -l)
        FRONTEND_RUNNING=\$(ps aux | grep -v grep | grep 'node.*next' | wc -l)
        
        echo \"Backend processes: \$BACKEND_RUNNING\"
        echo \"Streamlit processes: \$STREAMLIT_RUNNING\"
        echo \"Frontend processes: \$FRONTEND_RUNNING\"
        
        # Check HTTP endpoints
        echo 'Testing HTTP endpoints...'
        
        # Test FastAPI backend
        echo 'Checking FastAPI backend health...'
        if curl --silent --fail --max-time 10 http://localhost:8020/health > /dev/null; then
            echo '✓ Backend is healthy and responding'
        else
            echo '✗ Backend health check failed'
            echo 'Backend logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/backend.log' 2>/dev/null || echo 'No backend logs found'
        fi
        
        # Test Streamlit dashboard
        echo 'Checking Streamlit dashboard...'
        if curl --silent --fail --max-time 10 http://localhost:8501 > /dev/null; then
            echo '✓ Streamlit dashboard is responding'
        else
            echo '✗ Streamlit dashboard health check failed'
            echo 'Streamlit logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/streamlit.log' 2>/dev/null || echo 'No streamlit logs found'
        fi
        
        # Test Next.js frontend
        echo 'Checking Next.js frontend...'
        if curl --silent --fail --max-time 10 http://localhost:3020 > /dev/null; then
            echo '✓ Frontend is responding'
        else
            echo '✗ Frontend health check failed'
            echo 'Frontend logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/frontend.log' 2>/dev/null || echo 'No frontend logs found'
        fi
        
        # Show port status
        echo 'Port status:'
        for port in 8020 8501 3020; do
            if lsof -i:\$port >/dev/null 2>&1; then
                echo \"✓ Port \$port is in use (service running)\"
            else
                echo \"✗ Port \$port is not in use (service may be down)\"
            fi
        done
        
        # Final service summary
        echo 'Service Summary:'
        ps aux | grep -E '(uvicorn|streamlit|node.*next)' | grep -v grep | while read line; do
            echo \"  \$line\"
        done
    "
    
    if [ $? -eq 0 ]; then
        success "✓ Health check completed."
    else
        warning "Health check completed with some issues. Check logs for details."
    fi
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
    warning "Backend FastAPI running on: http://${PROD_SERVER}:8020"
    warning "Streamlit Dashboard running on: http://${PROD_SERVER}:8501"
    warning "API Documentation: http://${PROD_SERVER}:8020/docs"
    warning "Next.js frontend running on: http://${PROD_SERVER}:3020"
    echo
    info "Useful commands:"
    echo "Check logs: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/*.log'"
    echo "Check status: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ps aux | grep -E \"(uvicorn|streamlit)\"'"
    echo "Restart services: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ./restart_services_aligned.sh'"
}

main "$@"
