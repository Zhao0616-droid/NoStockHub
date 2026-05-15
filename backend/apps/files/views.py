import mimetypes
import os
import uuid

from django.conf import settings
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Attachment
from .serializers import AttachmentSerializer

ALLOWED_EXTENSIONS = {
    # 图片
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp',
    # 文档
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.md', '.json', '.xml', '.yaml', '.yml',
    # 压缩包
    '.zip', '.rar', '.7z', '.tar', '.gz',
    # 代码
    '.py', '.js', '.ts', '.vue', '.html', '.css', '.java', '.go',
}

ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml',
    'image/webp', 'image/bmp',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain', 'text/csv', 'text/markdown',
    'application/json', 'application/xml', 'text/xml',
    'application/zip', 'application/x-rar-compressed',
    'application/x-7z-compressed', 'application/x-tar', 'application/gzip',
    'text/x-python', 'application/javascript', 'text/javascript',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class AttachmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return Attachment.objects.select_related('uploader').all()

    def get_serializer_class(self):
        return AttachmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        project_id = request.query_params.get('project_id')
        task_id = request.query_params.get('task_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        queryset = queryset.filter(uploader=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'detail': 'No file provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size > MAX_FILE_SIZE:
            return Response(
                {'detail': 'File size exceeds 50MB limit.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {'detail': f'File extension "{ext}" is not allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = uploaded_file.content_type
        if content_type not in ALLOWED_MIME_TYPES:
            return Response(
                {'detail': f'File type "{content_type}" is not allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        stored_name = f'{uuid.uuid4().hex}{ext}'
        file_path = os.path.join(upload_dir, stored_name)

        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        task_id = request.data.get('task_id')
        project_id = request.data.get('project_id')

        attachment = Attachment.objects.create(
            filename=uploaded_file.name,
            file_path=file_path,
            file_size=uploaded_file.size,
            mime_type=content_type,
            task_id=task_id or None,
            project_id=project_id or None,
            uploader=request.user,
        )

        return Response(
            AttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        attachment = self.get_object()
        if not os.path.exists(attachment.file_path):
            return Response(
                {'detail': 'File not found on disk.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        content_type, _ = mimetypes.guess_type(attachment.filename)
        response = FileResponse(
            open(attachment.file_path, 'rb'),
            content_type=content_type or attachment.mime_type,
            as_attachment=True,
            filename=attachment.filename,
        )
        return response

    def destroy(self, request, *args, **kwargs):
        attachment = self.get_object()
        if attachment.uploader_id != request.user.id:
            return Response(
                {'detail': 'Only the uploader can delete this file.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
