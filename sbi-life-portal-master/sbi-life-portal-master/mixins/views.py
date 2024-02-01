from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import BasePermission


# Create your views here.
class GroupRequiredMixin(AccessMixin):
    """Verify that the current user has all specified permissions."""
    group_required = []

    def get_permission_required(self):
        """
        Override this method to override the permission_required attribute.
        Must return an iterable.
        """
        if self.group_required is None:
            return
        if isinstance(self.group_required, str):
            groups = tuple(self.group_required.split(','))
            perms = groups
        else:
            perms = self.group_required
        return perms

    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        if self.request.user.is_active and self.request.user.is_superuser:
            return True
        perms = self.get_permission_required()
        permission = []
        for group in perms:
            permission.append(
                self.request.user.groups.filter(name=group).exists())
        if any(permission):
            return True
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class IsSuperuserGroup(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser and request.user.is_active:
            return True
        return False


class IsAdminGroup(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_active and request.user.is_superuser:
            return True
        if request.user.groups.filter(name='admin').exists():
            return True
        else:
            return False


class IsReviewerGroup(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_active and request.user.is_superuser:
            return True
        if request.user.groups.filter(name='reviewer').exists():
            return True
        else:
            return False


class IsMemberGroup(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_active and request.user.is_superuser:
            return True
        if request.user.groups.filter(name='member').exists():
            return True
        else:
            return False


class IsUploaderGroup(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_active and request.user.is_superuser:
            return True
        if request.user.groups.filter(name='uploader').exists():
            return True
        else:
            return False
