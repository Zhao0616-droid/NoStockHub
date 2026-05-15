# from django.urls import path

# app_name = 'tasks'

# urlpatterns = []
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]