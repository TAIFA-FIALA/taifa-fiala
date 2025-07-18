#!/bin/bash

# TAIFA-FIALA Simple Frontend Sync Script
# This script syncs frontend changes to the separate repository

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_REPO_URL="git@github.com:TAIFA-FIALA/taifa-fiala-frontend.git"
FRONTEND_DIR="frontend/nextjs_dashboard"
TEMP_DIR="/tmp/taifa-frontend-sync-$(date +%s)"

echo -e "${GREEN}=== TAIFA-FIALA Frontend Sync ===${NC}"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Get current branch and commit info
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)

echo -e "${BLUE}Syncing from branch: ${CURRENT_BRANCH} (${CURRENT_COMMIT})${NC}"

# Check for uncommitted changes in frontend
if [ -n "$(git status --porcelain $FRONTEND_DIR)" ]; then
    echo -e "${YELLOW}Warning: Uncommitted changes in frontend directory${NC}"
    git status --porcelain "$FRONTEND_DIR"
    echo
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Sync cancelled. Please commit your changes.${NC}"
        exit 1
    fi
fi

# Create temporary directory
echo -e "${YELLOW}Creating temporary directory...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Clone the frontend repository
echo -e "${YELLOW}Cloning frontend repository...${NC}"
git clone "$FRONTEND_REPO_URL" "$TEMP_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to clone frontend repository${NC}"
    exit 1
fi

# Navigate to temp directory
cd "$TEMP_DIR"

# Remove all existing files (except .git)
echo -e "${YELLOW}Clearing existing files...${NC}"
find . -not -path './.git*' -not -name '.' -not -name '..' -delete

# Copy new frontend files
echo -e "${YELLOW}Copying updated frontend files...${NC}"
cd - > /dev/null
cp -r "$FRONTEND_DIR/"* "$TEMP_DIR/" 2>/dev/null || true
cp -r "$FRONTEND_DIR/".[!.]* "$TEMP_DIR/" 2>/dev/null || true

# Navigate back to temp directory
cd "$TEMP_DIR"

# Update README if it doesn't exist
if [ ! -f "README.md" ]; then
    echo -e "${YELLOW}Creating README...${NC}"
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
fi

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓ No changes detected - frontend is up to date${NC}"
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Commit and push changes
echo -e "${YELLOW}Committing and pushing changes...${NC}"
git add .
git commit -m "Sync from main repository

Source branch: $CURRENT_BRANCH
Source commit: $CURRENT_COMMIT
Sync time: $(date '+%Y-%m-%d %H:%M:%S')"

git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend successfully synced${NC}"
    echo
    echo -e "${GREEN}=== Sync Complete ===${NC}"
    echo -e "${BLUE}Frontend repository: $FRONTEND_REPO_URL${NC}"
    echo -e "${BLUE}Source commit: $CURRENT_COMMIT${NC}"
    echo -e "${BLUE}Vercel will automatically deploy the changes${NC}"
    
    # Clean up
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
else
    echo -e "${RED}Error: Failed to push changes${NC}"
    echo -e "${BLUE}Temp files available at: $TEMP_DIR${NC}"
    exit 1
fi