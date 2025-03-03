#!/bin/bash

# Exit on error
set -e

echo "Starting NextAuth fix deployment..."

# Stop all services to ensure clean state
echo "Stopping all services..."
docker compose -f docker-compose.prod.yml down

# Create backup of current Nginx configuration
echo "Creating backup of current Nginx configuration..."
BACKUP_DIR="nginx_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp nginx/templates/https.conf.template "$BACKUP_DIR/"

# Ensure Nginx environment variables are set
echo "Setting up Nginx environment variables..."
cat > nginx.env << EOL
VIRTUAL_HOST=brandfocus.ai
EOL

# Start services in the correct order
echo "Starting services in correct order..."

# Start database and Redis first
echo "Starting database and Redis..."
docker compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Start the backend
echo "Starting backend service..."
docker compose -f docker-compose.prod.yml up -d conduit-api

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 5

# Start the frontend
echo "Starting frontend service..."
docker compose -f docker-compose.prod.yml up -d conduit-frontend

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
sleep 5

# Rebuild and start Nginx last
echo "Rebuilding Nginx..."
docker compose -f docker-compose.prod.yml build nginx

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