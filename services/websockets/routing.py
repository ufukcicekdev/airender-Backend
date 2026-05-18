from django.urls import re_path

from .consumers import RenderConsumer

websocket_urlpatterns = [
    re_path(r"ws/render/(?P<task_id>[0-9a-f-]+)/$", RenderConsumer.as_asgi()),
]
