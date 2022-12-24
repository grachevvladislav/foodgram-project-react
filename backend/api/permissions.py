from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """
    GET - для всех
    POST - для авторизованных пользователей
    PATCH, DEL - для автора
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated or (
            request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or (
            request.method in permissions.SAFE_METHODS
        )


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
