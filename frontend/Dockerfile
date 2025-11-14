# Multi-stage build for production-optimized Lit frontend

# ============================================
# Stage 1: Build Stage
# ============================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# Using npm ci for faster, reproducible builds in production
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Build argument for API URL
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
# This creates the dist/ directory with optimized production files
RUN npm run build

# ============================================
# Stage 2: Production Stage
# ============================================
FROM nginx:1.25-alpine

# Install wget for healthchecks
RUN apk add --no-cache wget

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built static files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add health check endpoint
RUN echo '<!DOCTYPE html><html><body>OK</body></html>' > /usr/share/nginx/html/health

# Set correct permissions
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]

# Metadata
LABEL maintainer="Conduit Team" \
      version="2.0" \
      description="Production Nginx server for Conduit Lit PWA frontend"
