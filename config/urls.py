"""
URL configuration for Django transcription starter.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def index(request):
    """Serve index.html from frontend/dist/"""
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse("Frontend not built. Run 'make build'.", status=404)

urlpatterns = [
    path('', index, name='index'),
    path('', include('starter.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
