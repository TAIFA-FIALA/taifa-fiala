#!/bin/bash

# AI Africa Funding Tracker - Production Deployment Script
# Consolidated script that includes both the original deployment and the file watcher service

# --- Configuration ---
PROD_SERVER="100.75.201.24"
SSH_USER="jforrest"
PROD_PATH="/Users/jforrest/production/TAIFA-FIALA"
LOCAL_PATH="$(pwd)"
VENV_PATH="$PROD_PATH/venv"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# File ingestion configuration
DATA_INGESTION_PATH="$PROD_PATH/data_ingestion"
DEV_WATCH_DIR="./data_ingestion_dev"  # Local development watch directory

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

    # Check for Docker-related files
    info "Checking for Docker-related files..."
    for f in "docker-compose.watcher.yml" "data_processors/Dockerfile.watcher"; do
        if [ ! -f "$f" ]; then
            error "$f not found. File watcher service cannot be deployed."
            exit 1
        fi
    done
    success "✓ Docker files for file watcher service are present."
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

setup_file_ingestion_local() {
    step "Step 3: Setting up File Ingestion Local Environment"
    
    info "Creating local development watch directory..."
    mkdir -p ${DEV_WATCH_DIR}/{inbox/{pdfs,csvs,articles},processing,completed,failed,logs}
    touch ${DEV_WATCH_DIR}/inbox/urls.txt
    
    # Create a README file in the dev watch directory
    cat > ${DEV_WATCH_DIR}/README.md << EOF
# AI Africa Funding Tracker - Development Watch Directory

This directory is automatically synced to the production watch folder.

## Usage

1. Place files in the appropriate subdirectory:
   - PDFs: \`inbox/pdfs/\`
   - CSVs: \`inbox/csvs/\`
   - Text/HTML: \`inbox/articles/\`
   - URLs: Add to \`inbox/urls.txt\` (one per line)

2. Files will be automatically synced to production every minute.

3. Check the \`logs\` directory for processing logs.

## Directories

- \`inbox/\`: Drop files here
- \`processing/\`: Files being processed
- \`completed/\`: Processed files
- \`failed/\`: Failed files
- \`logs/\`: Processing logs
EOF

    # Create rsync script for automatic syncing
    cat > ${DEV_WATCH_DIR}/sync_to_prod.sh << EOF
#!/bin/bash

# Sync local watch directory to production
rsync -avz --delete ${DEV_WATCH_DIR}/ ${SSH_USER}@${PROD_SERVER}:${DATA_INGESTION_PATH}/

# Log the sync
echo "\$(date): Synced to production" >> ${DEV_WATCH_DIR}/logs/sync.log
EOF

    # Make the sync script executable
    chmod +x ${DEV_WATCH_DIR}/sync_to_prod.sh

    # Create a cron job to run the sync script every minute
    CRON_JOB="* * * * * $(pwd)/${DEV_WATCH_DIR}/sync_to_prod.sh"
    (crontab -l 2>/dev/null | grep -v "sync_to_prod.sh"; echo "$CRON_JOB") | crontab -
    
    success "✓ Local development watch directory set up at ${DEV_WATCH_DIR}"
    success "✓ Files will be automatically synced to production every minute"
}

run_migrations() {
    step "Step 4: Running Local Database Migrations"
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

backup_production() {
    step "Step 5: Creating Backup on Remote Server"
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
    step "Step 6: Syncing Project Files"
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

setup_file_ingestion_remote() {
    step "Step 7: Setting Up File Ingestion on Remote Server"
    
    ssh $SSH_USER@$PROD_SERVER "
        # Create data ingestion directories
        mkdir -p ${DATA_INGESTION_PATH}/{inbox/{pdfs,csvs,articles},processing,completed,failed,logs}
        touch ${DATA_INGESTION_PATH}/inbox/urls.txt
        
        # Set permissions
        chmod -R 755 ${DATA_INGESTION_PATH}
        
        echo '✓ File ingestion directories created on remote server'
    " || cleanup_and_exit
    
    success "✓ File ingestion environment set up on remote server."
}

setup_environment() {
    step "Step 8: Setting Up Production Environment"
    
    ssh $SSH_USER@$PROD_SERVER "
        cd '$PROD_PATH'
        
        # Stop existing services cleanly
        echo 'Stopping existing services...'
        pkill -f 'uvicorn.*main:app' || echo 'No FastAPI process found'
        pkill -f 'streamlit run' || echo 'No Streamlit process found'
        pkill -f 'next.*start' || echo 'No Next.js process found'
        
        # Stop any running Docker containers
        if command -v docker >/dev/null 2>&1; then
            echo 'Stopping Docker containers...'
            cd '$PROD_PATH'
            docker-compose down || echo 'No Docker Compose services to stop'
        fi
        
        # Wait for processes to stop gracefully
        sleep 3
        
        # Verify ports are available
        echo 'Checking port availability...'
        for port in 8020 8501 3020 8000; do
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
        $NPM_CMD install
        
        # Build the frontend
        $NPM_CMD run build
        
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

start_services() {
    step "Step 9: Starting Services"
    
    # Ask user which deployment method to use
    echo "Choose deployment method:"
    echo "1) Traditional deployment (FastAPI, Streamlit, Next.js as separate processes)"
    echo "2) Docker-based deployment (includes file watcher service)"
    read -p "Enter your choice (1 or 2): " deployment_choice
    
    if [ "$deployment_choice" == "2" ]; then
        # Docker-based deployment
        ssh $SSH_USER@$PROD_SERVER "
            cd '$PROD_PATH'
            
            # Check if Docker is installed
            if ! command -v docker >/dev/null 2>&1; then
                echo 'Error: Docker is not installed on the server.'
                exit 1
            fi
            
            # Check if Docker Compose is installed
            if ! command -v docker-compose >/dev/null 2>&1; then
                echo 'Error: Docker Compose is not installed on the server.'
                exit 1
            fi
            
            # Start the services with Docker Compose
            echo 'Starting services with Docker Compose...'
            docker-compose -f docker-compose.watcher.yml up -d
            
            # Check if services are running
            echo 'Docker services status:'
            docker-compose -f docker-compose.watcher.yml ps
            
            # Wait for services to initialize
            echo 'Waiting for services to initialize...'
            sleep 10
        "
    else
        # Traditional deployment
        ssh $SSH_USER@$PROD_SERVER "
            cd '$PROD_PATH'
            source '$VENV_PATH/bin/activate'
            
            # Create logs directory if it doesn't exist
            mkdir -p logs
            
            # Start FastAPI backend
            echo 'Starting FastAPI backend...'
            cd '$PROD_PATH'
            export PYTHONPATH='$PROD_PATH:$PYTHONPATH'
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
            
            # Check for Node.js and npm availability
            if command -v npm >/dev/null 2>&1; then
                echo 'Using system npm'
                nohup npm start -- --port 3020 > ../../logs/frontend.log 2>&1 &
                FRONTEND_PID=\$!
                echo \"Frontend started with PID: \$FRONTEND_PID\"
            elif [ -f '/usr/local/opt/node@22/bin/npm' ]; then
                echo 'Using Homebrew npm'
                export PATH='/usr/local/opt/node@22/bin:$PATH'
                nohup /usr/local/opt/node@22/bin/npm start -- --port 3020 > ../../logs/frontend.log 2>&1 &
                FRONTEND_PID=\$!
                echo \"Frontend started with PID: \$FRONTEND_PID\"
            else
                echo '✗ Cannot start frontend: npm not found at expected path'
                FRONTEND_PID=''
            fi
            
            # Start file watcher service manually if not using Docker
            echo 'Starting file watcher service...'
            cd '$PROD_PATH'
            export PYTHONPATH='$PROD_PATH:$PYTHONPATH'
            export DATA_INGESTION_PATH='$DATA_INGESTION_PATH'
            nohup '$VENV_PATH/bin/python' -m data_processors.src.taifa_etl.services.file_ingestion.cli.file_ingestion_cli watch > logs/file_watcher.log 2>&1 &
            WATCHER_PID=\$!
            echo \"File watcher started with PID: \$WATCHER_PID\"
            
            # Wait for services to initialize
            echo 'Waiting for services to initialize...'
            sleep 10
            
            # Check if processes are still running
            echo 'Verifying service status...'
            if kill -0 \$BACKEND_PID 2>/dev/null; then
                echo '✓ Backend process is running'
            else
                echo '✗ Backend process failed to start'
                echo 'Backend logs (last 20 lines):'
                tail -20 '$PROD_PATH/logs/backend.log' 2>/dev/null || echo 'No backend logs found'
            fi
            
            if kill -0 \$STREAMLIT_PID 2>/dev/null; then
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
            
            if kill -0 \$WATCHER_PID 2>/dev/null; then
                echo '✓ File watcher process is running'
            else
                echo '✗ File watcher process failed to start'
                echo 'File watcher logs (last 20 lines):'
                tail -20 '$PROD_PATH/logs/file_watcher.log' 2>/dev/null || echo 'No file watcher logs found'
            fi
            
            # Show running processes
            echo 'Current service processes:'
            ps aux | grep -E '(uvicorn|streamlit|node.*next|file_ingestion)' | grep -v grep || echo 'No matching processes found'
        "
    fi
    
    if [ $? -eq 0 ]; then
        success "✓ Services started successfully."
    else
        error "Failed to start services."
        rollback_deployment
        exit 1
    fi
}

health_check() {
    step "Step 10: Health Check"
    
    info "Waiting for services to fully initialize..."
    sleep 15
    
    ssh $SSH_USER@$PROD_SERVER "
        echo 'Performing health checks...'
        
        # Check if processes are running
        echo 'Checking process status...'
        BACKEND_RUNNING=\$(ps aux | grep -v grep | grep 'uvicorn.*main:app' | wc -l)
        STREAMLIT_RUNNING=\$(ps aux | grep -v grep | grep 'streamlit run' | wc -l)
        FRONTEND_RUNNING=\$(ps aux | grep -v grep | grep 'node.*next' | wc -l)
        WATCHER_RUNNING=\$(ps aux | grep -v grep | grep 'file_ingestion_cli watch' | wc -l)
        
        # Check if Docker containers are running
        DOCKER_RUNNING=0
        if command -v docker >/dev/null 2>&1; then
            DOCKER_RUNNING=\$(docker ps | grep -c 'file_watcher')
        fi
        
        echo \"Backend processes: \$BACKEND_RUNNING\"
        echo \"Streamlit processes: \$STREAMLIT_RUNNING\"
        echo \"Frontend processes: \$FRONTEND_RUNNING\"
        echo \"File watcher processes: \$WATCHER_RUNNING\"
        echo \"Docker file watcher containers: \$DOCKER_RUNNING\"
        
        # Check HTTP endpoints
        echo 'Testing HTTP endpoints...'
        
        # Test FastAPI backend
        echo 'Checking FastAPI backend health...'
        if curl --silent --fail --max-time 10 http://localhost:8020/health > /dev/null; then
            echo '✓ Backend is healthy and responding'
        elif curl --silent --fail --max-time 10 http://localhost:8000/health > /dev/null; then
            echo '✓ Backend (Docker) is healthy and responding'
        else
            echo '✗ Backend health check failed'
            echo 'Backend logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/backend.log' 2>/dev/null || echo 'No backend logs found'
            if command -v docker >/dev/null 2>&1; then
                echo 'Docker backend logs:'
                docker logs \$(docker ps -q -f name=backend) 2>/dev/null || echo 'No Docker backend logs found'
            fi
        fi
        
        # Test Streamlit dashboard
        echo 'Checking Streamlit dashboard...'
        if curl --silent --fail --max-time 10 http://localhost:8501 > /dev/null; then
            echo '✓ Streamlit dashboard is responding'
        else
            echo '✗ Streamlit dashboard health check failed'
            echo 'Streamlit logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/streamlit.log' 2>/dev/null || echo 'No streamlit logs found'
            if command -v docker >/dev/null 2>&1; then
                echo 'Docker streamlit logs:'
                docker logs \$(docker ps -q -f name=streamlit) 2>/dev/null || echo 'No Docker streamlit logs found'
            fi
        fi
        
        # Test Next.js frontend
        echo 'Checking Next.js frontend...'
        if curl --silent --fail --max-time 10 http://localhost:3020 > /dev/null; then
            echo '✓ Frontend is responding'
        else
            echo '✗ Frontend health check failed'
            echo 'Frontend logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/frontend.log' 2>/dev/null || echo 'No frontend logs found'
            if command -v docker >/dev/null 2>&1; then
                echo 'Docker frontend logs:'
                docker logs \$(docker ps -q -f name=frontend) 2>/dev/null || echo 'No Docker frontend logs found'
            fi
        fi
        
        # Check file watcher service
        echo 'Checking file watcher service...'
        if [ \$WATCHER_RUNNING -gt 0 ] || [ \$DOCKER_RUNNING -gt 0 ]; then
            echo '✓ File watcher service is running'
            
            # Check if watch directory exists
            if [ -d '$DATA_INGESTION_PATH' ]; then
                echo '✓ Data ingestion directory exists'
                ls -la '$DATA_INGESTION_PATH'
            else
                echo '✗ Data ingestion directory does not exist'
            fi
        else
            echo '✗ File watcher service is not running'
            echo 'File watcher logs (last 10 lines):'
            tail -10 '$PROD_PATH/logs/file_watcher.log' 2>/dev/null || echo 'No file watcher logs found'
            if command -v docker >/dev/null 2>&1; then
                echo 'Docker file watcher logs:'
                docker logs \$(docker ps -q -f name=file_watcher) 2>/dev/null || echo 'No Docker file watcher logs found'
            fi
        fi
        
        # Show port status
        echo 'Port status:'
        for port in 8020 8501 3020 8000; do
            if lsof -i:\$port >/dev/null 2>&1; then
                echo \"✓ Port \$port is in use (service running)\"
            else
                echo \"✗ Port \$port is not in use (service may be down)\"
            fi
        done
        
        # Final service summary
        echo 'Service Summary:'
        ps aux | grep -E '(uvicorn|streamlit|node.*next|file_ingestion)' | grep -v grep | while read line; do
            echo \"  \$line\"
        done
        
        if command -v docker >/dev/null 2>&1; then
            echo 'Docker containers:'
            docker ps
        fi
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
    setup_file_ingestion_local
    run_migrations
    backup_production
    sync_files
    setup_file_ingestion_remote
    setup_environment
    start_services
    health_check

    echo
    success "=== Deployment Complete ==="
    info "Deployment tag: ${DEPLOY_TAG}"
    info "Branch deployed: ${CURRENT_BRANCH} ${CURRENT_COMMIT}"
    warning "Backend FastAPI running on: http://${PROD_SERVER}:8020 or http://${PROD_SERVER}:8000 (Docker)"
    warning "Streamlit Dashboard running on: http://${PROD_SERVER}:8501"
    warning "API Documentation: http://${PROD_SERVER}:8020/docs or http://${PROD_SERVER}:8000/docs (Docker)"
    warning "Next.js frontend running on: http://${PROD_SERVER}:3020"
    echo
    info "File Ingestion:"
    info "Local watch directory: ${DEV_WATCH_DIR}"
    info "Remote watch directory: ${DATA_INGESTION_PATH}"
    info "To add files for processing:"
    info "1. Place files in ${DEV_WATCH_DIR}/inbox/"
    info "2. Files will be automatically synced to production"
    info "3. Check ${DEV_WATCH_DIR}/logs/ for processing logs"
    echo
    info "Useful commands:"
    echo "Check logs: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && tail -f logs/*.log'"
    echo "Check status: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ps aux | grep -E \"(uvicorn|streamlit|file_ingestion)\"'"
    echo "Check Docker status: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && docker-compose -f docker-compose.watcher.yml ps'"
    echo "Restart services: ssh $SSH_USER@$PROD_SERVER 'cd $PROD_PATH && ./restart_services.sh'"
}

main "$@"
