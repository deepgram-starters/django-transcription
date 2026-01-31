"""
URL configuration for Django transcription starter.
"""
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
import os

def index(request):
    """Serve index.html from frontend/dist/"""
    index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("Frontend not built. Run 'make build'.", status=404)

urlpatterns = [
    path('', index, name='index'),
    path('', include('starter.urls')),
    # Serve static files in development
    re_path(r'^(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
