#!/bin/bash

# Deploy Production Docker Script using Docker CLI directly
# This script is designed to be run in the Docker Desktop console on the production server
# where keychain access is available

set -e  # Exit on error

# Configuration
PROD_DIR="$(pwd)"  # Current directory (works locally or on production)
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

echo -e "${GREEN}=== AI Africa Funding Tracker Docker CLI Deployment ===${NC}"
echo -e "${YELLOW}Deploying directly using Docker CLI commands${NC}"

# Check if we're in the right directory
step "Step 1: Verifying Environment"
if [ ! -d "$PROD_DIR" ]; then
    error "Production directory $PROD_DIR not found"
    error "Please ensure the project has been deployed to the production server first"
    exit 1
fi

cd "$PROD_DIR"
info "Working in: $(pwd)"

# Check for required files
if [ ! -f "docker-compose.watcher.yml" ]; then
    error "docker-compose.watcher.yml not found in $PROD_DIR"
    error "Please ensure the project files have been copied to the production server"
    exit 1
fi

# Test keychain access
step "Step 2: Testing Keychain Access"
KEYCHAIN_PASSWORD=$(security find-generic-password -w -s 'keychain-unlock' -a $USER 2>/dev/null)
if [ -n "$KEYCHAIN_PASSWORD" ]; then
    if security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null; then
        success "✓ Keychain unlocked successfully"
        # Set extended timeout
        security set-keychain-settings -t 3600 "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null || true
    else
        warning "⚠ Failed to unlock keychain with stored password"
    fi
else
    warning "⚠ No stored keychain password found"
    warning "⚠ Run the keychain setup script first if credential access is needed"
fi

# Stop existing containers
step "Step 3: Stopping Existing Containers"
info "Stopping any running containers..."
/usr/local/bin/docker stop $(/usr/local/bin/docker ps -q) 2>/dev/null || true
/usr/local/bin/docker container prune -f 2>/dev/null || true
success "✓ Existing containers stopped"

# Build images using Docker CLI
step "Step 4: Building Docker Images"

# Build backend
info "Building backend image..."
/usr/local/bin/docker build -t taifa-backend ./backend
if [ $? -eq 0 ]; then
    success "✓ Backend image built successfully"
else
    error "✗ Failed to build backend image"
    exit 1
fi

# Build frontend
info "Building frontend image..."
/usr/local/bin/docker build -t taifa-frontend ./frontend/nextjs
if [ $? -eq 0 ]; then
    success "✓ Frontend image built successfully"
else
    error "✗ Failed to build frontend image"
    exit 1
fi

# Build streamlit
info "Building streamlit image..."
/usr/local/bin/docker build -t taifa-streamlit ./frontend/streamlit_app
if [ $? -eq 0 ]; then
    success "✓ Streamlit image built successfully"
else
    error "✗ Failed to build streamlit image"
    exit 1
fi

# Build file watcher
info "Building file watcher image..."
/usr/local/bin/docker build -t taifa-file-watcher -f data_processors/Dockerfile.watcher .
if [ $? -eq 0 ]; then
    success "✓ File watcher image built successfully"
else
    error "✗ Failed to build file watcher image"
    exit 1
fi

# Create network
step "Step 5: Creating Docker Network"
/usr/local/bin/docker network create taifa-network 2>/dev/null || true
success "✓ Docker network ready"

# Start containers using Docker CLI
step "Step 6: Starting Containers"

# Start backend
info "Starting backend container..."
/usr/local/bin/docker run -d \
    --name taifa-backend \
    --network taifa-network \
    -p 8000:8000 \
    --env-file ./backend/.env \
    -v "$(pwd)/backend:/app/backend" \
    -v "$(pwd)/data_connectors:/app/data_connectors" \
    -e PYTHONPATH=/app \
    taifa-backend \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

if [ $? -eq 0 ]; then
    success "✓ Backend container started"
else
    error "✗ Failed to start backend container"
fi

# Start frontend
info "Starting frontend container..."
/usr/local/bin/docker run -d \
    --name taifa-frontend \
    --network taifa-network \
    -p 3020:3000 \
    -v "$(pwd)/frontend/nextjs:/app" \
    -v /app/node_modules \
    -v /app/.next \
    taifa-frontend

if [ $? -eq 0 ]; then
    success "✓ Frontend container started"
else
    error "✗ Failed to start frontend container"
fi

# Start streamlit
info "Starting streamlit container..."
/usr/local/bin/docker run -d \
    --name taifa-streamlit \
    --network taifa-network \
    -p 8501:8501 \
    -v "$(pwd)/frontend/streamlit_app:/app" \
    taifa-streamlit

if [ $? -eq 0 ]; then
    success "✓ Streamlit container started"
else
    error "✗ Failed to start streamlit container"
fi

# Start file watcher
info "Starting file watcher container..."
/usr/local/bin/docker run -d \
    --name taifa-file-watcher \
    --network taifa-network \
    -v "$(pwd)/data_processors:/app/data_processors" \
    -v "$(pwd)/data_ingestion:/data_ingestion" \
    -e PYTHONPATH=/app \
    -e DATA_INGESTION_PATH=/data_ingestion \
    taifa-file-watcher

if [ $? -eq 0 ]; then
    success "✓ File watcher container started"
else
    error "✗ Failed to start file watcher container"
fi

# Health check
step "Step 7: Performing Health Check"
info "Waiting for services to initialize..."
sleep 15

info "Checking container status..."
/usr/local/bin/docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test endpoints
info "Testing HTTP endpoints..."

# Test backend
if curl --silent --fail --max-time 10 http://localhost:8000/health > /dev/null 2>&1; then
    success "✓ Backend is healthy and responding"
else
    warning "⚠ Backend health check failed"
    /usr/local/bin/docker logs taifa-backend --tail 10
fi

# Test frontend
if curl --silent --fail --max-time 10 http://localhost:3020 > /dev/null 2>&1; then
    success "✓ Frontend is responding"
else
    warning "⚠ Frontend health check failed"
    /usr/local/bin/docker logs taifa-frontend --tail 10
fi

# Test streamlit
if curl --silent --fail --max-time 10 http://localhost:8501 > /dev/null 2>&1; then
    success "✓ Streamlit dashboard is responding"
else
    warning "⚠ Streamlit dashboard health check failed"
    /usr/local/bin/docker logs taifa-streamlit --tail 10
fi

# Create restart script
step "Step 8: Creating Restart Script"
cat > restart_services_cli.sh << 'EOF'
#!/bin/bash

# AI Africa Funding Tracker - Docker CLI Restart Script
cd $(dirname $0)

echo "Stopping containers..."
/usr/local/bin/docker stop taifa-backend taifa-frontend taifa-streamlit taifa-file-watcher 2>/dev/null || true

echo "Starting containers..."
/usr/local/bin/docker start taifa-backend taifa-frontend taifa-streamlit taifa-file-watcher

echo "Container status:"
/usr/local/bin/docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
EOF

chmod +x restart_services_cli.sh
success "✓ Restart script created: restart_services_cli.sh"

echo
success "=== Docker CLI Deployment Complete ==="
info "Deployment completed at: $(date)"
echo
warning "Services running on:"
warning "Backend FastAPI: http://localhost:8000"
warning "Streamlit Dashboard: http://localhost:8501"
warning "API Documentation: http://localhost:8000/docs"
warning "Next.js Frontend: http://localhost:3020"
echo
info "Useful commands:"
echo "Check container status: /usr/local/bin/docker ps"
echo "View logs: /usr/local/bin/docker logs <container-name>"
echo "Restart services: ./restart_services_cli.sh"
echo "Stop all: /usr/local/bin/docker stop taifa-backend taifa-frontend taifa-streamlit taifa-file-watcher"