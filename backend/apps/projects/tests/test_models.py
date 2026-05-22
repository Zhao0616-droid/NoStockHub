import pytest
from datetime import date
from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember, Milestone, ProjectTemplate

pytestmark = pytest.mark.django_db


class TestProjectModel:
    def test_create_project_defaults(self, django_user):
        project = Project.objects.create(name='测试项目', owner=django_user)
        assert project.status == 'planning'
        assert project.visibility == 'private'
        assert project.id is not None

    def test_project_status_choices(self):
        choices = [c[0] for c in Project.Status.choices]
        assert choices == ['planning', 'active', 'completed', 'archived']

    def test_project_visibility_choices(self):
        choices = [c[0] for c in Project.Visibility.choices]
        assert choices == ['public', 'private']

    def test_project_str(self, django_user):
        project = Project.objects.create(name='我的项目', owner=django_user)
        assert str(project) == '我的项目'

    def test_project_default_ordering(self, django_user):
        p1 = Project.objects.create(name='旧项目', owner=django_user)
        p2 = Project.objects.create(name='新项目', owner=django_user)
        projects = list(Project.objects.all())
        assert projects[0] == p2


class TestProjectMemberModel:
    def test_create_member_default_role(self, django_user):
        owner = User.objects.create_user(username='owner1', email='o1@t.com', password='pass')
        project = Project.objects.create(name='P1', owner=owner)
        member = ProjectMember.objects.create(project=project, user=django_user)
        assert member.role == 'member'

    def test_unique_project_user_constraint(self, django_user):
        owner = User.objects.create_user(username='owner2', email='o2@t.com', password='pass')
        project = Project.objects.create(name='P2', owner=owner)
        ProjectMember.objects.create(project=project, user=django_user)
        with pytest.raises(Exception):
            ProjectMember.objects.create(project=project, user=django_user)

    def test_member_role_choices(self):
        choices = [c[0] for c in ProjectMember.Role.choices]
        assert 'manager' in choices and 'member' in choices and 'viewer' in choices


class TestMilestoneModel:
    def test_create_milestone_defaults(self, django_user):
        project = Project.objects.create(name='P3', owner=django_user)
        ms = Milestone.objects.create(name='M1', due_date=date(2026, 6, 30), project=project)
        assert ms.status == 'pending'

    def test_milestone_str(self, django_user):
        project = Project.objects.create(name='P4', owner=django_user)
        ms = Milestone.objects.create(name='需求评审', due_date=date(2026, 7, 1), project=project)
        assert str(ms) == '需求评审'
