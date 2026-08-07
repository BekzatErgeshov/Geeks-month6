from rest_framework import permissions

from apps.testapp.models import CustomUser


class IsCommentAuthorOrModerator(permissions.BasePermission):
    """
    Доступ к комментариям:
      * работать с эндпоинтом могут только авторизованные пользователи;
      * читать (GET и другие безопасные методы) — любой авторизованный;
      * изменять / удалять (PUT, PATCH, DELETE) — только автор комментария
        либо пользователь с ролью ADMIN или MODERATOR.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Безопасные методы (GET, HEAD, OPTIONS) доступны всем авторизованным.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Автор комментария может его редактировать и удалять.
        if obj.author == request.user:
            return True

        # Администратор или модератор тоже могут редактировать и удалять.
        return request.user.role in (
            CustomUser.Role.ADMIN,
            CustomUser.Role.MODERATOR,
        )
