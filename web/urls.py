from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('stats/', views.stats, name='stats'),
    path('parse/', views.trigger_parse, name='trigger_parse'),
    path('progress/', views.parse_progress, name='progress'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
]