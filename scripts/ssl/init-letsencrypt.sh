#!/bin/bash

# Exit on error
set -e

# Configuration
domain="brandfocus.ai"
email="bogdan@codeswiftr.com"
staging=0

# Create required directories with proper permissions
sudo mkdir -p certbot/www certbot/conf/live/$domain
sudo mkdir -p nginx/conf.d nginx/templates
sudo chown -R $USER:$USER certbot nginx

# Create temporary Nginx config template for SSL acquisition
cat > nginx/templates/init.conf.template << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Ready for SSL acquisition';
        add_header Content-Type text/plain;
    }
}
EOF

# Create temporary docker-compose file for SSL setup
cat > docker-compose.ssl.yml << EOF
services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/templates:/etc/nginx/templates:ro
      - ./certbot/www:/var/www/certbot:ro
      - ./nginx/conf.d:/etc/nginx/conf.d
    environment:
      - DOMAIN=$domain
    command: sh -c "envsubst '\$\$DOMAIN' < /etc/nginx/templates/init.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"

  certbot:
    image: certbot/certbot:latest
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
EOF

# Stop any running containers
docker compose -f docker-compose.prod.yml down || true

# Start nginx with minimal config
docker compose -f docker-compose.ssl.yml up -d nginx

echo "Waiting for nginx to start..."
sleep 5

# Request the certificate
docker compose -f docker-compose.ssl.yml run --rm certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email $email \
    --agree-tos --no-eff-email \
    ${staging:+"--staging"} \
    -d $domain

# Clean up
docker compose -f docker-compose.ssl.yml down
rm docker-compose.ssl.yml

echo "SSL certificates obtained successfully!"
echo "Starting production services..."

# Start production services
docker compose -f docker-compose.prod.yml up -d 