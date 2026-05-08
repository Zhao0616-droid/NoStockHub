from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, UserProfileView

app_name = 'accounts'

urlpatterns = [
    # 用户注册
    path('register/', RegisterView.as_view(), name='register'),
    # 用户登录
    path('login/', LoginView.as_view(), name='login'),
    # 刷新 Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 用户信息
    path('profile/', UserProfileView.as_view(), name='profile'),
]
