#!/bin/bash

# Exit on error
set -e

echo "Starting NextAuth fix deployment..."

# Stop all services to ensure clean state
echo "Stopping all services..."
docker compose -f docker-compose.prod.yml down

# Create backup of current Nginx configuration
echo "Creating backup of current Nginx configuration..."
BACKUP_DIR="nginx_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp nginx/templates/https.conf.template "$BACKUP_DIR/"

# Ensure Nginx environment variables are set
echo "Setting up Nginx environment variables..."
cat > nginx.env << EOL
VIRTUAL_HOST=brandfocus.ai
EOL

# Create Docker network if it doesn't exist
echo "Creating Docker network..."
docker network create nginx-proxy || true

# Check Docker networks
echo "Checking Docker networks..."
docker network ls

# Start services in the correct order
echo "Starting services in correct order..."

# Start database and Redis first
echo "Starting database and Redis..."
docker compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! docker compose -f docker-compose.prod.yml exec db pg_isready; do
    echo "Database not ready yet, waiting..."
    sleep 5
done
echo "Database is ready."

# Start the backend
echo "Starting backend service..."
docker compose -f docker-compose.prod.yml up -d app

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec app curl -s http://localhost:8000/api/health/ > /dev/null; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Backend health check timed out, continuing anyway..."
        break
    fi
    echo "Backend not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Backend is ready or timeout occurred."

# Start the frontend
echo "Starting frontend service..."
docker compose -f docker-compose.prod.yml up -d frontend

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec frontend curl -s http://localhost:3000/health > /dev/null; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Frontend health check timed out, continuing anyway..."
        break
    fi
    echo "Frontend not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Frontend is ready or timeout occurred."

# Connect services to the nginx-proxy network
echo "Connecting services to nginx-proxy network..."
docker network connect nginx-proxy app || true
docker network connect nginx-proxy frontend || true
docker network connect nginx-proxy db || true
docker network connect nginx-proxy redis || true

# List running containers
echo "Listing running containers..."
docker compose -f docker-compose.prod.yml ps

# Rebuild and start Nginx last
echo "Rebuilding and starting Nginx..."
docker compose -f docker-compose.prod.yml up -d --build nginx

# Wait for Nginx to be ready
echo "Waiting for Nginx to be ready..."
COUNTER=0
MAX_TRIES=10
while ! docker compose -f docker-compose.prod.yml exec nginx nginx -t; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Nginx configuration test timed out, continuing anyway..."
        break
    fi
    echo "Nginx not ready yet, waiting... (attempt $COUNTER of $MAX_TRIES)"
    sleep 5
done
echo "Nginx is ready or timeout occurred."

# Test critical endpoints
echo "Testing critical endpoints..."
curl -s -I https://brandfocus.ai/api/health/ || echo "Health check failed"
curl -s -I https://brandfocus.ai/api/auth/session || echo "Session endpoint check failed"

# Ensure frontend can resolve itself without going through Nginx
echo "Preventing circular requests by updating hosts file in frontend container..."
docker compose -f docker-compose.prod.yml exec frontend sh -c "echo '127.0.0.1 brandfocus.ai www.brandfocus.ai' >> /etc/hosts"

# After starting all services, verify NextAuth connectivity
echo "===== VERIFYING NEXTAUTH CONNECTIVITY ====="

# Wait for a moment to make sure all services are ready
sleep 10

# Check the session endpoint directly from inside the frontend container
echo "Testing NextAuth session endpoint from inside frontend container..."
docker compose -f docker-compose.prod.yml exec frontend curl -v http://localhost:3000/api/auth/session

# Test the session endpoint through Nginx
echo "Testing NextAuth session endpoint through Nginx..."
curl -v https://${DOMAIN}/api/auth/session --insecure

# View the frontend logs for any NextAuth errors
echo "Checking frontend logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml logs --tail=50 frontend | grep -i "auth\|next"

# View Nginx logs
echo "Checking Nginx logs for errors..."
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/error.log | tail -n 50

# Add header debugging to detect any issues
echo "===== HEADER SIZE ANALYSIS ====="
docker compose -f docker-compose.prod.yml exec frontend curl -s -D - http://localhost:3000/api/auth/session -o /dev/null | wc -c
echo "Header size in bytes (should be less than 8192 for default Node.js)"

echo "Testing with simplified headers..."
docker compose -f docker-compose.prod.yml exec frontend curl -s -D - -H "Host: localhost" http://localhost:3000/api/auth/session -o /dev/null | wc -c

echo "Deployment completed. Check the logs for any issues:"
echo "docker compose -f docker-compose.prod.yml logs -f"

# Add direct NextAuth endpoint testing with minimal headers
echo "===== DETAILED NEXTAUTH DEBUGGING ====="

# Check the raw session response - no proxy, no complex headers
echo "Testing raw session endpoint response (should be valid JSON):"
docker compose -f docker-compose.prod.yml exec frontend curl -s http://localhost:3000/api/auth/session | jq . || echo "Invalid JSON returned"

# Test with explicit Accept header to ensure proper content negotiation
echo "Testing with explicit Accept header:"
docker compose -f docker-compose.prod.yml exec frontend curl -s -H "Accept: application/json" http://localhost:3000/api/auth/session | jq . || echo "Invalid JSON returned"

# Try a session POST request (which NextAuth uses internally)
echo "Testing session endpoint with POST method:"
docker compose -f docker-compose.prod.yml exec frontend curl -s -X POST -H "Content-Type: application/json" -d '{}' http://localhost:3000/api/auth/session | jq . || echo "Invalid JSON returned"

# Check direct session access from Nginx
echo "Testing session endpoint through Nginx (direct):"
docker compose -f docker-compose.prod.yml exec nginx curl -s http://frontend:3000/api/auth/session | jq . || echo "Invalid JSON returned"

# View the frontend logs for any NextAuth errors
echo "Checking frontend logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml logs --tail=50 frontend | grep -i "auth\|next"

# Add specific testing for AuthJS pattern mismatch issue
echo "===== TESTING FOR STRING PATTERN MISMATCH ====="

# Test session response format with schema validation
echo "Creating test file to validate session response format..."
docker compose -f docker-compose.prod.yml exec frontend sh -c "cat > /tmp/validate-session.js << 'EOF'
const http = require('http');

http.get('http://localhost:3000/api/auth/session', (res) => {
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('STATUS CODE:', res.statusCode);
    console.log('HEADERS:', JSON.stringify(res.headers, null, 2));
    
    try {
      const parsed = JSON.parse(data);
      console.log('VALID JSON: true');
      console.log('RESPONSE:', JSON.stringify(parsed, null, 2));
      
      // Check for expected session format
      if (typeof parsed === 'object' && (parsed === null || 'expires' in parsed)) {
        console.log('EXPECTED FORMAT: true (matches NextAuth session format)');
      } else {
        console.log('EXPECTED FORMAT: false (does not match NextAuth session format)');
        console.log('EXPECTED: A null object or an object with \'expires\' property');
      }
    } catch (e) {
      console.log('VALID JSON: false');
      console.log('ERROR:', e.message);
      console.log('RAW RESPONSE:', data);
    }
  });
}).on('error', (e) => {
  console.error('ERROR:', e.message);
});
EOF"

# Run the validation script
echo "Running session validation test..."
docker compose -f docker-compose.prod.yml exec frontend node /tmp/validate-session.js

# View NextAuth specific logs
echo "Checking for NextAuth errors in logs..."
docker compose -f docker-compose.prod.yml logs --tail=100 frontend | grep -i "error\|warn\|auth"

# View the frontend logs for any NextAuth errors
echo "Checking frontend logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml logs --tail=50 frontend | grep -i "auth\|next"

# Create advanced NextAuth diagnostics tools
echo "===== CREATING COMPREHENSIVE NEXTAUTH DIAGNOSTICS ====="

# Create a detailed diagnostic script in the frontend container
echo "Creating advanced NextAuth diagnostic tool..."
docker compose -f docker-compose.prod.yml exec frontend sh -c "cat > /tmp/nextauth-debug.js << 'EOF'
const http = require('http');
const https = require('https');
const fs = require('fs');
const process = require('process');

// Configuration
const endpoints = [
  { name: 'Direct Session', url: 'http://localhost:3000/api/auth/session' },
  { name: 'Proxy Session', url: 'https://brandfocus.ai/api/auth/session', ignoreCert: true },
  { name: 'Direct Signin', url: 'http://localhost:3000/api/auth/signin' },
  { name: 'Proxy Signin', url: 'https://brandfocus.ai/api/auth/signin', ignoreCert: true },
  { name: 'Debug Endpoint', url: 'https://brandfocus.ai/api/auth-debug', ignoreCert: true }
];

// Helper to write results to file
const outputFile = '/tmp/nextauth-diagnostics.log';
fs.writeFileSync(outputFile, `NextAuth Diagnostics - ${new Date().toISOString()}\n\n`);

function appendLog(message) {
  fs.appendFileSync(outputFile, message + '\n');
  console.log(message);
}

// Print environment variables related to NextAuth
appendLog('=== NEXTAUTH ENVIRONMENT VARIABLES ===');
Object.keys(process.env)
  .filter(key => key.includes('AUTH') || key.includes('NEXT') || key.includes('NODE'))
  .forEach(key => {
    appendLog(`${key}=${process.env[key]}`);
  });
appendLog('\n');

// Test each endpoint
async function testEndpoints() {
  appendLog('=== ENDPOINT TESTS ===\n');
  
  for (const endpoint of endpoints) {
    appendLog(`Testing ${endpoint.name}: ${endpoint.url}`);
    
    const options = {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'NextAuth-Debug-Script',
      },
      rejectUnauthorized: !endpoint.ignoreCert
    };
    
    const client = endpoint.url.startsWith('https') ? https : http;
    
    try {
      await new Promise((resolve, reject) => {
        const req = client.request(endpoint.url, options, (res) => {
          appendLog(`Status: ${res.statusCode}`);
          appendLog(`Headers: ${JSON.stringify(res.headers, null, 2)}`);
          
          let body = '';
          res.on('data', chunk => { body += chunk; });
          
          res.on('end', () => {
            appendLog('Response Body:');
            try {
              const parsedBody = JSON.parse(body);
              appendLog(JSON.stringify(parsedBody, null, 2));
              
              // Validate NextAuth session format
              if (endpoint.url.includes('session')) {
                if (parsedBody === null || (typeof parsedBody === 'object' && 'expires' in parsedBody)) {
                  appendLog('✅ Valid NextAuth session format');
                } else {
                  appendLog('❌ Invalid NextAuth session format! Expected null or object with expires property');
                  appendLog('This is likely the source of the string pattern mismatch error');
                }
              }
            } catch (e) {
              appendLog(`Failed to parse JSON: ${e.message}`);
              appendLog('Raw body:');
              appendLog(body);
            }
            appendLog('\n---\n');
            resolve();
          });
        });
        
        req.on('error', (error) => {
          appendLog(`Request error: ${error.message}`);
          appendLog('\n---\n');
          resolve(); // Continue with other tests even if this one fails
        });
        
        req.end();
      });
    } catch (error) {
      appendLog(`Test error: ${error.message}`);
      appendLog('\n---\n');
    }
  }
  
  appendLog('All tests completed. Full diagnostic log saved to ' + outputFile);
}

testEndpoints();
EOF"

# Run the advanced diagnostics
echo "Running advanced NextAuth diagnostics..."
docker compose -f docker-compose.prod.yml exec frontend node /tmp/nextauth-debug.js

# Extract the diagnostic logs
echo "Extracting NextAuth diagnostic logs..."
docker compose -f docker-compose.prod.yml exec frontend cat /tmp/nextauth-diagnostics.log

# Check Nginx logs specifically for NextAuth errors
echo "Checking Nginx logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml exec nginx sh -c "mkdir -p /var/log/nginx && touch /var/log/nginx/session_error.log && cat /var/log/nginx/session_error.log"

# View the frontend logs for any NextAuth errors
echo "Checking frontend logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml logs --tail=50 frontend | grep -i "auth\|next"

# Add a command to check NextAuth implementation in the frontend code
echo "===== EXAMINING FRONTEND AUTH IMPLEMENTATION ====="

# Find the NextAuth configuration files
echo "Looking for NextAuth configuration files..."
docker compose -f docker-compose.prod.yml exec frontend find /app -type f -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | grep -i auth | xargs grep -l "NextAuth\|AuthOptions\|getSession" || echo "No NextAuth files found"

# Check the NextAuth provider configuration
echo "Examining NextAuth provider configuration..."
docker compose -f docker-compose.prod.yml exec frontend sh -c "find /app -type f -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' | xargs grep -l 'NextAuth\\|getSession' | xargs cat" | grep -A 20 "NextAuth\|providers\|session"

# Create a temporary direct proxy for authentication
echo "===== CREATING TEMPORARY AUTH WORKAROUND ====="
echo "Setting up temporary fix for session endpoint..."

# Create emergency proxy implementation
docker compose -f docker-compose.prod.yml exec frontend sh -c "cat > /tmp/auth-fix.js << 'EOF'
// Emergency session fix script
const http = require('http');

const server = http.createServer((req, res) => {
  console.log('[Auth Fix] Received request:', req.method, req.url);
  
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Handle OPTIONS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }
  
  // Only handle /api/auth/session
  if (req.url === '/api/auth/session') {
    console.log('[Auth Fix] Serving emergency session data');
    
    // Respond with a valid null session format
    res.setHeader('Content-Type', 'application/json');
    res.writeHead(200);
    res.end(JSON.stringify(null));
  } 
  // Alternative: respond with a mock session
  else if (req.url === '/api/auth/mock-session') {
    console.log('[Auth Fix] Serving mock session data');
    
    const mockSession = {
      user: { name: 'Emergency User', email: 'emergency@example.com' },
      expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    };
    
    res.setHeader('Content-Type', 'application/json');
    res.writeHead(200);
    res.end(JSON.stringify(mockSession));
  } 
  else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(3333, () => {
  console.log('[Auth Fix] Emergency auth server running on port 3333');
});
EOF"

# Start the emergency auth server
echo "Starting emergency auth server on port 3333..."
docker compose -f docker-compose.prod.yml exec -d frontend node /tmp/auth-fix.js

# Continue with the regular diagnostics
echo "Proceeding with regular diagnostics..."

# View the frontend logs for any NextAuth errors
echo "Checking frontend logs for NextAuth errors..."
docker compose -f docker-compose.prod.yml logs --tail=50 frontend | grep -i "auth\|next" 