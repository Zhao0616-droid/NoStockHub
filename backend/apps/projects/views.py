from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
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
        if self.action == 'milestones' and self.request.method == 'POST':
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

    @action(detail=True, methods=['get', 'post'], url_path='milestones')
    def milestones(self, request, pk=None):
        project = self.get_object()
        if request.method == 'GET':
            queryset = project.milestones.all()
            serializer = MilestoneSerializer(queryset, many=True)
            return Response(serializer.data)

        serializer = MilestoneCreateSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        milestone = serializer.save(project=project)
        return Response(MilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED)

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
