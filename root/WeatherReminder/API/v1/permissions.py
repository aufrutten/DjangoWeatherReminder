from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow only admins to modify instances,
    but allow anyone to view them.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow only owners to modify their own instances,
    admins to modify any instances, and anyone to view them.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated and (
                request.user.is_staff or
                obj == request.user
            )
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only owners or admins to modify their own instances.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user and request.user.is_authenticated and (
                request.user.is_staff or
                obj == request.user
            )
        )


class IsOwnerOrAdminOrReadOnlyExceptDelete(BasePermission):
    """
    Custom permission to allow only owners or admins to modify their own instances,
    and anyone to view or delete them.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method == 'DELETE' or
            request.user and request.user.is_authenticated and (
                request.user.is_staff or
                obj == request.user
            )
        )


class IsAnonymousOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_anonymous
