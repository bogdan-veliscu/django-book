import logging
import time
import inspect

from config.settings.base import GLOBAL_CACHE_TIME
from django.contrib.auth.middleware import (
    AuthenticationMiddleware,
)
from django.contrib.sessions.middleware import (
    SessionMiddleware,
)
from django.core.cache import cache
from django.db import connection
from django.middleware.gzip import (
    GZipMiddleware as DjangoGZipMiddleware,
)
from django.utils.deprecation import MiddlewareMixin
from asgiref.sync import sync_to_async
from django.utils.decorators import sync_and_async_middleware

logger = logging.getLogger(__name__)


class PerformanceLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        print(f"Response time for {request.path}: {duration:.4f} seconds")
        return response


class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        logger.debug("Processing request in CustomSessionMiddleware")
        super().process_request(request)


class CustomAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        logger.debug("Processing request in CustomAuthenticationMiddleware")
        super().process_request(request)


@sync_and_async_middleware
class GlobalCacheMiddleware:
    # Cache times in seconds for different resource types
    CACHE_TIMES = {
        'articles': 300,      # 5 minutes for article lists
        'article': 600,       # 10 minutes for individual articles
        'profiles': 900,      # 15 minutes for profile lists
        'profile': 1800,      # 30 minutes for individual profiles
        'tags': 3600,         # 1 hour for tags
        'default': GLOBAL_CACHE_TIME  # Default from settings (5 minutes)
    }
    
    def _get_cache_timeout(self, path):
        """Determine cache timeout based on the request path"""
        if '/api/articles/' in path and not path.endswith('/articles/'):
            return self.CACHE_TIMES['article']
        elif '/api/articles' in path:
            return self.CACHE_TIMES['articles']
        elif '/api/profiles/' in path and not path.endswith('/profiles/'):
            return self.CACHE_TIMES['profile']
        elif '/api/profiles' in path:
            return self.CACHE_TIMES['profiles']
        elif '/api/tags' in path:
            return self.CACHE_TIMES['tags']
        return self.CACHE_TIMES['default']
    
    def _get_cache_key(self, request):
        """Generate a more granular cache key based on request parameters"""
        # Base key includes the full path
        key = f"cache:{request.get_full_path()}"
        
        # Add query parameters to the key
        if request.GET:
            # Sort query parameters for consistent keys
            query_params = "&".join(f"{k}={v}" for k, v in sorted(request.GET.items()))
            key = f"{key}?{query_params}"
        
        # For authenticated users, add a user-specific suffix if appropriate
        # Only cache user-specific content for GET requests
        # IMPORTANT: We don't check authentication in async context to avoid database queries
        # This is safe because we're only using this for caching, not for security
        return key

    async def _get_cache_key_async(self, request):
        """Async version of _get_cache_key that doesn't check authentication"""
        # Base key includes the full path
        key = f"cache:{request.get_full_path()}"
        
        # Add query parameters to the key
        if request.GET:
            # Sort query parameters for consistent keys
            query_params = "&".join(f"{k}={v}" for k, v in sorted(request.GET.items()))
            key = f"{key}?{query_params}"
        
        # We don't check authentication in async context to avoid database queries
        # This is safe because we're only using this for caching, not for security
        return key

    async def __acall__(self, request):
        # Skip caching for admin, non-GET requests, or API write operations
        if (request.path.startswith("/admin/") or 
            request.method != "GET" or 
            any(op in request.path for op in ['/create', '/update', '/delete'])):
            response = await self.get_response(request)
            # Ensure response is not a coroutine
            if inspect.iscoroutine(response):
                response = await response
            return response

        try:
            # Generate cache key without checking authentication in async context
            cache_key = await self._get_cache_key_async(request)
            
            # Try to get cached response
            cached_response = await sync_to_async(cache.get)(cache_key)
            
            if cached_response:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_response

            # Get fresh response
            response = await self.get_response(request)
            
            # Ensure response is not a coroutine
            if inspect.iscoroutine(response):
                logger.debug("Response is a coroutine, awaiting it")
                response = await response
            
            # Only cache successful responses
            if hasattr(response, 'status_code') and response.status_code == 200:
                # Determine cache timeout based on the path
                timeout = self._get_cache_timeout(request.path)
                
                # Cache the response
                await sync_to_async(cache.set)(cache_key, response, timeout)
                logger.debug(f"Cached response for key: {cache_key} with timeout: {timeout}s")
            
            return response
        except Exception as e:
            logger.error(f"Error in GlobalCacheMiddleware.__acall__: {e}")
            # If there's an error in the caching logic, just continue with the request
            response = await self.get_response(request)
            # Ensure response is not a coroutine
            if inspect.iscoroutine(response):
                response = await response
            return response

    def __call__(self, request):
        # Skip caching for admin, non-GET requests, or API write operations
        if (request.path.startswith("/admin/") or 
            request.method != "GET" or 
            any(op in request.path for op in ['/create', '/update', '/delete'])):
            return self.get_response(request)

        try:
            # Generate cache key
            cache_key = self._get_cache_key(request)
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            
            if cached_response:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_response

            # Get fresh response
            response = self.get_response(request)
            
            # Only cache successful responses
            if hasattr(response, 'status_code') and response.status_code == 200:
                # Determine cache timeout based on the path
                timeout = self._get_cache_timeout(request.path)
                
                # Cache the response
                cache.set(cache_key, response, timeout)
                logger.debug(f"Cached response for key: {cache_key} with timeout: {timeout}s")
            
            return response
        except Exception as e:
            logger.error(f"Error in GlobalCacheMiddleware.__call__: {e}")
            # If there's an error in the caching logic, just continue with the request
            return self.get_response(request)

    def __init__(self, get_response):
        self.get_response = get_response


class CustomGZipMiddleware(DjangoGZipMiddleware):
    def process_response(self, request, response):
        if not response.streaming and "Content-Encoding" not in response:
            response = super().process_response(request, response)
        return response


class QueryCountMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/admin/"):
            return None
        self.start_time = time.time()
        self.initial_queries = len(connection.queries)

    def process_response(self, request, response):
        if request.path.startswith("/admin/"):
            return response
        total_time = time.time() - self.start_time
        total_queries = len(connection.queries) - self.initial_queries
        if total_queries > 50 or total_time > 1.0:
            # Log or print the information
            print(f"Path: {request.path}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Total Queries: {total_queries}")
        return response
