import re
import string
import secrets
import base64
import configparser
from urllib.parse import urljoin

import requests

vocabulary_64 = string.ascii_letters + string.digits + '.+'


def vmck_config(submission):
    config_data = get_config_data(submission)

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


def get_url_base(link):
    m = re.match(r'https://github.com/(?P<org>[^/]+)/(?P<repo>[^/]+)/?$',
                 link.assignment.repo_url)
    url_base = ('https://raw.githubusercontent.com/'
                '{0}/{1}/'.format(*list(m.groups())))

    return url_base


def get_script_url(link):
    url_base = get_url_base(link)
    script_url = urljoin(url_base,
                         f'{link.assignment.repo_branch}/checker.sh')

    return script_url


def get_config_data(link):
    url_base = get_url_base(link)
    config_data = requests.get(
                    urljoin(
                        url_base,
                        f'{link.assignment.repo_branch}/config.ini',
                    )
                  )

    return config_data
