from minio import Minio, ResponseError
from django.conf import settings
from datetime import timedelta

import io

_client = Minio(settings.MINIO_ADDRESS,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False)


def upload(filename, filedata):
    _client.put_object(settings.MINIO_BUCKET,
                       filename,
                       io.BytesIO(filedata),
                       len(filedata),
                       content_type='application/zip')


def download(filename, path):
    with open(path, 'wb') as file:
        data = _client.get_object(settings.MINIO_BUCKET, filename)
        for chunck in data.stream(32*1024):
            file.write(chunck)


def get_link(filename):
    return _client.presigned_get_object(settings.MINIO_BUCKET,
                                        filename,
                                        expires=timedelta(hours=1))


def exists(filename):
    try:
        _client.stat_object(settings.MINIO_BUCKET, filename)
        return True
    except ResponseError:
        return False
