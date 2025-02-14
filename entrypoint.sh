#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if postgres is ready
postgres_ready() {
python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST:-db}",
        port="${POSTGRES_PORT:-5432}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for postgres to become available
until postgres_ready; do
  echo "Waiting for PostgreSQL to become available..."
  sleep 2
done
echo "PostgreSQL is available"

# Change to the application directory
cd /code

# Apply database migrations
echo "Applying database migrations..."
python -m conduit.manage migrate --noinput

# Collect static files
echo "Collecting static files..."
python -m conduit.manage collectstatic --noinput

# Create cache table
echo "Creating cache table..."
python -m conduit.manage createcachetable

# Start the application
echo "Starting the application..."
exec "$@"