from rest_framework import serializers
from .models import Task, TaskDependency, Comment, Mention
from apps.accounts.serializers import UserSerializer

class TaskDependencySerializer(serializers.ModelSerializer):
    predecessor_title = serializers.CharField(source='predecessor.title', read_only=True)
    successor_title = serializers.CharField(source='successor.title', read_only=True)

    class Meta:
        model = TaskDependency
        fields = ['id', 'predecessor', 'predecessor_title', 'successor', 'successor_title', 'relation_type']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'task', 'project', 'parent_comment', 'replies', 'created_at', 'updated_at']

    def get_replies(self, obj):
        # 仅展示直接回复，避免无限递归，前端可另行请求或递归处理
        replies = obj.replies.all()[:5] 
        return CommentSerializer(replies, many=True).data

class TaskListSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'status_display', 'priority', 'priority_display', 
                  'due_date', 'assignee', 'progress', 'project']

class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reporter = UserSerializer(read_only=True)
    subtasks = serializers.SerializerMethodField()
    dependencies = TaskDependencySerializer(many=True, read_only=True, source='predecessor_dependencies') # 注意：这里展示的是当前任务作为前驱的依赖，或者根据需求调整
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'

    def get_subtasks(self, obj):
        subtasks = obj.subtasks.all()
        return TaskListSerializer(subtasks, many=True).data

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'type', 'priority', 'start_date', 'due_date', 
                  'estimated_hours', 'project', 'sprint', 'parent_task', 'assignee']

    def validate(self, data):
        if data.get('due_date') and data.get('start_date'):
            if data['due_date'] < data['start_date']:
                raise serializers.ValidationError("截止日期不能早于开始日期。")
        return data

class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']