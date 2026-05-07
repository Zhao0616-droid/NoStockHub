from rest_framework import permissions


def get_project_from_object(obj):
    if hasattr(obj, 'members'):
        return obj
    return getattr(obj, 'project', None)


class IsProjectMember(permissions.BasePermission):
    """Allow access to project members or project owners."""

    def has_object_permission(self, request, view, obj):
        project = get_project_from_object(obj)
        if project is None or not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS and getattr(project, 'visibility', None) == 'public':
            return True
        return project.owner_id == request.user.id or project.members.filter(user=request.user).exists()


class IsProjectManager(permissions.BasePermission):
    """Allow access to project owners or project managers."""

    def has_object_permission(self, request, view, obj):
        project = get_project_from_object(obj)
        if project is None or not request.user or not request.user.is_authenticated:
            return False
        return (
            project.owner_id == request.user.id
            or project.members.filter(user=request.user, role='manager').exists()
        )
