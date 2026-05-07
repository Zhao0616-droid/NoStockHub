from rest_framework import permissions


class IsProjectMember(permissions.BasePermission):
    """检查用户是否为项目成员"""
    def has_object_permission(self, request, view, obj):
        return obj.project.members.filter(user=request.user).exists()


class IsProjectManager(permissions.BasePermission):
    """检查用户是否为项目管理者"""
    def has_object_permission(self, request, view, obj):
        return obj.project.members.filter(
            user=request.user, role='manager'
        ).exists()
