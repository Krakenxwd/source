"""
Django settings for sbilife project.

Generated by 'django-admin startproject' using Django 4.1.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

import environ


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

if env.str('ALLOWED_HOSTS', None):
    ALLOWED_HOSTS = [i[1:] for i in env.list('ALLOWED_HOSTS', None)] if env.list('ALLOWED_HOSTS', None) else ['*']
else:
    ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Project apps
    'registration',
    'claim_application',
    'master',
    'mixins',
    'audittrail',
    'glib_sftp',

    # Third parties
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'debug_toolbar',
    'django_tables2',
    'django_filters',
    'rest_framework',
    'widget_tweaks',
    'django_celery_results',
    'auditlog',
]

SITE_ID = env.int('SITE_ID', default=1)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'audittrail.middleware.UserRequestAuditTrailMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'registration.custom_auth.CustomAuthentication',
    ],
}


ROOT_URLCONF = 'sbilife.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'master.custom_context_processor.show_setting_fields',
            ],
        },
    },
]

WSGI_APPLICATION = 'sbilife.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# Database
DB_NAME = env.str('DB_NAME')
DB_USER = env.str('DB_USER')
DB_PASSWORD = env.str('DB_PASSWORD')
DB_HOST = env.str('DB_HOST')
DB_PORT = env.str('DB_PORT')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_TZ = True

# File storage

DEFAULT_FILE_STORAGE = env.str(
    'DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
# print("DEFAULT_FILE_STORAGE", DEFAULT_FILE_STORAGE)
MEDIA_ROOT = env.str('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
if DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
    MEDIA_URL = '/media/'
    MEDIA_STORAGE = 'LOCAL'
elif DEFAULT_FILE_STORAGE == 'sbilife.storage_backends.MediaStorage':
    AWS_S3_BUCKET_NAME = env.str('S3_MEDIA_BUCKET', default='')
    # print("AWS_S3_BUCKET_NAME", AWS_S3_BUCKET_NAME)
    AWS_DEFAULT_REGION = env.str(
        'AWS_DEFAULT_REGION', default='ap-south-1')
    # print("AWS_S3_REGION_NAME", AWS_S3_REGION_NAME)
    AWS_S3_FILE_OVERWRITE = env.bool('AWS_S3_FILE_OVERWRITE', default=False)
    # print("AWS_S3_FILE_OVERWRITE", AWS_S3_FILE_OVERWRITE)
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = "path"
    MEDIA_STORAGE = 'REMOTE'


# Static files (CSS, JavaScript, Images)

DEFAULT_STATICFILES_STORAGE = env.str(
    'DEFAULT_STATICFILES_STORAGE', 'django.core.files.storage.FileSystemStorage')
# print("DEFAULT_STATICFILES_STORAGE", DEFAULT_STATICFILES_STORAGE)
if DEFAULT_STATICFILES_STORAGE == 'invogo.storage_backends.StaticStorage':
    STATICFILES_STORAGE = DEFAULT_STATICFILES_STORAGE
    STATIC_URL = f"https://{env.str('S3_STATIC_BUCKET')}.s3.amazonaws.com/static/"
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Settings

MAIL_DEBUG = env.bool('MAIL_DEBUG', True)
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', 'notifications@glib.ai')

EMAIL_BACKEND_SERVICE = env.str(
    'EMAIL_BACKEND_SERVICE', 'django.core.mail.backends.console.EmailBackend')

if MAIL_DEBUG or EMAIL_BACKEND_SERVICE == 'django.core.mail.backends.console.EmailBackend':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
elif EMAIL_BACKEND_SERVICE == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env.str('EMAIL_HOST')
    EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

if EMAIL_BACKEND_SERVICE == 'django_ses.SESBackend':
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_REGION_NAME = os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")
    AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"

AWS_SES_ACCESS_KEY_ID = env.str('AWS_SES_ACCESS_KEY_ID', default='')
AWS_SES_SECRET_ACCESS_KEY = env.str('AWS_SES_SECRET_ACCESS_KEY', default='')

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000000000

# Add security

if not DEBUG:
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 15552000
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7 * 2  # 2 weeks
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login'
ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_ADAPTER = 'registration.adapter.CustomLoginAdapter'

INTERNAL_IPS = [
    "127.0.0.1",
]

# Celery Configuration

CACHE_HOST = env.str("CACHE_HOST", default="localhost")
CACHE_PORT = env.str("CACHE_PORT", default="6379")
CACHE_CELERY_DB_NAME = env.str("CACHE_CELERY_DB_NAME", default="0")
CACHE_DB_NAME = env.str("CACHE_DB_NAME", default="1")

# Celery Broker Using Redis
CELERY_BROKER_URL = "redis://{}:{}/{}".format(
    CACHE_HOST, CACHE_PORT, CACHE_CELERY_DB_NAME)

CELERY_RESULT_BACKEND = 'django-db'

CACHE_URL = "redis://{}:{}/{}".format(CACHE_HOST, CACHE_PORT, CACHE_DB_NAME)

NEED_CACHE = env.bool("NEED_CACHE", default=False)

if NEED_CACHE:
    # Cache
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

CELERY_PREFETCH_MULTIPLIER = 1  # how many task will fetch from the broker
CELERY_ACKS_LATE = True  # when the worker acknowledge the task.

ADMIN_USER = env.str('ADMIN_USER', 'admin@glib.ai')
ADMIN_PASSWORD = env.str('ADMIN_PASSWORD', 'StairwayToParadise')


# Audit Log Configuration
AUDITLOG_INCLUDE_ALL_MODELS = True

# SFTP Email
SFTP_BOT_EMAIL = env.str('SFTP_BOT_EMAIL', 'sftp-bot@glib.ai')