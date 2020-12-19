import string
import secrets
import base64
from typing import List

import requests
from requests import Response
from cachetools import cached, TTLCache

# from interface.models import Assignment, Submission


vocabulary_64 = string.ascii_letters + string.digits + ".+"


def encode(message: str) -> str:
    encoded_message = base64.encodebytes(bytes(message, encoding="latin-1"))

    return str(encoded_message, encoding="latin-1")


def decode(message: str) -> str:
    decoded_message = base64.decodebytes(bytes(message, encoding="latin-1"))

    return str(decoded_message, encoding="latin-1")


def random_code(length: str, vocabulary=vocabulary_64) -> str:
    return "".join(secrets.choice(vocabulary) for _ in range(length))


def is_true(value: str) -> bool:
    text = (value or "").lower().strip()
    return text in ["1", "yes", "true", "on", "enabled"]


# cache for 10 seconds
@cached(cache=TTLCache(maxsize=10, ttl=10))
def cached_get_file(url: str) -> Response:
    return requests.get(url)


def get_last_submissions_of_every_user(
    assignment,
) -> List[any]:
    submission_set = assignment.submission_set.order_by("timestamp")

    submissions = {}

    # we only want the last submission of every user
    for submission in submission_set:
        submissions[submission.user.username] = submission

    return submissions.values()
