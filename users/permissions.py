from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """
    Разрешает доступ только пользователям, которые авторизованы и входят в группу "Moderators".
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Moderators").exists()


class IsOwner(BasePermission):
    """
    Позволяет владельцу объекта редактировать, просматривать и удалять только свои объекты.
    """

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner == request.user
