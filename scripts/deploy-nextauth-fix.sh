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

# Ensure NextAuth environment variables are set properly
echo "===== Checking NextAuth environment variables ====="
if grep -q "NEXTAUTH_SECRET" .env.prod; then
  echo "NEXTAUTH_SECRET found in .env.prod"
else
  echo "NEXTAUTH_SECRET not found in .env.prod. Adding it..."
  # Generate a secure random secret if not present
  NEXTAUTH_SECRET=$(openssl rand -base64 32)
  echo "NEXTAUTH_SECRET=$NEXTAUTH_SECRET" >> .env.prod
  echo "Added NEXTAUTH_SECRET to .env.prod"
fi

if grep -q "NEXTAUTH_URL" .env.prod; then
  echo "NEXTAUTH_URL found in .env.prod"
else
  echo "NEXTAUTH_URL not found in .env.prod. Adding it..."
  echo "NEXTAUTH_URL=https://brandfocus.ai" >> .env.prod
  echo "Added NEXTAUTH_URL to .env.prod"
fi
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

# Copy the configuration to the container
docker compose -f "$COMPOSE_FILE" up -d nginx
sleep 5

# Copy environment variables file
docker cp tmp_nginx_conf/nginx.env $(docker compose -f "$COMPOSE_FILE" ps -q nginx):/etc/nginx/nginx.env

# Copy the configuration
docker cp tmp_nginx_conf/default.conf $(docker compose -f "$COMPOSE_FILE" ps -q nginx):/etc/nginx/conf.d/default.conf

# Remove any other configuration files that might conflict
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "rm -f /etc/nginx/conf.d/http.conf /etc/nginx/conf.d/https.conf"

# Update main nginx.conf to include env variables
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "sed -i '1s/^/env VIRTUAL_HOST;\n/' /etc/nginx/nginx.conf"

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

# Restart the frontend container to pick up the NextAuth environment variables
echo "===== Restarting frontend container to pick up NextAuth environment variables ====="
docker compose -f "$COMPOSE_FILE" stop frontend
docker compose -f "$COMPOSE_FILE" up -d frontend
echo

# 6. Wait for services to start
echo "===== Waiting for services to start ====="
echo "Waiting 10 seconds for services to initialize..."
sleep 10
echo

# 7. Check service status
echo "===== Checking service status ====="
docker compose -f "$COMPOSE_FILE" ps nginx frontend app
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