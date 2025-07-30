#!/bin/bash

# Simple deployment script to fix production services
echo "🚀 Deploying TAIFA-FIALA to production..."

# Copy .env file to production
echo "📄 Copying .env file..."
scp .env jforrest@100.75.201.24:/Users/jforrest/production/TAIFA-FIALA/

# Deploy and restart services on production
echo "🔄 Restarting services on production..."
ssh jforrest@100.75.201.24 << 'EOF'
cd /Users/jforrest/production/TAIFA-FIALA

# Set up pyenv environment
export PATH="$HOME/.pyenv/shims:$PATH"

# Stop existing services
pkill -f "uvicorn\|npm.*start\|next.*start" || true
sleep 5

# Pull latest changes
git pull org-origin main

# Install Python dependencies
python3 -m pip install -r requirements.txt

# Install frontend dependencies and build
cd frontend/nextjs
npm install
npm run build
cd ../..

# Create logs directory
mkdir -p logs

# Start backend with environment variables
cd backend
export $(cat ../.env | xargs)
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8030 > ../logs/backend.log 2>&1 &
cd ..

# Start frontend
cd frontend/nextjs
nohup npm start > ../../logs/frontend.log 2>&1 &
cd ../..

# Wait for services to start
sleep 15

# Check health
echo "🔍 Checking service health..."
curl -f http://localhost:8030/health && echo "✅ Backend OK" || echo "❌ Backend FAILED"
curl -f http://localhost:3030 && echo "✅ Frontend OK" || echo "❌ Frontend FAILED"

echo "✅ Deployment complete!"
EOF

echo "🌐 Check your site: https://taifa-fiala.net"
