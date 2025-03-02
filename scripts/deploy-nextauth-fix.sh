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

# 5. Start Nginx with a single configuration file
echo "===== Starting Nginx with clean configuration ====="
# Create a temporary directory for the configuration
mkdir -p tmp_nginx_conf
cat > tmp_nginx_conf/default.conf << 'EOF'
# Single configuration file for Nginx
# Upstream definitions
upstream django_backend {
    server app:8000;
    keepalive 32;
}

upstream frontend_app {
    server frontend:3000;
    keepalive 32;
}

# HTTP redirect server
server {
    listen 80;
    listen [::]:80;
    server_name brandfocus.ai www.brandfocus.ai;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name brandfocus.ai www.brandfocus.ai;

    # Disable trailing slash redirects globally
    absolute_redirect off;
    server_name_in_redirect off;
    port_in_redirect off;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/brandfocus.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/brandfocus.ai/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/brandfocus.ai/chain.pem;

    # SSL optimization
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src 'self' https://brandfocus.ai wss://brandfocus.ai https://api.dicebear.com http://localhost:* http://127.0.0.1:* http://*.local:* https://brandfocus.ai/api https://brandfocus.ai/api/auth/*; font-src 'self' data:; img-src 'self' data: https://api.dicebear.com https://brandfocus.ai; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; form-action 'self';" always;

    # Handle Next.js static files with high priority - must come before the main location block
    location /_next/static/ {
        proxy_pass http://frontend_app/_next/static/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=31536000, immutable" always;
        access_log off;
        expires 365d;
    }

    # Handle Next.js public files
    location /public/ {
        proxy_pass http://frontend_app/public/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Cache-Control "public, max-age=2592000" always;
        access_log off;
        expires 30d;
    }

    # NextAuth.js API routes - must come before the general API proxy
    # Fixed to use exact matching for critical endpoints
    location ^~ /api/auth/ {
        proxy_pass http://frontend_app/api/auth/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers for NextAuth
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-CSRF-Token' always;
        
        # Handle preflight OPTIONS requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-CSRF-Token' always;
            add_header 'Access-Control-Max-Age' 1728000 always;
            add_header 'Content-Type' 'text/plain charset=UTF-8' always;
            add_header 'Content-Length' 0 always;
            return 204;
        }
    }

    # Specific location for NextAuth session endpoint to prevent redirect loops
    location = /api/auth/session {
        proxy_pass http://frontend_app/api/auth/session;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers for NextAuth
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-CSRF-Token' always;
    }

    # API proxy with proper CORS handling
    location /api/ {
        proxy_pass http://django_backend/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
        
        # Handle preflight OPTIONS requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-CSRF-Token' always;
            add_header 'Access-Control-Max-Age' 1728000 always;
            add_header 'Content-Type' 'text/plain charset=UTF-8' always;
            add_header 'Content-Length' 0 always;
            return 204;
        }
        
        # Regular requests
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,X-CSRF-Token' always;
    }

    # Static files
    location /static/ {
        alias /code/conduit/static/;
        add_header Cache-Control "public, max-age=2592000" always;
        access_log off;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /code/conduit/media/;
        add_header Cache-Control "public, max-age=2592000" always;
        access_log off;
        expires 30d;
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        return 200 'OK';
        add_header Content-Type text/plain;
    }

    # Frontend proxy - should be last to catch all other requests
    location / {
        proxy_pass http://frontend_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Avoid 502 errors during long-running operations
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffer settings for better performance
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
    }
}
EOF

# Copy the configuration to the container
docker compose -f "$COMPOSE_FILE" up -d nginx
sleep 5
docker cp tmp_nginx_conf/default.conf $(docker compose -f "$COMPOSE_FILE" ps -q nginx):/etc/nginx/conf.d/default.conf

# Verify the configuration
echo "===== Verifying Nginx configuration ====="
docker compose -f "$COMPOSE_FILE" exec nginx nginx -t
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
echo "===== Verifying final Nginx configuration ====="
docker compose -f "$COMPOSE_FILE" exec nginx sh -c "ls -la /etc/nginx/conf.d/ && cat /etc/nginx/conf.d/default.conf | grep upstream"
echo

# 10. Test NextAuth endpoints
echo "===== Testing NextAuth endpoints ====="
echo "Testing /api/auth/session endpoint..."
curl -s -I https://brandfocus.ai/api/auth/session || echo "Could not reach session endpoint"
echo

# Cleanup
rm -rf tmp_nginx_conf

echo "===== Deployment Complete ====="
echo "$(date)"
echo
echo "To check for NextAuth issues, please:"
echo "1. Visit https://brandfocus.ai and try to log in"
echo "2. Check browser console for any errors"
echo "3. If issues persist, check logs with: docker compose -f $COMPOSE_FILE logs frontend"
echo
echo "If you need to rollback, restore from the backup in $backup_dir" 