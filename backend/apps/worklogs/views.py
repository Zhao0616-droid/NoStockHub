from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import WorkLog, HourlyRate
from .serializers import WorkLogSerializer, HourlyRateSerializer
from core.permissions import IsProjectMember

class WorkLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        user = self.request.user
        queryset = WorkLog.objects.filter(task__project__members__user=user)

        project_id = self.request.query_params.get('project_id')
        task_id = self.request.query_params.get('task_id')
        user_id = self.request.query_params.get('user_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if project_id:
            queryset = queryset.filter(task__project_id=project_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset.select_related('task', 'user')

    def perform_create(self, serializer):
        # 确保用户只能为自己记录工时，或者项目经理为任何人记录
        # 这里简化处理，默认记录人为当前用户，除非是经理且指定了其他人
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({"error": "project_id required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 汇总统计
        total_hours = WorkLog.objects.filter(task__project_id=project_id).aggregate(total=Sum('hours'))['total'] or 0
        
        by_user = WorkLog.objects.filter(task__project_id=project_id).values('user__username').annotate(hours=Sum('hours'))
        
        return Response({
            "total_hours": total_hours,
            "by_user": list(by_user)
        })


class HourlyRateViewSet(viewsets.ModelViewSet):
    serializer_class = HourlyRateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = HourlyRate.objects.select_related('user', 'project')
        project_id = self.request.query_params.get('project_id')
        user_id = self.request.query_params.get('user_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def perform_create(self, serializer):
        if not serializer.validated_data.get('user'):
            serializer.save(user=self.request.user)
        else:
            serializer.save()