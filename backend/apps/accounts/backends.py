from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """支持用户名或邮箱登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            User().set_password(password)  # 防时序攻击
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
