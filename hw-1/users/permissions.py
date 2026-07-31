from rest_framework import permissions

from .models import CustomUser


def is_admin(user):
    """Администратор: staff/superuser или пользователь с ролью admin."""
    return bool(
        user
        and user.is_authenticated
        and (user.is_staff or user.role == CustomUser.Role.ADMIN)
    )


class IsAdminOrSelf(permissions.BasePermission):
    """Админ управляет всеми; обычный пользователь — только своей записью.

    list / create / destroy доступны только администратору.
    retrieve / update / partial_update — администратору или самому пользователю.
    """

    admin_only_actions = ('list', 'create', 'destroy')

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if getattr(view, 'action', None) in self.admin_only_actions:
            return is_admin(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        return obj == request.user
