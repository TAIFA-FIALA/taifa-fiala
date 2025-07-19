#!/bin/bash

# TAIFA-FIALA Frontend Sync Setup Script
# Configures Git hook for automatic frontend synchronization

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 TAIFA-FIALA Frontend Sync Setup${NC}"
echo "=================================================="

# Default configuration
DEFAULT_FRONTEND_REPO_PATH="/Users/drjforrest/dev/devprojects/taifa-fiala-frontend"
HOOK_PATH=".git/hooks/post-commit"

echo -e "${YELLOW}📋 Current Configuration:${NC}"
echo "Frontend repo path: $DEFAULT_FRONTEND_REPO_PATH"
echo "Hook location: $HOOK_PATH"
echo ""

# Check if hook exists and is executable
if [ -f "$HOOK_PATH" ] && [ -x "$HOOK_PATH" ]; then
    echo -e "${GREEN}✅ Git hook is already installed and executable${NC}"
else
    echo -e "${RED}❌ Git hook is not properly installed${NC}"
    exit 1
fi

# Prompt for custom frontend repo path
echo -e "${BLUE}🎯 Configuration Options:${NC}"
echo "1. Use default path: $DEFAULT_FRONTEND_REPO_PATH"
echo "2. Specify custom path"
echo "3. Test the current setup"
echo ""
read -p "Choose an option (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}✅ Using default configuration${NC}"
        FRONTEND_REPO_PATH="$DEFAULT_FRONTEND_REPO_PATH"
        ;;
    2)
        read -p "Enter custom frontend repo path: " CUSTOM_PATH
        if [ -n "$CUSTOM_PATH" ]; then
            FRONTEND_REPO_PATH="$CUSTOM_PATH"
            # Update the hook with custom path
            sed -i.bak "s|FRONTEND_REPO_PATH=\".*\"|FRONTEND_REPO_PATH=\"$FRONTEND_REPO_PATH\"|" "$HOOK_PATH"
            echo -e "${GREEN}✅ Updated hook with custom path: $FRONTEND_REPO_PATH${NC}"
        else
            echo -e "${RED}❌ No path provided. Using default.${NC}"
            FRONTEND_REPO_PATH="$DEFAULT_FRONTEND_REPO_PATH"
        fi
        ;;
    3)
        echo -e "${BLUE}🧪 Testing current setup...${NC}"
        
        # Check if frontend source exists
        if [ -d "frontend/nextjs" ]; then
            echo -e "${GREEN}✅ Frontend source directory found${NC}"
        else
            echo -e "${RED}❌ Frontend source directory not found${NC}"
        fi
        
        # Check hook syntax
        if bash -n "$HOOK_PATH"; then
            echo -e "${GREEN}✅ Hook syntax is valid${NC}"
        else
            echo -e "${RED}❌ Hook has syntax errors${NC}"
        fi
        
        # Test rsync command
        if command -v rsync >/dev/null 2>&1; then
            echo -e "${GREEN}✅ rsync is available${NC}"
        else
            echo -e "${RED}❌ rsync is not installed${NC}"
        fi
        
        echo -e "${BLUE}📝 To test the hook, make a commit with frontend changes${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid option. Exiting.${NC}"
        exit 1
        ;;
esac

# Create frontend repo directory if it doesn't exist
if [ ! -d "$FRONTEND_REPO_PATH" ]; then
    echo -e "${YELLOW}📁 Creating frontend repo directory: $FRONTEND_REPO_PATH${NC}"
    mkdir -p "$FRONTEND_REPO_PATH"
fi

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}📋 How it works:${NC}"
echo "1. Make changes to frontend files in frontend/nextjs/"
echo "2. Commit your changes: git add . && git commit -m 'Your message'"
echo "3. The hook automatically syncs frontend to: $FRONTEND_REPO_PATH"
echo "4. A new commit is created in the frontend repo with sync details"
echo ""
echo -e "${BLUE}🔧 Configuration:${NC}"
echo "• Source: frontend/nextjs/"
echo "• Target: $FRONTEND_REPO_PATH"
echo "• Excludes: node_modules, .next, .env.local, logs"
echo "• Trigger: After each commit to main repo"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "• Only commits with frontend changes trigger sync"
echo "• The frontend repo is automatically created if it doesn't exist"
echo "• You can push the frontend repo to GitHub/Vercel separately"
echo "• To disable: rm .git/hooks/post-commit"
echo ""
echo -e "${GREEN}✅ Ready to use! Make a commit with frontend changes to test.${NC}"
