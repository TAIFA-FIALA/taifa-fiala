#!/bin/bash

# TAIFA-FIALA Initial Frontend Push Script
# This script does the initial push of frontend code to the separate repository

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_REPO_URL="git@github.com:TAIFA-FIALA/taifa-fiala-frontend.git"
FRONTEND_DIR="frontend/nextjs_dashboard"
TEMP_DIR="/tmp/taifa-frontend-push"

echo -e "${GREEN}=== TAIFA-FIALA Initial Frontend Push ===${NC}"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Create temporary directory
echo -e "${YELLOW}Creating temporary directory...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy frontend files
echo -e "${YELLOW}Copying frontend files...${NC}"
cp -r "$FRONTEND_DIR/"* "$TEMP_DIR/" 2>/dev/null || true
cp -r "$FRONTEND_DIR/".[!.]* "$TEMP_DIR/" 2>/dev/null || true

# Navigate to temp directory
cd "$TEMP_DIR"

# Create README for frontend repo
echo -e "${YELLOW}Creating frontend README...${NC}"
cat > README.md << 'EOF'
# TAIFA-FIALA Frontend

Next.js application for the TAIFA-FIALA AI Africa Funding Intelligence System.

## Quick Start

```bash
npm install
npm run dev
```

## Deployment

This repository is automatically deployed to Vercel when changes are pushed to main.

## Sync

This repository is synced from the main TAIFA-FIALA repository.
Changes should be made in the main repository and synced using the sync script.
EOF

# Initialize git and push
echo -e "${YELLOW}Initializing git repository...${NC}"
git init
git add .
git commit -m "Initial commit: TAIFA-FIALA Frontend

Frontend application for AI Africa Funding Intelligence System.
Synced from main repository on $(date '+%Y-%m-%d %H:%M:%S')"

echo -e "${YELLOW}Adding remote and pushing...${NC}"
git branch -M main
git remote add origin "$FRONTEND_REPO_URL"
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend successfully pushed to separate repository${NC}"
    echo
    echo -e "${GREEN}=== Success! ===${NC}"
    echo -e "${BLUE}Frontend repository: $FRONTEND_REPO_URL${NC}"
    echo -e "${BLUE}Repository is ready for Vercel deployment${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Go to https://vercel.com/new"
    echo "2. Import: $FRONTEND_REPO_URL" 
    echo "3. Configure environment variables"
    echo "4. Future syncs: ./sync_frontend.sh"
    
    # Clean up
    echo -e "${YELLOW}Cleaning up temporary directory...${NC}"
    rm -rf "$TEMP_DIR"
    
else
    echo -e "${RED}Error: Failed to push to frontend repository${NC}"
    echo -e "${YELLOW}Check that the repository exists and you have push access${NC}"
    echo -e "${BLUE}Temp files available at: $TEMP_DIR${NC}"
    exit 1
fi