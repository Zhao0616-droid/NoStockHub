"""业务代码下发通知时请使用此处封装，便于统一字段与后续扩展。"""
from __future__ import annotations

from uuid import UUID

from django.contrib.auth import get_user_model

from .models import Notification


def create_notification(
    *,
    recipient,
    notification_type: str,
    title: str,
    content: str = '',
    related_type: str = '',
    related_id: UUID | str | None = None,
    is_read: bool = False,
) -> Notification:
    """
    创建一条站内通知。

    :param recipient: 接收人，``User`` 实例或其主键（UUID/str）。
    :param notification_type: ``Notification.Type`` 的值，例如 ``task_assigned``。
    """
    User = get_user_model()
    user = recipient if isinstance(recipient, User) else User.objects.get(pk=recipient)

    oid: UUID | None
    if related_id is None or related_id == '':
        oid = None
    elif isinstance(related_id, UUID):
        oid = related_id
    else:
        oid = UUID(str(related_id))

    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        content=content or '',
        related_type=related_type or '',
        related_id=oid,
        is_read=is_read,
    )
