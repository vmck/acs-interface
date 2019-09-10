from django.conf import settings
from urllib.parse import urljoin
from interface.models import Submission
from interface.utils import is_number

import interface.backend.minio_api as storage
import configparser
import requests
import logging

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def get_config(branch):
    config_data = requests.get(urljoin(settings.BASE_ASSIGNMENT_URL,
                                       f'{branch}/config.ini'))

    config = configparser.ConfigParser()
    config.read_string(config_data.text)

    config_dict = dict(config['VMCK'])

    for key, value in config_dict.items():
        if is_number(value):
            config_dict[key] = int(value)

    return config_dict


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')

    submission = Submission.objects.create()

    storage.upload(f'{submission.id}.zip', file.read())

    submission.archive_size = file.size >> 10
    submission.username = request.user.username
    submission.assignment_id = request.POST['assignment_id']
    submission.max_score = 100

    config_url = urljoin(settings.BASE_ASSIGNMENT_URL,
                         f'{submission.assignment_id}/checker.sh')

    options = get_config(submission.assignment_id)
    options['name'] = f'{submission.assignment_id} submission #{submission.id}'
    options['env'] = {}
    options['env']['archive'] = submission.url
    options['env']['script'] = config_url
    options['env']['memory'] = settings.MANAGER_MEMORY
    options['env']['cpu_mhz'] = settings.MANAGER_MHZ
    options['env']['vmck_api'] = settings.VMCK_API_URL
    options['env']['interface_address'] = settings.ACS_INTERFACE_ADDRESS
    options['env']['id'] = submission.id

    response = requests.post(urljoin(settings.VMCK_API_URL, 'jobs'),
                             json=options)

    submission.vmck_id = response.json()['id']

    log.debug(f'Submission #{submission.id} sent to VMCK as #{submission.vmck_id}')  # noqa: E501
    submission.save()
