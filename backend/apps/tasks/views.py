from django.db import models as db_models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsProjectMember, IsProjectManager

from .models import Comment, Task, TaskDependency
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    TaskCreateSerializer,
    TaskDependencyCreateSerializer,
    TaskDependencySerializer,
    TaskListSerializer,
    TaskSerializer,
    TaskStatusTransitionSerializer,
    TaskUpdateSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'due_date', 'priority', 'status', 'order']
    ordering = ['order', '-created_at']
    filterset_fields = ['status', 'priority', 'type', 'project', 'sprint', 'assignee']

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'project', 'sprint', 'assignee', 'reporter', 'parent_task'
        ).prefetch_related('subtasks', 'comments', 'comments__replies')

        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        sprint_id = self.request.query_params.get('sprint_id')
        if sprint_id:
            queryset = queryset.filter(sprint_id=sprint_id)

        assignee_id = self.request.query_params.get('assignee_id')
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)

        parent_task_isnull = self.request.query_params.get('parent_task_isnull')
        if parent_task_isnull == 'true':
            queryset = queryset.filter(parent_task__isnull=True)
        elif parent_task_isnull == 'false':
            queryset = queryset.filter(parent_task__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        if self.action == 'list':
            return TaskListSerializer
        if self.action == 'transition':
            return TaskStatusTransitionSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'transition',
                           'manage_dependencies', 'add_dependency', 'remove_dependency']:
            return [IsAuthenticated(), IsProjectManager()]
        if self.action in ['retrieve', 'list', 'manage_comments', 'add_comment',
                           'subtasks_list', 'dependencies_list']:
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        task = self.get_object()
        serializer = TaskStatusTransitionSerializer(
            data=request.data, context={'instance': task}
        )
        serializer.is_valid(raise_exception=True)
        task.status = serializer.validated_data['status']
        if task.status == Task.Status.DONE:
            task.progress = 100
        task.save(update_fields=['status', 'progress'])
        return Response(TaskSerializer(task).data)

    # --- Comments ---

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def manage_comments(self, request, pk=None):
        task = self.get_object()

        if request.method == 'GET':
            comments = task.comments.filter(parent_comment__isnull=True)
            return Response(CommentSerializer(comments, many=True).data)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(author=request.user, task=task)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        task = self.get_object()
        try:
            comment = task.comments.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if comment.author_id != request.user.id:
            return Response({'detail': 'Only the author can delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # --- Dependencies ---

    @action(detail=True, methods=['get'], url_path='dependencies')
    def dependencies_list(self, request, pk=None):
        task = self.get_object()
        deps = TaskDependency.objects.filter(
            db_models.Q(predecessor=task) | db_models.Q(successor=task)
        )
        return Response(TaskDependencySerializer(deps, many=True).data)

    @action(detail=True, methods=['post'], url_path='dependencies/add')
    def add_dependency(self, request, pk=None):
        task = self.get_object()
        serializer = TaskDependencyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dep = serializer.save()
        return Response(TaskDependencySerializer(dep).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='dependencies/(?P<dep_id>[^/.]+)')
    def remove_dependency(self, request, pk=None, dep_id=None):
        task = self.get_object()
        try:
            dep = TaskDependency.objects.filter(
                db_models.Q(predecessor=task) | db_models.Q(successor=task)
            ).get(id=dep_id)
        except TaskDependency.DoesNotExist:
            return Response({'detail': 'Dependency not found.'}, status=status.HTTP_404_NOT_FOUND)
        dep.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # --- Subtasks ---

    @action(detail=True, methods=['get'], url_path='subtasks')
    def subtasks_list(self, request, pk=None):
        task = self.get_object()
        subtasks = task.subtasks.all()
        return Response(TaskListSerializer(subtasks, many=True).data)
