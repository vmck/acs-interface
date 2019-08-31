from tempfile import TemporaryDirectory
from zipfile import ZipFile
from pathlib import Path
from django.conf import settings
from interface.utils import random_code, is_number
from interface.models import Submission
from urllib.parse import urljoin

import interface.backend.minio_api as storage
import requests
import logging
import configparser

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(settings.CONFIG_DIR / config_file)

    return config['VMCK']


def build_vagrantfile(config):
    confing_str = ''

    with open(settings.VAGRANTFILE) as vagrantfile:
        for key, value in config.items():
            if not is_number(value):
                value = f'"{value}"'
            confing_str = confing_str + f'vmck.{key} = {value}\n'

        new_vagrantfile = vagrantfile.read()
        new_vagrantfile = new_vagrantfile.replace('!CONFIGUARATION!',
                                                  confing_str)

        return new_vagrantfile


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')
    # stub just for now, in the end we will get it from `request`
    assignment_id = 'pc'

    with TemporaryDirectory() as _tmp:
        tmp = Path(str(_tmp))

        config = read_config(f'{assignment_id}.ini')
        config['token'] = random_code(settings.TOKEN_SIZE)

        vagrantfile = build_vagrantfile(config)

        submission_arch = ZipFile(tmp / file.name, mode='x')
        submission_arch.writestr('submission.zip', data=file.read())
        submission_arch.writestr('Vagrantfile', data=vagrantfile)
        submission_arch.write(settings.CONFIG_DIR / f'{assignment_id}.sh',
                              'checker.sh')
        submission_arch.close()

        with open(tmp / file.name, 'rb') as data:
            storage.upload(file.name, data.read())

    options = {'vm': dict(config), 'manager': {}}
    options['manager']['archive'] = storage.get_link(file.name)
    options['manager']['memory'] = settings.MANAGER_MEMORY
    options['manager']['cpu_mhz'] = settings.MANAGER_MHZ
    options['manager']['vmck_api'] = settings.VMCK_API_URL

    submission = Submission.objects.create()
    submission.token = config['token']
    submission.username = request.user.username if request.user.id is None else 'anonymous'  # noqa: E501
    submission.url = options['manager']['archive']
    submission.assignment_id = assignment_id
    submission.max_score = 100

    options['manager']['id'] = submission.id

    requests.post(urljoin(settings.VMCK_API_URL, 'submission'), json=options)

    log.debug(f'Submission #{submission.id} sent to VMCK')
    submission.save()
