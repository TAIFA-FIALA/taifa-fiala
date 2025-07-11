#!/bin/bash

# Production Deployment Script for AI Africa Funding Tracker
# Deploys to mac-mini-local via SSH

set -e

echo "🚀 Starting deployment to mac-mini-local..."

# Configuration
REMOTE_HOST="mac-mini-local"
REMOTE_USER="$(whoami)"
REMOTE_PATH="/opt/ai-africa-funding-tracker"
LOCAL_PATH="$(pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Must be run from project root directory"
    exit 1
fi

# Backup current deployment on remote
print_status "Creating backup on remote server..."
ssh $REMOTE_USER@$REMOTE_HOST "
    if [ -d $REMOTE_PATH ]; then
        sudo cp -r $REMOTE_PATH ${REMOTE_PATH}_backup_$(date +%Y%m%d_%H%M%S)
        echo 'Backup created'
    fi
"

# Create remote directory if it doesn't exist
print_status "Preparing remote directory..."
ssh $REMOTE_USER@$REMOTE_HOST "
    sudo mkdir -p $REMOTE_PATH
    sudo chown $REMOTE_USER:staff $REMOTE_PATH
"

# Sync files to remote server (excluding development files)
print_status "Syncing files to remote server..."
rsync -av --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'node_modules' \
    --exclude '.next' \
    --exclude '.env' \
    --exclude '*.log' \
    $LOCAL_PATH/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

# Copy production environment file
print_status "Setting up production environment..."
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $REMOTE_PATH
    cp .env.example .env.production
    # Update environment for production
    sed -i '' 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env.production
    sed -i '' 's/DEBUG=true/DEBUG=false/' .env.production
    sed -i '' 's/LOG_LEVEL=DEBUG/LOG_LEVEL=INFO/' .env.production
    mv .env.production .env
"

# Stop existing services
print_status "Stopping existing services..."
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $REMOTE_PATH
    docker-compose down --remove-orphans || true
"

# Build and start services
print_status "Building and starting services..."
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $REMOTE_PATH
    docker-compose build --no-cache
    docker-compose up -d
"

# Run database migrations
print_status "Running database migrations..."
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $REMOTE_PATH
    docker-compose exec -T backend alembic upgrade head
"

# Health check
print_status "Performing health check..."
sleep 10
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $REMOTE_PATH
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo 'Backend health check passed'
    else
        echo 'Backend health check failed'
        exit 1
    fi
"

# Show running services
print_status "Deployment completed! Running services:"
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $REMOTE_PATH
    docker-compose ps
"

print_status "🎉 Deployment to mac-mini-local completed successfully!"
echo ""
echo "Services available at:"
echo "- Backend API: http://mac-mini-local:8000"
echo "- Streamlit App: http://mac-mini-local:8501"
echo "- Next.js Dashboard: http://mac-mini-local:3000"
echo ""
echo "To check logs: ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && docker-compose logs -f'"
