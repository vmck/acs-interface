from tempfile import TemporaryDirectory
from zipfile import ZipFile
from pathlib import Path
from django.conf import settings

import interface.backend.minio_api as storage
import requests
import logging

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')

    with TemporaryDirectory() as _tmp:
        tmp = Path(str(_tmp))
        submission_arch = ZipFile(tmp / file.name, mode='x')
        submission_arch.writestr('submission.zip', data=file.read())
        submission_arch.write(settings.BASE_DIR / 'vagrant' / 'Vagrantfile', 'Vagrantfile')
        submission_arch.close()

        with open(tmp / file.name, 'rb') as data:
            print(dir(data.read()))
            storage.upload(file.name, data.read())

    url = storage.get_link(file.name)
