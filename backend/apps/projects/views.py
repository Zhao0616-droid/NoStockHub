from django.apps import apps
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsProjectManager, IsProjectMember

from .models import Milestone, Project, ProjectMember, ProjectTemplate
from .serializers import (
    MemberAddSerializer,
    MilestoneCreateSerializer,
    MilestoneSerializer,
    ProjectCreateSerializer,
    ProjectMemberSerializer,
    ProjectSerializer,
    ProjectTemplateSerializer,
    ProjectUpdateSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'end_date', 'status']
    ordering = ['-created_at']
    filterset_fields = ['status', 'visibility']

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Project.objects.select_related('owner', 'template', 'template__created_by')
            .annotate(member_count=Count('members', distinct=True))
        )

        if not user.is_staff:
            queryset = queryset.filter(
                Q(visibility=Project.Visibility.PUBLIC)
                | Q(owner=user)
                | Q(members__user=user)
            )
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        return ProjectSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'update_or_remove_member']:
            return [IsAuthenticated(), IsProjectManager()]
        if self.action == 'members' and self.request.method == 'POST':
            return [IsAuthenticated(), IsProjectManager()]
        if self.action == 'milestones' and self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsProjectManager()]
        if self.action in ['retrieve', 'members', 'milestones', 'gantt']:
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ProjectMember.objects.get_or_create(
            project=project,
            user=self.request.user,
            defaults={'role': ProjectMember.Role.MANAGER},
        )

    @action(detail=True, methods=['get', 'post'], url_path='members')
    def members(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            queryset = project.members.select_related('user')
            serializer = ProjectMemberSerializer(queryset, many=True)
            return Response(serializer.data)

        self.check_object_permissions(request, project)
        serializer = MemberAddSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        member = ProjectMember.objects.create(
            project=project,
            user=serializer.validated_data['user'],
            role=serializer.validated_data['role'],
        )
        return Response(ProjectMemberSerializer(member).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['put', 'patch', 'delete'],
        url_path='members/(?P<member_id>[^/.]+)',
    )
    def update_or_remove_member(self, request, pk=None, member_id=None):
        project = self.get_object()
        try:
            member = project.members.get(id=member_id)
        except ProjectMember.DoesNotExist:
            return Response({'detail': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            if member.user_id == project.owner_id:
                return Response({'detail': 'Project owner cannot be removed.'}, status=status.HTTP_400_BAD_REQUEST)
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        role = request.data.get('role')
        valid_roles = [choice[0] for choice in ProjectMember.Role.choices]
        if role not in valid_roles:
            return Response({'role': ['Invalid role.']}, status=status.HTTP_400_BAD_REQUEST)
        member.role = role
        member.save(update_fields=['role'])
        return Response(ProjectMemberSerializer(member).data)

    @action(detail=True, methods=['get', 'post', 'patch', 'delete'], url_path='milestones')
    def milestones(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            queryset = project.milestones.all()
            serializer = MilestoneSerializer(queryset, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = MilestoneCreateSerializer(data=request.data, context={'project': project})
            serializer.is_valid(raise_exception=True)
            milestone = serializer.save(project=project)
            return Response(MilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED)

        # PATCH / DELETE require milestone_id
        milestone_id = request.data.get('milestone_id')
        if not milestone_id:
            return Response({'detail': 'milestone_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            milestone = project.milestones.get(id=milestone_id)
        except Milestone.DoesNotExist:
            return Response({'detail': 'Milestone not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            milestone.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # PATCH
        serializer = MilestoneCreateSerializer(milestone, data=request.data, partial=True, context={'project': project})
        serializer.is_valid(raise_exception=True)
        milestone = serializer.save()
        return Response(MilestoneSerializer(milestone).data)

    @action(detail=True, methods=['get'], url_path='gantt')
    def gantt(self, request, pk=None):
        from django.apps import apps

        project = self.get_object()
        tasks = []
        dependencies = []

        try:
            Task = apps.get_model('tasks', 'Task')
            Dependency = apps.get_model('tasks', 'TaskDependency')
        except LookupError:
            Task = None
            Dependency = None

        if Task is not None:
            for task in Task.objects.filter(project=project).order_by('start_date', 'due_date'):
                tasks.append({
                    'id': str(task.id),
                    'title': task.title,
                    'start_date': task.start_date,
                    'due_date': task.due_date,
                    'status': task.status,
                    'progress': task.progress,
                })

        if Dependency is not None:
            for dep in Dependency.objects.filter(predecessor__project=project, successor__project=project):
                dependencies.append({
                    'id': str(dep.id),
                    'predecessor_id': str(dep.predecessor_id),
                    'successor_id': str(dep.successor_id),
                    'relation_type': dep.relation_type,
                })

        milestones = MilestoneSerializer(project.milestones.all(), many=True).data
        return Response({
            'project': ProjectSerializer(project).data,
            'tasks': tasks,
            'dependencies': dependencies,
            'milestones': milestones,
        })

    @action(detail=True, methods=['get'], url_path='activity')
    def activity(self, request, pk=None):
        from django.apps import apps

        project = self.get_object()
        activities = []

        try:
            Task = apps.get_model('tasks', 'Task')
        except LookupError:
            Task = None

        if Task is not None:
            tasks = Task.objects.filter(project=project).order_by('-created_at')[:20]
            for task in tasks:
                activities.append({
                    'id': f'task-{task.id}',
                    'type': 'task_created' if task.created_at == task.updated_at else 'task_updated',
                    'content': f'创建了任务「{task.title}」' if task.created_at == task.updated_at else f'更新了任务「{task.title}」',
                    'time': task.updated_at or task.created_at,
                    'user': task.assignee.username if task.assignee else (task.reporter.username if hasattr(task, 'reporter') and task.reporter else '系统'),
                })

        # milestones
        for ms in project.milestones.order_by('-created_at')[:10]:
            activities.append({
                'id': f'milestone-{ms.id}',
                'type': 'milestone',
                'content': f'里程碑「{ms.name}」',
                'time': ms.created_at,
                'user': '系统',
            })

        activities.sort(key=lambda x: x['time'], reverse=True)
        return Response(activities[:30])


class ProjectTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectTemplateSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return ProjectTemplate.objects.select_related('created_by').all()

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """仪表盘聚合数据"""
    user = request.user

    # 用户可访问的项目
    if user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(visibility=Project.Visibility.PUBLIC)
            | Q(owner=user)
            | Q(members__user=user)
        ).distinct()

    project_ids = list(projects.values_list('id', flat=True))

    # 任务查询
    Task = apps.get_model('tasks', 'Task')
    tasks = Task.objects.filter(project_id__in=project_ids) if project_ids else Task.objects.none()

    # 冲刺查询
    Sprint = apps.get_model('sprints', 'Sprint')
    sprints = Sprint.objects.filter(project_id__in=project_ids) if project_ids else Sprint.objects.none()

    # --- 统计 ---
    total_tasks = tasks.count()
    done_tasks = tasks.filter(status='done').count()
    pending_tasks = total_tasks - done_tasks
    completion_rate = round(done_tasks / total_tasks * 100) if total_tasks > 0 else 0

    stats = {
        'project_count': projects.count(),
        'pending_task_count': pending_tasks,
        'active_sprint_count': sprints.filter(status='active').count(),
        'completion_rate': completion_rate,
    }

    # --- 我的任务 ---
    my_tasks = tasks.filter(assignee=user).exclude(status='done').order_by('-created_at')[:10]
    my_tasks_data = [
        {
            'id': str(t.id),
            'title': t.title,
            'priority': t.priority,
            'status': t.status,
            'due_date': str(t.due_date) if t.due_date else None,
            'project_id': str(t.project_id),
            'project_name': t.project.name,
        }
        for t in my_tasks
    ]

    # --- 最近项目 ---
    recent_projects = projects.order_by('-created_at')[:5]
    recent_projects_data = []
    for p in recent_projects:
        # 计算进度: done / total
        if p.status == Project.Status.COMPLETED:
            progress = 100
        else:
            try:
                total = Task.objects.filter(project=p).count()
                done = Task.objects.filter(project=p, status='done').count()
                progress = round(done / total * 100) if total > 0 else 0
            except Exception:
                progress = 0
        recent_projects_data.append({
            'id': str(p.id),
            'name': p.name,
            'progress': progress,
            'status': p.status,
        })

    # --- 最近活动 ---
    activities = []
    # 最近创建的任务
    recent_created = tasks.order_by('-created_at')[:5]
    for t in recent_created:
        activities.append({
            'id': f'create_{t.id}',
            'content': f'创建了任务「{t.title}」',
            'time': t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else '',
            'project_name': t.project.name,
        })
    # 最近完成的任务
    recent_done = tasks.filter(status='done').order_by('-updated_at')[:5]
    for t in recent_done:
        activities.append({
            'id': f'done_{t.id}',
            'content': f'完成了任务「{t.title}」',
            'time': t.updated_at.strftime('%Y-%m-%d %H:%M') if t.updated_at else '',
            'project_name': t.project.name,
        })
    # 按时间倒序取最近15条
    activities.sort(key=lambda a: a['time'], reverse=True)
    activities = activities[:15]

    return Response({
        'stats': stats,
        'my_tasks': my_tasks_data,
        'recent_projects': recent_projects_data,
        'activities': activities,
    })
