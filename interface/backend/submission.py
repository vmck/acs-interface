from tempfile import TemporaryDirectory
from ..settings import base_dir, VMCK_API_URL
from ..minio_api import MinioAPI
from pathlib import Path
from shutil import copy

import logging
import subprocess

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')

    storage = MinioAPI.getInstance()
    storage.upload(file)

    with TemporaryDirectory() as _tmp:
        tmp = Path(str(_tmp))
        storage.download(file.name, tmp / 'archive.zip')
        copy(base_dir / 'vagrant' / 'Vagrantfile', tmp)
        proc = subprocess.Popen(f'docker run --env VMCK_URL={VMCK_API_URL} --network="host" -it --rm --volume $(pwd):/homework  vmck/vagrant-vmck:latest /bin/bash -c "cd /homework; vagrant up; vagrant destroy -f"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=tmp)  # noqa: E501
        while proc.poll() is None:
            print(''.join(proc.stdout.readline().decode('utf-8').strip()))  # noqa: E501