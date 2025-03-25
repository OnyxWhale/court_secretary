from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('summary/', include('summary.urls')),
    path('judges/', include('judges.urls')),  # Новый путь
]