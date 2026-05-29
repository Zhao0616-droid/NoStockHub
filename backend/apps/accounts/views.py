from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ChangePasswordSerializer


class RegisterView(generics.CreateAPIView):
    """用户注册接口"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """用户登录接口"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户信息接口"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码修改成功'})


class EnableTwoFactorView(APIView):
    """启用双因素认证"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.two_factor_enabled = True
        request.user.save(update_fields=['two_factor_enabled'])
        return Response({'detail': '双因素认证已启用', 'two_factor_enabled': True})


class UserSearchView(APIView):
    """用户搜索（按用户名/邮箱）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q or len(q) < 1:
            return Response([])
        User = get_user_model()
        users = User.objects.filter(
            username__icontains=q
        ) | User.objects.filter(email__icontains=q)
        users = users[:20]
        return Response([
            {'id': str(u.id), 'username': u.username, 'email': u.email}
            for u in users
        ])


class DisableTwoFactorView(APIView):
    """禁用双因素认证"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.two_factor_enabled = False
        request.user.save(update_fields=['two_factor_enabled'])
        return Response({'detail': '双因素认证已禁用', 'two_factor_enabled': False})