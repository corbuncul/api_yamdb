from rest_framework import permissions


class IsAdminOrStaff(permissions.BasePermission):
    """Разрешение для администраторов и модераторов."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Разрешение на полный доступ для администраторов
    или только чтение для всех остальных.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение на полный доступ администраторам, модераторам и авторам.
    Для всех остальных доступ на чтение.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
