#!/bin/bash

# TAIFA-FIALA Frontend Repository Setup Script
# This script helps set up a separate frontend repository for Vercel deployment

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== TAIFA-FIALA Frontend Repository Setup ===${NC}"

# Get repository details
echo -e "${YELLOW}Setting up separate frontend repository...${NC}"
echo "This will create a new repository containing only the Next.js frontend code."
echo

read -p "Enter the new frontend repository name (e.g., taifa-fiala-frontend): " REPO_NAME
read -p "Enter your GitHub username: " GITHUB_USER

FRONTEND_REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
FRONTEND_DIR="frontend/nextjs_dashboard"
TEMP_DIR="/tmp/taifa-frontend-setup"

echo
echo -e "${BLUE}Repository URL: ${FRONTEND_REPO_URL}${NC}"
echo -e "${BLUE}Source directory: ${FRONTEND_DIR}${NC}"
echo

# Confirm
read -p "Continue with setup? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Setup cancelled.${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Step 1: Create temporary directory
echo -e "${YELLOW}Step 1: Creating temporary directory...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Step 2: Copy frontend files
echo -e "${YELLOW}Step 2: Copying frontend files...${NC}"
cp -r "$FRONTEND_DIR/"* "$TEMP_DIR/"
cp -r "$FRONTEND_DIR/".[!.]* "$TEMP_DIR/" 2>/dev/null || true

# Step 3: Create frontend-specific files
echo -e "${YELLOW}Step 3: Creating frontend-specific files...${NC}"

# Create README for frontend repo
cat > "$TEMP_DIR/README.md" << 'EOF'
# TAIFA-FIALA Frontend

This is the frontend application for the TAIFA-FIALA AI Africa Funding Intelligence System.

## Architecture

- **Frontend**: Next.js application (this repository)
- **Backend**: Home server deployment
- **Database**: Supabase
- **Vector Search**: Pinecone

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Deployment

This repository is automatically deployed to Vercel when changes are pushed to the main branch.

## Environment Variables

Required environment variables for Vercel:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NEXT_PUBLIC_DASHBOARD_URL=https://your-backend-domain.com:8501
SUPABASE_PROJECT_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
```

## Sync from Main Repository

This repository is synced from the main TAIFA-FIALA repository using git subtree.
Changes should be made in the main repository and synced using the sync script.

## License

Same as main TAIFA-FIALA project.
EOF

# Create .gitignore specifically for frontend
cat > "$TEMP_DIR/.gitignore" << 'EOF'
# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts
EOF

# Create a simple deployment script
cat > "$TEMP_DIR/deploy.sh" << 'EOF'
#!/bin/bash

# Simple deployment script for Vercel
echo "Deploying TAIFA-FIALA Frontend to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Error: Vercel CLI not found. Install with: npm install -g vercel"
    exit 1
fi

# Deploy to production
vercel --prod

echo "Deployment complete!"
EOF

chmod +x "$TEMP_DIR/deploy.sh"

# Step 4: Initialize git repository
echo -e "${YELLOW}Step 4: Initializing git repository...${NC}"
cd "$TEMP_DIR"

git init
git add .
git commit -m "Initial commit: TAIFA-FIALA Frontend

This repository contains the Next.js frontend for the TAIFA-FIALA
AI Africa Funding Intelligence System.

Synced from main repository on $(date '+%Y-%m-%d %H:%M:%S')"

# Step 5: Instructions for creating GitHub repository
echo
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: TAIFA-FIALA Frontend - Next.js application"
echo "   - Public or Private (your choice)"
echo "   - Do NOT initialize with README (we already have one)"
echo
echo "2. Push the frontend code:"
echo "   cd $TEMP_DIR"
echo "   git branch -M main"
echo "   git remote add origin $FRONTEND_REPO_URL"
echo "   git push -u origin main"
echo
echo "3. Set up Vercel deployment:"
echo "   - Go to https://vercel.com/new"
echo "   - Import the new repository: $FRONTEND_REPO_URL"
echo "   - Configure these environment variables:"
echo "     * NEXT_PUBLIC_API_URL"
echo "     * NEXT_PUBLIC_DASHBOARD_URL"  
echo "     * SUPABASE_PROJECT_URL"
echo "     * SUPABASE_API_KEY"
echo
echo "4. Update the main repository sync script:"
echo "   - Edit sync_frontend.sh"
echo "   - Update FRONTEND_REPO_URL to: $FRONTEND_REPO_URL"
echo
echo "5. Future syncs:"
echo "   - Make changes in main repository"
echo "   - Run: ./sync_frontend.sh"
echo "   - Vercel will auto-deploy from the frontend repository"
echo
echo -e "${GREEN}Frontend repository setup complete!${NC}"
echo -e "${BLUE}Temporary files created in: $TEMP_DIR${NC}"
echo -e "${YELLOW}Remember to clean up the temporary directory after pushing to GitHub.${NC}"