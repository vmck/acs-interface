import logging
from django.conf import settings
from tempfile import TemporaryDirectory
from .minio_api import MinioAPI
from zipfile import ZipFile
from pathlib import Path
from shutil import copy

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def handle_submission(file):
    log.debug(f'Submission {file.name} received')
    storage =  MinioAPI.getInstance()

    storage.upload(file)
    with TemporaryDirectory() as _tmp:
        tmp = Path(str(_tmp))
        log.debug(f'Temporary directory at {tmp}')
        storage.download(file.name, tmp / 'archive.zip')
        copy(settings.base_dir / 'vagrant' / 'Vagrantfile', tmp)

