"""URL configuration for starter app"""
from django.urls import path
from . import views

urlpatterns = [
    path('stt/transcribe', views.transcribe, name='transcribe'),
    path('api/metadata', views.metadata, name='metadata'),
]
