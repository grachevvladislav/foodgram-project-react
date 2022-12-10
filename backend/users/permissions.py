from rest_framework import permissions


class IsSafeOrPost(permissions.BasePermission):
    """
    Безопасные методы и регистрация
    """
    def has_permission(self, request, view):
        return request.method == 'POST' or (request.method in
                                            permissions.SAFE_METHODS)
