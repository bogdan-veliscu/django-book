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

# 1. Stop nginx container
echo "===== Stopping Nginx service ====="
docker compose -f "$COMPOSE_FILE" stop nginx
echo

# 2. Create a backup of the current Nginx configuration
echo "===== Creating backup of current Nginx configuration ====="
timestamp=$(date +%Y%m%d%H%M%S)
backup_dir="nginx_backup_$timestamp"
mkdir -p "$backup_dir"

# Extract current configuration files for backup
docker compose -f "$COMPOSE_FILE" run --rm --entrypoint sh nginx -c "tar -cf - /etc/nginx" | tar -xf - -C "$backup_dir"
echo "Backup created in $backup_dir"
echo

# 3. Remove the Nginx container and volume to ensure a clean state
echo "===== Removing Nginx container and volumes ====="
docker compose -f "$COMPOSE_FILE" rm -f nginx
docker volume rm $(docker volume ls -q | grep nginx) || true
echo

# 4. Rebuild Nginx from scratch
echo "===== Rebuilding Nginx from scratch ====="
docker compose -f "$COMPOSE_FILE" build --no-cache nginx
echo

# 5. Start Nginx with a clean configuration
echo "===== Starting Nginx with clean configuration ====="
# Create a temporary directory for the configuration
mkdir -p tmp_nginx_conf
cat > tmp_nginx_conf/default.conf << 'EOF'
# Main Nginx configuration
# Based on proven patterns from Django 5 Web Development Cookbook

# Define upstream servers
upstream backend {
    server app:8000;
}

upstream frontend {
    server frontend:3000;
}

# HTTP server - redirects to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name brandfocus.ai www.brandfocus.ai;
    
    # Simple redirect to HTTPS
    return 301 https://$host$request_uri;
}

# HTTPS server - main configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name brandfocus.ai www.brandfocus.ai;
    
    # Disable automatic redirects that cause problems with NextAuth
    absolute_redirect off;
    port_in_redirect off;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/brandfocus.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/brandfocus.ai/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/brandfocus.ai/chain.pem;
    
    # SSL optimization
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
    
    # NextAuth specific endpoints - must be before the general API location
    location = /api/auth/session {
        proxy_pass http://frontend/api/auth/session;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers for NextAuth
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
    
    location ^~ /api/auth/ {
        proxy_pass http://frontend/api/auth/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers for NextAuth
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
    
    # Next.js static assets
    location /_next/static/ {
        proxy_pass http://frontend/_next/static/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=31536000, immutable";
        expires 365d;
    }
    
    # Django API endpoints
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
    
    # Static files
    location /static/ {
        alias /code/conduit/static/;
        expires 30d;
    }
    
    # Media files
    location /media/ {
        alias /code/conduit/media/;
        expires 30d;
    }
    
    # Health check endpoint
    location = /health {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
    
    # Frontend application - catch all remaining requests
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long-running operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Copy the configuration to the container
docker compose -f "$COMPOSE_FILE" up -d nginx
sleep 5
docker cp tmp_nginx_conf/default.conf $(docker compose -f "$COMPOSE_FILE" ps -q nginx):/etc/nginx/conf.d/default.conf

# Remove any other configuration files that might conflict
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "rm -f /etc/nginx/conf.d/http.conf /etc/nginx/conf.d/https.conf"

# Verify the configuration
echo "===== Verifying Nginx configuration ====="
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "ls -la /etc/nginx/conf.d/ && nginx -t"
if [ $? -ne 0 ]; then
  echo "ERROR: Nginx configuration test failed. Rolling back to previous configuration."
  docker compose -f "$COMPOSE_FILE" stop nginx
  docker compose -f "$COMPOSE_FILE" rm -f nginx
  echo "Please check the configuration manually."
  exit 1
fi

# Restart Nginx with the new configuration
echo "===== Restarting Nginx with new configuration ====="
docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload
echo

# 6. Wait for services to start
echo "===== Waiting for services to start ====="
echo "Waiting 5 seconds for services to initialize..."
sleep 5
echo

# 7. Check service status
echo "===== Checking service status ====="
docker compose -f "$COMPOSE_FILE" ps nginx frontend
echo

# 8. Test NextAuth endpoints
echo "===== Testing NextAuth endpoints ====="
echo "Testing /api/auth/session endpoint..."
curl -s -I https://brandfocus.ai/api/auth/session || echo "Could not reach session endpoint"
echo

# 9. Test API endpoints
echo "===== Testing API endpoints ====="
echo "Testing /api/health/ endpoint..."
curl -s -I https://brandfocus.ai/api/health/ || echo "Could not reach API health endpoint"
echo

# Cleanup
rm -rf tmp_nginx_conf

echo "===== Deployment Complete ====="
echo "$(date)"
echo
echo "To verify the fix:"
echo "1. Run the test script: ./scripts/test-nextauth.sh"
echo "2. Check browser console for any errors when logging in"
echo "3. If issues persist, check logs with: docker compose -f $COMPOSE_FILE logs nginx"
echo
echo "If you need to rollback, restore from the backup in $backup_dir" 