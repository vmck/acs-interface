import os
from pathlib import Path

import ldap
from django_auth_ldap.config import LDAPSearch

from interface.utils import is_true


BASE_DIR = Path(__file__).parent.parent

BLOCK_SIZE = 32*1024

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simple_history',
    'interface',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'interface.urls'
LOGIN_URL = '/'

AUTH_LDAP_SERVER_URI = os.getenv('LDAP_SERVER_URI')
AUTH_LDAP_BIND_DN = os.getenv('LDAP_BIND_DN')
AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD')
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.getenv('LDAP_USER_TREE'),
    ldap.SCOPE_SUBTREE,
    os.getenv('LDAP_USER_FILTER'),
)

AUTH_LDAP_FIND_GROUP_PERMS = False

AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_CACHE_TIMEOUT = 3600

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

if os.environ.get('LDAP_SERVER_URI'):
    AUTHENTICATION_BACKENDS.insert(0, 'django_auth_ldap.backend.LDAPBackend')

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

WSGI_APPLICATION = 'interface.wsgi.application'

_postgres_db = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('POSTGRES_DB'),
    'USER': os.getenv('POSTGRES_USER'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'HOST': os.getenv('POSTGRES_ADDRESS'),
    'PORT': os.getenv('POSTGRES_PORT'),
}

_sqlite_db = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': str(BASE_DIR / 'data' / 'db.sqlite3'),
    'OPTIONS': {
        'timeout': 20,  # in seconds
    }
}

default_db = _postgres_db if os.getenv('POSTGRES_DB') else _sqlite_db

DATABASES = {
    'default': default_db
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Bucharest'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'interface/static')

SECRET_KEY = 'changeme'

DEBUG = is_true(os.environ.get('DEBUG'))

_hostname = os.environ.get('HOSTNAME')
if _hostname:
    ALLOWED_HOSTS = [_hostname]

VMCK_API_URL = os.environ.get('VMCK_API_URL', 'http://localhost:8000/v0/')

MINIO_ADDRESS = os.environ.get('MINIO_ADDRESS', 'localhost:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', '1234')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', '123456789')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'test')

ACS_INTERFACE_ADDRESS = os.environ.get(
    'ACS_INTERFACE_ADDRESS',
    'localhost:8100',
)

MANAGER_MEMORY = int(os.environ.get('MANAGER_MEMORY', 50))
MANAGER_MHZ = int(os.environ.get('MANAGER_MHZ', 30))
MANAGER_TAG = os.environ.get('MANAGER_TAG', 'master')

SUBMISSIONS_PER_PAGE = 20

FILE_UPLOAD_MAX_MEMORY_SIZE = int(
    os.environ.get('FILE_UPLOAD_MAX_MEMORY_SIZE', 2621440),  # 2.5 MB
)

FILE_UPLOAD_HANDLERS = ['interface.uploadhandler.RestrictedFileUploadHandler']

MOSS_USER_ID = int(os.environ.get('MOSS_USER_ID', 9999999))

APP_THREAD_COUNT = int(os.environ.get('APP_THREAD_COUNT', 20))

# Used for updating the status of homeworks
CHECK_INTERVAL_SUBS = 2  # in seconds

TOTAL_MACHINES = int(os.environ.get("TOTAL_MACHINES", 4))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'interface': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}
