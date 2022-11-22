from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Полный доступ только для администратора или суперпользователя
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdminOrPost(permissions.BasePermission):
    """
    Полный доступ только для администратора,
    POST запросы для всех пользователей
    """
    def has_permission(self, request, view):
        return request.method == 'POST' or request.user.is_superuser
