# Active Context: Performance Optimization

## Current Focus
We are currently analyzing the performance issues in the Conduit API, focusing on:
1. Database query optimization in the ArticleViewSet
2. Memory usage reduction, particularly in image processing
3. Worker configuration adjustments
4. Caching strategy improvements

## Recent Findings
- The ArticleViewSet has inefficient database queries, especially in the feed and recent methods
- The Article model's save method processes images in memory without size limits
- The worker count (4 by default) may be too high for the available resources
- Multiple middleware components add overhead to each request
- Caching is only implemented for unauthenticated users
- The GlobalCacheMiddleware had an async/sync context issue causing article creation to fail

## Recent Changes
1. **Memory Limits Configuration**:
   - Added memory limits to all containers in docker-compose.prod.yml
   - Set app container memory limit to 1GB with 512MB reservation
   - Reduced worker count from 4 to 2 by default
   - Added timeout settings to prevent long-running requests
   - Modified entrypoint.sh to use the new worker count

2. **Middleware Fix**:
   - Fixed the GlobalCacheMiddleware to properly handle async context
   - Separated sync and async code paths with proper error handling
   - Fixed the SynchronousOnlyOperation error that was preventing article creation
   - Added more robust error handling for authentication checks

## Next Steps
1. Optimize the ArticleViewSet to reduce database queries and add pagination
2. Modify the Article model's save method to limit image size and memory usage
3. Enhance the caching strategy to include authenticated users where appropriate
4. Review and optimize custom middleware

## Active Decisions
- Focus on quick wins first (configuration changes and simple code optimizations)
- Document all changes for future reference
- Consider both immediate fixes and long-term architectural improvements 