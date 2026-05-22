from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, UserProfileView,
    ChangePasswordView, EnableTwoFactorView, DisableTwoFactorView,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('enable-two-factor/', EnableTwoFactorView.as_view(), name='enable_two_factor'),
    path('disable-two-factor/', DisableTwoFactorView.as_view(), name='disable_two_factor'),
]
