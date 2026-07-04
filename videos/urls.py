from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    path('', views.video_list, name='video_list'),
    path('upload/', views.upload_videos, name='upload_videos'),
    path('<int:pk>/', views.video_detail, name='video_detail'),
    path('run-migrations-securely/', views.run_remote_migrations, name='run_migrations'),
    path('<int:pk>/stream/', views.stream_video, name='stream_video'),
]
