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

# 2. Clear Next.js cache
echo "===== Clearing Next.js cache ====="
echo "Stopping frontend container to clear cache..."
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm -f frontend
echo "Removing Next.js cache..."
docker volume rm -f backend_next_cache || true
echo

# 3. Rebuild and restart services
echo "===== Rebuilding services ====="
echo "Rebuilding frontend and nginx..."
docker-compose -f docker-compose.prod.yml build frontend nginx
echo

echo "===== Restarting services ====="
echo "Starting frontend and nginx..."
docker-compose -f docker-compose.prod.yml up -d frontend nginx
echo

# 4. Wait for services to start
echo "===== Waiting for services to start ====="
echo "Waiting 10 seconds for services to initialize..."
sleep 10
echo

# 5. Check service status
echo "===== Checking service status ====="
docker-compose -f docker-compose.prod.yml ps
echo

# 6. Check logs for any errors
echo "===== Checking logs for errors ====="
echo "Frontend logs (last 20 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend
echo
echo "Nginx logs (last 20 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=20 nginx
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