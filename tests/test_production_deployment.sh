#!/bin/bash

# Test Production Deployment Script
# This script tests the deployment process directly on the production server
# where the actual dependency conflicts are occurring

set -e

# Configuration
PROD_USER="jforrest"
PROD_SERVER="100.75.201.24"
PROD_DIR="/Users/jforrest/production/TAIFA-FIALA"
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

echo -e "${GREEN}=== Testing Production Deployment on Host Server ===${NC}"
echo -e "${YELLOW}This will test dependency resolution directly on your production server${NC}"

# Step 1: Sync test files to production
step "Step 1: Syncing Test Files to Production Server"

# Copy test files to production server
rsync -avz requirements-unified.txt resolve_dependencies.py test_deployment.py \
    ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

success "✓ Test files synced to production server"

# Step 2: Run dependency analysis on production server
step "Step 2: Running Dependency Analysis on Production Server"

ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    # Set up environment
    export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH
    
    # Find Python 3.12
    PYTHON_CMD=""
    for cmd in python3.12 python3 python; do
        if command -v $cmd >/dev/null 2>&1; then
            VERSION=$($cmd --version 2>&1 | grep -o "3\.12" || echo "")
            if [ "$VERSION" = "3.12" ]; then
                PYTHON_CMD=$cmd
                break
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        echo "❌ Python 3.12 not found on production server"
        echo "Available Python versions:"
        for cmd in python3.12 python3 python; do
            if command -v $cmd >/dev/null 2>&1; then
                echo "  $cmd: $($cmd --version 2>&1)"
            fi
        done
        exit 1
    fi
    
    echo "Using Python: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"
    echo "Running dependency conflict analysis on production server..."
    $PYTHON_CMD resolve_dependencies.py
    
    echo ""
    echo "=== Dependency Analysis Results ==="
    cat dependency_report.txt
EOF

# Step 3: Test requirements installation on production server
step "Step 3: Testing Requirements Installation on Production Server"

ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    # Set up environment
    export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH
    
    # Find Python 3.12
    PYTHON_CMD=""
    for cmd in python3.12 python3 python; do
        if command -v $cmd >/dev/null 2>&1; then
            VERSION=$($cmd --version 2>&1 | grep -o "3\.12" || echo "")
            if [ "$VERSION" = "3.12" ]; then
                PYTHON_CMD=$cmd
                break
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        echo "❌ Python 3.12 not found on production server"
        exit 1
    fi
    
    echo "Testing requirements installation on production server..."
    echo "Using Python: $PYTHON_CMD"
    
    # Function to test component requirements
    test_component_requirements() {
        local component=$1
        local requirements_file=$2
        local test_dir="test_env_${component}_$(date +%s)"
        
        echo "Testing $component requirements..."
        
        # Create test environment
        $PYTHON_CMD -m venv $test_dir
        source $test_dir/bin/activate
        
        # Upgrade pip
        pip install --upgrade pip setuptools wheel
        
        # Test unified requirements first
        echo "  Testing unified requirements..."
        if pip install -r requirements-unified.txt --no-deps; then
            echo "  ✓ Unified requirements installed successfully"
        else
            echo "  ❌ Unified requirements installation failed"
            deactivate
            rm -rf $test_dir
            return 1
        fi
        
        # Test component-specific requirements
        if [ -f "$requirements_file" ]; then
            echo "  Testing component-specific requirements..."
            if pip install -r $requirements_file --upgrade; then
                echo "  ✓ Component requirements installed successfully"
            else
                echo "  ❌ Component requirements installation failed"
                deactivate
                rm -rf $test_dir
                return 1
            fi
        fi
        
        # Test critical imports
        echo "  Testing critical imports..."
        case $component in
            "backend")
                python -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('✓ Backend imports successful')" || {
                    echo "  ❌ Backend imports failed"
                    deactivate
                    rm -rf $test_dir
                    return 1
                }
                ;;
            "streamlit_app")
                python -c "import streamlit, pandas, numpy, plotly; print('✓ Streamlit imports successful')" || {
                    echo "  ❌ Streamlit imports failed"
                    deactivate
                    rm -rf $test_dir
                    return 1
                }
                ;;
            "data_processors")
                python -c "import pandas, numpy, aiohttp, beautifulsoup4; print('✓ Data processors imports successful')" || {
                    echo "  ❌ Data processors imports failed"
                    deactivate
                    rm -rf $test_dir
                    return 1
                }
                ;;
        esac
        
        # Cleanup
        deactivate
        rm -rf $test_dir
        echo "  ✓ $component test completed successfully"
        return 0
    }
    
    # Test each component
    echo ""
    echo "=== Component Testing Results ==="
    
    test_component_requirements "backend" "backend/requirements.txt"
    BACKEND_RESULT=$?
    
    test_component_requirements "streamlit_app" "frontend/streamlit_app/requirements.txt"
    STREAMLIT_RESULT=$?
    
    test_component_requirements "data_processors" "data_processors/requirements.txt"
    DATA_PROCESSORS_RESULT=$?
    
    echo ""
    echo "=== Test Summary ==="
    [ $BACKEND_RESULT -eq 0 ] && echo "✓ Backend: PASSED" || echo "❌ Backend: FAILED"
    [ $STREAMLIT_RESULT -eq 0 ] && echo "✓ Streamlit: PASSED" || echo "❌ Streamlit: FAILED"
    [ $DATA_PROCESSORS_RESULT -eq 0 ] && echo "✓ Data Processors: PASSED" || echo "❌ Data Processors: FAILED"
    
    TOTAL_FAILED=$((3 - (3 - $BACKEND_RESULT - $STREAMLIT_RESULT - $DATA_PROCESSORS_RESULT)))
    if [ $TOTAL_FAILED -eq 0 ]; then
        echo ""
        echo "🎉 All tests passed on production server!"
        echo "Ready for deployment with ./deploy_production_host_fixed.sh"
    else
        echo ""
        echo "⚠ $TOTAL_FAILED test(s) failed on production server"
        echo "Review the errors above before proceeding with deployment"
    fi
EOF

# Step 4: Test deployment script syntax on production server
step "Step 4: Testing Deployment Script Syntax on Production Server"

# Copy deployment script to production server
scp deploy_production_host_fixed.sh ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

ssh ${PROD_USER}@${PROD_SERVER} << 'EOF'
    cd /Users/jforrest/production/TAIFA-FIALA
    
    echo "Testing deployment script syntax..."
    if bash -n deploy_production_host_fixed.sh; then
        echo "✓ Deployment script syntax is valid"
    else
        echo "❌ Deployment script has syntax errors"
    fi
    
    # Make script executable
    chmod +x deploy_production_host_fixed.sh
    echo "✓ Deployment script is now executable"
EOF

success "✓ Production deployment testing completed"

echo
info "=== Next Steps ==="
echo "1. Review the test results above"
echo "2. If all tests passed, run: ./deploy_production_host_fixed.sh"
echo "3. If tests failed, check the specific error messages and resolve them"
echo "4. Monitor the deployment with the provided management scripts"

echo
warning "Production Server Access:"
echo "SSH: ssh ${PROD_USER}@${PROD_SERVER}"
echo "Project Dir: ${PROD_DIR}"
echo "Logs: ${PROD_DIR}/logs/"