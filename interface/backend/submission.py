from django.conf import settings
from interface.models import Submission
from urllib.parse import urljoin

import interface.backend.minio_api as storage
import requests
import logging
import configparser

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def get_config(branch):
    branch_url = urljoin(settings.BASE_ASSIGNMENT_URL, branch+'/')
    config_data = requests.get(urljoin(branch_url, 'config.ini'))

    config = configparser.ConfigParser()
    config.read_string(config_data.text)

    return config['VMCK']


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')

    submission = Submission.objects.create()

    storage.upload(f'{submission.id}.zip', file.read())

    submission.username = request.user.username
    submission.assignment_id = request.POST['assignment_id']
    submission.max_score = 100

    branch_url = urljoin(settings.BASE_ASSIGNMENT_URL,
                         submission.assignment_id+'/')
    config_url = urljoin(branch_url, 'checker.sh')

    options = {'vm': dict(get_config(submission.assignment_id)),
               'manager': {}}
    options['manager']['archive'] = submission.url
    options['manager']['script'] = config_url
    options['manager']['memory'] = settings.MANAGER_MEMORY
    options['manager']['cpu_mhz'] = settings.MANAGER_MHZ
    options['manager']['vmck_api'] = settings.VMCK_API_URL
    options['manager']['id'] = submission.id

    requests.post(urljoin(settings.VMCK_API_URL, 'submission'), json=options)

    log.debug(f'Submission #{submission.id} sent to VMCK')
    submission.save()
