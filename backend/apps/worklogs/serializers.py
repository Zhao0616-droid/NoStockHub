from rest_framework import serializers
from .models import WorkLog, HourlyRate
from apps.accounts.serializers import UserSerializer


class WorkLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = WorkLog
        fields = ['id', 'task', 'task_title', 'user', 'hours', 'date', 'description', 'created_at', 'updated_at']

    def validate_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("工时必须大于0")
        if value > 24:
            raise serializers.ValidationError("单日工时不能超过24小时")
        return value


class HourlyRateSerializer(serializers.ModelSerializer):
    user_summary = serializers.SerializerMethodField()

    class Meta:
        model = HourlyRate
        fields = ['id', 'user', 'user_summary', 'project', 'rate', 'effective_from', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'user': {'required': False}}

    def get_user_summary(self, obj):
        return {'id': str(obj.user_id), 'username': obj.user.username, 'avatar': getattr(obj.user, 'avatar', '')}