from rest_framework.routers import DefaultRouter

from .views import SprintViewSet

router = DefaultRouter()
router.register('', SprintViewSet, basename='sprint')

urlpatterns = router.urls
