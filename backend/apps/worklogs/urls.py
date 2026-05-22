from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkLogViewSet, HourlyRateViewSet

router = DefaultRouter()
router.register(r'', WorkLogViewSet, basename='worklog')

rate_router = DefaultRouter()
rate_router.register(r'', HourlyRateViewSet, basename='hourlyrate')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', WorkLogViewSet.as_view({'get': 'summary'}), name='worklog-summary'),
    path('rates/', include(rate_router.urls)),
]