#!/bin/bash

# Simple one-command deployment script
# Usage: ./deploy-latest.sh

echo "🚀 Deploying latest version to production..."

# Step 1: Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push org-origin main

# Step 2: Deploy to production
echo "🔄 Deploying to production server..."
./deploy_production_host.sh

echo "✅ Deployment complete!"
echo "🌐 Check your site: https://taifa-fiala.net"
