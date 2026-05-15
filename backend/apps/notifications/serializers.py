from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'content', 'is_read',
            'related_type', 'related_id', 'created_at',
        ]
        read_only_fields = [
            'id', 'type', 'title', 'content',
            'related_type', 'related_id', 'created_at',
        ]
