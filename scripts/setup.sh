#!/bin/bash

# Quick setup script for AI Africa Funding Tracker
# Sets up the development environment and tests connections

set -e

echo "🚀 AI Africa Funding Tracker - Quick Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Must be run from project root directory"
    exit 1
fi

# Function to print colored output
print_success() {
    echo -e "\033[0;32m✅ $1\033[0m"
}

print_info() {
    echo -e "\033[0;34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[0;31m❌ $1\033[0m"
}

# Step 1: Check dependencies
print_info "Checking dependencies..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_success "All dependencies are available"

# Step 2: Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found, copying from .env.example"
    cp .env.example .env
    print_info "Please edit .env file with your configuration if needed"
fi

# Step 3: Test database connection
print_info "Testing database connection to TAIFA_db..."
cd backend
python3 -c "
import sys
sys.path.append('.')
from app.core.database import test_connection
if not test_connection():
    print('Database connection failed')
    sys.exit(1)
print('Database connection successful')
"

if [ $? -eq 0 ]; then
    print_success "Database connection test passed"
else
    print_error "Database connection failed"
    print_info "Make sure:"
    print_info "1. PostgreSQL is running on mac-mini"
    print_info "2. Tailscale is connected"
    print_info "3. TAIFA_db exists with correct credentials"
    exit 1
fi

cd ..

# Step 4: Initialize database tables
print_info "Initializing database tables..."
cd scripts
python3 init_db.py

if [ $? -eq 0 ]; then
    print_success "Database initialization completed"
else
    print_error "Database initialization failed"
    exit 1
fi

cd ..

# Step 5: Install Python dependencies for local development
print_info "Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt &> /dev/null

if [ $? -eq 0 ]; then
    print_success "Backend dependencies installed"
else
    print_warning "Some backend dependencies may have failed to install"
fi

cd ../frontend/streamlit_app
pip3 install -r requirements.txt &> /dev/null

if [ $? -eq 0 ]; then
    print_success "Frontend dependencies installed"
else
    print_warning "Some frontend dependencies may have failed to install"
fi

cd ../..

# Success message
echo
print_success "🎉 Setup completed successfully!"
echo
echo "Ready to start development!"
echo
echo "Quick start options:"
echo
echo "1. 🐳 Start with Docker (recommended):"
echo "   docker-compose up -d"
echo
echo "2. 🐍 Start manually:"
echo "   Backend:   cd backend && uvicorn app.main:app --reload"
echo "   Frontend:  cd frontend/streamlit_app && streamlit run app.py"
echo
echo "3. 📊 Access the applications:"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Streamlit App:     http://localhost:8501"
echo
echo "4. 🔧 Test database connection anytime:"
echo "   python3 scripts/test_db_connection.py"
echo
print_info "Happy coding! 🚀"
