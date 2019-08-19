import os
from .base_settings import * # noqa
from .base_settings import base_dir

SECRET_KEY = 'changeme'

DEBUG = True

_hostname = os.environ.get('HOSTNAME')
if _hostname:
    ALLOWED_HOSTS = [_hostname]

VMCK_API_URL = os.environ.get('VMCK_API_URL', 'http://localhost:8000')

MINIO_ADDRESS = os.environ.get('MINIO_ADDRESS', 'localhost:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', "changeme")
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', "changemetoo")
