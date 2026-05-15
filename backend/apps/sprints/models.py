from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class Sprint(TimestampedModel):
    class Status(models.TextChoices):
        PLANNING = 'planning', 'Planning'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'

    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='sprints',
    )

    class Meta:
        db_table = 'sprints_sprint'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project'], name='idx_sprint_project'),
            models.Index(fields=['status'], name='idx_sprint_status'),
        ]

    def __str__(self):
        return self.name
