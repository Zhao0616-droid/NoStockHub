from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class Task(TimestampedModel):
    class Type(models.TextChoices):
        TASK = 'task', 'Task'
        MILESTONE = 'milestone', 'Milestone'
        BUG = 'bug', 'Bug'
        EPIC = 'epic', 'Epic'

    class Status(models.TextChoices):
        TODO = 'todo', 'Todo'
        IN_PROGRESS = 'in_progress', 'In Progress'
        REVIEW = 'review', 'Review'
        DONE = 'done', 'Done'
        BLOCKED = 'blocked', 'Blocked'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.TASK)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    progress = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    sprint = models.ForeignKey(
        'sprints.Sprint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_tasks',
    )

    class Meta:
        db_table = 'tasks_task'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['project'], name='idx_task_project'),
            models.Index(fields=['sprint'], name='idx_task_sprint'),
            models.Index(fields=['assignee'], name='idx_task_assignee'),
            models.Index(fields=['status'], name='idx_task_status'),
            models.Index(fields=['priority'], name='idx_task_priority'),
            models.Index(fields=['parent_task'], name='idx_task_parent'),
        ]

    def __str__(self):
        return self.title


class TaskDependency(TimestampedModel):
    class RelationType(models.TextChoices):
        BLOCKS = 'blocks', 'Blocks'
        PRECEDES = 'precedes', 'Precedes'
        RELATES_TO = 'relates_to', 'Relates To'

    predecessor = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='successor_deps',
    )
    successor = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='predecessor_deps',
    )
    relation_type = models.CharField(
        max_length=20,
        choices=RelationType.choices,
        default=RelationType.PRECEDES,
    )

    class Meta:
        db_table = 'tasks_taskdependency'
        constraints = [
            models.UniqueConstraint(
                fields=['predecessor', 'successor'],
                name='uk_dependency',
            ),
        ]
        indexes = [
            models.Index(fields=['predecessor'], name='idx_dep_predecessor'),
            models.Index(fields=['successor'], name='idx_dep_successor'),
        ]

    def __str__(self):
        return f'{self.predecessor_id} -> {self.successor_id}'


class Comment(TimestampedModel):
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )

    class Meta:
        db_table = 'tasks_comment'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task'], name='idx_comment_task'),
            models.Index(fields=['project'], name='idx_comment_project'),
            models.Index(fields=['author'], name='idx_comment_author'),
        ]

    def __str__(self):
        return f'{self.author_id}: {self.content[:50]}'


class Mention(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='mentions',
    )
    mentioned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentions_received',
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tasks_mention'
        constraints = [
            models.UniqueConstraint(
                fields=['comment', 'mentioned_user'],
                name='uk_mention',
            ),
        ]

    def __str__(self):
        return f'@{self.mentioned_user_id} in {self.comment_id}'
