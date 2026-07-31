from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер для модели CustomUser с входом по номеру телефона."""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Номер телефона обязателен для создания пользователя')

        extra_fields.setdefault('is_active', True)

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # role задаётся принудительно — для неё проверки нет.
        extra_fields['role'] = CustomUser.Role.ADMIN

        # Проверяем, что флаги действительно True (осмысленно только при setdefault).
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя LMS с входом по номеру телефона и ролями."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Студент'
        TEACHER = 'teacher', 'Преподаватель'
        ADMIN = 'admin', 'Администратор'

    phone = models.CharField('Номер телефона', max_length=20, unique=True)
    email = models.EmailField('Электронная почта', blank=True, null=True)
    username = models.CharField('Имя пользователя', max_length=150, blank=True, null=True)
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.phone} ({self.get_role_display()})'
