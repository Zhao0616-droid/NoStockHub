from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.pagination import StandardPagination

from .models import Notification
from .serializers import (
    NotificationPagedListSerializer,
    NotificationReadAllResponseSerializer,
    NotificationSerializer,
)


@extend_schema_view(
    retrieve=extend_schema(
        summary='通知详情',
        description='返回当前用户的一条通知；非本人或未找到时为 404。',
    ),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """列表含未读数；支持单条/全部标记已读。"""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    # 不显式绑定 pagination_class，避免 drf-spectacular 再包一层分页 schema
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        qs = Notification.objects.filter(user=self.request.user)
        raw = self.request.query_params.get('is_read')
        if raw is not None:
            key = raw.lower()
            if key == 'true':
                qs = qs.filter(is_read=True)
            elif key == 'false':
                qs = qs.filter(is_read=False)
        return qs

    @extend_schema(
        summary='通知列表',
        parameters=[
            OpenApiParameter(
                name='is_read',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                enum=[True, False],
                description='是否已读：`true` 仅已读，`false` 仅未读；不传则不限。',
                required=False,
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='页码，默认 1。',
                required=False,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='每页条数；默认 20，最大 100。',
                required=False,
            ),
        ],
        responses={200: NotificationPagedListSerializer},
    )
    def list(self, request, *args, **kwargs):
        base = Notification.objects.filter(user=request.user)
        unread_count = base.filter(is_read=False).count()
        queryset = self.filter_queryset(self.get_queryset())
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = paginator.get_paginated_response(serializer.data)
            response.data['unread_count'] = unread_count
            return response
        serializer = self.get_serializer(queryset, many=True)
        return Response({'unread_count': unread_count, 'results': serializer.data})

    @extend_schema(
        summary='标记单条已读',
        description='只能标记本人的通知。',
        request=None,
        responses={200: NotificationSerializer},
    )
    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read', 'updated_at'])
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @extend_schema(
        summary='全部标记已读',
        description='将当前用户的所有未读通知标为已读；返回受影响条数 `updated`。只能操作本人数据。',
        request=None,
        responses={200: NotificationReadAllResponseSerializer},
    )
    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'updated': count})
