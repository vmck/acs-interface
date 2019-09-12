from urllib.parse import urljoin
import configparser
import logging
import re

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
import requests

import interface.backend.minio_api as storage
from interface.utils import is_number
from interface.models import Submission, Assignment


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def vmck_config(submission):
    m = re.match(r'https://github.com/(?P<org>[^/]+)/(?P<repo>[^/]+)/?$',
                 submission.assignment.repo_url)
    url_base = ('https://raw.githubusercontent.com'
                '/{0}/{1}/'.format(*list(m.groups())))

    config_data = requests.get(
                    urljoin(
                        url_base,
                        f'{submission.assignment.repo_branch}/config.ini')
                        )

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

    assignment = get_object_or_404(Assignment.objects,
                                   code=request.GET['assignment_id'])
    # if not assignment.is_open_for(request.uesr):
    #     return render('ești bou.html')

    if not assignment:
        return Http404()

    submission = Submission.objects.create(
        archive_size=file.size,
        user=request.user,
        assignment=assignment,
    )

    storage.upload(f'{submission.id}.zip', file.read())

    m = re.match(r'https://github.com/(?P<org>[^/]+)/(?P<repo>[^/]+)/?$',
                 submission.assignment.repo_url)

    url_base = ('https://raw.githubusercontent.com/'
                '{0}/{1}/'.format(*list(m.groups())))

    config_url = urljoin(url_base,
                         f'{submission.assignment.repo_branch}/checker.sh')

    options = vmck_config(submission)
    options['name'] = f'{assignment.code} submission #{submission.id}'
    options['manager'] = True
    options['env'] = {}
    options['env']['archive'] = submission.get_url()
    options['env']['vagrant_tag'] = 'submission'
    options['env']['script'] = config_url
    options['env']['memory'] = settings.MANAGER_MEMORY
    options['env']['cpu_mhz'] = settings.MANAGER_MHZ
    options['env']['interface_address'] = settings.ACS_INTERFACE_ADDRESS
    options['env']['id'] = str(submission.id)

    response = requests.post(urljoin(settings.VMCK_API_URL, 'jobs'),
                             json=options)

    submission.vmck_job_id = response.json()['id']

    log.debug(f'Submission #{submission.id} sent to VMCK '
              f'as #{submission.vmck_job_id}')
    submission.save()
