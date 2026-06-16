from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/surveys/', include('apps.surveys.urls')),
    path('api/responses/', include('apps.responses.urls')),
    path('api/templates/', include('apps.templates_app.urls')),
    path('api/bank/', include('apps.bank.urls')),
]
