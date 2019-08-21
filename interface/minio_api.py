import io
from minio import Minio
from django.conf import settings


_client = Minio(settings.MINIO_ADDRESS,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False)


def upload(file):
    _client.put_object('test',
                       file.name,
                       io.BytesIO(file.read()),
                       file.size,
                       content_type='application/zip')


def download(filename, path):
    with open(path, 'wb') as file:
        data = _client.get_object('test', filename)
        for chunck in data.stream(32*1024):
            file.write(chunck)
