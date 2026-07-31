from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminOrSelf, is_admin
from .serializers import (
    AdminUserSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    SelfUserSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    """Публичная регистрация нового пользователя по номеру телефона."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT-логин по телефону (phone + password)."""

    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD пользователей.

    Администратор видит и редактирует всех; обычный пользователь — только себя.
    """

    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return User.objects.all().order_by('id')
        return User.objects.filter(pk=user.pk)

    def get_serializer_class(self):
        if is_admin(self.request.user):
            return AdminUserSerializer
        return SelfUserSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Профиль текущего пользователя: GET — просмотр, PATCH — обновление."""
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
