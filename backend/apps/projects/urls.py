from rest_framework.routers import DefaultRouter

from .views import ProjectTemplateViewSet, ProjectViewSet

router = DefaultRouter()
router.register('templates', ProjectTemplateViewSet, basename='project-template')
router.register('', ProjectViewSet, basename='project')

urlpatterns = router.urls
