# from django.urls import path

# app_name = 'worklogs'

# urlpatterns = []
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkLogViewSet

router = DefaultRouter()
router.register(r'', WorkLogViewSet, basename='worklog')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', WorkLogViewSet.as_view({'get': 'summary'}), name='worklog-summary'),
]