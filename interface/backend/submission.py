from tempfile import TemporaryDirectory
from zipfile import ZipFile
from pathlib import Path
from django.conf import settings

import interface.backend.minio_api as storage
import requests
import logging
import configparser

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def get_config(config_file):
    config = configparser.ConfigParser()
    config.read(settings.CONFIG_DIR / config_file)

    return config['VMCK']


def isNumber(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def build_vagrantfile(config):
    confing_str = 'vmck.vmck_url = ENV["VMCK_URL"]\n'

    with open(settings.VAGRANTFILE) as vagrantfile:
        for key, value in config.items():
            if not isNumber(value):
                value = f'"{value}"'
            confing_str = confing_str + f'vmck.{key} = {value}\n'

        new_vagrantfile = vagrantfile.read()
        new_vagrantfile = new_vagrantfile.replace('!CONFIGUARATION!',
                                                  confing_str)

        return new_vagrantfile


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')

    with TemporaryDirectory() as _tmp:
        tmp = Path(str(_tmp))

        config = get_config('pc.ini')
        vagrantfile = build_vagrantfile(config)

        submission_arch = ZipFile(tmp / file.name, mode='x')
        submission_arch.writestr('submission.zip', data=file.read())
        submission_arch.writestr('Vagrantfile', data=vagrantfile)
        submission_arch.close()

        with open(tmp / file.name, 'rb') as data:
            storage.upload(file.name, data.read())

    options = {'vm': dict(config), 'manager': {}}
    options['manager']['archive'] = storage.get_link(file.name)
    options['manager']['memory'] = 50
    options['manager']['cpu_mhz'] = 30

    requests.post(settings.VMCK_API_URL + 'submission', json=options)
