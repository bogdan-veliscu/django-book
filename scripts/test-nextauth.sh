#!/bin/bash

# Test script for NextAuth configuration
# This script tests the NextAuth endpoints to ensure they're working correctly

set -e

echo "===== Starting NextAuth Configuration Test ====="
echo "$(date)"
echo

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
  local endpoint=$1
  local expected_status=$2
  local description=$3
  
  echo -e "${YELLOW}Testing $description: $endpoint${NC}"
  
  # Make the request and capture the status code
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://brandfocus.ai$endpoint")
  
  if [ "$status" = "$expected_status" ]; then
    echo -e "${GREEN}✓ Success: $endpoint returned $status (expected $expected_status)${NC}"
    return 0
  else
    echo -e "${RED}✗ Failed: $endpoint returned $status (expected $expected_status)${NC}"
    return 1
  fi
}

# Test NextAuth session endpoint
test_endpoint "/api/auth/session" "200" "NextAuth session endpoint"

# Test NextAuth CSRF endpoint
test_endpoint "/api/auth/csrf" "200" "NextAuth CSRF endpoint"

# Test NextAuth signin endpoint
test_endpoint "/api/auth/signin" "200" "NextAuth signin endpoint"

# Test NextAuth callback endpoint (should redirect or return 404 if no provider specified)
test_endpoint "/api/auth/callback" "404" "NextAuth callback endpoint"

# Test API endpoint
test_endpoint "/api/health/" "200" "Django API health endpoint"

echo
echo "===== NextAuth Configuration Test Complete ====="
echo "$(date)"
echo

# Check if all tests passed
if [ $? -eq 0 ]; then
  echo -e "${GREEN}All tests passed! NextAuth is configured correctly.${NC}"
  echo
  echo "You can now verify the authentication flow by:"
  echo "1. Visiting https://brandfocus.ai and logging in"
  echo "2. Checking that you remain logged in after page refreshes"
  echo "3. Verifying that protected routes work correctly"
else
  echo -e "${RED}Some tests failed. Please check the Nginx configuration and NextAuth setup.${NC}"
  echo
  echo "Troubleshooting steps:"
  echo "1. Check Nginx logs: docker compose -f docker-compose.prod.yml logs nginx"
  echo "2. Check Frontend logs: docker compose -f docker-compose.prod.yml logs frontend"
  echo "3. Verify the Nginx configuration: docker compose -f docker-compose.prod.yml exec nginx nginx -T"
  echo "4. Check for any CORS errors in the browser console"
fi

exit 0 