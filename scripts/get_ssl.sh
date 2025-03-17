#!/bin/bash

# Install certbot and nginx plugin
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot certonly --nginx \
  -d brandfocus.ai \
  -d www.brandfocus.ai \
  -d api.brandfocus.ai \
  --agree-tos \
  --non-interactive \
  --email admin@brandfocus.ai

# Set up auto-renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

echo "SSL certificates have been installed and auto-renewal has been configured."
echo "Certificates are stored in /etc/letsencrypt/live/brandfocus.ai/" 