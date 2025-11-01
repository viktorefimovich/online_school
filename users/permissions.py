from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """
    Разрешает доступ только пользователям, которые авторизованы и входят в группу "Moderators".
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Moderators").exists()
