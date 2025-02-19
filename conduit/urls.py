from django.urls import include, path
from .core.views import health_check

urlpatterns = [
    path('', include('conduit.articles.urls')),
    path('', include('conduit.profiles.urls')),
    path('', include('conduit.comments.urls')),
    path('health/', health_check, name='health_check'),
] 