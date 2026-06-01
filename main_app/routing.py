# main_app/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # This must perfectly match the URL path pattern your frontend calls
    re_path(r"^ws/chat/$", consumers.ChatConsumer.as_asgi()),
]
