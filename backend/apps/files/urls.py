from rest_framework.routers import DefaultRouter

from .views import AttachmentViewSet

router = DefaultRouter()
router.register('', AttachmentViewSet, basename='file')

urlpatterns = router.urls
