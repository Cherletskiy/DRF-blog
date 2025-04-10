from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение для владельца комментария или админа"""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff