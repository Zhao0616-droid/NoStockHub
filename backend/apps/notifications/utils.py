"""兼容 ``tasks`` 等模块使用的 ``create_notification(user=..., type=...)`` 签名。"""
from __future__ import annotations

from .services import create_notification as _svc_create


def create_notification(user, type, title, content='', related_type='', related_id=''):
    return _svc_create(
        recipient=user,
        notification_type=type,
        title=title,
        content=content or '',
        related_type=related_type or '',
        related_id=related_id or None,
    )
