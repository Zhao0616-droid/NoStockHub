from .models import Notification


def create_notification(user, type, title, content='', related_type='', related_id=''):
    return Notification.objects.create(
        user=user,
        type=type,
        title=title,
        content=content,
        related_type=related_type,
        related_id=related_id,
    )
