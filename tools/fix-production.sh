#!/bin/bash

# Robust production fix script for TAIFA-FIALA
echo "🔧 Fixing TAIFA-FIALA production services..."

# Deploy to production with proper environment setup
ssh jforrest@100.75.201.24 << 'EOF'
cd /Users/jforrest/production/TAIFA-FIALA

echo "🛑 Stopping all conflicting services..."
# Stop any conflicting services
pkill -f "uvicorn\|npm.*start\|next.*start\|n8n" || true
sleep 5

echo "🔄 Setting up environment..."
# Set up proper PATH with pyenv and npm
export PATH="$HOME/.pyenv/shims:/usr/local/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "📦 Installing backend dependencies..."
# Install Python dependencies with pyenv
python3 -m pip install -r requirements.txt

echo "🌐 Setting up frontend..."
# Install frontend dependencies
cd frontend/nextjs
npm install
npm run build
cd ../..

echo "🚀 Starting backend service..."
# Create logs directory
mkdir -p logs

# Start backend with proper environment loading
cd backend
# Load environment variables properly
set -a
source ../.env
set +a
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8030 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
cd ..

echo "🎨 Starting frontend service..."
# Start frontend
cd frontend/nextjs
nohup npm start > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
cd ../..

echo "⏳ Waiting for services to start..."
sleep 20

echo "🔍 Checking service health..."
# Check backend health
if curl -f http://localhost:8030/health >/dev/null 2>&1; then
    echo "✅ Backend health check: PASSED"
else
    echo "❌ Backend health check: FAILED"
    echo "Backend logs:"
    tail -10 logs/backend.log
fi

# Check frontend
if curl -f http://localhost:3030 >/dev/null 2>&1; then
    echo "✅ Frontend health check: PASSED"
else
    echo "❌ Frontend health check: FAILED"
    echo "Frontend logs:"
    tail -10 logs/frontend.log
fi

echo "📊 Current running processes:"
ps aux | grep -E "(uvicorn|npm)" | grep -v grep

echo "🎉 Production fix complete!"
EOF

echo "🌐 Check your site: https://taifa-fiala.net"
