#!/bin/bash

# AI Africa Funding Tracker - Service Restart Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Restarting AI Africa Funding Tracker Services ===${NC}"

# Restart all services managed by docker-compose
/usr/local/bin/docker-compose restart

echo -e "${GREEN}✓ Services restarted successfully.${NC}"
echo
/usr/local/bin/docker-compose ps