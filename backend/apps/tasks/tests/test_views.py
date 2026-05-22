import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Task
from apps.tasks.views import TaskViewSet

pytestmark = pytest.mark.django_db


class TestTaskViewSetFiltering:
    def test_filter_by_status(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        ProjectMember.objects.create(project=project, user=django_user)
        Task.objects.create(title='待办', project=project, reporter=django_user, status='todo')
        Task.objects.create(title='已完成', project=project, reporter=django_user, status='done')
        factory = APIRequestFactory()
        request = factory.get('/api/tasks/?status=done')
        force_authenticate(request, user=django_user)
        view = TaskViewSet.as_view({'get': 'list'})
        response = view(request)
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == '已完成'

    def test_filter_by_priority(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        ProjectMember.objects.create(project=project, user=django_user)
        Task.objects.create(title='紧急', project=project, reporter=django_user, priority='urgent')
        Task.objects.create(title='普通', project=project, reporter=django_user, priority='low')
        factory = APIRequestFactory()
        request = factory.get('/api/tasks/?priority=urgent')
        force_authenticate(request, user=django_user)
        view = TaskViewSet.as_view({'get': 'list'})
        response = view(request)
        assert len(response.data['results']) == 1

    def test_filter_by_project_id(self, django_user):
        p1 = Project.objects.create(name='P1', owner=django_user)
        p2 = Project.objects.create(name='P2', owner=django_user)
        ProjectMember.objects.create(project=p1, user=django_user)
        ProjectMember.objects.create(project=p2, user=django_user)
        Task.objects.create(title='P1的任务', project=p1, reporter=django_user)
        Task.objects.create(title='P2的任务', project=p2, reporter=django_user)
        factory = APIRequestFactory()
        request = factory.get(f'/api/tasks/?project_id={p1.id}')
        force_authenticate(request, user=django_user)
        view = TaskViewSet.as_view({'get': 'list'})
        response = view(request)
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'P1的任务'
