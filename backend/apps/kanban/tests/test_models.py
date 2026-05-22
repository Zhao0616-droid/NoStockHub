import pytest
from apps.accounts.models import User
from apps.projects.models import Project
from apps.kanban.models import KanbanBoard, KanbanColumn, TaskColumn

pytestmark = pytest.mark.django_db


class TestKanbanBoardModel:
    def test_create_board_defaults(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        board = KanbanBoard.objects.create(name='团队看板', project=project)
        assert board.type == 'team'

    def test_board_type_choices(self):
        choices = [c[0] for c in KanbanBoard.BoardType.choices]
        assert choices == ['team', 'version', 'sub_project']


class TestKanbanColumnModel:
    def test_create_column_defaults(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        board = KanbanBoard.objects.create(name='B', project=project)
        column = KanbanColumn.objects.create(name='待办', board=board)
        assert column.wip_limit == 0
        assert column.order == 0

    def test_column_ordered_by_order_field(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        board = KanbanBoard.objects.create(name='B', project=project)
        c1 = KanbanColumn.objects.create(name='C1', board=board, order=2)
        c2 = KanbanColumn.objects.create(name='C2', board=board, order=1)
        columns = list(KanbanColumn.objects.all())
        assert columns[0] == c2


class TestTaskColumnModel:
    def test_unique_task_column_constraint(self, django_user):
        project = Project.objects.create(name='P', owner=django_user)
        board = KanbanBoard.objects.create(name='B', project=project)
        column = KanbanColumn.objects.create(name='待办', board=board)
        TaskColumn.objects.create(task_id='550e8400-e29b-41d4-a716-446655440000', column=column)
        with pytest.raises(Exception):
            TaskColumn.objects.create(task_id='550e8400-e29b-41d4-a716-446655440000', column=column)
