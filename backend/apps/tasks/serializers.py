from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models as db_models
from rest_framework import serializers

from .models import Comment, Mention, Task, TaskDependency


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
    }


def _get_sprint_model():
    try:
        return apps.get_model('sprints', 'Sprint')
    except LookupError:
        return None


class TaskListSerializer(serializers.ModelSerializer):
    """精简列表序列化器"""
    assignee = serializers.SerializerMethodField()
    project_id = serializers.UUIDField(source='project.id', read_only=True)
    sprint_id = serializers.UUIDField(source='sprint.id', read_only=True, default=None)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'type', 'status', 'priority',
            'start_date', 'due_date', 'progress', 'order',
            'project_id', 'sprint_id', 'assignee', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_assignee(self, obj):
        return user_summary(obj.assignee)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'task_id', 'project_id',
                   'parent_comment_id', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_author(self, obj):
        return user_summary(obj.author)

    def get_replies(self, obj):
        replies = obj.replies.all()
        if not replies:
            return []
        return CommentSerializer(replies, many=True).data


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'task_id', 'project_id', 'parent_comment_id']
        read_only_fields = ['id']


class TaskDependencySerializer(serializers.ModelSerializer):
    predecessor_title = serializers.CharField(source='predecessor.title', read_only=True)
    successor_title = serializers.CharField(source='successor.title', read_only=True)

    class Meta:
        model = TaskDependency
        fields = ['id', 'predecessor', 'successor', 'relation_type',
                   'predecessor_title', 'successor_title', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskDependencyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDependency
        fields = ['id', 'predecessor', 'successor', 'relation_type']
        read_only_fields = ['id']

    def validate(self, attrs):
        predecessor = attrs.get('predecessor')
        successor = attrs.get('successor')
        if predecessor and successor and predecessor.id == successor.id:
            raise serializers.ValidationError('A task cannot depend on itself.')
        if predecessor and successor and predecessor.project_id != successor.project_id:
            raise serializers.ValidationError('Tasks must belong to the same project.')
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reporter = serializers.SerializerMethodField()
    project_id = serializers.UUIDField(source='project.id', read_only=True)
    sprint_id = serializers.UUIDField(source='sprint.id', read_only=True, default=None)
    parent_task_id = serializers.UUIDField(source='parent_task.id', read_only=True, default=None)
    subtasks = TaskListSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    dependencies = serializers.SerializerMethodField()
    subtask_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'type', 'status', 'priority',
            'start_date', 'due_date', 'estimated_hours', 'actual_hours',
            'progress', 'order', 'project_id', 'sprint_id', 'parent_task_id',
            'assignee', 'reporter', 'subtasks', 'comments', 'dependencies',
            'subtask_count', 'comment_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'reporter', 'created_at', 'updated_at']

    def get_assignee(self, obj):
        return user_summary(obj.assignee)

    def get_reporter(self, obj):
        return user_summary(obj.reporter)

    def get_dependencies(self, obj):
        deps = TaskDependency.objects.filter(
            db_models.Q(predecessor=obj) | db_models.Q(successor=obj)
        )
        return TaskDependencySerializer(deps, many=True).data

    def get_subtask_count(self, obj):
        return obj.subtasks.count()

    def get_comment_count(self, obj):
        return obj.comments.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('projects', 'Project').objects.all(),
        source='project',
    )
    sprint_id = serializers.PrimaryKeyRelatedField(
        queryset=_get_sprint_model().objects.all() if _get_sprint_model() else [],
        source='sprint',
        required=False,
        allow_null=True,
    )
    parent_task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source='parent_task',
        required=False,
        allow_null=True,
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        source='assignee',
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'type', 'priority',
            'start_date', 'due_date', 'estimated_hours', 'order',
            'project_id', 'sprint_id', 'parent_task_id', 'assignee_id',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        due_date = attrs.get('due_date')
        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError('Due date cannot be earlier than start date.')
        parent = attrs.get('parent_task')
        if parent:
            project = attrs.get('project')
            if project and parent.project_id != project.id:
                raise serializers.ValidationError('Parent task must belong to the same project.')
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        source='assignee',
        required=False,
        allow_null=True,
    )
    sprint_id = serializers.PrimaryKeyRelatedField(
        queryset=_get_sprint_model().objects.all() if _get_sprint_model() else [],
        source='sprint',
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'type', 'status', 'priority',
            'start_date', 'due_date', 'estimated_hours', 'actual_hours',
            'progress', 'order', 'sprint_id', 'assignee_id',
        ]

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        due_date = attrs.get('due_date', getattr(self.instance, 'due_date', None))
        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError('Due date cannot be earlier than start date.')
        return attrs


class TaskStatusTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.Status.choices)

    def validate_status(self, value):
        valid_transitions = {
            Task.Status.TODO: [Task.Status.IN_PROGRESS],
            Task.Status.IN_PROGRESS: [Task.Status.REVIEW, Task.Status.BLOCKED, Task.Status.TODO],
            Task.Status.REVIEW: [Task.Status.DONE, Task.Status.IN_PROGRESS],
            Task.Status.BLOCKED: [Task.Status.IN_PROGRESS],
            Task.Status.DONE: [Task.Status.IN_PROGRESS],
        }
        current = self.instance.status if self.instance else None
        if current and value not in valid_transitions.get(current, []):
            raise serializers.ValidationError(
                f'Cannot transition from "{current}" to "{value}".'
            )
        return value
