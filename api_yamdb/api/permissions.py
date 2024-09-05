"""Классы для описания прав доступа."""
from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Только для администраторов."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Методы записи только для администраторов, суперюзера и
    зарегистрированных пользователей.
    Для остальных - только безопасные методы.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.is_admin
                or request.user.is_superuser))
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """
    Методы записи только для администраторов, модераторов и
    авторов.
    Для остальных - только безопасные методы.
    """

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
