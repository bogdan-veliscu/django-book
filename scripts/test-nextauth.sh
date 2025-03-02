#!/bin/bash

# Test script for NextAuth configuration
# This script should be run on the production server

set -e

echo "===== Testing NextAuth Configuration ====="
echo "$(date)"
echo

# Check if docker-compose.prod.yml or docker compose.prod.yml exists
if [ -f "docker-compose.prod.yml" ]; then
  COMPOSE_FILE="docker-compose.prod.yml"
elif [ -f "docker compose.prod.yml" ]; then
  COMPOSE_FILE="docker compose.prod.yml"
else
  echo "Error: Cannot find docker-compose.prod.yml or docker compose.prod.yml"
  exit 1
fi

echo "Using compose file: $COMPOSE_FILE"
echo

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    echo "Testing $endpoint endpoint..."
    echo "------------------------------------"
    curl -v -k "https://brandfocus.ai$endpoint" 2>&1 | grep -v "Authorization" | grep -E "HTTP|location|^< "
    echo "------------------------------------"
    echo
}

# Test all critical NextAuth endpoints
test_endpoint "/api/auth/session"
test_endpoint "/api/auth/csrf"
test_endpoint "/api/auth/providers"

# Test with trailing slashes to ensure they work too
echo "Testing with trailing slashes..."
test_endpoint "/api/auth/session/"
test_endpoint "/api/auth/csrf/"

echo "===== Test Complete ====="
echo "$(date)"
echo
echo "If you see 308 redirects in the output, the issue is still present."
echo "If you see 200 OK responses, the fix has been applied successfully."
echo
echo "Next steps if issues persist:"
echo "1. Check Nginx error logs: docker compose -f $COMPOSE_FILE logs nginx"
echo "2. Check frontend logs: docker compose -f $COMPOSE_FILE logs frontend"
echo "3. Verify the Nginx configuration is being applied correctly" 