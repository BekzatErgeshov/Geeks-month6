from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.testapp.models import CustomUser


class AuthenticationAPITests(APITestCase):
    credentials = {
        'email': 'student@example.com',
        'username': 'student',
        'phone': '+996700000000',
        'role': CustomUser.Role.USER,
        'password': 'secure-password-123',
        'password2': 'secure-password-123',
    }

    def test_authentication_flow(self):
        register = self.client.post('/api/v1/users/register/', self.credentials, format='json')
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', register.data)
        self.assertTrue(CustomUser.objects.get(email=self.credentials['email']).check_password(self.credentials['password']))

        registered_access = AccessToken(register.data['tokens']['access'])
        self.assertEqual(registered_access['email'], self.credentials['email'])
        self.assertEqual(registered_access['role'], self.credentials['role'])
        self.assertEqual(registered_access['phone'], self.credentials['phone'])

        login = self.client.post(
            '/api/v1/users/login/',
            {'email': self.credentials['email'], 'password': self.credentials['password']},
            format='json',
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn('user', login.data)

        access = login.data['access']
        refresh = login.data['refresh']
        access_token = AccessToken(access)
        self.assertEqual(access_token['email'], self.credentials['email'])
        self.assertEqual(access_token['role'], self.credentials['role'])
        self.assertEqual(access_token['phone'], self.credentials['phone'])

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        profile = self.client.get('/api/v1/users/profile/')
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data['email'], self.credentials['email'])

        refreshed = self.client.post('/api/v1/users/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(refreshed.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', refreshed.data)
        self.assertNotEqual(refreshed.data['refresh'], refresh)

        old_refresh = self.client.post('/api/v1/users/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(old_refresh.status_code, status.HTTP_401_UNAUTHORIZED)

        logout = self.client.post('/api/v1/users/logout/', {'refresh': refreshed.data['refresh']}, format='json')
        self.assertEqual(logout.status_code, status.HTTP_205_RESET_CONTENT, logout.data)

        blacklisted_refresh = self.client.post(
            '/api/v1/users/token/refresh/', {'refresh': refreshed.data['refresh']}, format='json'
        )
        self.assertEqual(blacklisted_refresh.status_code, status.HTTP_401_UNAUTHORIZED)
