from django.apps import apps
from rest_framework import serializers

from .models import Report


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
    }


class ReportSerializer(serializers.ModelSerializer):
    generated_by = serializers.SerializerMethodField()
    project_id = serializers.UUIDField(source='project.id', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'name', 'type', 'project_id', 'generated_by',
            'parameters', 'file_path', 'status', 'created_at',
        ]
        read_only_fields = [
            'id', 'generated_by', 'project_id', 'file_path',
            'status', 'created_at',
        ]

    def get_generated_by(self, obj):
        return user_summary(obj.generated_by)

    def get_status(self, obj):
        return 'ready' if obj.file_path else 'generating'


class ReportGenerateSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=apps.get_model('projects', 'Project').objects.all(),
        source='project',
    )

    class Meta:
        model = Report
        fields = ['id', 'name', 'type', 'project_id', 'parameters']
        read_only_fields = ['id']
