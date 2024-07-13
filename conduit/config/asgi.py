"""
ASGI config for conduit project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

print("# asgi.py")

import os

from django.core.asgi import get_asgi_application

print("# asgi.py 2")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

print("# asgi.py 3")
from channels.routing import ProtocolTypeRouter, URLRouter
import comments.routing

print("# asgi.py 4")
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(comments.routing.websocket_urlpatterns),
    }
)

print("ASGI application is running:", application)
