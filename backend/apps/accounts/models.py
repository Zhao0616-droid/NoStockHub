import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimestampedModel


class Role(TimestampedModel):
    """角色模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    description = models.CharField(max_length=200, blank=True, verbose_name='角色描述')
    permissions = models.JSONField(verbose_name='权限列表')

    class Meta:
        db_table = 'accounts_role'
        verbose_name = '角色'
        verbose_name_plural = '角色管理'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """用户模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.URLField(blank=True, verbose_name='头像URL')
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='角色'
    )
    role_type = models.CharField(
        max_length=20,
        choices=[('admin', '管理员'), ('manager', '项目经理'), ('member', '成员')],
        default='member',
        verbose_name='角色类型'
    )
    two_factor_enabled = models.BooleanField(default=False, verbose_name='双因素认证')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'accounts_user'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        return self.username