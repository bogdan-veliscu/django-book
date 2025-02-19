#!/bin/bash
set -e

# Configuration
SSL_DIR="postgres/ssl/postgresql"
CERT_FILE="$SSL_DIR/server.crt"
KEY_FILE="$SSL_DIR/server.key"

# Ensure we're in the project root
if [[ ! -d "postgres" ]]; then
    echo "Error: Must be run from project root directory"
    exit 1
fi

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Generate self-signed certificate if not exists
if [[ ! -f "$CERT_FILE" ]] || [[ ! -f "$KEY_FILE" ]]; then
    echo "Generating new SSL certificate and key..."
    openssl req -new -x509 -days 365 -nodes \
        -out "$CERT_FILE" \
        -keyout "$KEY_FILE" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Set proper permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

# Create a temporary Docker container to set proper ownership
echo "Setting correct ownership using Docker..."
docker run --rm \
    -v "$(pwd)/$SSL_DIR:/ssl" \
    postgres:15 \
    /bin/bash -c 'chown postgres:postgres /ssl/server.key /ssl/server.crt && chmod 600 /ssl/server.key && chmod 644 /ssl/server.crt'

echo "PostgreSQL SSL files have been configured with correct permissions."
echo "Certificate: $CERT_FILE"
echo "Private Key: $KEY_FILE"

# Verify the setup
ls -la "$SSL_DIR" 