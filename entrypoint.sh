#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e
set -x

source /app/.venv/bin/activate

# Run database migrations
echo "Applying database migrations..."
echo python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
echo python manage.py collectstatic --noinput

# Execute the main container command
echo "Starting application..."
exec "$@"