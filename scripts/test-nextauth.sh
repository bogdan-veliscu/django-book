#!/bin/bash

# Test script for NextAuth configuration
# This script should be run on the production server

set -e

echo "===== Testing NextAuth Configuration ====="
echo "$(date)"
echo

# Test the session endpoint
echo "Testing /api/auth/session endpoint..."
curl -v -k https://brandfocus.ai/api/auth/session 2>&1 | grep -v "Authorization"
echo

# Test the CSRF endpoint
echo "Testing /api/auth/csrf endpoint..."
curl -v -k https://brandfocus.ai/api/auth/csrf 2>&1 | grep -v "Authorization"
echo

echo "===== Test Complete ====="
echo "$(date)"
echo
echo "If you see 308 redirects in the output, the issue is still present."
echo "If you see 200 OK responses, the fix has been applied successfully." 