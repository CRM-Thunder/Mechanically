from rest_framework.permissions import BasePermission
from rest_framework.exceptions import MethodNotAllowed
from MechanicallyApp.models import UserLocationAssignment


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return False

class IsAdminOrSuperuserAndTargetUserHasLowerRole(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return False
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            valid_roles=('standard','mechanic','manager','admin')
        else:
            valid_roles=('standard','mechanic','manager')
        if obj.role in valid_roles:
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

class IsStandardAssignedToBranch(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'standard' and UserLocationAssignment.objects.filter(user=request.user,location__location_type='B').exists():
            return True
        return False

class IsMechanic(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'mechanic':
            return True
        return False

class IsMechanicAssignedToWorkshop(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'mechanic' and UserLocationAssignment.objects.filter(user=request.user,location__location_type='W').exists():
            return True
        return False

class DisableUnwantedHTTPMethods(BasePermission):
    def has_permission(self, request, view):
        if request.method.lower() in ('options','trace','connect'):
            raise MethodNotAllowed(method=request.method.upper())
        return True

class IsAccountOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return obj == request.user