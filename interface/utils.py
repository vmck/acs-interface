from django.conf import settings

import string
import secrets

vocabulary_64 = string.ascii_letters + string.digits + '.+'


def get_table_next_prev(submissions, base_url, page):
    next_url = ''
    prev_url = ''

    if submissions:
        first_id = submissions[0].id

        if first_id > settings.SUBMISSIONS_PER_PAGE:
            next_url = base_url + f'?page={page + 1}'
        else:
            next_url = base_url + f'?page={page}'

        if page == 1:
            prev_url = base_url + f'?page={page}'
        else:
            prev_url = base_url + f'?page={page - 1}'

    return (next_url, prev_url)


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
