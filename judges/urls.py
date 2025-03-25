from django.urls import path
from . import views

urlpatterns = [
    path('', views.judges_list, name='judges_list'),
    path('add/', views.judge_manage, name='judge_add'),  # Добавляем URL для добавления судьи
    path('edit/<int:judge_id>/', views.judge_manage, name='judge_edit'),
    path('delete/<int:judge_id>/', views.judge_delete, name='judge_delete'),
    path('history/delete/<int:pk>/', views.employment_history_delete, name='employment_history_delete'),
]