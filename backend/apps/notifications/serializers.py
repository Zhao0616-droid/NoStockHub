from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='notification_type', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'title',
            'content',
            'is_read',
            'related_type',
            'related_id',
            'created_at',
        ]
        read_only_fields = tuple(fields)


class NotificationPagedListSerializer(serializers.Serializer):
    """仅供 OpenAPI（与 StandardPagination + unread_count 一致）。"""

    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = NotificationSerializer(many=True)
    unread_count = serializers.IntegerField()


class NotificationReadAllResponseSerializer(serializers.Serializer):
    updated = serializers.IntegerField()
