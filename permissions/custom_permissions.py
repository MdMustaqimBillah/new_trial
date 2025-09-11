# myapp/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, or OPTIONS requests (read-only access) for any authenticated user.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
        

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff