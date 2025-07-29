#!/bin/bash

# Deploy Production Docker Script for AI Africa Funding Tracker
# This script deploys the application to production, including the file watcher service

set -e  # Exit on error

# Configuration
PROD_SERVER="100.75.201.24"  # Mac-mini server
PROD_USER="jforrest"  # Production server username
PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"  # Production directory
DEV_WATCH_DIR="./data_ingestion_dev"  # Local development watch directory
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

# Globals
CURRENT_BRANCH=""
CURRENT_COMMIT=""
DEPLOY_TAG=""
BACKUP_DIR=""

# Error handling
cleanup_and_exit() {
    error "Deployment failed."
    if [ -n "$DEPLOY_TAG" ]; then
        warning "Cleaning up deployment tag: $DEPLOY_TAG"
        git tag -d "$DEPLOY_TAG" 2>/dev/null
    fi
    exit 1
}

# Set up error handling
trap cleanup_and_exit SIGINT SIGTERM

echo -e "${GREEN}=== AI Africa Funding Tracker Production Deployment ===${NC}"
echo -e "${YELLOW}Deploying to ${PROD_SERVER}:${PROD_DIR}${NC}"

# Check prerequisites
step "Step 1: Verifying Prerequisites"

# Check for required files
if [ ! -f "docker-compose.watcher.yml" ] || [ ! -f "data_processors/Dockerfile.watcher" ]; then
    error "Required Docker files not found. Please run this script from the project root."
    exit 1
fi

# Check SSH connection
info "Testing SSH connection to server..."
if ! ssh -o ConnectTimeout=10 $PROD_USER@$PROD_SERVER 'echo "SSH connection successful"' >/dev/null 2>&1; then
    error "Cannot connect to server $PROD_SERVER"
    warning "Please check your SSH configuration and connection."
    exit 1
fi
success "✓ SSH connection verified."

# Check for Docker on remote server
info "Checking for Docker on remote server..."
# Check for Docker in common macOS and Linux locations
if ssh $PROD_USER@$PROD_SERVER 'test -f /usr/local/bin/docker || test -f /usr/bin/docker || command -v docker >/dev/null 2>&1'; then
    # Check for docker-compose
    if ssh $PROD_USER@$PROD_SERVER 'test -f /usr/local/bin/docker-compose || test -f /usr/bin/docker-compose || command -v docker-compose >/dev/null 2>&1'; then
        success "✓ Docker and Docker Compose are available on remote server."
        DOCKER_AVAILABLE=true
    else
        warning "Docker found but Docker Compose not found on remote server."
        warning "Continuing with deployment, but Docker-based services will not start."
        DOCKER_AVAILABLE=false
    fi
else
    warning "Docker not found on remote server."
    warning "You will need to install Docker and Docker Compose on the remote server."
    warning "Run the following commands on the remote server:"
    warning "  curl -fsSL https://get.docker.com -o get-docker.sh"
    warning "  sudo sh get-docker.sh"
    warning "  sudo apt-get install -y docker-compose"
    warning "Continuing with deployment, but Docker-based services will not start."
    DOCKER_AVAILABLE=false
fi

# Git safety checks
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

# Create local development watch directory if it doesn't exist
step "Step 3: Setting up Local Development Watch Directory"

# Check if rsync is installed
if ! command -v rsync >/dev/null 2>&1; then
    error "rsync is not installed on your local machine."
    warning "Please install rsync to enable file synchronization."
    exit 1
fi
success "✓ rsync is available."
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
rsync -avz --delete ${DEV_WATCH_DIR}/ ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/data_ingestion/

# Log the sync
echo "\$(date): Synced to production" >> ${DEV_WATCH_DIR}/logs/sync.log
EOF

# Make the sync script executable
chmod +x ${DEV_WATCH_DIR}/sync_to_prod.sh

# Create a cron job to run the sync script every minute
info "Setting up automatic sync to production server..."
CRON_JOB="* * * * * $(pwd)/${DEV_WATCH_DIR}/sync_to_prod.sh"
(crontab -l 2>/dev/null | grep -v "sync_to_prod.sh"; echo "$CRON_JOB") | crontab -

# Run the sync script once to ensure it works
info "Testing sync to production server..."
${DEV_WATCH_DIR}/sync_to_prod.sh
if [ $? -eq 0 ]; then
    success "✓ Initial sync to production server successful."
else
    warning "Initial sync to production server failed. Check your SSH connection and try again."
    warning "You can run the sync script manually: ${DEV_WATCH_DIR}/sync_to_prod.sh"
fi

success "✓ Local development watch directory set up at ${DEV_WATCH_DIR}"
success "✓ Files will be automatically synced to production every minute"

# Create backup on remote server
step "Step 4: Creating Backup on Remote Server"
BACKUP_DIR="${PROD_DIR}_backup_${TIMESTAMP}"
ssh $PROD_USER@$PROD_SERVER "
    if [ -d '$PROD_DIR' ]; then
        echo 'Creating backup...'
        mkdir -p '$BACKUP_DIR'
        
        # Use rsync instead of cp to exclude problematic directories
        rsync -a --exclude='.venv' --exclude='venv' --exclude='__pycache__' '$PROD_DIR/' '$BACKUP_DIR/'
        
        if [ \$? -eq 0 ]; then
            echo 'Backup created at $BACKUP_DIR'
        else
            echo 'Backup failed, but continuing with deployment'
        fi
    else
        echo 'No existing production directory found, skipping backup.'
    fi
"
success "✓ Backup completed."

# SSH to production server and set up the environment
step "Step 5: Setting up Production Environment"
ssh ${PROD_USER}@${PROD_SERVER} << EOF
    # Create production directory if it doesn't exist
    mkdir -p ${PROD_DIR}
    
    # Create data ingestion directories
    mkdir -p ${PROD_DIR}/data_ingestion/{inbox/{pdfs,csvs,articles},processing,completed,failed,logs}
    touch ${PROD_DIR}/data_ingestion/inbox/urls.txt
    
    # Set permissions
    chmod -R 755 ${PROD_DIR}/data_ingestion
EOF

# Copy files to production server
step "Step 6: Copying Files to Production Server"

# Check for .env file
if [ -f ".env" ]; then
    info "✓ Found .env file locally"
else
    warning "⚠ .env file not found locally! Deployment may fail."
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r; echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Deployment cancelled."
        cleanup_and_exit
    fi
fi
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '__pycache__' \
    --exclude 'venv' --exclude '.env' --exclude '.git' \
    ./ ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

# Copy the .env file separately
scp .env ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

# SSH to production server and start the services
step "Step 7: Starting Services on Production Server"

if [ "$DOCKER_AVAILABLE" = true ]; then
    ssh ${PROD_USER}@${PROD_SERVER} << EOF
        cd ${PROD_DIR}
        
        # Set Docker paths for macOS compatibility
        export PATH=/usr/local/bin:$PATH
        DOCKER_CMD=/usr/local/bin/docker
        DOCKER_COMPOSE_CMD=/usr/local/bin/docker-compose
        
        # Disable BuildKit to avoid build context issues
        export DOCKER_BUILDKIT=0
        
        # Bypass Docker credential issues by logging out
        echo "Logging out of Docker to avoid credential issues..."
        \$DOCKER_CMD logout 2>/dev/null || true
        
        # Stop any running containers
        \$DOCKER_COMPOSE_CMD down || true
        
        # Start the services with the watcher
        \$DOCKER_COMPOSE_CMD -f docker-compose.watcher.yml up -d
        
        # Check if services are running
        \$DOCKER_COMPOSE_CMD ps
EOF
else
    warning "Skipping Docker container startup as Docker is not available on the remote server."
    warning "Please install Docker and Docker Compose on the remote server and then run:"
    warning "  ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && docker-compose -f docker-compose.watcher.yml up -d'"
fi

# Perform health check
step "Step 8: Performing Health Check"

if [ "$DOCKER_AVAILABLE" = true ]; then
    info "Waiting for services to initialize..."
    sleep 15

    ssh $PROD_USER@$PROD_SERVER "
        cd ${PROD_DIR}
        
        # Set Docker paths for macOS compatibility
        export PATH=/usr/local/bin:\$PATH
        DOCKER_CMD=/usr/local/bin/docker
        DOCKER_COMPOSE_CMD=/usr/local/bin/docker-compose
        
        # Check if Docker containers are running
        echo 'Docker container status:'
        \$DOCKER_COMPOSE_CMD -f docker-compose.watcher.yml ps
        
        # Check if all expected containers are running
        RUNNING_CONTAINERS=\$(\$DOCKER_CMD ps --format '{{.Names}}' | wc -l)
        if [ \$RUNNING_CONTAINERS -lt 4 ]; then
            echo '⚠ Warning: Not all containers are running!'
            \$DOCKER_CMD ps
            echo 'Container logs:'
            for container in \$(\$DOCKER_COMPOSE_CMD -f docker-compose.watcher.yml ps -q); do
                echo \"Logs for \$(\$DOCKER_CMD inspect --format='{{.Name}}' \$container | sed 's/^\///')\"
                \$DOCKER_CMD logs \$container --tail 20
            done
        else
            echo '✓ All containers are running'
        fi
        
        # Check HTTP endpoints
        echo 'Testing HTTP endpoints...'
        
        # Test FastAPI backend
        if curl --silent --fail --max-time 10 http://localhost:8000/health > /dev/null; then
            echo '✓ Backend is healthy and responding'
        else
            echo '⚠ Backend health check failed'
            echo 'Backend container logs:'
            \$DOCKER_CMD logs \$(\$DOCKER_CMD ps -q -f name=backend) --tail 20
        fi
        
        # Test Streamlit dashboard
        if curl --silent --fail --max-time 10 http://localhost:8501 > /dev/null; then
            echo '✓ Streamlit dashboard is responding'
        else
            echo '⚠ Streamlit dashboard health check failed'
            echo 'Streamlit container logs:'
            \$DOCKER_CMD logs \$(\$DOCKER_CMD ps -q -f name=streamlit) --tail 20
        fi
        
        # Test Next.js frontend
        if curl --silent --fail --max-time 10 http://localhost:3020 > /dev/null; then
            echo '✓ Frontend is responding'
        else
            echo '⚠ Frontend health check failed'
            echo 'Frontend container logs:'
            \$DOCKER_CMD logs \$(\$DOCKER_CMD ps -q -f name=frontend) --tail 20
        fi
        
        # Check file watcher service
        echo 'Checking file watcher service...'
        if \$DOCKER_CMD ps | grep -q file_watcher; then
            echo '✓ File watcher service is running'
            
            # Check if watch directory exists
            if [ -d '${PROD_DIR}/data_ingestion' ]; then
                echo '✓ Data ingestion directory exists'
                ls -la '${PROD_DIR}/data_ingestion'
            else
                echo '⚠ Data ingestion directory does not exist'
            fi
        else
            echo '⚠ File watcher service is not running'
            echo 'File watcher container logs:'
            \$DOCKER_CMD logs \$(\$DOCKER_CMD ps -q -f name=file_watcher) --tail 20 || echo 'No file watcher container found'
        fi
    "
else
    warning "Skipping Docker health check as Docker is not available on the remote server."
    
    # Check if data ingestion directory exists
    ssh $PROD_USER@$PROD_SERVER "
        if [ -d '${PROD_DIR}/data_ingestion' ]; then
            echo '✓ Data ingestion directory exists'
            ls -la '${PROD_DIR}/data_ingestion'
        else
            echo '⚠ Data ingestion directory does not exist'
        fi
    "
fi

if [ $? -eq 0 ]; then
    success "✓ Health check completed."
else
    warning "Health check completed with some issues. Check logs for details."
fi

# Create a restart script on the remote server
step "Step 9: Creating Restart Script"

if [ "$DOCKER_AVAILABLE" = true ]; then
    ssh $PROD_USER@$PROD_SERVER "
        cat > ${PROD_DIR}/restart_services.sh << 'EOF'
#!/bin/bash

# AI Africa Funding Tracker - Service Restart Script
cd \$(dirname \$0)

echo 'Stopping Docker containers...'
docker-compose -f docker-compose.watcher.yml down

echo 'Starting Docker containers...'
docker-compose -f docker-compose.watcher.yml up -d

echo 'Container status:'
docker-compose -f docker-compose.watcher.yml ps
EOF

        chmod +x ${PROD_DIR}/restart_services.sh
        echo 'Restart script created at ${PROD_DIR}/restart_services.sh'
    "
else
    ssh $PROD_USER@$PROD_SERVER "
        cat > ${PROD_DIR}/install_docker.sh << 'EOF'
#!/bin/bash

# Script to install Docker and Docker Compose
echo 'Installing Docker...'
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

echo 'Installing Docker Compose...'
sudo apt-get update
sudo apt-get install -y docker-compose

echo 'Starting services...'
cd \$(dirname \$0)
docker-compose -f docker-compose.watcher.yml up -d

echo 'Container status:'
docker-compose -f docker-compose.watcher.yml ps
EOF

        chmod +x ${PROD_DIR}/install_docker.sh
        echo 'Docker installation script created at ${PROD_DIR}/install_docker.sh'
    "
    
    warning "Created install_docker.sh script on the remote server."
    warning "Run 'ssh ${PROD_USER}@${PROD_SERVER} \"cd ${PROD_DIR} && sudo ./install_docker.sh\"' to install Docker and start services."
fi

success "✓ Restart script created."

echo
success "=== Deployment Complete ==="
info "Deployment tag: ${DEPLOY_TAG}"
info "Branch deployed: ${CURRENT_BRANCH} ${CURRENT_COMMIT}"

if [ "$DOCKER_AVAILABLE" = true ]; then
    warning "Backend FastAPI running on: http://${PROD_SERVER}:8000"
    warning "Streamlit Dashboard running on: http://${PROD_SERVER}:8501"
    warning "API Documentation: http://${PROD_SERVER}:8000/docs"
    warning "Next.js frontend running on: http://${PROD_SERVER}:3020"
else
    warning "Docker is not available on the remote server."
    warning "Please install Docker and Docker Compose to start the services."
    warning "Run: ssh ${PROD_USER}@${PROD_SERVER} \"cd ${PROD_DIR} && sudo ./install_docker.sh\""
fi
echo
info "File Ingestion:"
info "Local watch directory: ${DEV_WATCH_DIR}"
info "Remote watch directory: ${PROD_DIR}/data_ingestion"
info "To add files for processing:"
info "1. Place files in ${DEV_WATCH_DIR}/inbox/"
info "2. Files will be automatically synced to production"
info "3. Check ${DEV_WATCH_DIR}/logs/ for processing logs"
echo
info "Useful commands:"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "Check Docker status: ssh $PROD_USER@$PROD_SERVER 'cd $PROD_DIR && docker-compose -f docker-compose.watcher.yml ps'"
    echo "View container logs: ssh $PROD_USER@$PROD_SERVER 'cd $PROD_DIR && docker logs \$(docker ps -q -f name=file_watcher)'"
    echo "Restart services: ssh $PROD_USER@$PROD_SERVER 'cd $PROD_DIR && ./restart_services.sh'"
else
    echo "Install Docker: ssh $PROD_USER@$PROD_SERVER 'cd $PROD_DIR && sudo ./install_docker.sh'"
    echo "After installing Docker, check status: ssh $PROD_USER@$PROD_SERVER 'cd $PROD_DIR && docker-compose -f docker-compose.watcher.yml ps'"
fi

echo "Manually sync files: ${DEV_WATCH_DIR}/sync_to_prod.sh"