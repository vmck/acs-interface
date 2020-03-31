import configparser
from urllib.parse import urljoin
import logging

from django.conf import settings
import requests

from .utils import is_number

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def vmck_config(submission):
    config_data = submission.get_config_ini()

    config = configparser.ConfigParser()
    config.read_string(config_data.text)

    config_dict = dict(config['VMCK'])

    for key, value in config_dict.items():
        if is_number(value):
            config_dict[key] = int(value)

    return config_dict


def evaluate(submission):
    callback = (f"submission/{submission.id}/done?"
                f"token={str(submission.generate_jwt(), encoding='latin1')}")

    options = vmck_config(submission)
    name = f'{submission.assignment.full_code} submission #{submission.id}'
    options['name'] = name
    options['restrict_network'] = True

    options['manager'] = {}
    options['manager']['vagrant_tag'] = settings.MANAGER_TAG
    options['manager']['memory_mb'] = settings.MANAGER_MEMORY
    options['manager']['cpu_mhz'] = settings.MANAGER_MHZ

    options['env'] = {}
    options['env']['archive_url'] = submission.get_url()
    options['env']['script_url'] = submission.get_script_url()
    options['env']['artifact_url'] = submission.get_artifact_url()
    options['env']['callback_url'] = urljoin(
        settings.ACS_INTERFACE_ADDRESS,
        callback,
    )

    log.debug(f'Submission #{submission.id} config is done')
    log.debug(f"Callback: {options['env']['callback_url']}")

    response = requests.post(urljoin(settings.VMCK_API_URL, 'jobs'),
                             json=options)

    log.debug(f"Submission's #{submission.id} VMCK response:\n{response}")

    return response.json()['id']


def update(submission):
    response = requests.get(urljoin(settings.VMCK_API_URL,
                                    f'jobs/{submission.vmck_job_id}'))

    return response.json()['state']
