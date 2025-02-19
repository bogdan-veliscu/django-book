#!/bin/bash
set -e

# Create SSL directory if it doesn't exist
mkdir -p postgres/ssl/postgresql

# Generate self-signed certificate if not exists
if [ ! -f postgres/ssl/postgresql/server.crt ]; then
    openssl req -new -x509 -days 365 -nodes \
        -out postgres/ssl/postgresql/server.crt \
        -keyout postgres/ssl/postgresql/server.key \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Set correct permissions
chmod 600 postgres/ssl/postgresql/server.key
chmod 644 postgres/ssl/postgresql/server.crt

# Create a Docker container to set proper ownership
docker run --rm \
    -v $(pwd)/postgres/ssl/postgresql:/ssl \
    postgres:15 \
    /bin/bash -c 'chown 70:70 /ssl/server.key /ssl/server.crt'

echo "PostgreSQL SSL files have been configured with correct permissions." 