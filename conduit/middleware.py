import logging
import time

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
    CACHE_TIME = GLOBAL_CACHE_TIME  # Cache time in seconds (5 minutes)

    async def __acall__(self, request):
        # Safe way to check if path starts with /admin/ in async context
        if request.path.startswith("/admin/") or request.method != "GET":
            return await self.get_response(request)

        # Check authentication status safely in async context
        is_authenticated = False
        try:
            is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
        except Exception as e:
            logger.error(f"Error checking authentication: {e}")
            # Continue processing even if auth check fails

        if is_authenticated:
            return await self.get_response(request)

        cache_key = f"cache:{request.get_full_path()}"
        cached_response = await sync_to_async(cache.get)(cache_key)
        
        if cached_response:
            return cached_response

        response = await self.get_response(request)

        # Only cache for unauthenticated users
        if not request.path.startswith("/admin/") and not is_authenticated:
            await sync_to_async(cache.set)(cache_key, response, self.CACHE_TIME)

        return response

    def __call__(self, request):
        # Synchronous path - check if path starts with /admin/
        if request.path.startswith("/admin/") or request.method != "GET":
            return self.get_response(request)

        # Check authentication status safely in sync context
        is_authenticated = False
        try:
            is_authenticated = request.user.is_authenticated
        except Exception as e:
            logger.error(f"Error checking authentication: {e}")
            # Continue processing even if auth check fails

        if is_authenticated:
            return self.get_response(request)

        cache_key = f"cache:{request.get_full_path()}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return cached_response

        response = self.get_response(request)

        # Only cache for unauthenticated users
        if not request.path.startswith("/admin/") and not is_authenticated:
            cache.set(cache_key, response, self.CACHE_TIME)

        return response

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
