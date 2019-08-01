#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Django settings for koku project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os

import sys
import logging

from boto3.session import Session
from corsheaders.defaults import default_headers

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
from . import database

from .env import ENVIRONMENT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# The SECRET_KEY is provided via an environment variable in OpenShift
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    # safe value used for development when DJANGO_SECRET_KEY might not be set
    'asvuhxowz)zjbo4%7pc$ek1nbfh_-#%$bq_x8tkh=#e24825=5'
)

# SECURITY WARNING: don't run with debug turned on in production!
# Default value: False
DEBUG = False if os.getenv('DJANGO_DEBUG', 'False') == 'False' else True  # pylint: disable=R1719

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'tenant_schemas',
    # django
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third-party
    'rest_framework',
    'django_filters',
    'corsheaders',
    'querystring_parser',
    'django_prometheus',

    # local apps
    'api',
    'masu',
    'reporting',
    'reporting_common',
    'cost_models',
]

SHARED_APPS = (
    'tenant_schemas',
    'api',
    'masu',
    'reporting_common',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
)

TENANT_APPS = (
    'reporting',
    'cost_models',
)

DEFAULT_FILE_STORAGE = 'tenant_schemas.storage.TenantFileSystemStorage'

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'koku.middleware.DisableCSRF',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'koku.middleware.IdentityHeaderMiddleware',
    'koku.middleware.KokuTenantMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

DEVELOPMENT = ENVIRONMENT.bool('DEVELOPMENT', default=False)
if DEVELOPMENT:
    MIDDLEWARE.insert(5, 'koku.dev_middleware.DevelopmentIdentityHeaderMiddleware')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

MASU = ENVIRONMENT.bool('MASU', default=False)
ROOT_URLCONF = 'koku.urls'
if MASU:
    ROOT_URLCONF = 'masu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'koku.wsgi.application'

REDIS_HOST = ENVIRONMENT.get_value('REDIS_HOST', default='redis')
REDIS_PORT = ENVIRONMENT.get_value('REDIS_PORT', default='6379')
if 'test' in sys.argv:
    CACHES = {
        "default": {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
        "rbac": {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}/1".format(REDIS_HOST, REDIS_PORT),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True
            },
        },
        "rbac": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:{}/1".format(REDIS_HOST, REDIS_PORT),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True
            },
        }
    }

DATABASES = {
    'default': database.config()
}

DATABASE_ROUTERS = (
    'tenant_schemas.routers.TenantSyncRouter',
)

#
TENANT_MODEL = 'api.Tenant'

PROMETHEUS_EXPORT_MIGRATIONS = False

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

API_PATH_PREFIX = os.getenv('API_PATH_PREFIX',
                            ENVIRONMENT.get_value('API_PATH_PREFIX', default='/api'))
STATIC_API_PATH_PREFIX = API_PATH_PREFIX
if STATIC_API_PATH_PREFIX != '' and (not STATIC_API_PATH_PREFIX.endswith('/')):
    STATIC_API_PATH_PREFIX = STATIC_API_PATH_PREFIX + '/'

STATIC_URL = '{}apidoc/'.format(STATIC_API_PATH_PREFIX)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'apidoc'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

INTERNAL_IPS = ['127.0.0.1']

DEFAULT_PAGINATION_CLASS = 'api.common.pagination.StandardResultsSetPagination'
DEFAULT_EXCEPTION_HANDLER = 'api.common.exception_handler.custom_exception_handler'

# django rest_framework settings
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': DEFAULT_PAGINATION_CLASS,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'api.common.csv.PaginatedCSVRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': DEFAULT_EXCEPTION_HANDLER
}

CW_AWS_ACCESS_KEY_ID = ENVIRONMENT.get_value('CW_AWS_ACCESS_KEY_ID', default=None)
CW_AWS_SECRET_ACCESS_KEY = ENVIRONMENT.get_value('CW_AWS_SECRET_ACCESS_KEY', default=None)
CW_AWS_REGION = ENVIRONMENT.get_value('CW_AWS_REGION', default='us-east-1')
CW_LOG_GROUP = ENVIRONMENT.get_value('CW_LOG_GROUP', default='platform-dev')

LOGGING_FORMATTER = os.getenv('DJANGO_LOG_FORMATTER', 'simple')
DJANGO_LOGGING_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
KOKU_LOGGING_LEVEL = os.getenv('KOKU_LOG_LEVEL', 'INFO')
LOGGING_HANDLERS = os.getenv('DJANGO_LOG_HANDLERS', 'console').split(',')
VERBOSE_FORMATTING = '%(levelname)s %(asctime)s %(module)s ' \
    '%(process)d %(thread)d %(message)s'

LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', BASE_DIR)
DEFAULT_LOG_FILE = os.path.join(LOG_DIRECTORY, 'app.log')
LOGGING_FILE = os.getenv('DJANGO_LOG_FILE', DEFAULT_LOG_FILE)

if CW_AWS_ACCESS_KEY_ID:
    LOGGING_HANDLERS += ['watchtower']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': VERBOSE_FORMATTING
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': LOGGING_FORMATTER
        },
        'file': {
            'level': KOKU_LOGGING_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOGGING_FILE,
            'formatter': LOGGING_FORMATTER
        },
    },
    'loggers': {
        'django': {
            'handlers': LOGGING_HANDLERS,
            'level': DJANGO_LOGGING_LEVEL,
        },
        'api': {
            'handlers': LOGGING_HANDLERS,
            'level': KOKU_LOGGING_LEVEL,
        },
        'koku': {
            'handlers': LOGGING_HANDLERS,
            'level': KOKU_LOGGING_LEVEL,
        },
        'providers': {
            'handlers': LOGGING_HANDLERS,
            'level': KOKU_LOGGING_LEVEL,
        },
        'reporting': {
            'handlers': LOGGING_HANDLERS,
            'level': KOKU_LOGGING_LEVEL,
        },
        'reporting_common': {
            'handlers': LOGGING_HANDLERS,
            'level': KOKU_LOGGING_LEVEL,
        },
        'masu': {
            'handlers': LOGGING_HANDLERS,
            'level': KOKU_LOGGING_LEVEL,
        },

    },
}

if CW_AWS_ACCESS_KEY_ID:
    NAMESPACE = 'unknown'
    BOTO3_SESSION = Session(aws_access_key_id=CW_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=CW_AWS_SECRET_ACCESS_KEY,
                            region_name=CW_AWS_REGION)
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            NAMESPACE = f.read()
    except Exception:  # pylint: disable=W0703
        pass
    WATCHTOWER_HANDLER = {
        'level': KOKU_LOGGING_LEVEL,
        'class': 'watchtower.CloudWatchLogHandler',
        'boto3_session': BOTO3_SESSION,
        'log_group': CW_LOG_GROUP,
        'stream_name': NAMESPACE,
        'formatter': LOGGING_FORMATTER,
    }
    LOGGING['handlers']['watchtower'] = WATCHTOWER_HANDLER

KOKU_DEFAULT_CURRENCY = ENVIRONMENT.get_value('KOKU_DEFAULT_CURRENCY', default='USD')
KOKU_DEFAULT_TIMEZONE = ENVIRONMENT.get_value('KOKU_DEFAULT_TIMEZONE', default='UTC')
KOKU_DEFAULT_LOCALE = ENVIRONMENT.get_value('KOKU_DEFAULT_LOCALE', default='en_US.UTF-8')


# Cors Setup
# See https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    'x-rh-identity',
    'HTTP_X_RH_IDENTITY',
)

APPEND_SLASH = False

# disable log messages less than CRITICAL when running unit tests.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

# Masu API Endpoints
MASU_SERVICE_HOST = ENVIRONMENT.get_value('MASU_SERVICE_HOST',
                                          default='localhost')
MASU_SERVICE_PORT = ENVIRONMENT.get_value('MASU_SERVICE_PORT',
                                          default='5000')
MASU_BASE_URL = 'http://{}:{}/'.format(MASU_SERVICE_HOST, MASU_SERVICE_PORT)

MASU_API_REPORT_DATA = 'api/v1/report_data/'

# AMQP Message Broker
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', '5672')

CELERY_BROKER_URL = f'amqp://{RABBITMQ_HOST}:{RABBITMQ_PORT}'
CELERY_IMPORTS = ('masu.processor.tasks', 'masu.celery.tasks',)
