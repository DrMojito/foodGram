from rest_framework import permissions
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        BasePermission)


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)


class AllowUnauthenticatedPost(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and not request.user.is_authenticated:
            return True
        return IsAuthenticatedOrReadOnly().has_permission(request, view)