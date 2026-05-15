from rest_framework.routers import DefaultRouter

from .views import HourlyRateViewSet, WorkLogViewSet

router = DefaultRouter()
router.register('rates', HourlyRateViewSet, basename='hourlyrate')
router.register('', WorkLogViewSet, basename='worklog')

urlpatterns = router.urls
