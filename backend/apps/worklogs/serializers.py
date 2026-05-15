from django.apps import apps
from rest_framework import serializers

from .models import HourlyRate, WorkLog


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
    }


class WorkLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    task_id = serializers.UUIDField(source='task.id', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = WorkLog
        fields = [
            'id', 'task_id', 'task_title', 'user', 'hours',
            'date', 'description', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'task_title', 'user', 'created_at', 'updated_at']

    def get_user(self, obj):
        return user_summary(obj.user)


class WorkLogCreateSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('tasks', 'Task').objects.all(),
        source='task',
    )

    class Meta:
        model = WorkLog
        fields = ['id', 'task_id', 'hours', 'date', 'description']
        read_only_fields = ['id']

    def validate_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError('Hours must be positive.')
        if value > 24:
            raise serializers.ValidationError('Hours cannot exceed 24 per entry.')
        return value


class WorkLogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = ['hours', 'date', 'description']


class HourlyRateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    project_id = serializers.UUIDField(source='project.id', read_only=True)

    class Meta:
        model = HourlyRate
        fields = ['id', 'user', 'project_id', 'rate', 'effective_from', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def get_user(self, obj):
        return user_summary(obj.user)


class HourlyRateCreateSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('projects', 'Project').objects.all(),
        source='project',
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('accounts', 'User').objects.all(),
        source='user',
    )

    class Meta:
        model = HourlyRate
        fields = ['id', 'user_id', 'project_id', 'rate', 'effective_from']
        read_only_fields = ['id']


class WorkLogSummarySerializer(serializers.Serializer):
    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    user_id = serializers.CharField()
    username = serializers.CharField()
    task_count = serializers.IntegerField()
