#!/bin/bash

# Script to rebuild and restart the frontend and nginx services
# This script should be run from the project root directory

set -e

echo "Rebuilding frontend and nginx services..."

# Stop the services
docker-compose -f docker-compose.prod.yml stop frontend nginx

# Remove the containers
docker-compose -f docker-compose.prod.yml rm -f frontend nginx

# Rebuild the services
docker-compose -f docker-compose.prod.yml build frontend nginx

# Start the services
docker-compose -f docker-compose.prod.yml up -d frontend nginx

echo "Waiting for services to start..."
sleep 5

# Check the status
docker-compose -f docker-compose.prod.yml ps frontend nginx

echo "Done! The frontend and nginx services have been rebuilt and restarted." 