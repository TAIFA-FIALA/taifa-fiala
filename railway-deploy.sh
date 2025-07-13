#!/bin/bash

# TAIFA-FIALA Railway Quick Deployment Script
# Automates the deployment process to Railway

set -e

echo "🚄 TAIFA-FIALA Railway Deployment Script"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI is not installed${NC}"
    echo "Install it with: npm install -g @railway/cli"
    exit 1
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway${NC}"
    echo "Please login with: railway login"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"

# Project setup
echo -e "${BLUE}🚀 Setting up Railway project...${NC}"

# Check if we're in a Railway project
if ! railway status &> /dev/null; then
    echo "Creating new Railway project..."
    railway init taifa-fiala-production
else
    echo "Using existing Railway project"
fi

echo -e "${GREEN}✅ Railway project ready${NC}"

# Environment variables setup
echo -e "${BLUE}🔧 Setting up environment variables...${NC}"

# Function to safely set environment variable
set_env_var() {
    local service=$1
    local key=$2
    local value=$3
    
    if [ -n "$value" ]; then
        echo "Setting $key for $service..."
        railway variables:set $key="$value" --service $service
    else
        echo -e "${YELLOW}⚠️  $key not provided for $service${NC}"
    fi
}

# Collect required environment variables
echo "Please provide the following environment variables:"

read -p "SERPER_DEV_API_KEY (required): " SERPER_KEY
read -p "OPENAI_API_KEY (recommended): " OPENAI_KEY
read -p "N8N_WEBHOOK_URL (optional): " N8N_WEBHOOK
read -p "SMTP_USER (optional): " SMTP_USER
read -s -p "SMTP_PASSWORD (optional): " SMTP_PASS
echo ""

# Generate secret key
SECRET_KEY=$(openssl rand -base64 32)

echo -e "${BLUE}📦 Deploying services...${NC}"

# Deploy PostgreSQL Database
echo -e "${BLUE}🗄️  Setting up PostgreSQL database...${NC}"
railway add postgresql
echo "Waiting for database to be ready..."
sleep 10

# Deploy Backend Service
echo -e "${BLUE}⚙️  Deploying FastAPI backend...${NC}"

# Set backend environment variables
railway variables:set ENVIRONMENT=production --service backend
railway variables:set DEBUG=false --service backend
railway variables:set LOG_LEVEL=INFO --service backend
railway variables:set SECRET_KEY="$SECRET_KEY" --service backend
railway variables:set DATABASE_URL='${{Postgres.DATABASE_URL}}' --service backend

# Set API keys
if [ -n "$SERPER_KEY" ]; then
    railway variables:set SERPER_DEV_API_KEY="$SERPER_KEY" --service backend
fi

if [ -n "$OPENAI_KEY" ]; then
    railway variables:set OPENAI_API_KEY="$OPENAI_KEY" --service backend
fi

# Set CORS origins
railway variables:set BACKEND_CORS_ORIGINS='["https://taifa-africa.com","https://fiala-afrique.com","https://taifa-fiala.net"]' --service backend

# Deploy backend
railway up backend --detach

# Deploy Frontend Service
echo -e "${BLUE}🖥️  Deploying Next.js frontend...${NC}"

# Set frontend environment variables
railway variables:set NODE_ENV=production --service frontend
railway variables:set NEXT_PUBLIC_API_URL=https://api.taifa-fiala.net --service frontend
railway variables:set NEXT_PUBLIC_APP_URL=https://taifa-africa.com --service frontend
railway variables:set NEXT_TELEMETRY_DISABLED=1 --service frontend

# Deploy frontend
railway up frontend/nextjs_dashboard --detach

# Deploy Data Collection Service
echo -e "${BLUE}📊 Deploying data collection service...${NC}"

# Set data collector environment variables
railway variables:set ENVIRONMENT=production --service data_collectors
railway variables:set DATABASE_URL='${{Postgres.DATABASE_URL}}' --service data_collectors

if [ -n "$SERPER_KEY" ]; then
    railway variables:set SERPER_DEV_API_KEY="$SERPER_KEY" --service data_collectors
fi

if [ -n "$N8N_WEBHOOK" ]; then
    railway variables:set N8N_WEBHOOK_URL="$N8N_WEBHOOK" --service data_collectors
fi

# Deploy data collector
railway up data_collectors --detach

echo -e "${BLUE}⏳ Waiting for services to deploy...${NC}"
sleep 30

# Run database migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
railway run ./railway-migrate.sh --service backend

# Get service URLs
echo -e "${BLUE}📋 Getting service information...${NC}"

BACKEND_URL=$(railway domain --service backend 2>/dev/null || echo "Not assigned")
FRONTEND_URL=$(railway domain --service frontend 2>/dev/null || echo "Not assigned")
COLLECTOR_URL=$(railway domain --service data_collectors 2>/dev/null || echo "Not assigned")

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "📊 Service URLs:"
echo "  Backend:    $BACKEND_URL"
echo "  Frontend:   $FRONTEND_URL"  
echo "  Collector:  $COLLECTOR_URL"
echo ""

# Domain configuration instructions
echo -e "${YELLOW}🌐 Next Steps - Domain Configuration:${NC}"
echo ""
echo "1. Configure your DNS records:"
echo "   taifa-africa.com    CNAME → your-frontend.up.railway.app"
echo "   fiala-afrique.com   CNAME → your-frontend.up.railway.app"
echo "   api.taifa-fiala.net CNAME → your-backend.up.railway.app"
echo ""
echo "2. Add custom domains in Railway:"
echo "   railway domain:add taifa-africa.com --service frontend"
echo "   railway domain:add fiala-afrique.com --service frontend"
echo "   railway domain:add api.taifa-fiala.net --service backend"
echo ""

# Health check
echo -e "${BLUE}🏥 Running health checks...${NC}"

# Check backend health
if [ "$BACKEND_URL" != "Not assigned" ]; then
    echo "Testing backend health..."
    if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend health check failed (may need time to start)${NC}"
    fi
fi

# Check frontend
if [ "$FRONTEND_URL" != "Not assigned" ]; then
    echo "Testing frontend..."
    if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend check failed (may need time to build)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🚀 TAIFA-FIALA is now deployed on Railway!${NC}"
echo ""
echo "📖 For detailed configuration, see: RAILWAY_DEPLOYMENT.md"
echo "🔧 To monitor services: railway status"
echo "📝 To view logs: railway logs --service <service_name>"
echo ""
echo -e "${BLUE}Happy funding discovery! 🌍${NC}"
