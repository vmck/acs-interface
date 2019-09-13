from django.conf import settings

import string
import secrets

vocabulary_64 = string.ascii_letters + string.digits + '.+'


def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def random_code(length, vocabulary=vocabulary_64):
    return ''.join(secrets.choice(vocabulary) for _ in range(length))


def is_true(value):
    text = (value or '').lower().strip()
    return text in ['1', 'yes', 'true', 'on', 'enabled']
