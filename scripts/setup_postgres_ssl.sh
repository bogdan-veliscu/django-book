#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p postgres/ssl

# Generate self-signed certificate
openssl req -new -x509 -days 365 -nodes \
  -out postgres/ssl/server.crt \
  -keyout postgres/ssl/server.key \
  -subj "/CN=db"

# Set correct permissions
chmod 600 postgres/ssl/server.key
chmod 644 postgres/ssl/server.crt

# Create directory for certificates in PostgreSQL config
mkdir -p postgres/ssl/postgresql

# Copy certificates to PostgreSQL config directory
cp postgres/ssl/server.crt postgres/ssl/postgresql/
cp postgres/ssl/server.key postgres/ssl/postgresql/

echo "PostgreSQL SSL certificates have been generated successfully." 