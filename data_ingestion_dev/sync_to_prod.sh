#!/bin/bash

# Sync local watch directory to production
rsync -avz --delete ./data_ingestion_dev/ jforrest@100.75.201.24:/Users/jforrest/production/TAIFA-FIALA/data_ingestion/

# Log the sync
echo "$(date): Synced to production" >> ./data_ingestion_dev/logs/sync.log
