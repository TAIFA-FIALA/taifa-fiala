#!/bin/bash

# Deploy Production Host Script - Fixed Version with Dependency Resolution
# This script runs all services natively on the production server
# Includes dependency conflict resolution and better error handling

set -e  # Exit on error

# Configuration
PROD_USER="jforrest"
PROD_SERVER="100.75.201.24"
PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"
DEV_WATCH_DIR="./data_ingestion_dev"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/Users/jforrest/production/backups/TAIFA-FIALA-${TIMESTAMP}"

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

echo -e "${GREEN}=== AI Africa Funding Tracker Host-Based Deployment (Fixed) ===${NC}"
echo -e "${YELLOW}Deploying services with dependency conflict resolution${NC}"

# Step 0: Pre-deployment checks and backup
step "Step 0: Pre-deployment Checks and Backup"

# Check if unified requirements exists
if [ ! -f "requirements-unified.txt" ]; then
    error "❌ requirements-unified.txt not found. Please run resolve_dependencies.py first."
    exit 1
fi

# Run dependency analysis
info "Running dependency conflict analysis..."
python3.12 resolve_dependencies.py
if [ $? -ne 0 ]; then
    warning "⚠ Dependency conflicts detected. Proceeding with unified requirements..."
fi

# Create backup on production server
ssh ${PROD_USER}@${PROD_SERVER} << EOF
    if [ -d "${PROD_DIR}" ]; then
        echo "Creating backup at ${BACKUP_DIR}..."
        mkdir -p $(dirname ${BACKUP_DIR})
        # Create backup excluding virtual environments and temporary files
        rsync -av --exclude='venv' --exclude='.venv' --exclude='__pycache__' \
              --exclude='node_modules' --exclude='.next' --exclude='logs' \
              --exclude='pids' "${PROD_DIR}/" "${BACKUP_DIR}/"
        echo "✓ Backup created successfully (excluding virtual environments)"
    fi
EOF

success "✓ Pre-deployment checks completed"

# Step 1: Verify prerequisites and sync files
step "Step 1: Syncing Files to Production Server"

# Copy files to production server
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '__pycache__' \
    --exclude 'venv' --exclude '.env' --exclude '.git' \
    ./ ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

# Copy the .env file separately
scp .env ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/
scp backend/.env ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/backend/ 2>/dev/null || true

# Copy unified requirements
scp requirements-unified.txt ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/
scp resolve_dependencies.py ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

success "✓ Files synced to production server"

# Step 2: Setup and start services on production server
step "Step 2: Setting up Host-Based Services with Dependency Resolution"

ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    # Set up environment
    export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH
    
    # Create directories for logs and PIDs early
    mkdir -p logs pids
    
    # Function to safely install requirements with conflict resolution
    install_requirements_safely() {
        local component=$1
        local venv_path=$2
        local requirements_file=$3
        
        echo "Installing requirements for $component..."
        
        # Find and use Python 3.12 specifically
        PYTHON312_CMD=""
        for cmd in python3.12 /usr/local/bin/python3.12 /opt/homebrew/bin/python3.12; do
            if command -v $cmd >/dev/null 2>&1; then
                VERSION=$($cmd --version 2>&1 | grep -o "3\.12" || echo "")
                if [ "$VERSION" = "3.12" ]; then
                    PYTHON312_CMD=$cmd
                    break
                fi
            fi
        done
        
        if [ -z "$PYTHON312_CMD" ]; then
            echo "❌ Python 3.12 not found for $component. Please install Python 3.12"
            return 1
        fi
        
        echo "Using Python 3.12: $PYTHON312_CMD for $component"
        # Create virtual environment
        $PYTHON312_CMD -m venv $venv_path 2>/dev/null || true
        source $venv_path/bin/activate
        
        # Upgrade pip and setuptools
        pip install --upgrade pip setuptools wheel
        
        # Try unified requirements first
        if [ -f "../requirements-unified.txt" ]; then
            echo "Using unified requirements for $component..."
            pip install --only-binary=pandas,numpy -r ../requirements-unified.txt --no-deps
            # Then install component-specific requirements to fill gaps
            if [ -f "$requirements_file" ]; then
                pip install --only-binary=pandas,numpy -r $requirements_file --upgrade
            fi
        else
            # Fallback to component requirements
            echo "Using component-specific requirements for $component..."
            pip install --only-binary=pandas,numpy -r $requirements_file
        fi
        
        # Verify critical imports
        python -c "
import sys
critical_packages = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'streamlit': 'streamlit',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'beautifulsoup4': 'bs4'
}
failed = []
for pkg_name, import_name in critical_packages.items():
    try:
        __import__(import_name)
        print(f'✓ {pkg_name} imported successfully')
    except ImportError as e:
        failed.append(pkg_name)
        print(f'✗ {pkg_name} import failed: {e}')

if failed:
    print(f'Failed imports: {failed}')
    sys.exit(1)
else:
    print('All critical packages imported successfully')
" || {
            echo "❌ Critical package import test failed for $component"
            return 1
        }
        
        echo "✓ Requirements installed successfully for $component"
        return 0
    }
    
    # Unlock keychain directly (no Docker issues!)
    echo "Unlocking keychain for host-based deployment..."
    STORED_PASSWORD=$(security find-generic-password -a "$USER" -s "docker-deployment" -w 2>/dev/null || echo "")
    if [ -n "$STORED_PASSWORD" ]; then
        security unlock-keychain -p "$STORED_PASSWORD" "$HOME/Library/Keychains/login.keychain-db" 2>/dev/null || true
        echo "✓ Keychain unlocked successfully"
    else
        echo "⚠ No stored keychain password found, continuing without unlock"
    fi
    
    # Stop any existing processes
    echo "Stopping existing services..."
    pkill -f "uvicorn.*taifa" 2>/dev/null || true
    pkill -f "streamlit.*run" 2>/dev/null || true
    pkill -f "next.*start" 2>/dev/null || true
    pkill -f "python.*file_watcher" 2>/dev/null || true
    sleep 3
    
    # Setup and start backend service
    echo "Setting up Python environment for backend..."
    cd backend
    if install_requirements_safely "backend" "venv" "requirements.txt"; then
        source venv/bin/activate
        echo "Starting FastAPI backend..."
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../pids/backend.pid
        echo "✓ Backend started (PID: $BACKEND_PID)"
    else
        echo "❌ Failed to setup backend environment"
        exit 1
    fi
    cd ..
    
    # Setup and start Streamlit
    echo "Setting up Streamlit dashboard..."
    cd frontend/streamlit_app
    
    # Create streamlit requirements if missing
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << 'STREAMLIT_REQ'
streamlit>=1.30.0,<1.40.0
requests==2.32.3
pandas==2.1.4
plotly==5.17.0
numpy==1.26.4
aiohttp==3.12.14
packaging>=24.2
STREAMLIT_REQ
    fi
    
    if install_requirements_safely "streamlit" "venv" "requirements.txt"; then
        source venv/bin/activate
        echo "Starting Streamlit dashboard..."
        nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../../logs/streamlit.log 2>&1 &
        STREAMLIT_PID=$!
        echo $STREAMLIT_PID > ../../pids/streamlit.pid
        echo "✓ Streamlit started (PID: $STREAMLIT_PID)"
    else
        echo "❌ Failed to setup Streamlit environment"
        exit 1
    fi
    cd ../..
    
    # Setup Next.js frontend
    echo "Setting up Next.js frontend..."
    cd frontend/nextjs
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo "⚠ package.json not found, skipping Next.js setup"
        cd ../..
    else
        npm install --legacy-peer-deps
        npm run build
        
        echo "Starting Next.js frontend..."
        nohup bash -c "export PATH=/usr/local/bin:$PATH && PORT=3030 npm start" > ../../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../../pids/frontend.pid
        echo "✓ Frontend started (PID: $FRONTEND_PID)"
        cd ../..
    fi
    
    # Setup file watcher
    echo "Setting up file watcher..."
    cd data_processors
    if install_requirements_safely "data_processors" "venv" "requirements.txt"; then
        source venv/bin/activate
        echo "Starting file watcher..."
        export PYTHONPATH=/Users/jforrest/production/TAIFA-FIALA
        export DATA_INGESTION_PATH=/Users/jforrest/production/TAIFA-FIALA/data_ingestion
        
        # Check if file_watcher.py exists
        if [ -f "file_watcher.py" ]; then
            nohup python file_watcher.py > ../logs/file_watcher.log 2>&1 &
            WATCHER_PID=$!
            echo $WATCHER_PID > ../pids/file_watcher.pid
            echo "✓ File watcher started (PID: $WATCHER_PID)"
        else
            echo "⚠ file_watcher.py not found, skipping file watcher"
        fi
    else
        echo "❌ Failed to setup data processors environment"
    fi
    cd ..
    
    echo "✓ All services started successfully"
    
    # Show running processes
    echo "Running services:"
    echo "Backend (PID: $(cat pids/backend.pid 2>/dev/null || echo 'N/A'))"
    echo "Streamlit (PID: $(cat pids/streamlit.pid 2>/dev/null || echo 'N/A'))"
    echo "Frontend (PID: $(cat pids/frontend.pid 2>/dev/null || echo 'N/A'))"
    echo "File Watcher (PID: $(cat pids/file_watcher.pid 2>/dev/null || echo 'N/A'))"
EOF

# Step 3: Health check with retry logic
step "Step 3: Performing Health Check with Retry Logic"
info "Waiting for services to initialize..."
sleep 20

# Function to test endpoint with retries
test_endpoint() {
    local url=$1
    local service_name=$2
    local max_retries=5
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl --silent --fail --max-time 10 "$url" > /dev/null; then
            success "✓ $service_name is healthy and responding"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                warning "⚠ $service_name health check failed (attempt $retry_count/$max_retries), retrying..."
                sleep 10
            fi
        fi
    done
    
    error "❌ $service_name health check failed after $max_retries attempts"
    return 1
}

info "Testing HTTP endpoints..."

# Test FastAPI backend
test_endpoint "http://100.75.201.24:8030/health" "Backend"

# Test Streamlit dashboard
test_endpoint "http://100.75.201.24:8501" "Streamlit dashboard"

# Test Next.js frontend
test_endpoint "http://100.75.201.24:3030" "Frontend"

# Step 4: Create improved management scripts
step "Step 4: Creating Improved Management Scripts"

ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    # Create enhanced restart script
    cat > restart_services_host.sh << 'RESTART_EOF'
#!/bin/bash

# AI Africa Funding Tracker - Enhanced Host-Based Restart Script
cd $(dirname $0)

echo "=== Restarting AI Africa Funding Tracker Services ==="

# Function to stop service safely
stop_service() {
    local service=$1
    local pid_file="pids/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service (PID: $pid)..."
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force stopping $service..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$pid_file"
    fi
}

# Stop all services
stop_service "backend"
stop_service "streamlit" 
stop_service "frontend"
stop_service "file_watcher"

sleep 5

echo "Starting services..."

# Backend
if [ -d "backend" ]; then
    cd backend && source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload > ../logs/backend.log 2>&1 &
    echo $! > ../pids/backend.pid
    echo "✓ Backend restarted (PID: $!)"
    cd ..
fi

# Streamlit
if [ -d "frontend/streamlit_app" ]; then
    cd frontend/streamlit_app && source venv/bin/activate
    nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../../logs/streamlit.log 2>&1 &
    echo $! > ../../pids/streamlit.pid
    echo "✓ Streamlit restarted (PID: $!)"
    cd ../..
fi

# Frontend
if [ -d "frontend/nextjs" ] && [ -f "frontend/nextjs/package.json" ]; then
    cd frontend/nextjs
    nohup bash -c "export PATH=/usr/local/bin:$PATH && PORT=3030 npm start" > ../../logs/frontend.log 2>&1 &
    echo $! > ../../pids/frontend.pid
    echo "✓ Frontend restarted (PID: $!)"
    cd ../..
fi

# File watcher
if [ -d "data_processors" ] && [ -f "data_processors/file_watcher.py" ]; then
    cd data_processors && source venv/bin/activate
    export PYTHONPATH=/Users/jforrest/production/TAIFA-FIALA
    export DATA_INGESTION_PATH=/Users/jforrest/production/TAIFA-FIALA/data_ingestion
    nohup python file_watcher.py > ../logs/file_watcher.log 2>&1 &
    echo $! > ../pids/file_watcher.pid
    echo "✓ File watcher restarted (PID: $!)"
    cd ..
fi

echo "✓ All services restarted successfully"
RESTART_EOF

    chmod +x restart_services_host.sh
    
    # Create enhanced stop script
    cat > stop_services_host.sh << 'STOP_EOF'
#!/bin/bash

# AI Africa Funding Tracker - Enhanced Host-Based Stop Script
cd $(dirname $0)

echo "=== Stopping AI Africa Funding Tracker Services ==="

# Function to stop service safely
stop_service() {
    local service=$1
    local pid_file="pids/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service (PID: $pid)..."
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force stopping $service..."
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo "✓ $service stopped"
        else
            echo "⚠ $service was not running"
        fi
        rm -f "$pid_file"
    else
        echo "⚠ No PID file found for $service"
    fi
}

# Stop all services
stop_service "backend"
stop_service "streamlit"
stop_service "frontend" 
stop_service "file_watcher"

echo "✓ All services stopped successfully"
STOP_EOF

    chmod +x stop_services_host.sh
    
    # Create status check script
    cat > check_services_status.sh << 'STATUS_EOF'
#!/bin/bash

# AI Africa Funding Tracker - Service Status Check
cd $(dirname $0)

echo "=== AI Africa Funding Tracker Service Status ==="

check_service() {
    local service=$1
    local port=$2
    local pid_file="pids/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✓ $service is running (PID: $pid)"
            if [ -n "$port" ]; then
                if curl --silent --fail --max-time 5 "http://localhost:$port" > /dev/null 2>&1; then
                    echo "  └─ HTTP endpoint responding on port $port"
                else
                    echo "  └─ ⚠ HTTP endpoint not responding on port $port"
                fi
            fi
        else
            echo "❌ $service is not running (stale PID file)"
        fi
    else
        echo "❌ $service is not running (no PID file)"
    fi
}

check_service "backend" "8030"
check_service "streamlit" "8501"
check_service "frontend" "3030"
check_service "file_watcher"

echo ""
echo "Log files:"
ls -la logs/ 2>/dev/null || echo "No log files found"
STATUS_EOF

    chmod +x check_services_status.sh
EOF

success "✓ Enhanced management scripts created"

echo
success "=== Enhanced Host-Based Deployment Complete ==="
info "Deployment completed at: $(date)"
echo
warning "Services running on:"
warning "Backend FastAPI: http://100.75.201.24:8030"
warning "Streamlit Dashboard: http://100.75.201.24:8501"
warning "API Documentation: http://100.75.201.24:8030/docs"
warning "Next.js Frontend: http://100.75.201.24:3030"
echo
info "Management commands:"
echo "Restart services: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && ./restart_services_host.sh'"
echo "Stop services: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && ./stop_services_host.sh'"
echo "Check status: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && ./check_services_status.sh'"
echo "View logs: ssh ${PROD_USER}@${PROD_SERVER} 'cd ${PROD_DIR} && tail -f logs/<service>.log'"
echo "Rollback: ssh ${PROD_USER}@${PROD_SERVER} 'rm -rf ${PROD_DIR} && mv ${BACKUP_DIR} ${PROD_DIR}'"

echo
info "Dependency Management:"
echo "Run conflict analysis: python3.12 resolve_dependencies.py"
echo "Unified requirements: requirements-unified.txt"

echo
info "File Ingestion:"
echo "Local watch directory: ${DEV_WATCH_DIR}"
echo "Remote watch directory: ${PROD_DIR}/data_ingestion"
echo "To add files for processing:"
echo "1. Place files in ${DEV_WATCH_DIR}/inbox/"
echo "2. Files will be automatically synced to production"
echo "3. Check ${DEV_WATCH_DIR}/logs/ for processing logs"