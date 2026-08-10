from rest_framework import serializers
from apps.testapp.models import CustomUser, Post
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'phone', 'role', 'avatar')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'phone', 'role', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return CustomUser.objects.create_user(**validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = CustomTokenObtainPairSerializer.get_token(instance)
        data['tokens'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['role'] = user.role
        token['phone'] = user.phone
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserProfileSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            token = RefreshToken(attrs['refresh'])
        except TokenError as exc:
            raise serializers.ValidationError({'refresh': 'Недействительный refresh-токен.'}) from exc

        if str(token.get('user_id')) != str(self.context['request'].user.id):
            raise serializers.ValidationError({'refresh': 'Токен принадлежит другому пользователю.'})

        attrs['token'] = token
        return attrs

    def save(self, **kwargs):
        self.validated_data['token'].blacklist()
