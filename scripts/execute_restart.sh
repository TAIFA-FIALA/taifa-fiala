#!/bin/bash

# Make scripts executable
chmod +x restart_services_fixed.sh
chmod +x stop_services.sh  
chmod +x check_services_status.sh

echo "=== Running TAIFA-FIALA Service Restart ==="

# Run the restart script
./restart_services_fixed.sh