from rest_framework.routers import DefaultRouter

from .views import KanbanBoardViewSet

router = DefaultRouter()
router.register('', KanbanBoardViewSet, basename='board')

urlpatterns = router.urls
