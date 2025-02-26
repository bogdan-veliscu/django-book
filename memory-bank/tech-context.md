# Tech Context: Conduit API

## Technologies Used
- **Backend Framework**: Django 5.0 with Django REST Framework
- **Database**: PostgreSQL 15
- **Caching**: Redis 6 with django-redis
- **Web Server**: Uvicorn (ASGI) with multiple workers
- **Container**: Docker with multi-stage builds
- **Authentication**: JWT (SimpleJWT)
- **Image Processing**: Pillow for image resizing and format conversion
- **Tagging**: django-taggit for article tagging
- **Documentation**: drf-yasg (Swagger)
- **Channels**: Django Channels with Redis backend
- **Monitoring**: Django Prometheus for metrics
- **Error Tracking**: Sentry for error reporting
- **Compression**: Whitenoise for static files, django-compressor

## Development Setup
- Docker Compose for local development
- Environment variables for configuration
- UV package manager for Python dependencies
- Multi-stage Docker build for production
- Debug toolbar for development debugging
- Pytest for testing

## Technical Constraints
- **Hardware Limitations**:
  - Digital Ocean droplet with limited resources
  - Memory constraints leading to worker timeouts
  - CPU limitations affecting request processing time

- **Application Configuration**:
  - Multiple worker processes (default: 2)
  - No worker memory limits
  - No worker timeout settings
  - No max request settings

- **Memory Management**:
  - In-memory image processing without size limits
  - Large image sizes (800x800 pixels)
  - No streaming responses for large datasets
  - Property methods making additional queries

- **Database Configuration**:
  - Connection pooling with CONN_MAX_AGE=600
  - No database indexes for frequently queried fields
  - No query optimization for list endpoints
  - No pagination for some list endpoints

## Dependencies
- **Core**:
  - Django 5.0: Web framework
  - Django REST Framework: API framework
  - Uvicorn: ASGI server
  - Channels: WebSocket support

- **Database**:
  - psycopg2: PostgreSQL adapter
  - django-filter: Query filtering

- **Caching**:
  - Redis: In-memory data store
  - django-redis: Redis integration

- **Media**:
  - Pillow: Image processing
  - django-storages: S3 storage backend

- **Authentication**:
  - SimpleJWT: JWT authentication
  - django-cors-headers: CORS support

- **Monitoring**:
  - Sentry: Error tracking
  - django-prometheus: Metrics

- **Compression**:
  - Whitenoise: Static file serving
  - django-compressor: CSS/JS compression

## Environment Variables
- **Database Configuration**:
  - POSTGRES_DB: Database name
  - POSTGRES_USER: Database user
  - POSTGRES_PASSWORD: Database password
  - POSTGRES_HOST: Database host
  - POSTGRES_PORT: Database port

- **Redis Configuration**:
  - REDIS_HOST: Redis host
  - REDIS_PORT: Redis port
  - REDIS_URL: Redis connection URL

- **AWS Configuration**:
  - AWS_ACCESS_KEY_ID: AWS access key
  - AWS_SECRET_ACCESS_KEY: AWS secret key
  - AWS_STORAGE_BUCKET_NAME: S3 bucket name

- **Application Configuration**:
  - DJANGO_SECRET_KEY: Secret key
  - DJANGO_SETTINGS_MODULE: Settings module
  - DEBUG: Debug mode
  - WORKERS: Number of worker processes
  - PORT: Application port

- **Email Configuration**:
  - EMAIL_HOST: SMTP host
  - EMAIL_PORT: SMTP port
  - EMAIL_HOST_USER: SMTP user
  - EMAIL_HOST_PASSWORD: SMTP password
  - EMAIL_USE_TLS: Use TLS

## Resource Limits
- **Docker Container Limits**:
  - App container: 1GB limit with 512MB reservation
  - Database container: 1GB limit with 512MB reservation
  - Redis container: 512MB limit with 256MB reservation
  - Frontend container: 512MB limit with 256MB reservation
  - Nginx container: 256MB limit with 128MB reservation

- **Database Limits**:
  - max_connections: 100
  - shared_buffers: 128MB
  - work_mem: 4MB
  - maintenance_work_mem: 64MB
  - effective_cache_size: 4GB

- **Application Limits**:
  - DATA_UPLOAD_MAX_MEMORY_SIZE: 10MB
  - GLOBAL_CACHE_TIME: 300 seconds (5 minutes)
  - CONN_MAX_AGE: 600 seconds (10 minutes) 