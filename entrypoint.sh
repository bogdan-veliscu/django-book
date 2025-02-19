#!/bin/bash

# Exit on error
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@"
}

# Function to check if PostgreSQL is ready
postgres_ready() {
    python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT:-5432}"
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Function to check if Redis is ready
redis_ready() {
    python << END
import sys
import redis
try:
    r = redis.Redis(
        host="${REDIS_HOST:-redis}",
        port="${REDIS_PORT:-6379}",
        db=0
    )
    r.ping()
except redis.ConnectionError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL
until postgres_ready; do
    log "PostgreSQL is unavailable - sleeping"
    sleep 1
done
log "PostgreSQL is up"

# Wait for Redis
until redis_ready; do
    log "Redis is unavailable - sleeping"
    sleep 1
done
log "Redis is up"

# Ensure we're in the right directory
cd /code/conduit

# Create necessary directories
mkdir -p staticfiles media logs

# Apply database migrations
log "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start the application
log "Starting application..."
if [ "$1" = "uvicorn" ]; then
    exec uvicorn conduit.config.asgi:application \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --workers ${WORKERS:-4} \
        --log-level info
else
    exec "$@"
fi