import sys

from django.urls import path

from . import views

app_name = 'djangorealtime'


sse_view = views.sse_view

# Auto-detect WSGI/ASGI and pick the right view
if 'django.core.handlers.wsgi' in sys.modules:
    sse_view = views.sse_view_sync

urlpatterns = [
    path('sse/', sse_view, name='sse'),
]
