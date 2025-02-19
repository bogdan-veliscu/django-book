from prometheus_client import Counter, Histogram
from functools import wraps
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

def track_metrics(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        
        response = view_func(request, *args, **kwargs)
        
        duration = time.time() - start_time
        endpoint = request.resolver_match.view_name if request.resolver_match else 'unknown'
        
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
    return wrapper 