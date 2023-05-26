"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta

from rest_framework.settings import api_settings

from pyowm import OWM
import geonamescache


from .tools.etc import (DJANGO_CONFIG,
                        DATABASE_CONFIG,
                        GOOGLE_AUTH_CONFIG,
                        GITHUB_AUTH_CONFIG)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = DJANGO_CONFIG["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if DJANGO_CONFIG["DEBUG"] == "True" else False

ALLOWED_HOSTS = tuple(DJANGO_CONFIG["ALLOWED_HOSTS"]) if DEBUG is False else ('*', )

# HTTPS
# CSRF_COOKIE_SECURE = False if DEBUG else True
# SECURE_SSL_REDIRECT = False if DEBUG else True
# SESSION_COOKIE_SECURE = False if DEBUG else True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'WeatherReminder.apps.WeatherReminderConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'crispy_forms',
    'crispy_bootstrap5',
    'social_django',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'main.urls'

AUTHENTICATION_BACKENDS = (
    'main.tools.OAuth2.AppleIdAuth',
    'main.tools.OAuth2.GithubOAuth2',
    'main.tools.OAuth2.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend'
)


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

# URL NAMESPACE
SOCIAL_AUTH_URL_NAMESPACE = 'social'


# Allow to create user by social django
AUTH_USER_MODEL = 'WeatherReminder.User'
AUTH_PROFILE_MODULE = 'WeatherReminder.User'
SOCIAL_AUTH_USER_MODEL = 'WeatherReminder.User'
SOCIAL_AUTH_USER_FIELDS = ['first_name', 'last_name', 'email', 'is_active']
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_EMAIL_AS_USERNAME = True

# AppleID
# TODO: To Configuru in future
SOCIAL_AUTH_APPLE_ID_CLIENT = ''
SOCIAL_AUTH_APPLE_ID_TEAM = ''
SOCIAL_AUTH_APPLE_ID_KEY = ''
SOCIAL_AUTH_APPLE_ID_SECRET = ''
SOCIAL_AUTH_APPLE_ID_SCOPE = ['email', 'name']

# GitHub
GITHUB_AUTH_CONFIG = GITHUB_AUTH_CONFIG['DEV'] if DEBUG else GITHUB_AUTH_CONFIG['PROD']
SOCIAL_AUTH_GITHUB_KEY = GITHUB_AUTH_CONFIG['client_id']
SOCIAL_AUTH_GITHUB_SECRET = GITHUB_AUTH_CONFIG['client_secret']
SOCIAL_AUTH_GITHUB_SCOPE = ['email', 'name', 'is_active']

# Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_AUTH_CONFIG['web']['client_id']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = GOOGLE_AUTH_CONFIG['web']['client_secret']


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
)


TEMPLATES = (
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'base_template'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
)

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = DATABASE_CONFIG
SOCIAL_AUTH_JSONFIELD_ENABLED = True if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql' else False


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = (
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
)


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATICFILES_DIRS = [BASE_DIR / 'base_template' / 'static']

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR.parent / 'uploads'

if (DEBUG is False) and (STATIC_ROOT.exists() is False):
    raise FileNotFoundError(f"{STATIC_ROOT} isn't exist. to resolve that, do collectstatic when DEBUG=TRUE")


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LENGTH_OF_CODE_CONFIRM = 2 if DEBUG else 6
ADMINS = DJANGO_CONFIG['ADMINS']


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = DJANGO_CONFIG['EMAIL']
DEFAULT_FROM_EMAIL = DJANGO_CONFIG['EMAIL']
EMAIL_HOST_PASSWORD = DJANGO_CONFIG['EMAIL_PASSWORD']


REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        api_settings.DEFAULT_AUTHENTICATION_CLASSES,
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        api_settings.DEFAULT_FILTER_BACKENDS,
    ],
}

OWN = OWM(DJANGO_CONFIG["OWM_TOKEN_KEY"])
MGR = OWN.weather_manager()
FREQUENCY_UPDATE_DATA = timedelta(**DJANGO_CONFIG["FREQUENCY_UPDATE_DATA"])
GC = geonamescache.GeonamesCache()


# Crispy
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


