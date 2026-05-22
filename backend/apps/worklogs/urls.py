from django.urls import path
from .views import WorkLogViewSet, HourlyRateViewSet

urlpatterns = [
    path('', WorkLogViewSet.as_view({'get': 'list', 'post': 'create'}), name='worklog-list'),
    path('summary/', WorkLogViewSet.as_view({'get': 'summary'}), name='worklog-summary'),
    path('rates/', HourlyRateViewSet.as_view({'get': 'list', 'post': 'create'}), name='hourlyrate-list'),
    path('rates/<uuid:pk>/', HourlyRateViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='hourlyrate-detail'),
    path('<uuid:pk>/', WorkLogViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='worklog-detail'),
]
