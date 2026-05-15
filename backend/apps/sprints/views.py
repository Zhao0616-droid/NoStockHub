from datetime import date, timedelta

from django.apps import apps
from django.db import models as db_models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsProjectMember, IsProjectManager

from .models import Sprint
from .serializers import (
    SprintCreateSerializer,
    SprintSerializer,
    SprintTaskManageSerializer,
    SprintUpdateSerializer,
)


def _get_task_model():
    try:
        return apps.get_model('tasks', 'Task')
    except LookupError:
        return None


class SprintViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'goal']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'status']
    ordering = ['-created_at']
    filterset_fields = ['status']

    def get_queryset(self):
        queryset = Sprint.objects.select_related('project').all()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return SprintCreateSerializer
        if self.action in ['update', 'partial_update']:
            return SprintUpdateSerializer
        return SprintSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'start', 'complete']:
            return [IsAuthenticated(), IsProjectManager()]
        if self.action in ['retrieve', 'manage_tasks', 'burndown']:
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        sprint = self.get_object()
        if sprint.status != Sprint.Status.PLANNING:
            return Response(
                {'detail': 'Only planning sprints can be started.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if sprint.start_date > date.today():
            return Response(
                {'detail': 'Cannot start a sprint before its start date.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sprint.status = Sprint.Status.ACTIVE
        sprint.save(update_fields=['status'])
        return Response(SprintSerializer(sprint).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        sprint = self.get_object()
        if sprint.status != Sprint.Status.ACTIVE:
            return Response(
                {'detail': 'Only active sprints can be completed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Task = _get_task_model()
        if Task is not None:
            incomplete = Task.objects.filter(sprint=sprint).exclude(
                status__in=['done', 'completed']
            )
            incomplete.update(sprint=None)
        sprint.status = Sprint.Status.COMPLETED
        sprint.save(update_fields=['status'])
        return Response(SprintSerializer(sprint).data)

    @action(detail=True, methods=['get', 'post', 'delete'], url_path='tasks')
    def manage_tasks(self, request, pk=None):
        sprint = self.get_object()
        Task = _get_task_model()
        if Task is None:
            return Response(
                {'detail': 'Tasks module is not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if request.method == 'GET':
            tasks = Task.objects.filter(sprint=sprint).order_by('order', 'created_at')
            return Response([{
                'id': str(t.id),
                'title': getattr(t, 'title', ''),
                'status': getattr(t, 'status', ''),
                'priority': getattr(t, 'priority', ''),
                'assignee_id': str(t.assignee_id) if getattr(t, 'assignee_id', None) else None,
            } for t in tasks])

        if request.method == 'POST':
            serializer = SprintTaskManageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.validated_data['task_id']
            task_project_id = getattr(task, 'project_id', None)
            if str(task_project_id) != str(sprint.project_id):
                return Response(
                    {'detail': 'Task does not belong to the same project.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            task.sprint = sprint
            task.save(update_fields=['sprint'])
            return Response({'detail': 'Task added to sprint.'}, status=status.HTTP_200_OK)

        # DELETE
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {'detail': 'task_id query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            task = Task.objects.get(id=task_id, sprint=sprint)
        except Task.DoesNotExist:
            return Response(
                {'detail': 'Task not found in this sprint.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        task.sprint = None
        task.save(update_fields=['sprint'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def burndown(self, request, pk=None):
        sprint = self.get_object()
        Task = _get_task_model()

        total_days = (sprint.end_date - sprint.start_date).days + 1
        if total_days < 1:
            total_days = 1

        if Task is not None:
            total_tasks = Task.objects.filter(sprint=sprint).count()
        else:
            total_tasks = 0

        ideal_line = []
        actual_line = []

        today = date.today()
        for i in range(total_days):
            d = sprint.start_date + timedelta(days=i)
            ideal_remaining = max(0, total_tasks - int(total_tasks * (i + 1) / total_days))

            if Task is not None and d <= today:
                completed_count = Task.objects.filter(
                    sprint=sprint,
                    status__in=['done', 'completed'],
                ).count()
                actual_remaining = max(0, total_tasks - completed_count)
            else:
                actual_remaining = ideal_remaining

            ideal_line.append({'date': str(d), 'remaining': ideal_remaining})
            actual_line.append({'date': str(d), 'remaining': actual_remaining})

        return Response({
            'sprint_id': str(sprint.id),
            'sprint_name': sprint.name,
            'ideal_line': ideal_line,
            'actual_line': actual_line,
        })
