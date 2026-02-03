"""
URL configuration for Django transcription starter.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('starter.urls')),
]
