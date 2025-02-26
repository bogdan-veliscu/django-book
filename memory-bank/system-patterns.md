# System Patterns: Conduit API

## Architecture Overview
The Conduit API follows a typical Django REST Framework architecture with:
- Models for data representation (User, Article, Comment)
- Serializers for data transformation
- ViewSets for API endpoints
- Custom middleware for request/response processing
- Redis for caching and channels
- PostgreSQL for data storage

## Key Technical Decisions
1. **Database Access Patterns**:
   - Using `select_related` and `prefetch_related` for optimizing queries
   - Custom QuerySets for common query patterns
   - Taggit for article tagging

2. **Caching Strategy**:
   - Redis as the cache backend
   - Cache middleware for unauthenticated requests
   - Method-level caching for specific endpoints (e.g., recent articles)

3. **Image Processing**:
   - In-memory image processing during article save
   - Resizing to 800x800 pixels
   - JPEG conversion for all images

4. **Authentication**:
   - JWT-based authentication with SimpleJWT
   - 7-day token lifetime
   - Custom authentication middleware

5. **Deployment**:
   - Docker-based deployment
   - Multi-stage Docker build for optimization
   - Uvicorn as the ASGI server
   - Multiple worker processes

## Component Relationships
- Articles have many-to-one relationship with Users (authors)
- Articles have many-to-many relationship with Users (favorites)
- Comments have many-to-one relationship with both Articles and Users
- Tags have many-to-many relationship with Articles

## Performance Considerations
- Custom middleware for performance logging and query counting
- Global cache middleware for public pages
- Database connection pooling
- Redis for caching frequently accessed data 