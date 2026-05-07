from django.conf import settings
from django.db import models

from core.models import BaseModel, TimestampedModel


class ProjectTemplate(TimestampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_templates',
    )

    class Meta:
        db_table = 'projects_projecttemplate'
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(TimestampedModel):
    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'

    class Status(models.TextChoices):
        PLANNING = 'planning', 'Planning'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    template = models.ForeignKey(
        ProjectTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
    )

    class Meta:
        db_table = 'projects_project'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_project_status'),
            models.Index(fields=['owner'], name='idx_project_owner'),
        ]

    def __str__(self):
        return self.name


class ProjectMember(BaseModel):
    class Role(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        MEMBER = 'member', 'Member'
        VIEWER = 'viewer', 'Viewer'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_members',
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects_projectmember'
        ordering = ['joined_at']
        constraints = [
            models.UniqueConstraint(fields=['project', 'user'], name='uk_project_user'),
        ]

    def __str__(self):
        return f'{self.project_id}:{self.user_id}:{self.role}'


class Milestone(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')

    class Meta:
        db_table = 'projects_milestone'
        ordering = ['due_date', 'created_at']
        indexes = [
            models.Index(fields=['project', 'status'], name='idx_milestone_project_status'),
        ]

    def __str__(self):
        return self.name
