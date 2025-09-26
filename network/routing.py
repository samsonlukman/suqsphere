# network/routing.py
from django.urls import re_path
from . import consumers

# WebSocket routes (ONLY for Channels, not Django URLconf)
urlpatterns = [
    re_path(r"ws/chat/(?P<conversation_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
