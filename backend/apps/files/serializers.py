from rest_framework import serializers

from .models import Attachment


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
    }


class AttachmentSerializer(serializers.ModelSerializer):
    uploader = serializers.SerializerMethodField()
    project_id = serializers.UUIDField(source='project.id', read_only=True)

    class Meta:
        model = Attachment
        fields = [
            'id', 'filename', 'file_path', 'file_size', 'mime_type',
            'task_id', 'project_id', 'uploader', 'uploaded_at',
        ]
        read_only_fields = [
            'id', 'filename', 'file_path', 'file_size', 'mime_type',
            'task_id', 'project_id', 'uploader', 'uploaded_at',
        ]

    def get_uploader(self, obj):
        return user_summary(obj.uploader)
