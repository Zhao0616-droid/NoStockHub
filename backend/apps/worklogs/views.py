from django.db.models import Count, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsProjectMember

from .models import HourlyRate, WorkLog
from .serializers import (
    HourlyRateCreateSerializer,
    HourlyRateSerializer,
    WorkLogCreateSerializer,
    WorkLogSerializer,
    WorkLogUpdateSerializer,
)


class WorkLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['description']
    ordering_fields = ['date', 'hours', 'created_at']
    ordering = ['-date', '-created_at']
    filterset_fields = ['task', 'user']

    def get_queryset(self):
        queryset = WorkLog.objects.select_related('task', 'user').all()

        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(task__project_id=project_id)

        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return WorkLogCreateSerializer
        if self.action in ['update', 'partial_update']:
            return WorkLogUpdateSerializer
        return WorkLogSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        project_id = request.query_params.get('project_id')

        queryset = WorkLog.objects.select_related('user')
        if project_id:
            queryset = queryset.filter(task__project_id=project_id)

        summary = queryset.values('user_id', 'user__username').annotate(
            total_hours=Sum('hours'),
            task_count=Count('task', distinct=True),
        ).order_by('-total_hours')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_map = {
            str(u.id): u.username
            for u in User.objects.filter(id__in=[s['user_id'] for s in summary])
        }

        return Response([{
            'user_id': str(s['user_id']),
            'username': s['user__username'],
            'total_hours': float(s['total_hours'] or 0),
            'task_count': s['task_count'],
        } for s in summary])


class HourlyRateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'project']

    def get_queryset(self):
        return HourlyRate.objects.select_related('user', 'project').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return HourlyRateCreateSerializer
        return HourlyRateSerializer
