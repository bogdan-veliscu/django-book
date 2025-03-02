#!/bin/bash

# Deployment script for NextAuth fixes
# This script should be run on the production server

set -e

echo "===== Starting NextAuth Fix Deployment ====="
echo "$(date)"
echo

# Define directories
BACKEND_DIR=$(pwd)

echo "Backend directory: $BACKEND_DIR"
echo

# Check if docker-compose.prod.yml or docker compose.prod.yml exists
if [ -f "docker-compose.prod.yml" ]; then
  COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "docker compose.prod.yml" ]; then
  COMPOSE_FILE="docker compose.prod.yml"
else
  echo "Error: Cannot find docker-compose.prod.yml or docker compose.prod.yml"
  exit 1
fi

echo "Using compose file: $COMPOSE_FILE"
echo

# 0. Make sure frontend service is running
echo "===== Ensuring frontend service is running ====="
docker compose -f "$COMPOSE_FILE" up -d frontend
echo

# 1. Stop nginx container
echo "===== Stopping Nginx service ====="
docker compose -f "$COMPOSE_FILE" stop nginx
echo

# 2. Clear Nginx cache and remove default.conf
echo "===== Clearing Nginx cache and removing default configuration ====="
docker compose -f "$COMPOSE_FILE" exec -T frontend sh -c "rm -rf /tmp/.next/cache" || true
echo "Removing default.conf..."
docker compose -f "$COMPOSE_FILE" exec -T nginx rm -f /etc/nginx/conf.d/default.conf || true
echo "Pruning unused Docker resources..."
docker system prune -f
echo

# 3. Rebuild Nginx
echo "===== Rebuilding Nginx ====="
docker compose -f "$COMPOSE_FILE" build nginx
echo

# 4. Verify Nginx configuration before starting
echo "===== Verifying Nginx configuration before starting ====="
docker compose -f "$COMPOSE_FILE" run --rm nginx nginx -t
echo

# 5. Start Nginx
echo "===== Starting Nginx ====="
docker compose -f "$COMPOSE_FILE" up -d nginx
echo

# 6. Wait for services to start
echo "===== Waiting for services to start ====="
echo "Waiting 10 seconds for services to initialize..."
sleep 10
echo

# 7. Check service status
echo "===== Checking service status ====="
docker compose -f "$COMPOSE_FILE" ps nginx frontend
echo

# 8. Check logs for any errors
echo "===== Checking logs for errors ====="
echo "Nginx logs (last 30 lines):"
docker compose -f "$COMPOSE_FILE" logs --tail=30 nginx
echo

# 9. Verify Nginx configuration
echo "===== Verifying Nginx configuration ====="
docker compose -f "$COMPOSE_FILE" exec -T nginx nginx -T | grep -A 10 "location /api/auth"
docker compose -f "$COMPOSE_FILE" exec -T nginx nginx -T | grep -A 10 "location = /api/auth/session"
docker compose -f "$COMPOSE_FILE" exec -T nginx nginx -T | grep -A 10 "location = /api/auth/csrf"
echo

echo "===== Deployment Complete ====="
echo "$(date)"
echo
echo "To check for NextAuth issues, please:"
echo "1. Visit https://brandfocus.ai and try to log in"
echo "2. Check browser console for any errors"
echo "3. If issues persist, check logs with: docker compose -f $COMPOSE_FILE logs frontend"
echo
echo "If you need to rollback, restore the previous Nginx configuration and restart the Nginx container" 