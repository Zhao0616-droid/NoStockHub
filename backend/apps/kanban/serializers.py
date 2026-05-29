from django.apps import apps
from rest_framework import serializers

from .models import KanbanBoard, KanbanColumn, TaskColumn


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
        'avatar': getattr(user, 'avatar', ''),
    }


def _get_task_model():
    try:
        return apps.get_model('tasks', 'Task')
    except LookupError:
        return None


class KanbanColumnSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = KanbanColumn
        fields = ['id', 'name', 'order', 'wip_limit', 'board_id', 'tasks', 'created_at']
        read_only_fields = ['id', 'board_id', 'created_at']

    def get_tasks(self, obj):
        Task = _get_task_model()
        task_columns = obj.task_columns.all()
        task_ids = [tc.task_id for tc in task_columns]

        tasks = []
        if Task is not None:
            task_map = {
                str(t.id): t
                for t in Task.objects.filter(id__in=task_ids)
            }
        else:
            task_map = {}

        for tc in task_columns:
            task = task_map.get(str(tc.task_id))
            tasks.append({
                'task_column_id': str(tc.id),
                'id': str(tc.task_id),
                'order': tc.order,
                'title': getattr(task, 'title', '') if task else '',
                'status': getattr(task, 'status', '') if task else '',
                'priority': getattr(task, 'priority', '') if task else '',
                'type': getattr(task, 'type', 'task') if task else 'task',
                'due_date': str(getattr(task, 'due_date', '')) if task and getattr(task, 'due_date', None) else '',
                'estimated_hours': getattr(task, 'estimated_hours', 0) or 0 if task else 0,
                'progress': getattr(task, 'progress', 0) or 0 if task else 0,
                'assignee': user_summary(task.assignee) if task and getattr(task, 'assignee', None) else None,
            })
        return tasks


class KanbanColumnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanColumn
        fields = ['id', 'name', 'order', 'wip_limit']
        read_only_fields = ['id']


class KanbanBoardSerializer(serializers.ModelSerializer):
    columns = KanbanColumnSerializer(many=True, read_only=True)
    project_id = serializers.UUIDField(source='project.id', read_only=True)

    class Meta:
        model = KanbanBoard
        fields = ['id', 'name', 'type', 'project_id', 'columns', 'created_at', 'updated_at']
        read_only_fields = ['id', 'project_id', 'created_at', 'updated_at']


class KanbanBoardCreateSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('projects', 'Project').objects.all(),
        source='project',
    )

    class Meta:
        model = KanbanBoard
        fields = ['id', 'name', 'type', 'project_id']
        read_only_fields = ['id']


class KanbanTaskMoveSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()
    target_column_id = serializers.UUIDField()
    order = serializers.IntegerField(default=0)

    def validate_target_column_id(self, value):
        try:
            return KanbanColumn.objects.get(id=value)
        except KanbanColumn.DoesNotExist as exc:
            raise serializers.ValidationError('Target column does not exist.') from exc
