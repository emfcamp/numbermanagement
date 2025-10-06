from django.urls import path
from . import views

urlpatterns = [
    path('audio/', views.audio_list, name='audio_list'),
    path('audio/upload/', views.upload_audio, name='upload_audio'),
    path('audio/delete/<int:pk>/', views.delete_audio, name='delete_audio'),
]