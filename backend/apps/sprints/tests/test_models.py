import pytest
from datetime import date
from apps.accounts.models import User
from apps.projects.models import Project
from apps.sprints.models import Sprint

pytestmark = pytest.mark.django_db


class TestSprintModel:
    def test_create_sprint_defaults(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        sprint = Sprint.objects.create(
            name='Sprint 1', start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 14), project=project,
        )
        assert sprint.status == 'planning'

    def test_sprint_status_choices(self):
        choices = [c[0] for c in Sprint.Status.choices]
        assert choices == ['planning', 'active', 'completed']

    def test_sprint_str(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        sprint = Sprint.objects.create(
            name='Sprint 2', start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 14), project=project,
        )
        assert str(sprint) == 'Sprint 2'

    def test_sprint_belongs_to_project(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        sprint = Sprint.objects.create(
            name='S1', start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 14), project=project,
        )
        assert sprint.project_id == project.id
