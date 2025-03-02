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

# 1. Stop nginx container
echo "===== Stopping Nginx service ====="
docker compose -f docker-compose.prod.yml stop nginx
echo

# 2. Clear Nginx cache
echo "===== Clearing Nginx cache ====="
docker compose -f docker-compose.prod.yml exec -T frontend sh -c "rm -rf /tmp/.next/cache" || true
echo "Pruning unused Docker resources..."
docker system prune -f
echo

# 3. Rebuild Nginx
echo "===== Rebuilding Nginx ====="
docker compose -f docker-compose.prod.yml build nginx
echo

# 4. Verify Nginx configuration before starting
echo "===== Verifying Nginx configuration before starting ====="
docker compose -f docker-compose.prod.yml run --rm nginx nginx -t
echo

# 5. Start Nginx
echo "===== Starting Nginx ====="
docker compose -f docker-compose.prod.yml up -d nginx
echo

# 6. Wait for services to start
echo "===== Waiting for services to start ====="
echo "Waiting 10 seconds for services to initialize..."
sleep 10
echo

# 7. Check service status
echo "===== Checking service status ====="
docker compose -f docker-compose.prod.yml ps nginx
echo

# 8. Check logs for any errors
echo "===== Checking logs for errors ====="
echo "Nginx logs (last 30 lines):"
docker compose -f docker-compose.prod.yml logs --tail=30 nginx
echo

# 9. Verify Nginx configuration
echo "===== Verifying Nginx configuration ====="
docker compose -f docker-compose.prod.yml exec -T nginx nginx -T | grep -A 10 "location /api/auth"
docker compose -f docker-compose.prod.yml exec -T nginx nginx -T | grep -A 10 "location = /api/auth/session"
docker compose -f docker-compose.prod.yml exec -T nginx nginx -T | grep -A 10 "location = /api/auth/csrf"
echo

echo "===== Deployment Complete ====="
echo "$(date)"
echo
echo "To check for NextAuth issues, please:"
echo "1. Visit https://brandfocus.ai and try to log in"
echo "2. Check browser console for any errors"
echo "3. If issues persist, check logs with: docker compose -f docker-compose.prod.yml logs frontend"
echo
echo "If you need to rollback, restore the previous Nginx configuration and restart the Nginx container" 