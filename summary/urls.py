from django.urls import path
from . import views

app_name = 'summary'

urlpatterns = [
    path('', views.summary_table, name='summary_table'),
]