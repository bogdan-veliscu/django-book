# Production Deployment Guide

This guide covers deploying the Conduit application (FastAPI backend + Lit frontend) to production using Docker Compose.

## Files Created

### 1. **docker-compose.prod.yml**
Production-ready Docker Compose configuration with:
- PostgreSQL 15 (Alpine) with health checks
- Redis 7 (Alpine) with persistence and memory limits
- FastAPI backend with production settings
- Nginx serving the Lit frontend with API proxying
- Proper networking and volume management
- Restart policies for high availability

### 2. **frontend/Dockerfile**
Multi-stage Dockerfile for the Lit frontend:
- **Stage 1 (builder)**: Builds the Vite application
- **Stage 2 (production)**: Nginx serving optimized static files
- Includes health check endpoint
- Optimized for minimal image size

### 3. **frontend/nginx.conf**
Nginx configuration featuring:
- SPA routing (all routes fallback to index.html)
- API proxying to FastAPI backend
- WebSocket support
- Gzip compression
- Aggressive caching for static assets
- Security headers
- SSL/TLS configuration (commented, ready to enable)

### 4. **.env.example**
Complete environment variable template with:
- Database configuration
- Redis settings
- Authentication secrets
- CORS configuration
- AWS S3 settings (optional)
- Cache TTL settings
- Detailed comments and security notes

### 5. **frontend/.env.example**
Frontend environment variables:
- VITE_API_URL for backend API connection
- Build-time environment variable instructions

### 6. **docker-compose.yml** (updated)
Added development-specific comments to distinguish from production setup.

## Quick Start Deployment

### Prerequisites
- Docker and Docker Compose installed
- Domain name configured (for production with SSL)
- SSL certificates (optional, for HTTPS)

### Step 1: Configure Environment Variables

```bash
# Copy and configure backend environment
cp .env.example .env

# Edit .env and set secure values
nano .env
```

**Critical settings to change:**
```bash
# Generate a secure secret key (must be at least 32 characters)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Set strong database password
POSTGRES_PASSWORD=your-very-secure-password

# Configure CORS for your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Set API URL for frontend
VITE_API_URL=https://yourdomain.com
```

### Step 2: Build and Start Services

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Start in detached mode
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 3: Verify Deployment

```bash
# Check all services are healthy
docker-compose -f docker-compose.prod.yml ps

# Test backend health
curl http://localhost:8000/health

# Test frontend (via nginx)
curl http://localhost/health

# Test API through nginx
curl http://localhost/api/health
```

### Step 4: Enable SSL/TLS (Production)

1. **Update nginx.conf**: Uncomment HTTPS server block
2. **Mount certificates**: Uncomment volume mounts in docker-compose.prod.yml
3. **Configure certbot**: Uncomment certbot service for automatic certificate renewal
4. **Update environment**: Set VITE_API_URL to use https://

```bash
# Restart services with SSL configuration
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## Production Deployment Checklist

- [ ] **Security**
  - [ ] Generated strong SECRET_KEY (min 32 characters)
  - [ ] Set secure POSTGRES_PASSWORD
  - [ ] ENVIRONMENT=production in .env
  - [ ] DEBUG=false
  - [ ] CORS_ORIGINS configured with actual domain(s)
  - [ ] .env file is in .gitignore (never commit secrets)

- [ ] **Database**
  - [ ] PostgreSQL configured with proper password
  - [ ] Database backups configured
  - [ ] Volume persistence verified
  - [ ] Connection pooling reviewed

- [ ] **Networking**
  - [ ] Domain DNS configured
  - [ ] SSL/TLS certificates installed
  - [ ] Firewall rules configured (allow 80, 443)
  - [ ] HTTPS redirect enabled

- [ ] **Performance**
  - [ ] Redis memory limits set appropriately
  - [ ] Static asset caching verified
  - [ ] Gzip compression enabled
  - [ ] CDN configured (optional)

- [ ] **Monitoring**
  - [ ] Health check endpoints working
  - [ ] Log aggregation configured
  - [ ] Error tracking setup (e.g., Sentry)
  - [ ] Uptime monitoring configured

- [ ] **Backups**
  - [ ] Database backup strategy
  - [ ] Automated backup schedule
  - [ ] Backup restoration tested
  - [ ] Volume snapshots configured

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Nginx (Port   │
                    │   80/443)      │
                    │  + Lit Frontend│
                    └───────┬────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        ┌───────▼─────────┐    ┌───────▼────────┐
        │  FastAPI Backend │    │  Static Files  │
        │   (Port 8000)    │    │   (Cached)     │
        └───────┬──────────┘    └────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼────────┐ ┌────▼──────┐
│  PostgreSQL    │ │   Redis   │
│  (Port 5432)   │ │ (Port 6379)│
└────────────────┘ └───────────┘
```

## Useful Commands

### Service Management
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restart a specific service
docker-compose -f docker-compose.prod.yml restart backend

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

### Database Management
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U conduit conduit_prod > backup.sql

# Restore database backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U conduit conduit_prod < backup.sql

# Access PostgreSQL shell
docker-compose -f docker-compose.prod.yml exec db psql -U conduit conduit_prod
```

### Debugging
```bash
# Shell access to backend
docker-compose -f docker-compose.prod.yml exec backend /bin/bash

# Shell access to frontend nginx
docker-compose -f docker-compose.prod.yml exec frontend /bin/sh

# View backend Python logs
docker-compose -f docker-compose.prod.yml exec backend cat /var/log/app.log

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec frontend nginx -t

# Reload nginx configuration
docker-compose -f docker-compose.prod.yml exec frontend nginx -s reload
```

### Monitoring
```bash
# Watch resource usage
docker stats

# Check container health
docker-compose -f docker-compose.prod.yml ps

# Follow all logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Scaling Considerations

### Horizontal Scaling
To scale the backend:
```bash
# Run multiple backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

Update nginx.conf to load balance:
```nginx
upstream backend {
    server backend:8000;
    server backend:8001;
    server backend:8002;
}
```

### Production Best Practices
1. **Use managed database services** (AWS RDS, Google Cloud SQL)
2. **Use managed Redis** (AWS ElastiCache, Redis Cloud)
3. **Store secrets in vault** (AWS Secrets Manager, HashiCorp Vault)
4. **Use container orchestration** (Kubernetes, ECS, GKE)
5. **Implement CI/CD pipeline** (GitHub Actions, GitLab CI)
6. **Set up monitoring** (Prometheus, Grafana, DataDog)
7. **Configure log aggregation** (ELK Stack, CloudWatch)
8. **Use CDN for static assets** (CloudFlare, AWS CloudFront)

## Environment-Specific Deployments

### Staging Environment
```bash
# Use separate environment file
cp .env.example .env.staging
# Edit .env.staging with staging-specific values
docker-compose -f docker-compose.prod.yml --env-file .env.staging up -d
```

### Multiple Environments
```bash
# Development
docker-compose up -d

# Staging
docker-compose -f docker-compose.prod.yml --env-file .env.staging up -d

# Production
docker-compose -f docker-compose.prod.yml --env-file .env up -d
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common issues:
# - Database connection failure: Check DATABASE_URL
# - Migration errors: Run `alembic upgrade head` manually
# - Secret key validation: Ensure SECRET_KEY is at least 32 characters
```

### Frontend serving 404
```bash
# Verify build completed
docker-compose -f docker-compose.prod.yml exec frontend ls -la /usr/share/nginx/html

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec frontend nginx -t

# Verify API proxy
curl -v http://localhost/api/health
```

### Database connection errors
```bash
# Check database is healthy
docker-compose -f docker-compose.prod.yml exec db pg_isready -U conduit

# Verify connection from backend
docker-compose -f docker-compose.prod.yml exec backend python -c "from src.db.database import engine; print(engine)"
```

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review health checks: `docker-compose -f docker-compose.prod.yml ps`
- Verify environment variables are set correctly
- Ensure all prerequisites are met

## Security Notes

- Never commit .env files to version control
- Rotate SECRET_KEY and database passwords regularly
- Keep Docker images updated for security patches
- Use strong passwords for all services
- Enable SSL/TLS in production
- Implement rate limiting at nginx level
- Set up fail2ban for SSH protection
- Regular security audits and penetration testing
