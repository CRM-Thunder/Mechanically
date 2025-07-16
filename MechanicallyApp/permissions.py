from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return False

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'admin' and request.user.is_superuser:
            return True
        return False

class IsManager(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'manager':
            return True
        return False

class IsStandard(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'standard':
            return True
        return False

class IsMechanic(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'mechanic':
            return True
        return False

class DisableOPTIONSMethod(BasePermission):
    message="Method \"OPTIONS\" not allowed"
    def has_permission(self, request, view):
        if request.method=='OPTIONS':
            return False
        return True