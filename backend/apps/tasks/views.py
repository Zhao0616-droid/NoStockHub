from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task, TaskDependency, Comment, Mention
from .serializers import (
    TaskDetailSerializer, TaskListSerializer, TaskCreateSerializer, 
    TaskStatusUpdateSerializer, TaskDependencySerializer, CommentSerializer
)
from core.permissions import IsProjectMember
from apps.notifications.utils import create_notification

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        user = self.request.user
        # 基本隔离：只能看到参与项目的任务
        queryset = Task.objects.filter(project__members__user=user)
        
        # 筛选逻辑
        project_id = self.request.query_params.get('project_id')
        status_filter = self.request.query_params.get('status')
        assignee_id = self.request.query_params.get('assignee_id')
        priority_filter = self.request.query_params.get('priority')

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
            
        return queryset.select_related('assignee', 'reporter', 'project').prefetch_related('subtasks')

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskDetailSerializer

    def perform_create(self, serializer):
        task = serializer.save(reporter=self.request.user)
        # 发送通知给负责人
        if task.assignee:
            create_notification(
                user=task.assignee,
                type='task_assigned',
                title=f'新任务分配: {task.title}',
                content=f'{self.request.user.username} 将任务分配给了您',
                related_type='Task',
                related_id=str(task.id)
            )

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        old_status = task.status
        
        # 简单的状态机校验 (可根据 db.md扩展)
        valid_transitions = {
            'todo': ['in_progress', 'blocked'],
            'in_progress': ['review', 'blocked', 'todo'],
            'review': ['done', 'in_progress'],
            'blocked': ['todo', 'in_progress'],
            'done': []
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            return Response(
                {"error": f"无法从 {old_status} 流转到 {new_status}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        
        # 发送状态变更通知
        if task.assignee and task.assignee != request.user:
             create_notification(
                user=task.assignee,
                type='status_change',
                title=f'任务状态变更: {task.title}',
                content=f'任务状态从 {old_status} 变为 {new_status}',
                related_type='Task',
                related_id=str(task.id)
            )
            
        return Response(TaskDetailSerializer(task).data)

    @action(detail=True, methods=['get', 'post', 'delete'], url_path='dependencies(?:/(?P<dep_id>[^/.]+))?')
    def dependencies(self, request, pk=None, dep_id=None):
        task = self.get_object()
        if request.method == 'GET':
            deps = TaskDependency.objects.filter(predecessor=task)
            serializer = TaskDependencySerializer(deps, many=True)
            return Response(serializer.data)

        if request.method == 'DELETE':
            if not dep_id:
                return Response({"error": "dep_id required"}, status=status.HTTP_400_BAD_REQUEST)
            dep = get_object_or_404(TaskDependency, id=dep_id, predecessor=task)
            dep.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'POST':
            successor_id = request.data.get('successor_id')
            if not successor_id:
                return Response({"error": "successor_id required"}, status=status.HTTP_400_BAD_REQUEST)
            if successor_id == str(task.id):
                 return Response({"error": "不能依赖自身"}, status=status.HTTP_400_BAD_REQUEST)
            dep, created = TaskDependency.objects.get_or_create(
                predecessor=task,
                successor_id=successor_id,
                defaults={'relation_type': request.data.get('relation_type', 'precedes')}
            )
            serializer = TaskDependencySerializer(dep)
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == 'GET':
            comments = task.comments.filter(parent_comment__isnull=True) # 只获取根评论
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(author=request.user, task=task)
            
            # TODO: 解析 content 中的 @username 并创建 Mention 记录
            # parse_mentions(comment) 
            
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
