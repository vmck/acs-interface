from interface.utils import is_true
from pathlib import Path

import os

BASE_DIR = Path(__file__).parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
]

ROOT_URLCONF = 'interface.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'data' / 'db.sqlite3'),
    }
}


AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
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
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'changeme')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'changemetoo')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'test')

BASE_ASSIGNMENT_URL = os.environ.get('BASE_ASSIGNMENT_URL', 'https://raw.githubusercontent.com/vmck/assignment/')  # noqa: E501
SETUP_ASSIGNMENT_URL = os.environ.get('SETUP_ASSIGNMENT_URL', 'https://raw.githubusercontent.com/vmck/assignment/master/setup.ini')  # noqa: E501

ACS_INTERFACE_ADDRESS = os.environ.get('ACS_INTERFACE_ADDRESS', 'localhost:8100')  # noqa: E501

MANAGER_MEMORY = 50
MANAGER_MHZ = 30

SUBMISSIONS_PER_PAGE = 20
