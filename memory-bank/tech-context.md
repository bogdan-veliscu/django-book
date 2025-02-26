# Tech Context: Conduit API

## Technologies Used
- **Backend Framework**: Django 5.0 with Django REST Framework
- **Database**: PostgreSQL 15
- **Caching**: Redis 6
- **Web Server**: Uvicorn (ASGI)
- **Container**: Docker with multi-stage builds
- **Authentication**: JWT (SimpleJWT)
- **Image Processing**: Pillow
- **Tagging**: django-taggit
- **Documentation**: drf-yasg (Swagger)
- **Channels**: Django Channels with Redis backend

## Development Setup
- Docker Compose for local development
- Environment variables for configuration
- UV package manager for Python dependencies
- Multi-stage Docker build for production

## Technical Constraints
- Digital Ocean droplet with limited resources
- Memory constraints leading to worker timeouts
- Multiple worker processes (4 by default)
- No apparent worker memory limits
- In-memory image processing without size limits
- Multiple middleware components adding overhead

## Dependencies
- **Core**: Django, DRF, Uvicorn, Channels
- **Database**: psycopg2 for PostgreSQL
- **Caching**: Redis, django-redis
- **Media**: Pillow for image processing
- **Storage**: django-storages with AWS S3
- **Frontend Integration**: CORS headers
- **Authentication**: SimpleJWT
- **Compression**: Whitenoise, django-compressor

## Environment Variables
- Database configuration (POSTGRES_*)
- Redis configuration (REDIS_*)
- AWS S3 configuration (AWS_*)
- Email configuration (SMTP_*)
- Django settings (DJANGO_*)
- Worker configuration (WORKERS) 