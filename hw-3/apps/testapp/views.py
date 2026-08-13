from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.testapp.models import CustomUser
from apps.testapp.serializers import CustomTokenObtainPairSerializer, GoogleAuthSerializer, LogoutSerializer, RegisterSerializer, UserProfileSerializer
from apps.testapp.services import get_google_access_token, get_google_user_info


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class GoogleAuthView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        google_token = get_google_access_token(serializer.validated_data['code'])
        user_info = get_google_user_info(google_token)
        email = user_info.get('email')
        if not email:
            return Response({'detail': 'Google не предоставил email пользователя.'}, status=status.HTTP_400_BAD_REQUEST)

        first_name = user_info.get('given_name', user_info.get('first_name', ''))
        last_name = user_info.get('family_name', user_info.get('last_name', ''))
        user, is_new_user = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': user_info.get('name', email.split('@')[0]),
                'first_name': first_name, 'last_name': last_name,
                'role': CustomUser.Role.USER,
            },
        )
        if is_new_user:
            user.set_unusable_password()
            user.save(update_fields=['password'])

        refresh = RefreshToken.for_user(user)
        refresh['email'], refresh['role'], refresh['phone'] = user.email, user.role, user.phone or ''
        return Response({
            'access': str(refresh.access_token), 'refresh': str(refresh), 'is_new_user': is_new_user,
            'user': {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name},
        })
