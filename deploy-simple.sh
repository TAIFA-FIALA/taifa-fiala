#!/bin/bash

# Simple deployment script to fix production services
echo "🚀 Deploying TAIFA-FIALA to production..."

# Copy .env file to production
echo "📄 Copying .env file..."
scp -o Ciphers=aes256-gcm@openssh.com .env jforrest@100.75.201.24:/Users/jforrest/production/TAIFA-FIALA/

# Deploy and restart services on production
echo "🔄 Restarting services on production..."
ssh -T -o Ciphers=aes256-gcm@openssh.com jforrest@100.75.201.24 << 'EOF'
cd /Users/jforrest/production/TAIFA-FIALA

# Set up pyenv environment
export PATH="$HOME/.pyenv/shims:$PATH"

# Set up Node.js/nvm environment
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# Use specific Node.js version or fallback to available version
nvm use v20.19.0 2>/dev/null || nvm use node || echo "⚠️ nvm not available, using system node"
# Add npm to PATH explicitly
export PATH="$HOME/.nvm/versions/node/v20.19.0/bin:$PATH"

# Check and kill processes on ports 8030 and 3000/3030
echo "🔍 Checking for processes on ports 8030 and 3030..."

# Function to kill process on a specific port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "⚠️ Found process on port $port (PID: $pid), killing it..."
        kill -9 $pid || true
        sleep 2
        # Verify it's gone
        local check_pid=$(lsof -ti:$port)
        if [ ! -z "$check_pid" ]; then
            echo "❌ Failed to kill process on port $port"
        else
            echo "✅ Successfully killed process on port $port"
        fi
    else
        echo "✅ Port $port is free"
    fi
}

# Kill processes on required ports
kill_port 8030
kill_port 3030

# Stop existing services (fallback) 
pkill -f "uvicorn\|npm.*start\|next.*start" || true

# Clean up any remaining backend processes
pkill -f "python.*uvicorn" || true
pkill -f "start_backend.sh" || true

sleep 5

echo "🧹 Cleaning up old SSE connections..."

# Sync latest changes from local to production
echo "📤 Syncing local changes to production..."
rsync -avz -e "ssh -o Ciphers=aes256-gcm@openssh.com" --exclude='.git' --exclude='node_modules' --exclude='venv' --exclude='.next' --exclude='logs' --exclude='*.log' /Users/drjforrest/dev/devprojects/ai-africa-funding-tracker/ jforrest@100.75.201.24:/Users/jforrest/production/TAIFA-FIALA/

# Install Python dependencies
/usr/local/bin/uv run pip install -r requirements.txt

# Install frontend dependencies and build
cd frontend/nextjs
npm install
# Clean build to ensure latest changes are included
rm -rf .next
npm run build
cd ../..

# Create logs directory
mkdir -p logs

# Start backend with environment variables
cd backend
# Export environment variables safely
set -a  # automatically export all variables
source ../.env
export ENVIRONMENT=production
set +a  # stop automatically exporting

# Debug: verify key environment variables are loaded
echo "🔍 Environment variables check:"
echo "SUPABASE_URL: ${SUPABASE_URL:0:30}..." 
echo "SUPABASE_PROJECT_URL: ${SUPABASE_PROJECT_URL:0:30}..." 
echo "ENVIRONMENT: $ENVIRONMENT"

# Create a wrapper script with environment variables
cat > start_backend.sh << 'SCRIPT_EOF'
#!/bin/bash
export SUPABASE_URL="https://turcbnsgdlyelzmcqixd.supabase.co"
export SUPABASE_PROJECT_URL="https://turcbnsgdlyelzmcqixd.supabase.co"
export SUPABASE_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1cmNibnNnZGx5ZWx6bWNxaXhkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjY1NzQ4OCwiZXhwIjoyMDY4MjMzNDg4fQ.Vdn2zHMhQ2V6rJf-MazNX1wxXJknnYighekkruEXMrA"
export ENVIRONMENT="production"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8030
SCRIPT_EOF

chmod +x start_backend.sh
nohup ./start_backend.sh > ../logs/backend.log 2>&1 &
cd ..

# Start frontend on port 3030
cd frontend/nextjs
nohup npm start -- -p 3030 > ../../logs/frontend.log 2>&1 &
cd ../..

# Wait for services to start
sleep 15

# Check health
echo "🔍 Checking service health..."
echo "Backend process check:"
ps aux | grep "uvicorn\|python.*main" | grep -v grep || echo "❌ No backend process found"

echo "Port 8030 check:"
netstat -tlnp | grep :8030 || echo "❌ Port 8030 not listening"

echo "Testing backend endpoints:"
curl -f http://localhost:8030/health && echo "✅ Backend health OK" || echo "❌ Backend health FAILED"
curl -f http://localhost:8030/ && echo "✅ Backend root OK" || echo "❌ Backend root FAILED" 
curl -f http://localhost:8030/api/v1/events/stream --max-time 5 && echo "✅ SSE endpoint OK" || echo "❌ SSE endpoint FAILED"

echo "Frontend process check:"
ps aux | grep "npm.*start\|next.*start" | grep -v grep || echo "❌ No frontend process found"

echo "Port 3030 check:"
netstat -tlnp | grep :3030 || echo "❌ Port 3030 not listening"

curl -f http://localhost:3030 && echo "✅ Frontend OK" || echo "❌ Frontend FAILED"

echo "✅ Deployment complete!"
EOF

echo "🌐 Check your site: https://taifa-fiala.net"
