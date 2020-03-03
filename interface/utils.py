import string
import secrets
import base64

import requests
from cachetools import cached, TTLCache

vocabulary_64 = string.ascii_letters + string.digits + '.+'


def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def decode(message):
    decoded_message = base64.decodestring(bytes(message,
                                                encoding='latin-1'))

    return str(decoded_message, encoding='latin-1')


def random_code(length, vocabulary=vocabulary_64):
    return ''.join(secrets.choice(vocabulary) for _ in range(length))


def is_true(value):
    text = (value or '').lower().strip()
    return text in ['1', 'yes', 'true', 'on', 'enabled']


# cache for 10 seconds
@cached(cache=TTLCache(maxsize=10, ttl=10))
def cached_get_file(url):
    return requests.get(url)


def get_last_submissions_of_every_user(assignment):
    submission_set = assignment.submission_set.order_by('timestamp')

    submissions = {}

    # we only want the last submission of every user
    for submission in submission_set:
        submissions[submission.user.username] = submission

    return submissions.values()
