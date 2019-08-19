import logging
import io
from django.conf import settings
from minio import Minio
from minio.error import ResponseError
from .utils import random_code
from zipfile import ZipFile
from tempfile import TemporaryDirectory

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def save(file):
    minioClient = Minio(settings.MINIO_ADDRESS,
                        access_key=settings.MINIO_ACCESS_KEY,
                        secret_key=settings.MINIO_SECRET_KEY,
                        secure=False)

    minioClient.put_object('test',
                           file.name,
                           io.BytesIO(file.read()),
                           file.size,
                           content_type='application/zip')


def handle_submission(file):
    log.debug(f'Submission {file.name} received')

    save(file)
