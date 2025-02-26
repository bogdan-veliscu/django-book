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

# Calculate optimal worker count based on available memory
# For small droplets, use 1 worker to avoid memory issues
# For larger droplets, calculate based on available memory
AVAILABLE_MEMORY_MB=$(free -m | awk '/^Mem:/{print $2}')
log "Available memory: ${AVAILABLE_MEMORY_MB}MB"

# Default to 1 worker for small droplets (less than 2GB)
if [ ${AVAILABLE_MEMORY_MB} -lt 2048 ]; then
    WORKER_COUNT=1
    log "Small droplet detected (< 2GB RAM), using 1 worker"
else
    # For larger droplets, use the WORKERS env var or calculate based on memory
    # Each worker needs about 512MB of memory
    CALCULATED_WORKERS=$((AVAILABLE_MEMORY_MB / 512))
    # Use the smaller of WORKERS env var or calculated value, default to 1
    WORKER_COUNT=${WORKERS:-$CALCULATED_WORKERS}
    # Ensure at least 1 worker
    WORKER_COUNT=$(( WORKER_COUNT > 0 ? WORKER_COUNT : 1 ))
    log "Larger droplet detected, calculated ${CALCULATED_WORKERS} workers"
fi

log "Using ${WORKER_COUNT} workers"

# Set timeout values
TIMEOUT=${TIMEOUT:-60}
GRACEFUL_TIMEOUT=${GRACEFUL_TIMEOUT:-60}
KEEP_ALIVE=${KEEP_ALIVE:-5}
MAX_REQUESTS=${MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-100}

# Start the application
log "Starting application..."
if [ "$1" = "uvicorn" ]; then
    # Handle graceful shutdown
    function graceful_shutdown() {
        log "Received shutdown signal, stopping gracefully..."
        kill -TERM $PID
        wait $PID
    }
    
    # Set up signal handling
    trap graceful_shutdown SIGTERM SIGINT
    
    # Start uvicorn with optimized settings
    exec uvicorn conduit.config.asgi:application \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --workers ${WORKER_COUNT} \
        --log-level info \
        --timeout-keep-alive ${KEEP_ALIVE} \
        --timeout ${TIMEOUT} \
        --limit-max-requests ${MAX_REQUESTS} \
        --limit-max-requests-jitter ${MAX_REQUESTS_JITTER} \
        --backlog 2048 \
        --no-access-log &
    
    PID=$!
    wait $PID
else
    exec "$@"
fi