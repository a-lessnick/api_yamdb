from rest_framework import permissions


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Проверка разрешений для админа, модератора и автора."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )


class IsAdmin(permissions.BasePermission):
    """Проверка разрешений для админа."""

    def has_permission(self, request, view):
        """Переопределение разрешения."""
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Проверка разрешений для админа или на чтение."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )
