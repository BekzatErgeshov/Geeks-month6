from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTeacherOrReadOnly(BasePermission):
    """
    Разрешает запись (POST/PUT/PATCH/DELETE) только пользователям с ролью 'teacher'.
    Остальным — только чтение (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'teacher'
        )
