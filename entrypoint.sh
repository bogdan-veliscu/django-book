#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Activating virtual environment..."
source /code/.venv/bin/activate

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the main container command
echo "Starting application..."
exec "$@"