from rest_framework.permissions import BasePermission


class IsOwnerOrModerator(BasePermission):
    """
    Разрешает доступ владельцу объекта или модератору.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.groups.filter(name="Moderators").exists()