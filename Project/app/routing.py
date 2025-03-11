from django.urls import re_path
from app.consumers import VoiceRecognitionConsumer

websocket_urlpatterns = [
    re_path(r"ws/voice/$", VoiceRecognitionConsumer.as_asgi()),
]
