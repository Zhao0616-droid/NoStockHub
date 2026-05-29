import logging
import mimetypes
import os

from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsProjectMember

from .models import Report
from .serializers import ReportGenerateSerializer, ReportSerializer
from .tasks import generate_report_task

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = Report.objects.select_related('generated_by', 'project').all()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ReportGenerateSerializer
        return ReportSerializer

    def get_permissions(self):
        if self.action in ('retrieve', 'download', 'list'):
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save(generated_by=request.user)
        try:
            generate_report_task(str(report.id))
        except Exception:
            logger.warning("Failed to generate report %s", report.id, exc_info=True)
            return Response(
                {'detail': '报表生成失败，请重试'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        report.refresh_from_db()
        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        report = self.get_object()
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        report = self.get_object()
        if not report.file_path:
            return Response(
                {'detail': 'Report is still being generated.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not os.path.exists(report.file_path):
            return Response(
                {'detail': 'Report file not found on disk.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        content_type, _ = mimetypes.guess_type(report.file_path)
        return FileResponse(
            open(report.file_path, 'rb'),
            content_type=content_type or 'text/csv',
            as_attachment=True,
            filename=os.path.basename(report.file_path),
        )
