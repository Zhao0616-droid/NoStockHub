from django.db import models

from core.models import BaseModel, TimestampedModel


class KanbanBoard(TimestampedModel):
    class BoardType(models.TextChoices):
        TEAM = 'team', 'Team'
        VERSION = 'version', 'Version'
        SUB_PROJECT = 'sub_project', 'Sub Project'

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=BoardType.choices,
        default=BoardType.TEAM,
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='kanban_boards',
    )

    class Meta:
        db_table = 'kanban_kanbanboard'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project'], name='idx_board_project'),
        ]

    def __str__(self):
        return self.name


class KanbanColumn(TimestampedModel):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    wip_limit = models.IntegerField(default=0)
    board = models.ForeignKey(
        KanbanBoard,
        on_delete=models.CASCADE,
        related_name='columns',
    )

    class Meta:
        db_table = 'kanban_kanbancolumn'
        ordering = ['order']
        indexes = [
            models.Index(fields=['board', 'order'], name='idx_column_board_order'),
        ]

    def __str__(self):
        return f'{self.board.name} / {self.name}'


class TaskColumn(BaseModel):
    task_id = models.UUIDField()
    column = models.ForeignKey(
        KanbanColumn,
        on_delete=models.CASCADE,
        related_name='task_columns',
    )
    order = models.IntegerField(default=0)
    moved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kanban_taskcolumn'
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['task_id', 'column'],
                name='uk_task_column',
            ),
        ]

    def __str__(self):
        return f'{self.task_id} @ {self.column_id}'
