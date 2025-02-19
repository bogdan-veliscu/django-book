#!/bin/bash

# Install certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
systemctl stop nginx

# Get SSL certificate
certbot certonly --standalone \
  -d brandfocus.ai \
  -d www.brandfocus.ai \
  -d api.brandfocus.ai \
  --email admin@brandfocus.ai \
  --agree-tos \
  --non-interactive

# Start nginx
systemctl start nginx

# Set up auto-renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

echo "SSL certificates have been installed and auto-renewal has been configured." 