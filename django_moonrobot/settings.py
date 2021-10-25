"""
Django settings for django_moonrobot project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from distutils.util import strtobool
from pathlib import Path

MRB_TELEGRAM_TOKEN = os.environ['MRB_TELEGRAM_TOKEN']
MRB_WEBHOOK_HOST = os.environ['MRB_WEBHOOK_HOST']
MRB_TELEGRAM_WEBHOOK = f"https://{MRB_WEBHOOK_HOST}/{MRB_TELEGRAM_TOKEN}"

MRB_NOTION_TOKEN = os.environ['MRB_NOTION_TOKEN']
MRB_NOTION_ENTRYPOINTS_DB_ID = os.environ['MRB_NOTION_ENTRYPOINTS_DB_ID']
MRB_NOTION_MESSAGES_DB_ID = os.environ['MRB_NOTION_MESSAGES_DB_ID']

MRB_WORKERS = int(os.getenv('MRB_WORKERS') or 4)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-rbjeml#e1e8ujpy8i2%*-mprrqb1q29=3rpt3t1&d)yxd&5-va'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(strtobool(os.environ.get('DEBUG') or 'no'))
MRB_USE_SQLITE = bool(strtobool(os.environ.get('MRB_USE_SQLITE') or 'no'))

ALLOWED_HOSTS = [MRB_WEBHOOK_HOST]
if DEBUG:
    ALLOWED_HOSTS.append('localhost')

# Application definition

INSTALLED_APPS = [
    'moonrobot',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_moonrobot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_moonrobot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if MRB_USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'moonrobot'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ['POSTGRES_PASSWORD'],
            'HOST': os.environ['POSTGRES_HOST'],
            'PORT': int(os.getenv('POSTGRES_PORT', 5432)),
        },
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/' if DEBUG else os.environ['MRB_STATIC_URL']
STATIC_ROOT = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('MRB_LOG_LEVEL') or 'WARNING',
    },
}
