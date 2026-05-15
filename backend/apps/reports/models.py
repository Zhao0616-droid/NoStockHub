from django.conf import settings
from django.db import models

from core.models import BaseModel


class Report(BaseModel):
    class ReportType(models.TextChoices):
        TASK_LIST = 'task_list', 'Task List'
        WORKLOG_SUMMARY = 'worklog_summary', 'Worklog Summary'
        GANTT = 'gantt', 'Gantt'
        PROGRESS = 'progress', 'Progress'
        BURNDOWN = 'burndown', 'Burndown'

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ReportType.choices)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='reports',
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports',
    )
    parameters = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports_report'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project'], name='idx_report_project'),
        ]

    def __str__(self):
        return self.name
