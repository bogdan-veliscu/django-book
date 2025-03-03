#!/bin/bash

# Exit on error
set -e

echo "Starting NextAuth fix deployment..."

# Stop Nginx container
echo "Stopping Nginx container..."
docker compose -f docker-compose.prod.yml stop nginx

# Create backup of current Nginx configuration
echo "Creating backup of current Nginx configuration..."
BACKUP_DIR="nginx_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp nginx/templates/https.conf.template "$BACKUP_DIR/"

# Remove Nginx container and volumes to ensure clean state
echo "Removing Nginx container and volumes..."
docker compose -f docker-compose.prod.yml rm -f nginx
docker volume rm $(docker volume ls -q | grep nginx) || true

# Ensure Nginx environment variables are set
echo "Setting up Nginx environment variables..."
cat > nginx.env << EOL
VIRTUAL_HOST=brandfocus.ai
EOL

# Rebuild Nginx from scratch
echo "Rebuilding Nginx..."
docker compose -f docker-compose.prod.yml build nginx

# Start Nginx with new configuration
echo "Starting Nginx with new configuration..."
docker compose -f docker-compose.prod.yml up -d nginx

# Wait for Nginx to start
echo "Waiting for Nginx to start..."
sleep 5

# Test Nginx configuration
echo "Testing Nginx configuration..."
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Restart Nginx to apply changes
echo "Restarting Nginx to apply changes..."
docker compose -f docker-compose.prod.yml restart nginx

# Test critical endpoints
echo "Testing critical endpoints..."
./scripts/test-nextauth.sh

echo "Deployment completed successfully!"
echo "If you need to rollback, the backup is in: $BACKUP_DIR" 