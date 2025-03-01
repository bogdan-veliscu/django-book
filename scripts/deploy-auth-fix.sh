#!/bin/bash

# Comprehensive deployment script for authentication fixes
# This script should be run on the production server

set -e

echo "===== Starting Authentication Fix Deployment ====="
echo "$(date)"
echo

# Define directories
BACKEND_DIR=$(pwd)
FRONTEND_DIR=$(cd ../frontend && pwd)

echo "Backend directory: $BACKEND_DIR"
echo "Frontend directory: $FRONTEND_DIR"
echo

# 1. Pull latest changes for both repositories
echo "===== Pulling latest changes ====="
echo "Pulling backend changes..."
git pull origin feat/prod-deploy

echo
echo "Pulling frontend changes..."
cd $FRONTEND_DIR
git pull origin main
cd $BACKEND_DIR
echo

# 2. Stop all related services
echo "===== Stopping services ====="
echo "Stopping frontend and nginx containers..."
docker-compose -f docker-compose.prod.yml stop frontend nginx
docker-compose -f docker-compose.prod.yml rm -f frontend nginx
echo

# 3. Clear all caches
echo "===== Clearing caches ====="
echo "Removing Next.js cache..."
docker volume rm -f backend_next_cache || true
echo "Clearing Nginx cache..."
docker-compose -f docker-compose.prod.yml exec -T nginx sh -c "rm -rf /var/cache/nginx/*" || true
echo "Pruning unused Docker resources..."
docker system prune -f
echo

# 4. Rebuild services from scratch
echo "===== Rebuilding services ====="
echo "Rebuilding frontend and nginx with --no-cache option..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend nginx
echo

# 5. Start services
echo "===== Starting services ====="
echo "Starting frontend and nginx..."
docker-compose -f docker-compose.prod.yml up -d frontend nginx
echo

# 6. Wait for services to start
echo "===== Waiting for services to start ====="
echo "Waiting 20 seconds for services to initialize..."
sleep 20
echo

# 7. Check service status
echo "===== Checking service status ====="
docker-compose -f docker-compose.prod.yml ps
echo

# 8. Check logs for any errors
echo "===== Checking logs for errors ====="
echo "Frontend logs (last 30 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=30 frontend
echo
echo "Nginx logs (last 30 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=30 nginx
echo

# 9. Verify Nginx configuration
echo "===== Verifying Nginx configuration ====="
docker-compose -f docker-compose.prod.yml exec -T nginx nginx -T | grep -A 10 "location /api/auth"
echo

echo "===== Deployment Complete ====="
echo "$(date)"
echo
echo "To check for authentication issues, please:"
echo "1. Visit https://brandfocus.ai and try to log in"
echo "2. Check browser console for any errors"
echo "3. If issues persist, check logs with: docker-compose -f docker-compose.prod.yml logs frontend"
echo
echo "If you need to rollback, use: git checkout <previous-commit> and run this script again" 