import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampedModel

class Task(TimestampedModel):
    TASK_TYPE_CHOICES = [
        ('task', 'Task'),
        ('milestone', 'Milestone'),
        ('bug', 'Bug'),
        ('epic', 'Epic'),
    ]
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='task', verbose_name='类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name='状态')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    due_date = models.DateField(null=True, blank=True, verbose_name='截止日期')
    
    order = models.IntegerField(default=0, verbose_name='排序')
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='预估工时')
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='实际工时')
    progress = models.IntegerField(default=0, verbose_name='进度(%)')

    # Foreign Keys
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='tasks', verbose_name='所属项目')
    sprint = models.ForeignKey('sprints.Sprint', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='所属冲刺')
    parent_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subtasks', verbose_name='父任务')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name='负责人')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_tasks', verbose_name='创建人')

    class Meta:
        db_table = 'tasks_task'
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['assignee']),
            models.Index(fields=['status']),
        ]
        verbose_name = '任务'
        verbose_name_plural = '任务'

    def __str__(self):
        return self.title

class TaskDependency(TimestampedModel):
    RELATION_CHOICES = [
        ('blocks', 'Blocks'),
        ('precedes', 'Precedes'),
        ('relates_to', 'Relates To'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    predecessor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='successor_dependencies', verbose_name='前驱任务')
    successor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='predecessor_dependencies', verbose_name='后继任务')
    relation_type = models.CharField(max_length=20, choices=RELATION_CHOICES, default='precedes', verbose_name='关系类型')

    class Meta:
        db_table = 'tasks_taskdependency'
        unique_together = ('predecessor', 'successor')
        verbose_name = '任务依赖'
        verbose_name_plural = '任务依赖'

class Comment(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='评论人')
    
    # Generic relation logic: either task or project must be present
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='comments', verbose_name='关联任务')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='comments', verbose_name='关联项目')
    
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies', verbose_name='父评论')

    class Meta:
        db_table = 'tasks_comment'
        verbose_name = '评论'
        verbose_name_plural = '评论'

    def save(self, *args, **kwargs):
        if not self.task and not self.project:
            raise ValueError("Comment must be associated with either a Task or a Project.")
        super().save(*args, **kwargs)

class Mention(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='mentions', verbose_name='所属评论')
    mentioned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentions', verbose_name='被提及用户')
    is_read = models.BooleanField(default=False, verbose_name='已读状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tasks_mention'
        verbose_name = '@提及'
        verbose_name_plural = '@提及'