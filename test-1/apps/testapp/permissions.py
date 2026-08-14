from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsTeacherOrReadOnly(BasePermission):
    """Allow authenticated users to read; only teachers may change lessons."""

    message = "Only teachers may modify lessons."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or request.user.role == "teacher"
