from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Полный доступ только для администратора или суперпользователя
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()