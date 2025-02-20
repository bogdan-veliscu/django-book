#!/bin/bash

# Exit on error
set -e

# Domain names
domains=(brandfocus.ai www.brandfocus.ai)
email="bogdan@codeswiftr.com"
staging=0 # Set to 1 if you want to test with Let's Encrypt staging

# Create directories for certbot
mkdir -p certbot/conf/live/brandfocus.ai
mkdir -p certbot/www

# Stop any running containers
docker compose -f docker-compose.prod.yml down

# Create temporary Nginx config for SSL acquisition
cat > nginx/conf.d/default.conf << EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${domains[0]} www.${domains[0]};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Ready for SSL certificate acquisition';
        add_header Content-Type text/plain;
    }
}
EOF

# Start nginx with minimal config
docker compose -f docker-compose.prod.yml up --force-recreate -d nginx

# Wait for nginx to start
echo "Waiting for nginx to start..."
sleep 5

# Get SSL certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email $email \
    --agree-tos --no-eff-email \
    ${staging:+"--staging"} \
    ${domains[@]/#/-d }

# Stop containers
docker compose -f docker-compose.prod.yml down

# Remove temporary config
rm nginx/conf.d/default.conf

# Start all services with HTTPS
docker compose -f docker-compose.prod.yml up -d

echo "SSL certificates obtained successfully!" 