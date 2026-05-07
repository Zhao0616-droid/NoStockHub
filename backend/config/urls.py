from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/boards/', include('apps.kanban.urls')),
    path('api/sprints/', include('apps.sprints.urls')),
    path('api/worklogs/', include('apps.worklogs.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/files/', include('apps.files.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
