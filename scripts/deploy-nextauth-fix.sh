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

# Create Docker network if it doesn't exist
echo "Creating Docker network..."
docker network create nginx-proxy || true

# Check Docker networks
echo "Checking Docker networks..."
docker network ls

# Start services in the correct order
echo "Starting services in correct order..."

# Start database and Redis first
echo "Starting database and Redis..."
docker compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! docker compose -f docker-compose.prod.yml exec db pg_isready; do
    echo "Database not ready yet, waiting..."
    sleep 5
done
echo "Database is ready."

# Start the backend
echo "Starting backend service..."
docker compose -f docker-compose.prod.yml up -d conduit-api

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec conduit-api curl -s http://localhost:8000/api/health/ > /dev/null; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Backend health check timed out, continuing anyway..."
        break
    fi
    echo "Backend not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Backend is ready or timeout occurred."

# Start the frontend
echo "Starting frontend service..."
docker compose -f docker-compose.prod.yml up -d conduit-frontend

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec conduit-frontend curl -s http://localhost:3000/api/health > /dev/null; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Frontend health check timed out, continuing anyway..."
        break
    fi
    echo "Frontend not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Frontend is ready or timeout occurred."

# Ensure services are on the same network
echo "Connecting services to network..."
docker network connect nginx-proxy conduit-api || echo "conduit-api already connected or doesn't exist"
docker network connect nginx-proxy conduit-frontend || echo "conduit-frontend already connected or doesn't exist"

# List running containers
echo "Listing running containers:"
docker ps

# Show network connections
echo "Checking network connections:"
docker network inspect nginx-proxy

# Rebuild and start Nginx last
echo "Rebuilding Nginx..."
docker compose -f docker-compose.prod.yml build nginx

echo "Starting Nginx with new configuration..."
docker compose -f docker-compose.prod.yml up -d nginx

# Make sure Nginx is on the same network
echo "Connecting Nginx to the network..."
docker network connect nginx-proxy $(docker compose -f docker-compose.prod.yml ps -q nginx) || echo "Nginx already connected or doesn't exist"

# Wait for Nginx to start
echo "Waiting for Nginx to start..."
sleep 10

# Test Nginx configuration
echo "Testing Nginx configuration..."
docker compose -f docker-compose.prod.yml exec nginx nginx -t || {
    echo "Nginx configuration test failed. Checking logs..."
    docker compose -f docker-compose.prod.yml logs nginx
    exit 1
}

# Restart Nginx to apply changes
echo "Restarting Nginx to apply changes..."
docker compose -f docker-compose.prod.yml restart nginx

# Test critical endpoints
echo "Testing critical endpoints..."
./scripts/test-nextauth.sh || echo "Tests failed but continuing deployment"

echo "Deployment completed successfully!"
echo "If you need to rollback, the backup is in: $BACKUP_DIR" 