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
docker compose -f docker-compose.prod.yml up -d app

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec app curl -s http://localhost:8000/api/health/ > /dev/null; do
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
docker compose -f docker-compose.prod.yml up -d frontend

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec frontend curl -s http://localhost:3000/health > /dev/null; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Frontend health check timed out, continuing anyway..."
        break
    fi
    echo "Frontend not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Frontend is ready or timeout occurred."

# Connect services to the nginx-proxy network
echo "Connecting services to nginx-proxy network..."
docker network connect nginx-proxy app || true
docker network connect nginx-proxy frontend || true
docker network connect nginx-proxy db || true
docker network connect nginx-proxy redis || true

# List running containers
echo "Listing running containers..."
docker compose -f docker-compose.prod.yml ps

# Rebuild and start Nginx last
echo "Rebuilding and starting Nginx..."
docker compose -f docker-compose.prod.yml up -d --build nginx

# Wait for Nginx to be ready
echo "Waiting for Nginx to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec nginx nginx -t; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Nginx configuration test timed out, continuing anyway..."
        break
    fi
    echo "Nginx not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Nginx is ready or timeout occurred."

# Test critical endpoints
echo "Testing critical endpoints..."
curl -s -I https://brandfocus.ai/api/health/ || echo "Health check failed"
curl -s -I https://brandfocus.ai/api/auth/session || echo "Session endpoint check failed"

# After starting all services, verify NextAuth connectivity
echo "===== VERIFYING NEXTAUTH CONNECTIVITY ====="

# Wait for a moment to make sure all services are ready
sleep 10

# Check the session endpoint directly from inside the frontend container
echo "Testing NextAuth session endpoint from inside frontend container..."
docker compose -f docker-compose.prod.yml exec frontend curl -v http://localhost:3000/api/auth/session

# Test the session endpoint through Nginx
echo "Testing NextAuth session endpoint through Nginx..."
curl -v https://${DOMAIN}/api/auth/session --insecure

# View the frontend logs for any NextAuth errors
echo "Checking frontend logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml logs --tail=50 frontend | grep -i "auth\|next"

# View Nginx logs
echo "Checking Nginx logs for errors..."
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/error.log | tail -n 50

echo "Deployment completed. Check the logs for any issues:"
echo "docker compose -f docker-compose.prod.yml logs -f" 