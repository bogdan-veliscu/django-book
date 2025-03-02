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

# Load environment variables from .env.prod
if [ -f ".env.prod" ]; then
    echo "Loading environment variables from .env.prod"
    export $(cat .env.prod | grep -v '^#' | xargs)
fi

# Ensure NextAuth environment variables are set properly
echo "===== Checking NextAuth environment variables ====="
if [ -z "$NEXTAUTH_SECRET" ]; then
    echo "NEXTAUTH_SECRET not found in environment. Generating new one..."
    export NEXTAUTH_SECRET=$(openssl rand -base64 32)
    echo "NEXTAUTH_SECRET=$NEXTAUTH_SECRET" >> .env.prod
    echo "Added NEXTAUTH_SECRET to .env.prod"
else
    echo "NEXTAUTH_SECRET is set"
fi

if [ -z "$NEXTAUTH_URL" ]; then
    echo "NEXTAUTH_URL not found in environment. Adding it..."
    export NEXTAUTH_URL=https://brandfocus.ai
    echo "NEXTAUTH_URL=$NEXTAUTH_URL" >> .env.prod
    echo "Added NEXTAUTH_URL to .env.prod"
else
    echo "NEXTAUTH_URL is set"
fi
echo

# Stop all services to ensure clean state
echo "===== Stopping all services ====="
docker compose -f "$COMPOSE_FILE" down
echo

# Create a backup of the current Nginx configuration
echo "===== Creating backup of current Nginx configuration ====="
timestamp=$(date +%Y%m%d%H%M%S)
backup_dir="nginx_backup_$timestamp"
mkdir -p "$backup_dir"

# Extract current configuration files for backup
if docker compose -f "$COMPOSE_FILE" ps -q nginx > /dev/null 2>&1; then
    docker compose -f "$COMPOSE_FILE" run --rm --entrypoint sh nginx -c "tar -cf - /etc/nginx" | tar -xf - -C "$backup_dir"
    echo "Backup created in $backup_dir"
else
    echo "No running Nginx container found for backup"
fi
echo

# Remove all containers and volumes to ensure clean state
echo "===== Removing containers and volumes ====="
docker compose -f "$COMPOSE_FILE" down -v
echo

# Rebuild all services from scratch
echo "===== Rebuilding services from scratch ====="
docker compose -f "$COMPOSE_FILE" build --no-cache
echo

# Start services in the correct order
echo "===== Starting services ====="
# Start dependencies first
docker compose -f "$COMPOSE_FILE" up -d db redis
echo "Waiting for database to be ready..."
sleep 10

# Start the backend
docker compose -f "$COMPOSE_FILE" up -d app
echo "Waiting for backend to be ready..."
sleep 5

# Start the frontend
docker compose -f "$COMPOSE_FILE" up -d frontend
echo "Waiting for frontend to be ready..."
sleep 5

# Configure and start Nginx last
echo "===== Configuring Nginx ====="
# Create a temporary directory for the configuration
mkdir -p tmp_nginx_conf

# Create environment variables file for Nginx
cat > tmp_nginx_conf/nginx.env << 'EOF'
VIRTUAL_HOST=brandfocus.ai
EOF

# Create main configuration file
cat > tmp_nginx_conf/default.conf << 'EOF'
# Main Nginx configuration
# Based on proven patterns and previous working configuration

# Environment variables
env VIRTUAL_HOST;

# Define upstream servers with clear naming
upstream django_backend {
    server app:8000;
    keepalive 32;
}

upstream nextjs_frontend {
    server frontend:3000;
    keepalive 32;
}

# HTTP server - redirects to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${VIRTUAL_HOST} www.${VIRTUAL_HOST};
    
    # Simple redirect to HTTPS
    return 301 https://${VIRTUAL_HOST}$request_uri;
}

# HTTPS server - main configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${VIRTUAL_HOST} www.${VIRTUAL_HOST};
    charset utf-8;
    
    # Critical for NextAuth - disable automatic redirects
    absolute_redirect off;
    port_in_redirect off;
    server_name_in_redirect off;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/${VIRTUAL_HOST}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${VIRTUAL_HOST}/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/${VIRTUAL_HOST}/chain.pem;
    
    # SSL optimization
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Next.js static assets - high priority
    location ^~ /_next/static/ {
        proxy_pass http://nextjs_frontend/_next/static/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=31536000, immutable" always;
        expires 365d;
        access_log off;
    }
    
    # NextAuth specific endpoints - exact match for session to prevent redirect loops
    location = /api/auth/session {
        absolute_redirect off;
        port_in_redirect off;
        server_name_in_redirect off;
        proxy_redirect off;
        
        proxy_pass http://nextjs_frontend/api/auth/session;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Ssl on;
        
        # Buffer settings to prevent issues with larger session data
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # CORS headers for NextAuth
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
            add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
            add_header Access-Control-Allow-Credentials "true" always;
            add_header Access-Control-Max-Age 1728000 always;
            add_header Content-Type "text/plain charset=UTF-8" always;
            add_header Content-Length 0 always;
            return 204;
        }
    }
    
    # Also add exact matches for other critical NextAuth endpoints
    location = /api/auth/signin {
        absolute_redirect off;
        port_in_redirect off;
        server_name_in_redirect off;
        proxy_redirect off;
        
        proxy_pass http://nextjs_frontend/api/auth/signin;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Ssl on;
    }

    location = /api/auth/signout {
        absolute_redirect off;
        port_in_redirect off;
        server_name_in_redirect off;
        proxy_redirect off;
        
        proxy_pass http://nextjs_frontend/api/auth/signout;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Ssl on;
    }
    
    # Other NextAuth endpoints
    location ~ ^/api/auth/ {
        absolute_redirect off;
        port_in_redirect off;
        server_name_in_redirect off;
        proxy_redirect off;
        
        proxy_pass http://nextjs_frontend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Ssl on;
        
        # CORS headers for NextAuth
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
            add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
            add_header Access-Control-Allow-Credentials "true" always;
            add_header Access-Control-Max-Age 1728000 always;
            add_header Content-Type "text/plain charset=UTF-8" always;
            add_header Content-Length 0 always;
            return 204;
        }
    }
    
    # Django API endpoints - FIXED: Don't strip /api prefix when proxying to Django
    location /api/ {
        # Make sure app:8000 receives the /api/ prefix in the URL
        proxy_pass http://django_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /api;  # Add this to inform Django about the /api prefix
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        # Handle preflight requests
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization" always;
            add_header Access-Control-Allow-Credentials "true" always;
            add_header Access-Control-Max-Age 1728000 always;
            add_header Content-Type "text/plain charset=UTF-8" always;
            add_header Content-Length 0 always;
            return 204;
        }
    }
    
    # Static files
    location /static/ {
        alias /code/conduit/static/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public, max-age=2592000" always;
    }
    
    # Media files
    location /media/ {
        alias /code/conduit/media/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public, max-age=2592000" always;
    }
    
    # Health check endpoint
    location = /health {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
    
    # Try files pattern for static HTML (for Next.js static exports if used)
    location ~ \.html$ {
        try_files $uri =404;
    }
    
    # Frontend application - catch all remaining requests
    location / {
        proxy_pass http://nextjs_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Increase timeouts for long-running operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Error handling
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
EOF

# Start Nginx
docker compose -f "$COMPOSE_FILE" up -d nginx
echo "Waiting for Nginx to start..."
sleep 5

# Copy configurations
echo "===== Applying Nginx configuration ====="
docker cp tmp_nginx_conf/nginx.env $(docker compose -f "$COMPOSE_FILE" ps -q nginx):/etc/nginx/nginx.env
docker cp tmp_nginx_conf/default.conf $(docker compose -f "$COMPOSE_FILE" ps -q nginx):/etc/nginx/conf.d/default.conf

# Remove any other configuration files that might conflict
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "rm -f /etc/nginx/conf.d/http.conf /etc/nginx/conf.d/https.conf"

# Update main nginx.conf to include env variables
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak && echo 'env VIRTUAL_HOST;' | cat - /etc/nginx/nginx.conf.bak > /etc/nginx/nginx.conf"

# Verify the configuration
echo "===== Verifying Nginx configuration ====="
docker compose -f "$COMPOSE_FILE" exec nginx nginx -t
if [ $? -ne 0 ]; then
    echo "ERROR: Nginx configuration test failed. Rolling back..."
    docker compose -f "$COMPOSE_FILE" exec nginx sh -c "mv /etc/nginx/nginx.conf.bak /etc/nginx/nginx.conf"
    echo "Please check the configuration manually."
    exit 1
fi

# Reload Nginx configuration
echo "===== Reloading Nginx configuration ====="
docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload
echo

# Wait for all services to be fully ready
echo "===== Waiting for all services to be ready ====="
echo "Waiting 15 seconds for services to initialize..."
sleep 15
echo

# Check service status
echo "===== Checking service status ====="
docker compose -f "$COMPOSE_FILE" ps
echo

# Test endpoints
echo "===== Testing endpoints ====="
echo "Testing /api/auth/session endpoint..."
curl -s -I https://brandfocus.ai/api/auth/session || echo "Could not reach session endpoint"
echo
echo "Testing /api/health/ endpoint..."
curl -s -I https://brandfocus.ai/api/health/ || echo "Could not reach API health endpoint"
echo "Testing /api/articles endpoint..."
curl -s -I https://brandfocus.ai/api/articles || echo "Could not reach API articles endpoint"
echo

# Cleanup
rm -rf tmp_nginx_conf

echo "===== Deployment Complete ====="
echo "$(date)"
echo
echo "To verify the fix:"
echo "1. Run the test script: ./scripts/test-nextauth.sh"
echo "2. Check browser console for any errors when logging in"
echo "3. If issues persist, check logs with: docker compose -f $COMPOSE_FILE logs nginx app frontend"
echo
echo "If you need to rollback, restore from the backup in $backup_dir" 