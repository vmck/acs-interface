import string
import secrets
import base64
import configparser

import requests
from cachetools import cached, TTLCache

vocabulary_64 = string.ascii_letters + string.digits + '.+'


def vmck_config(submission):
    config_data = get_config_ini(submission)

    config = configparser.ConfigParser()
    config.read_string(config_data.text)

    config_dict = dict(config['VMCK'])

    for key, value in config_dict.items():
        if is_number(value):
            config_dict[key] = int(value)

    return config_dict


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


def get_script_url(link):
    return link.assignment.url_for('checker.sh')


def get_artifact_url(link):
    return link.assignment.url_for('artifact.zip')


# cache for 10 seconds
@cached(cache=TTLCache(maxsize=10, ttl=10))
def cached_get_file(url):
    return requests.get(url)


def get_config_ini(link):
    url = link.assignment.url_for('config.ini')
    return cached_get_file(url)


def get_penalty_info(link):
    config_data = get_config_ini(link)

    config = configparser.ConfigParser()
    config.read_string(config_data.text)

    penalty_info = dict(config['PENALTY'])

    penalty = [int(x) for x in penalty_info['penaltyweights'].split(',')]
    holiday_s = [x for x in penalty_info.get('holidaystart', '').split(',')]
    holiday_f = [x for x in penalty_info.get('holidayfinish', '').split(',')]

    return (penalty, holiday_s, holiday_f)


def get_last_submissions_of_every_user(assignment):
    submission_set = assignment.submission_set.order_by('timestamp')

    submissions = {}

    # we only want the last submission of every user
    for submission in submission_set:
        submissions[submission.user.username] = submission

    return submissions.values()
