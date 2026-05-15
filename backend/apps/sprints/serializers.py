from datetime import date, timedelta

from django.apps import apps
from django.db import models as db_models
from rest_framework import serializers

from .models import Sprint


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
    }


def _get_task_model():
    try:
        return apps.get_model('tasks', 'Task')
    except LookupError:
        return None


class SprintSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='project.id', read_only=True)
    task_count = serializers.SerializerMethodField()
    total_estimated = serializers.SerializerMethodField()
    total_actual = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Sprint
        fields = [
            'id', 'name', 'goal', 'start_date', 'end_date',
            'status', 'project_id', 'task_count', 'total_estimated',
            'total_actual', 'progress', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'project_id', 'task_count',
            'total_estimated', 'total_actual', 'progress',
            'created_at', 'updated_at',
        ]

    def get_task_count(self, obj):
        Task = _get_task_model()
        if Task is None:
            return 0
        return Task.objects.filter(sprint=obj).count()

    def get_total_estimated(self, obj):
        Task = _get_task_model()
        if Task is None:
            return 0
        result = Task.objects.filter(sprint=obj).aggregate(
            total=db_models.Sum('estimated_hours')
        )
        return result['total'] or 0

    def get_total_actual(self, obj):
        Task = _get_task_model()
        if Task is None:
            return 0
        result = Task.objects.filter(sprint=obj).aggregate(
            total=db_models.Sum('actual_hours')
        )
        return result['total'] or 0

    def get_progress(self, obj):
        Task = _get_task_model()
        if Task is None:
            return 0
        tasks = Task.objects.filter(sprint=obj)
        total = tasks.count()
        if total == 0:
            return 0
        completed = tasks.filter(status__in=['done', 'completed']).count()
        return round(completed / total * 100)


class SprintCreateSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('projects', 'Project').objects.all(),
        source='project',
    )

    class Meta:
        model = Sprint
        fields = ['id', 'name', 'goal', 'start_date', 'end_date', 'project_id']
        read_only_fields = ['id']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError('End date cannot be earlier than start date.')
        return attrs


class SprintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['name', 'goal', 'start_date', 'end_date']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError('End date cannot be earlier than start date.')
        return attrs


class SprintTaskManageSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()

    def validate_task_id(self, value):
        Task = _get_task_model()
        if Task is None:
            raise serializers.ValidationError('Tasks module is not available.')
        try:
            return Task.objects.get(id=value)
        except Task.DoesNotExist as exc:
            raise serializers.ValidationError('Task does not exist.') from exc
