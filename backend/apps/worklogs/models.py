import uuid
from django.db import models
from django.conf import settings
from core.models import TimestampedModel

class WorkLog(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='worklogs', verbose_name='关联任务')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worklogs', verbose_name='记录人')
    hours = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='工时(小时)')
    date = models.DateField(verbose_name='工作日期')
    description = models.TextField(blank=True, null=True, verbose_name='工作内容说明')

    class Meta:
        db_table = 'worklogs_worklog'
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['user']),
            models.Index(fields=['date']),
        ]
        verbose_name = '工时记录'
        verbose_name_plural = '工时记录'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 更新任务的实际工时
        total = self.task.worklogs.aggregate(total=models.Sum('hours'))['total'] or 0
        self.task.actual_hours = total
        self.task.save(update_fields=['actual_hours'])

class HourlyRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hourly_rates', verbose_name='用户')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='hourly_rates', verbose_name='项目')
    rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='每小时费率')
    effective_from = models.DateField(verbose_name='生效日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'worklogs_hourlyrate'
        unique_together = ('user', 'project', 'effective_from')
        verbose_name = '工时费率'
        verbose_name_plural = '工时费率'