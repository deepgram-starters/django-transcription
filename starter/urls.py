"""URL configuration for starter app"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.serve_index, name='index'),
    path('api/session', views.get_session, name='session'),
    path('api/transcription', views.transcribe, name='transcribe'),
    path('api/metadata', views.metadata, name='metadata'),
]
