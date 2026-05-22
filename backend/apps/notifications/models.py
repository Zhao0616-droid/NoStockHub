from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class Notification(TimestampedModel):
    """站内通知，由业务侧写入；当前 API 提供列表与已读状态。"""

    class Type(models.TextChoices):
        TASK_ASSIGNED = 'task_assigned', '任务分配'
        STATUS_CHANGE = 'status_change', '状态变更'
        COMMENT = 'comment', '评论'
        DEADLINE = 'deadline', '截止提醒'
        MENTION = 'mention', '提及'
        PROJECT_INVITE = 'project_invite', '项目邀请'
        SPRINT_START = 'sprint_start', '冲刺开始'
        SPRINT_END = 'sprint_end', '冲刺结束'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收人',
    )
    notification_type = models.CharField(
        '类型',
        max_length=32,
        choices=Type.choices,
        db_column='type',
    )
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容', blank=True)
    is_read = models.BooleanField('已读', default=False)
    related_type = models.CharField(
        '关联实体类型',
        max_length=50,
        blank=True,
        help_text='如 Task / Project / Sprint',
    )
    related_id = models.UUIDField('关联实体 ID', null=True, blank=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read'], name='idx_notif_user_read'),
            models.Index(fields=['created_at'], name='idx_notif_created'),
        ]
        verbose_name = '通知'
        verbose_name_plural = '通知'

    def __str__(self):
        return f'{self.title} → {self.user_id}'
