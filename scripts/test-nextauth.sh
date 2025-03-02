#!/bin/bash

# NextAuth and Nginx Configuration Test Script
# This script tests various endpoints to verify the NextAuth integration

set -e

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Starting NextAuth Integration Tests =====${NC}"
echo "$(date)"
echo

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -e "${YELLOW}Testing $description${NC}"
    echo "Endpoint: $endpoint"
    
    # Get status code and headers
    response=$(curl -s -I "$endpoint")
    status=$(echo "$response" | head -n 1 | cut -d' ' -f2)
    
    if [[ "$status" == "$expected_status" ]]; then
        echo -e "${GREEN}✓ Success: Status $status${NC}"
    else
        echo -e "${RED}✗ Failed: Expected status $expected_status, got $status${NC}"
        echo "Response headers:"
        echo "$response"
    fi
    echo
}

# Test NextAuth session endpoint
test_endpoint "https://brandfocus.ai/api/auth/session" "200" "NextAuth Session Endpoint"

# Test NextAuth CSRF endpoint
test_endpoint "https://brandfocus.ai/api/auth/csrf" "200" "NextAuth CSRF Endpoint"

# Test NextAuth providers endpoint
test_endpoint "https://brandfocus.ai/api/auth/providers" "200" "NextAuth Providers Endpoint"

# Test Next.js static assets
test_endpoint "https://brandfocus.ai/_next/static/chunks/main.js" "200" "Next.js Static Assets"

# Test Django API endpoint
test_endpoint "https://brandfocus.ai/api/health/" "200" "Django API Health Endpoint"

# Test frontend
test_endpoint "https://brandfocus.ai/" "200" "Frontend Application"

echo -e "${YELLOW}===== Testing CORS Headers =====${NC}"
# Test CORS headers for NextAuth
cors_response=$(curl -s -X OPTIONS -I -H "Origin: https://example.com" -H "Access-Control-Request-Method: GET" https://brandfocus.ai/api/auth/session)
allow_origin=$(echo "$cors_response" | grep -i "Access-Control-Allow-Origin")

if [[ -n "$allow_origin" ]]; then
    echo -e "${GREEN}✓ CORS headers are present${NC}"
    echo "$allow_origin"
else
    echo -e "${RED}✗ CORS headers are missing${NC}"
    echo "Response headers:"
    echo "$cors_response"
fi
echo

echo -e "${YELLOW}===== Testing Redirect Behavior =====${NC}"
# Test trailing slash behavior
redirect_response=$(curl -s -I -L "https://brandfocus.ai/api/auth/session/")
redirect_count=$(echo "$redirect_response" | grep -c "HTTP/")

if [[ "$redirect_count" -gt 1 ]]; then
    echo -e "${RED}✗ Redirect loop detected${NC}"
    echo "Response headers:"
    echo "$redirect_response"
else
    echo -e "${GREEN}✓ No redirect loop${NC}"
fi
echo

echo -e "${YELLOW}===== Summary =====${NC}"
echo "If all tests passed, your NextAuth integration should be working correctly."
echo "If you encountered any failures, check the following:"
echo "1. Nginx configuration for proper location blocks"
echo "2. CORS headers configuration"
echo "3. NextAuth.js configuration in your frontend app"
echo "4. Nginx logs: docker compose -f docker-compose.prod.yml logs nginx"
echo "5. Frontend logs: docker compose -f docker-compose.prod.yml logs frontend"
echo

echo -e "${YELLOW}===== Test Completed =====${NC}"
echo "$(date)" 