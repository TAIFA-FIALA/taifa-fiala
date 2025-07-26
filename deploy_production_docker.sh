#!/bin/bash

# Deploy Production Docker Script for AI Africa Funding Tracker
# This script deploys the application to production, including the file watcher service

set -e  # Exit on error

# Configuration
PROD_SERVER="your-production-server.com"  # Replace with your production server
PROD_USER="ubuntu"  # Replace with your production server username
PROD_DIR="/opt/ai-africa-funding-tracker"  # Production directory
DEV_WATCH_DIR="./data_ingestion_dev"  # Local development watch directory

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Africa Funding Tracker Production Deployment ===${NC}"
echo -e "${YELLOW}Deploying to ${PROD_SERVER}:${PROD_DIR}${NC}"

# Create local development watch directory if it doesn't exist
echo -e "${YELLOW}Setting up local development watch directory...${NC}"
mkdir -p ${DEV_WATCH_DIR}/{inbox/{pdfs,csvs,articles},processing,completed,failed,logs}
touch ${DEV_WATCH_DIR}/inbox/urls.txt

# Create a README file in the dev watch directory
cat > ${DEV_WATCH_DIR}/README.md << EOF
# AI Africa Funding Tracker - Development Watch Directory

This directory is automatically synced to the production watch folder.

## Usage

1. Place files in the appropriate subdirectory:
   - PDFs: \`inbox/pdfs/\`
   - CSVs: \`inbox/csvs/\`
   - Text/HTML: \`inbox/articles/\`
   - URLs: Add to \`inbox/urls.txt\` (one per line)

2. Files will be automatically synced to production every minute.

3. Check the \`logs\` directory for processing logs.

## Directories

- \`inbox/\`: Drop files here
- \`processing/\`: Files being processed
- \`completed/\`: Processed files
- \`failed/\`: Failed files
- \`logs/\`: Processing logs
EOF

# Create rsync script for automatic syncing
cat > ${DEV_WATCH_DIR}/sync_to_prod.sh << EOF
#!/bin/bash

# Sync local watch directory to production
rsync -avz --delete ${DEV_WATCH_DIR}/ ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/data_ingestion/

# Log the sync
echo "\$(date): Synced to production" >> ${DEV_WATCH_DIR}/logs/sync.log
EOF

# Make the sync script executable
chmod +x ${DEV_WATCH_DIR}/sync_to_prod.sh

# Create a cron job to run the sync script every minute
CRON_JOB="* * * * * $(pwd)/${DEV_WATCH_DIR}/sync_to_prod.sh"
(crontab -l 2>/dev/null | grep -v "sync_to_prod.sh"; echo "$CRON_JOB") | crontab -

echo -e "${GREEN}Local development watch directory set up at ${DEV_WATCH_DIR}${NC}"
echo -e "${GREEN}Files will be automatically synced to production every minute${NC}"

# SSH to production server and set up the environment
echo -e "${YELLOW}Setting up production environment...${NC}"
ssh ${PROD_USER}@${PROD_SERVER} << EOF
    # Create production directory if it doesn't exist
    mkdir -p ${PROD_DIR}
    
    # Create data ingestion directories
    mkdir -p ${PROD_DIR}/data_ingestion/{inbox/{pdfs,csvs,articles},processing,completed,failed,logs}
    touch ${PROD_DIR}/data_ingestion/inbox/urls.txt
    
    # Set permissions
    chmod -R 755 ${PROD_DIR}/data_ingestion
EOF

# Copy files to production server
echo -e "${YELLOW}Copying files to production server...${NC}"
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '__pycache__' \
    --exclude 'venv' --exclude '.env' --exclude '.git' \
    ./ ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

# Copy the .env file separately
scp .env ${PROD_USER}@${PROD_SERVER}:${PROD_DIR}/

# SSH to production server and start the services
echo -e "${YELLOW}Starting services on production server...${NC}"
ssh ${PROD_USER}@${PROD_SERVER} << EOF
    cd ${PROD_DIR}
    
    # Stop any running containers
    docker-compose down || true
    
    # Start the services with the watcher
    docker-compose -f docker-compose.watcher.yml up -d
    
    # Check if services are running
    docker-compose ps
EOF

echo -e "${GREEN}=== Deployment completed successfully ===${NC}"
echo -e "${YELLOW}To add files for processing:${NC}"
echo -e "1. Place files in ${DEV_WATCH_DIR}/inbox/"
echo -e "2. Files will be automatically synced to production"
echo -e "3. Check ${DEV_WATCH_DIR}/logs/ for processing logs"