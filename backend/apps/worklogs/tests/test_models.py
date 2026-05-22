import pytest
from datetime import date
from decimal import Decimal
from apps.accounts.models import User
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.worklogs.models import WorkLog, HourlyRate

pytestmark = pytest.mark.django_db


class TestWorkLogModel:
    def test_create_worklog_updates_task_hours(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        task = Task.objects.create(title='T', project=project, reporter=django_user)
        assert task.actual_hours == Decimal('0.00')

        WorkLog.objects.create(task=task, user=django_user, hours=4.5, date=date.today())
        task.refresh_from_db()
        assert task.actual_hours == Decimal('4.50')

    def test_multiple_worklogs_sum_hours(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        task = Task.objects.create(title='T', project=project, reporter=django_user)
        WorkLog.objects.create(task=task, user=django_user, hours=3.0, date=date.today())
        WorkLog.objects.create(task=task, user=django_user, hours=2.5, date=date.today())
        task.refresh_from_db()
        assert task.actual_hours == Decimal('5.50')


class TestHourlyRateModel:
    def test_unique_user_project_date_constraint(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        HourlyRate.objects.create(
            user=django_user, project=project, rate=100, effective_from=date.today()
        )
        with pytest.raises(Exception):
            HourlyRate.objects.create(
                user=django_user, project=project, rate=120, effective_from=date.today()
            )
