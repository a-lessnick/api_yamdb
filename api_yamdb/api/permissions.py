"""Классы для описания прав доступа."""
from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Доступ только для админа."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Админ или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.is_admin
                or request.user.is_superuser))
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Доступ только для админа/модератора/автора"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
        )
