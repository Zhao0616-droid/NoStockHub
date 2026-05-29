from django.contrib.auth import get_user_model
from django.apps import apps
from rest_framework import serializers

from .models import Milestone, Project, ProjectMember, ProjectTemplate


def user_summary(user):
    if user is None:
        return None
    return {
        'id': str(user.id),
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
    }


class ProjectTemplateSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTemplate
        fields = ['id', 'name', 'description', 'config', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_created_by(self, obj):
        return user_summary(obj.created_by)


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']

    def get_user(self, obj):
        return user_summary(obj.user)


class MemberAddSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=False)
    username = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=ProjectMember.Role.choices, default=ProjectMember.Role.MEMBER)

    def validate(self, attrs):
        User = get_user_model()
        project = self.context['project']

        username = attrs.get('username')
        user_id = attrs.get('user_id')

        if not username and not user_id:
            raise serializers.ValidationError({'user_id': '请输入用户ID或用户名'})

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError({'username': '用户不存在'})
        else:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'user_id': '用户不存在'})

        if ProjectMember.objects.filter(project=project, user=user).exists():
            raise serializers.ValidationError({'user_id': '该用户已是项目成员'})

        attrs['user'] = user
        return attrs


class MilestoneSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='project.id', read_only=True)

    class Meta:
        model = Milestone
        fields = ['id', 'name', 'description', 'due_date', 'status', 'project_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'project_id', 'created_at', 'updated_at']


class MilestoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'name', 'description', 'due_date', 'status']
        read_only_fields = ['id']

    def validate_due_date(self, value):
        project = self.context.get('project')
        if project and project.start_date and value < project.start_date:
            raise serializers.ValidationError('Due date cannot be earlier than project start date.')
        if project and project.end_date and value > project.end_date:
            raise serializers.ValidationError('Due date cannot be later than project end date.')
        return value


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    template = ProjectTemplateSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'visibility',
            'status',
            'owner',
            'template',
            'member_count',
            'task_count',
            'progress',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'member_count', 'task_count', 'progress', 'created_at', 'updated_at']

    def get_owner(self, obj):
        return user_summary(obj.owner)

    def get_task_count(self, obj):
        try:
            Task = apps.get_model('tasks', 'Task')
        except LookupError:
            return 0

        if not hasattr(Task, 'project'):
            return 0
        return Task.objects.filter(project=obj).count()

    def get_project_tasks_progress(self, obj):
        try:
            Task = apps.get_model('tasks', 'Task')
        except LookupError:
            return None

        if not hasattr(Task, 'project'):
            return None
        total = Task.objects.filter(project=obj).count()
        if total == 0:
            return 0
        done = Task.objects.filter(project=obj, status='done').count()
        return round(done / total * 100)

    def get_progress(self, obj):
        if obj.status == Project.Status.COMPLETED:
            return 100
        avg_progress = self.get_project_tasks_progress(obj)
        if avg_progress is not None:
            return round(avg_progress)
        return 0


class ProjectCreateSerializer(serializers.ModelSerializer):
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=ProjectTemplate.objects.all(),
        source='template',
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'visibility', 'template_id']
        read_only_fields = ['id']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError('End date cannot be earlier than start date.')
        return attrs


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'visibility', 'status']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError('End date cannot be earlier than start date.')
        return attrs
