from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Предоставление доступа для модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsNotModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Модераторы").exists()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
