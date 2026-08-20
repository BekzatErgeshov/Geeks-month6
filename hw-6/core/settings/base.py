import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from core.settings.jazzmin import JAZZMIN_SETTINGS
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

IS_PRODUCTION = os.getenv("PRODUCTION", "False").lower() == "true"

if IS_PRODUCTION:
    from core.settings.production import *
else:
    from core.settings.development import *

THEME_APPS = [
    'jazzmin',
]

MY_APPS = [
    'apps.testapp',
    'apps.lessons',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LIBRARY_APPS = [
    'rest_framework',
    'drf_yasg',
    'django_ckeditor_5',
    'modeltranslation',
    "corsheaders",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

INSTALLED_APPS = [
    *THEME_APPS,
    *DJANGO_APPS,
    *LIBRARY_APPS,
    *MY_APPS,
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LANGUAGES = [
    ('ru', _('Russian')),
    ('ky', _('Kyrgyz')),
    ('en', _('English')),
]


MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_CUSTOM_FIELDS = ('CKEditor5Field',)


MEDIA_URL = '/back_media/'
MEDIA_ROOT = BASE_DIR / 'back_media/'


STATIC_URL = '/back_static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'back_static')


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


CKEDITOR_5_CONFIGS = {
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3', 
            '|', 'bulletedList', 'numberedList', 'alignment'
        ],
        'toolbar': [
            'heading', '|', 
            'bold', 'italic', 'underline', 'strikethrough', 'code', '|',
            'fontSize', 'fontColor', 'fontBackgroundColor', '|',
            'link', 'imageUpload', 'mediaEmbed', 'insertTable', 'blockQuote', '|',
            'alignment', 'outdent', 'indent', '|',
            'sourceEditing', 'removeFormat'
        ],
        'upload_url': '/ckeditor5/image_upload/',
        'heading': {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells', 
                'tableProperties', 'tableCellProperties'
            ]
        },
        'image': {
            'toolbar': [
                'imageTextAlternative', '|', 
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight', '|',
                'imageStyle:full', 'imageStyle:side'
            ]
        }
    },
    'minimal': {
        'toolbar': ['bold', 'italic', 'link'],
    },
}

AUTH_USER_MODEL = 'testapp.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Access-С‚РѕРєРµРЅ Р¶РёРІС‘С‚ 15 РјРёРЅСѓС‚
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Refresh-С‚РѕРєРµРЅ Р¶РёРІС‘С‚ 7 РґРЅРµР№

    'ROTATE_REFRESH_TOKENS': True,          # РџСЂРё РѕР±РЅРѕРІР»РµРЅРёРё access РІС‹РґР°РµС‚СЃСЏ РЅРѕРІС‹Р№ refresh
    'BLACKLIST_AFTER_ROTATION': True,       # РЎС‚Р°СЂС‹Р№ refresh СЃСЂР°Р·Сѓ СѓС…РѕРґРёС‚ РІ Р±Р»СЌРєР»РёСЃС‚
}

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


# ===== Redis Cache =====
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# ===== Email Configuration =====
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===== Celery Configuration =====
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE