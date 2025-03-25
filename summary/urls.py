from django.urls import path
from . import views

urlpatterns = [
    path('', views.summary_table, name='summary_table'),
]