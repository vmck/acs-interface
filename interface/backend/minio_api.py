from datetime import timedelta

from minio import Minio
from minio.error import ResponseError
from minio.error import NoSuchKey
from django.conf import settings

import io


_client = Minio(
    settings.MINIO_ADDRESS,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)


class MissingFile(Exception):
    pass


def upload(filename, filedata):
    _client.put_object(
        settings.MINIO_BUCKET,
        filename,
        io.BytesIO(filedata),
        len(filedata),
        content_type="application/zip",
    )


def copy(source_file, destination_file):
    _client.copy_object(
        settings.MINIO_BUCKET,
        destination_file,
        f"/{settings.MINIO_BUCKET}/{source_file}",
    )


def download_buffer(filename, buffer):
    try:
        data = _client.get_object(settings.MINIO_BUCKET, filename)
    except NoSuchKey:
        raise MissingFile(filename)
    for chunck in data.stream(settings.BLOCK_SIZE):
        buffer.write(chunck)


def download(filename, path):
    try:
        data = _client.get_object(settings.MINIO_BUCKET, filename)
    except NoSuchKey:
        raise MissingFile(filename)
    with open(path, "wb") as file:
        for chunck in data.stream(settings.BLOCK_SIZE):
            file.write(chunck)


def get_link(filename):
    return _client.presigned_get_object(
        settings.MINIO_BUCKET,
        filename,
        expires=timedelta(hours=1),
    )


def create_bucket(bucket_name):
    if not _client.bucket_exists(bucket_name):
        _client.make_bucket(bucket_name)


def exists(filename):
    try:
        _client.stat_object(settings.MINIO_BUCKET, filename)
        return True
    except ResponseError:
        return False
