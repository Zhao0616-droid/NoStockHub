from django.conf import settings
from django.db import models

from core.models import TimestampedModel, BaseModel


class WorkLog(TimestampedModel):
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='worklogs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='worklogs',
    )
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'worklogs_worklog'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['task'], name='idx_worklog_task'),
            models.Index(fields=['user'], name='idx_worklog_user'),
            models.Index(fields=['date'], name='idx_worklog_date'),
        ]

    def __str__(self):
        return f'{self.user_id}: {self.hours}h on {self.date}'


class HourlyRate(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hourly_rates',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='hourly_rates',
    )
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'worklogs_hourlyrate'
        ordering = ['-effective_from']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project', 'effective_from'],
                name='uk_user_project_rate',
            ),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_rate_user'),
            models.Index(fields=['project'], name='idx_rate_project'),
        ]

    def __str__(self):
        return f'{self.user_id}: {self.rate}/h from {self.effective_from}'
