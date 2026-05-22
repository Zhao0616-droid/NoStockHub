import pytest
from datetime import date
from decimal import Decimal
from apps.accounts.models import User
from apps.projects.models import Project
from apps.tasks.models import Task, TaskDependency, Comment

pytestmark = pytest.mark.django_db


class TestTaskModel:
    def test_create_task_defaults(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        task = Task.objects.create(title='测试任务', project=project, reporter=django_user)
        assert task.status == 'todo'
        assert task.priority == 'medium'
        assert task.type == 'task'
        assert task.progress == 0

    def test_task_status_choices(self):
        choices = [c[0] for c in Task.STATUS_CHOICES]
        assert choices == ['todo', 'in_progress', 'review', 'done', 'blocked']

    def test_task_priority_choices(self):
        choices = [c[0] for c in Task.PRIORITY_CHOICES]
        assert choices == ['low', 'medium', 'high', 'urgent']

    def test_task_type_choices(self):
        choices = [c[0] for c in Task.TASK_TYPE_CHOICES]
        assert 'epic' in choices and 'bug' in choices

    def test_task_str(self, django_user):
        project = Project.objects.create(name='P2', owner=django_user)
        task = Task.objects.create(title='设计ER图', project=project, reporter=django_user)
        assert str(task) == '设计ER图'

    def test_parent_subtask_relationship(self, django_user):
        project = Project.objects.create(name='P3', owner=django_user)
        parent = Task.objects.create(title='父任务', project=project, reporter=django_user)
        child = Task.objects.create(title='子任务', project=project, reporter=django_user, parent_task=parent)
        assert child.parent_task == parent
        assert parent.subtasks.count() == 1

    def test_task_belongs_to_project(self, django_user):
        project = Project.objects.create(name='P4', owner=django_user)
        task = Task.objects.create(title='T', project=project, reporter=django_user)
        assert task.project_id == project.id
        assert project.tasks.count() == 1


class TestTaskDependencyModel:
    def test_create_dependency_default(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        t1 = Task.objects.create(title='前驱', project=project, reporter=django_user)
        t2 = Task.objects.create(title='后继', project=project, reporter=django_user)
        dep = TaskDependency.objects.create(predecessor=t1, successor=t2)
        assert dep.relation_type == 'precedes'

    def test_dependency_unique_pair(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        t1 = Task.objects.create(title='A', project=project, reporter=django_user)
        t2 = Task.objects.create(title='B', project=project, reporter=django_user)
        TaskDependency.objects.create(predecessor=t1, successor=t2)
        with pytest.raises(Exception):
            TaskDependency.objects.create(predecessor=t1, successor=t2)


class TestCommentModel:
    def test_comment_on_task(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        task = Task.objects.create(title='T', project=project, reporter=django_user)
        comment = Comment.objects.create(content='测试评论', author=django_user, task=task)
        assert comment.task == task
        assert comment.project is None

    def test_comment_without_target_raises(self, django_user):
        with pytest.raises(ValueError, match='Task or a Project'):
            Comment.objects.create(content='无关联', author=django_user)

    def test_comment_nested_reply(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        task = Task.objects.create(title='T', project=project, reporter=django_user)
        parent = Comment.objects.create(content='主评论', author=django_user, task=task)
        reply = Comment.objects.create(content='回复', author=django_user, task=task, parent_comment=parent)
        assert reply.parent_comment == parent
        assert parent.replies.count() == 1

    def test_comment_on_project(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        comment = Comment.objects.create(content='项目评论', author=django_user, project=project)
        assert comment.project == project
        assert comment.task is None
