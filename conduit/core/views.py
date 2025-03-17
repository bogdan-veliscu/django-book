import logging
from django.http import JsonResponse
from django.db import connections
from django.core.cache import cache
import psutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def health_check(request):
    """
    Health check endpoint that verifies critical system components.
    """
    logger.debug("Starting health check")
    
    # Check database connection
    try:
        logger.debug("Checking database connection")
        connections['default'].cursor()
        db_status = True
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        db_status = False

    # Check cache connection
    try:
        logger.debug("Checking cache connection")
        cache.set('health_check', 'OK', 1)
        cache_status = cache.get('health_check') == 'OK'
        logger.info("Cache connection successful")
    except Exception as e:
        logger.error(f"Cache connection failed: {str(e)}")
        cache_status = False

    # Check disk usage
    try:
        logger.debug("Checking disk usage")
        disk = psutil.disk_usage('/')
        disk_status = disk.percent < 90  # Alert if disk usage is over 90%
        logger.info(f"Disk usage: {disk.percent}%")
    except Exception as e:
        logger.error(f"Disk usage check failed: {str(e)}")
        disk_status = False

    # Check memory usage
    try:
        logger.debug("Checking memory usage")
        memory = psutil.virtual_memory()
        memory_status = memory.percent < 90  # Alert if memory usage is over 90%
        logger.info(f"Memory usage: {memory.percent}%")
    except Exception as e:
        logger.error(f"Memory usage check failed: {str(e)}")
        memory_status = False

    status_code = 200 if all([db_status, cache_status, disk_status, memory_status]) else 503
    logger.info(f"Health check completed with status code: {status_code}")

    response = {
        'status': 'healthy' if status_code == 200 else 'unhealthy',
        'database': 'up' if db_status else 'down',
        'cache': 'up' if cache_status else 'down',
        'disk': 'ok' if disk_status else 'warning',
        'memory': 'ok' if memory_status else 'warning',
    }
    
    logger.debug(f"Health check response: {response}")
    return JsonResponse(response, status=status_code) 