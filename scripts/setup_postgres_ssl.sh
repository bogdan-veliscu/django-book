#!/bin/bash
set -e

# Configuration
SSL_BASE="postgres/ssl"
SSL_DIR="$SSL_BASE/postgresql"
CERT_FILE="$SSL_DIR/server.crt"
KEY_FILE="$SSL_DIR/server.key"

echo "Starting PostgreSQL SSL setup..."

# Ensure we're in the project root
if [[ ! -d "postgres" ]]; then
    echo "Error: Must be run from project root directory"
    exit 1
fi

# Clean up existing SSL directory and recreate it
echo "Cleaning up existing SSL directory..."
sudo rm -rf "$SSL_BASE"
sudo mkdir -p "$SSL_DIR"

# Generate self-signed certificate if not exists
echo "Generating new SSL certificate and key..."
sudo openssl req -new -x509 -days 365 -nodes \
    -out "$CERT_FILE" \
    -keyout "$KEY_FILE" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set correct ownership and permissions
echo "Setting correct ownership and permissions..."
sudo chown -R 70:70 "$SSL_BASE"
sudo chmod 700 "$SSL_BASE"
sudo chmod 700 "$SSL_DIR"
sudo chmod 600 "$KEY_FILE"
sudo chmod 644 "$CERT_FILE"

echo "PostgreSQL SSL files have been configured with correct permissions."
echo "Certificate: $CERT_FILE"
echo "Private Key: $KEY_FILE"

# Verify the setup
echo "Final permissions:"
sudo ls -la "$SSL_BASE"
sudo ls -la "$SSL_DIR"