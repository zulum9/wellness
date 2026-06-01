"""
ASGI config for wellness project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

# wellness/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import main_app.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wellness.settings")

application = ProtocolTypeRouter(
    {
        # Handles standard HTTP requests
        "http": get_asgi_application(),
        # Handles WebSocket chat requests
        "websocket": AuthMiddlewareStack(
            URLRouter(main_app.routing.websocket_urlpatterns)
        ),
    }
)
