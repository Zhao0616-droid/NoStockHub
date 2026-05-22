from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register('', NotificationViewSet, basename='notification')

urlpatterns = router.urls
