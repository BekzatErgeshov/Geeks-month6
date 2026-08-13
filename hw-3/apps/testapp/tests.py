from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.testapp.models import CustomUser


class AuthenticationAPITests(APITestCase):
    credentials = {
        'email': 'student@example.com', 'username': 'student',
        'phone': '+996700000000', 'role': CustomUser.Role.USER,
        'password': 'secure-password-123', 'password2': 'secure-password-123',
    }

    def test_authentication_flow(self):
        register = self.client.post('/api/v1/users/register/', self.credentials, format='json')
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.get(email=self.credentials['email']).check_password(self.credentials['password']))
        registered_access = AccessToken(register.data['tokens']['access'])
        self.assertEqual(registered_access['email'], self.credentials['email'])

        login = self.client.post('/api/v1/users/login/', {'email': self.credentials['email'], 'password': self.credentials['password']}, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        access, refresh = login.data['access'], login.data['refresh']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        self.assertEqual(self.client.get('/api/v1/users/profile/').status_code, status.HTTP_200_OK)
        refreshed = self.client.post('/api/v1/users/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        self.assertNotEqual(refreshed.data['refresh'], refresh)

        logout = self.client.post('/api/v1/users/logout/', {'refresh': refreshed.data['refresh']}, format='json')
        self.assertEqual(logout.status_code, status.HTTP_205_RESET_CONTENT)


class GoogleOAuthAPITests(APITestCase):
    @patch('apps.testapp.views.get_google_user_info')
    @patch('apps.testapp.views.get_google_access_token')
    def test_google_authorization_creates_then_reuses_user(self, get_access_token, get_user_info):
        get_access_token.return_value = 'google-access-token'
        get_user_info.return_value = {
            'email': 'google.user@example.com', 'given_name': 'Google',
            'family_name': 'User', 'name': 'Google User',
        }

        first = self.client.post('/api/v1/auth/google/', {'code': 'fresh-code'}, format='json')
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertTrue(first.data['is_new_user'])
        self.assertIn('access', first.data)
        self.assertIn('refresh', first.data)
        self.assertEqual(first.data['user']['first_name'], 'Google')
        self.assertEqual(first.data['user']['last_name'], 'User')
        self.assertFalse(CustomUser.objects.get(email='google.user@example.com').has_usable_password())

        second = self.client.post('/api/v1/auth/google/', {'code': 'another-code'}, format='json')
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertFalse(second.data['is_new_user'])
        self.assertEqual(CustomUser.objects.filter(email='google.user@example.com').count(), 1)

    def test_google_authorization_requires_code(self):
        response = self.client.post('/api/v1/auth/google/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
