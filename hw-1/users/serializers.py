from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Публичная регистрация по номеру телефона."""

    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password], style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'password2',
                  'first_name', 'last_name', 'email', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Пароли не совпадают'})
        # Нельзя зарегистрироваться администратором через публичный эндпоинт.
        if attrs.get('role') == User.Role.ADMIN:
            raise serializers.ValidationError(
                {'role': 'Роль «admin» назначается только администратором'}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class AdminUserSerializer(serializers.ModelSerializer):
    """Полный CRUD для администратора (все поля, включая роль и флаги доступа)."""

    password = serializers.CharField(
        write_only=True, required=False, allow_blank=False,
        validators=[validate_password], style={'input_type': 'password'},
    )
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'first_name', 'last_name', 'email',
                  'role', 'role_display', 'is_active', 'is_staff', 'is_superuser',
                  'date_joined')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Пароль обязателен при создании'})
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class SelfUserSerializer(serializers.ModelSerializer):
    """Профиль текущего пользователя: роль и флаги доступа — только чтение."""

    password = serializers.CharField(
        write_only=True, required=False,
        validators=[validate_password], style={'input_type': 'password'},
    )
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'password', 'first_name', 'last_name', 'email',
                  'role', 'role_display', 'is_active', 'is_staff', 'date_joined')
        read_only_fields = ('id', 'role', 'is_active', 'is_staff', 'date_joined')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT-логин по телефону; в ответ и в токен добавляем роль и телефон."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['phone'] = user.phone
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['phone'] = self.user.phone
        return data
