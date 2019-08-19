import os
from .base_settings import * # noqa

SECRET_KEY = 'changeme'

DEBUG = True

_hostname = os.environ.get('HOSTNAME')
if _hostname:
    ALLOWED_HOSTS = [_hostname]
