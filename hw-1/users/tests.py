from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CustomUserManagerTests(APITestCase):
    """Тесты менеджера CustomUserManager."""

    def test_create_user_defaults(self):
        user = User.objects.create_user(phone='+996700000001', password='StrongPass123')
        self.assertEqual(user.phone, '+996700000001')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('StrongPass123'))

    def test_create_user_requires_phone(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(phone='', password='x')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(phone='+996700000000', password='AdminPass123')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, User.Role.ADMIN)

    def test_create_superuser_rejects_false_flags(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                phone='+996700000002', password='x', is_staff=False
            )


class AuthAPITests(APITestCase):
    """Регистрация и JWT-логин по номеру телефона."""

    def test_register(self):
        resp = self.client.post(reverse('register'), {
            'phone': '+996700000010', 'password': 'StrongPass123',
            'password2': 'StrongPass123', 'role': 'student',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(phone='+996700000010').exists())

    def test_register_password_mismatch(self):
        resp = self.client.post(reverse('register'), {
            'phone': '+996700000011', 'password': 'StrongPass123',
            'password2': 'Other12345',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_as_admin_blocked(self):
        resp = self.client.post(reverse('register'), {
            'phone': '+996700000012', 'password': 'StrongPass123',
            'password2': 'StrongPass123', 'role': 'admin',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_tokens(self):
        User.objects.create_user(phone='+996700000013', password='StrongPass123')
        resp = self.client.post(reverse('token_obtain_pair'), {
            'phone': '+996700000013', 'password': 'StrongPass123',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['role'], 'student')


class UserViewSetPermissionTests(APITestCase):
    """Права доступа в CRUD пользователей."""

    def setUp(self):
        self.student = User.objects.create_user(
            phone='+996700000020', password='StrongPass123',
            first_name='Ivan', role='student',
        )
        self.other = User.objects.create_user(
            phone='+996700000021', password='StrongPass123', role='teacher',
        )
        self.admin = User.objects.create_superuser(
            phone='+996700000000', password='AdminPass123',
        )

    def auth(self, user, password):
        resp = self.client.post(reverse('token_obtain_pair'), {
            'phone': user.phone, 'password': password,
        }, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_anonymous_denied(self):
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_list_all(self):
        self.auth(self.student, 'StrongPass123')
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_me(self):
        self.auth(self.student, 'StrongPass123')
        resp = self.client.get('/api/users/me/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['phone'], self.student.phone)

    def test_student_cannot_escalate_via_me(self):
        self.auth(self.student, 'StrongPass123')
        resp = self.client.patch('/api/users/me/', {
            'is_staff': True, 'role': 'admin', 'first_name': 'Ivan2',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_staff)          # флаг проигнорирован
        self.assertEqual(self.student.role, 'student')   # роль неизменна
        self.assertEqual(self.student.first_name, 'Ivan2')

    def test_student_cannot_access_other(self):
        self.auth(self.student, 'StrongPass123')
        resp = self.client.get(f'/api/users/{self.other.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_full_crud(self):
        self.auth(self.admin, 'AdminPass123')
        # list
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)
        # create
        resp = self.client.post('/api/users/', {
            'phone': '+996700000030', 'password': 'TeacherPass123',
            'first_name': 'Anna', 'role': 'teacher',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_id = resp.data['id']
        # update role
        resp = self.client.patch(f'/api/users/{new_id}/', {'role': 'admin'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['role'], 'admin')
        # delete
        resp = self.client.delete(f'/api/users/{new_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=new_id).exists())
