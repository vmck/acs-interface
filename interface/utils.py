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
