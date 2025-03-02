#!/bin/bash

# Test script for NextAuth configuration
# This script should be run on the production server

set -e

echo "===== Testing NextAuth Configuration ====="
echo "$(date)"
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
echo "1. Check Nginx error logs: docker compose -f docker compose.prod.yml logs nginx"
echo "2. Check frontend logs: docker compose -f docker compose.prod.yml logs frontend"
echo "3. Verify the Nginx configuration is being applied correctly" 