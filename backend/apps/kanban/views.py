from django.apps import apps
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsProjectMember, IsProjectManager

from .models import KanbanBoard, KanbanColumn, TaskColumn
from .serializers import (
    KanbanBoardCreateSerializer,
    KanbanBoardSerializer,
    KanbanColumnCreateSerializer,
    KanbanColumnSerializer,
    KanbanTaskMoveSerializer,
)


class KanbanBoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    filterset_fields = ['type']

    def get_queryset(self):
        queryset = KanbanBoard.objects.prefetch_related(
            'columns', 'columns__task_columns'
        ).all()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return KanbanBoardCreateSerializer
        return KanbanBoardSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy',
                           'manage_columns', 'update_column', 'delete_column',
                           'move_task']:
            return [IsAuthenticated(), IsProjectManager()]
        if self.action in ['retrieve', 'columns_list']:
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        board = serializer.save()
        # Create default columns
        defaults = [
            {'name': '待办', 'order': 0, 'wip_limit': 0},
            {'name': '进行中', 'order': 1, 'wip_limit': 5},
            {'name': '审核中', 'order': 2, 'wip_limit': 3},
            {'name': '已完成', 'order': 3, 'wip_limit': 0},
        ]
        for col in defaults:
            KanbanColumn.objects.create(board=board, **col)

    @action(detail=True, methods=['get', 'post'], url_path='columns')
    def manage_columns(self, request, pk=None):
        board = self.get_object()

        if request.method == 'GET':
            columns = board.columns.order_by('order')
            # Auto-assign unassigned project tasks to first column
            first_col = columns.first()
            if first_col:
                existing_task_ids = set()
                for col in columns:
                    existing_task_ids.update(tc.task_id for tc in col.task_columns.all())
                Task = apps.get_model('tasks', 'Task')
                if Task is not None:
                    project_tasks = Task.objects.filter(project=board.project).values_list('id', flat=True)
                    next_order = first_col.task_columns.count()
                    for task_id in project_tasks:
                        if task_id not in existing_task_ids:
                            TaskColumn.objects.create(
                                task_id=task_id,
                                column=first_col,
                                order=next_order,
                            )
                            next_order += 1
            # Refresh columns after potential inserts
            columns = board.columns.order_by('order')
            return Response(KanbanColumnSerializer(columns, many=True).data)

        serializer = KanbanColumnCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        column = KanbanColumn.objects.create(board=board, **serializer.validated_data)
        return Response(
            KanbanColumnSerializer(column).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['put'], url_path='columns/(?P<column_id>[^/.]+)')
    def update_column(self, request, pk=None, column_id=None):
        board = self.get_object()
        try:
            column = board.columns.get(id=column_id)
        except KanbanColumn.DoesNotExist:
            return Response(
                {'detail': 'Column not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = KanbanColumnCreateSerializer(column, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(KanbanColumnSerializer(column).data)

    @action(detail=True, methods=['delete'], url_path='columns/(?P<column_id>[^/.]+)')
    def delete_column(self, request, pk=None, column_id=None):
        board = self.get_object()
        try:
            column = board.columns.get(id=column_id)
        except KanbanColumn.DoesNotExist:
            return Response(
                {'detail': 'Column not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        column.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='move-task')
    def move_task(self, request, pk=None):
        board = self.get_object()
        serializer = KanbanTaskMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = serializer.validated_data['task_id']
        target_column = serializer.validated_data['target_column_id']
        new_order = serializer.validated_data['order']

        if target_column.board_id != board.id:
            return Response(
                {'detail': 'Target column does not belong to this board.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        TaskColumn.objects.filter(task_id=task_id).delete()

        tc = TaskColumn.objects.create(
            task_id=task_id,
            column=target_column,
            order=new_order,
        )
        return Response({
            'task_column_id': str(tc.id),
            'task_id': str(tc.task_id),
            'column_id': str(tc.column_id),
            'order': tc.order,
        }, status=status.HTTP_201_CREATED)
