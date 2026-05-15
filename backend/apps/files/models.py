from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class Attachment(TimestampedModel):
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, default='application/octet-stream')
    task_id = models.UUIDField(null=True, blank=True)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attachments',
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'files_attachment'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['task_id'], name='idx_attach_task'),
            models.Index(fields=['project'], name='idx_attach_project'),
            models.Index(fields=['uploader'], name='idx_attach_uploader'),
        ]

    def __str__(self):
        return self.filename
