from django.conf import settings
from django.db import models

from core.models import BaseModel


class Notification(BaseModel):
    class Type(models.TextChoices):
        TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
        STATUS_CHANGE = 'status_change', 'Status Change'
        COMMENT = 'comment', 'Comment'
        DEADLINE = 'deadline', 'Deadline'
        MENTION = 'mention', 'Mention'
        PROJECT_INVITE = 'project_invite', 'Project Invite'
        SPRINT_START = 'sprint_start', 'Sprint Start'
        SPRINT_END = 'sprint_end', 'Sprint End'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    related_type = models.CharField(max_length=50, blank=True)
    related_id = models.CharField(max_length=36, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read'], name='idx_notif_user'),
            models.Index(fields=['created_at'], name='idx_notif_created'),
        ]

    def __str__(self):
        return f'{self.type}: {self.title}'
