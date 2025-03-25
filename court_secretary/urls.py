from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('web.urls', 'web'), namespace='web')),  # Главная страница и базовые функции
    path('summary/', include(('summary.urls', 'summary'), namespace='summary')),  # Сводная таблица
    path('judges/', include(('judges.urls', 'judges'), namespace='judges')),  # Управление судьями
]