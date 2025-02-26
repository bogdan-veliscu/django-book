# System Patterns: Conduit API

## Architecture Overview
The Conduit API follows a typical Django REST Framework architecture with:
- Models for data representation (User, Article, Comment)
- Serializers for data transformation
- ViewSets for API endpoints
- Custom middleware for request/response processing
- Redis for caching and channels
- PostgreSQL for data storage
- Uvicorn as the ASGI server with multiple workers

## Key Technical Decisions
1. **Database Access Patterns**:
   - Using `select_related` and `prefetch_related` for optimizing queries
   - Custom QuerySets for common query patterns (ArticleQuerySet)
   - Taggit for article tagging
   - SoftDeletableModel for logical deletion
   - Many-to-many relationships for favorites and comments

2. **Caching Strategy**:
   - Redis as the cache backend (django_redis.cache.RedisCache)
   - GlobalCacheMiddleware for caching unauthenticated requests
   - Method-level caching for specific endpoints (e.g., recent articles)
   - Fixed cache timeout of 5 minutes (300 seconds)
   - No cache invalidation strategy for modified resources

3. **Image Processing**:
   - In-memory image processing during article save
   - Resizing to 800x800 pixels using Pillow
   - JPEG conversion for all images (including RGBA and P mode)
   - Using InMemoryUploadedFile which keeps the entire file in memory
   - No size limits for uploaded images

4. **Authentication**:
   - JWT-based authentication with SimpleJWT
   - Custom authentication middleware
   - User model with followers/following relationships
   - Permission classes for endpoint access control

5. **Deployment**:
   - Docker-based deployment with multi-stage builds
   - Uvicorn as the ASGI server
   - Multiple worker processes (default: 2)
   - Redis for caching and channels
   - PostgreSQL for data storage
   - Nginx as the reverse proxy

## Component Relationships
- **User Model**:
  - Has many Articles (author relationship)
  - Has many Comments (author relationship)
  - Has many-to-many relationship with Articles (favorites)
  - Has many-to-many relationship with Users (followers/following)

- **Article Model**:
  - Belongs to a User (author)
  - Has many Comments
  - Has many-to-many relationship with Users (favorites)
  - Has many-to-many relationship with Tags

- **Comment Model**:
  - Belongs to a User (author)
  - Belongs to an Article

## Performance Considerations
- **Database Optimization**:
  - Custom QuerySets with optimized query methods
  - Using select_related and prefetch_related for reducing queries
  - Database connection pooling with CONN_MAX_AGE setting
  - No database indexes for frequently queried fields

- **Caching Strategy**:
  - Redis as the cache backend
  - GlobalCacheMiddleware for caching unauthenticated requests
  - Method-level caching for specific endpoints
  - No cache versioning or invalidation strategy

- **Memory Management**:
  - In-memory image processing without size limits
  - No memory limits for worker processes
  - No streaming responses for large datasets
  - Property methods that make additional queries

- **Worker Configuration**:
  - Multiple worker processes (default: 2)
  - No worker timeout settings
  - No max request settings to recycle workers
  - No graceful shutdown implementation

## Identified Performance Bottlenecks
1. **Database Queries**:
   - Inefficient queries in ArticleViewSet methods
   - Missing pagination in list endpoints
   - Property methods making additional queries
   - Missing database indexes for frequently queried fields

2. **Memory Usage**:
   - In-memory image processing without size limits
   - Large image sizes (800x800 pixels)
   - No streaming responses for large datasets
   - Multiple worker processes consuming memory

3. **Caching Strategy**:
   - Limited caching for unauthenticated users only
   - Fixed cache timeout for all resources
   - No cache invalidation strategy
   - No user-specific caching

4. **Worker Configuration**:
   - Too many workers for the available resources
   - No worker timeout settings
   - No max request settings
   - No graceful shutdown implementation 