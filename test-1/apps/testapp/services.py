import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


def get_google_access_token(code: str) -> str:
    """Обменивает одноразовый authorization code на токен Google."""
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code, 'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI, 'grant_type': 'authorization_code',
            }, timeout=10,
        )
    except requests.RequestException as exc:
        raise AuthenticationFailed('Не удалось связаться с сервером Google.') from exc
    if not response.ok:
        raise AuthenticationFailed('Не удалось обменять code на токен Google.')
    access_token = response.json().get('access_token')
    if not access_token:
        raise AuthenticationFailed('Google не вернул access token.')
    return access_token


def get_google_user_info(access_token: str) -> dict:
    """Запрашивает данные профиля пользователя у Google UserInfo API."""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}, timeout=10,
        )
    except requests.RequestException as exc:
        raise AuthenticationFailed('Не удалось связаться с сервером Google.') from exc
    if not response.ok:
        raise AuthenticationFailed('Не удалось получить профиль пользователя из Google.')
    return response.json()
