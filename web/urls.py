from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('stats/', views.stats, name='stats'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('parse/', views.trigger_parse, name='trigger_parse'),
]