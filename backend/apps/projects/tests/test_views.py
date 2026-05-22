import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.accounts.models import User
from apps.projects.models import Project
from apps.projects.views import ProjectViewSet

pytestmark = pytest.mark.django_db


class TestProjectViewSetPermissions:
    def test_unauthenticated_access_denied(self):
        factory = APIRequestFactory()
        request = factory.get('/api/projects/')
        view = ProjectViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 401

    def test_authenticated_can_list(self, django_user):
        factory = APIRequestFactory()
        request = factory.get('/api/projects/')
        force_authenticate(request, user=django_user)
        view = ProjectViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200

    def test_owner_sees_private_project(self, django_user):
        Project.objects.create(name='Private', owner=django_user, visibility='private')
        factory = APIRequestFactory()
        request = factory.get('/api/projects/')
        force_authenticate(request, user=django_user)
        view = ProjectViewSet.as_view({'get': 'list'})
        response = view(request)
        project_ids = [p['id'] for p in response.data['results']]
        assert len(project_ids) == 1

    def test_non_member_cannot_see_private(self):
        owner = User.objects.create_user(username='owner99', email='o99@t.com', password='pass')
        other = User.objects.create_user(username='other99', email='other99@t.com', password='pass')
        Project.objects.create(name='Private', owner=owner, visibility='private')
        factory = APIRequestFactory()
        request = factory.get('/api/projects/')
        force_authenticate(request, user=other)
        view = ProjectViewSet.as_view({'get': 'list'})
        response = view(request)
        project_ids = [p['id'] for p in response.data['results']]
        assert len(project_ids) == 0


class TestProjectViewSetCreate:
    def test_creator_becomes_manager(self, django_user):
        factory = APIRequestFactory()
        request = factory.post('/api/projects/', {'name': '新项目', 'start_date': '2026-06-01', 'end_date': '2026-07-01'}, format='json')
        force_authenticate(request, user=django_user)
        view = ProjectViewSet.as_view({'post': 'create'})
        response = view(request)
        assert response.status_code == 201
        project = Project.objects.get(id=response.data['id'])
        assert project.members.filter(user=django_user, role='manager').exists()
