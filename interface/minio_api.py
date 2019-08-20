import io
from minio import Minio
from django.conf import settings


class MinioAPI:
    __instance = None

    @staticmethod
    def getInstance():
        if MinioAPI.__instance is None:
            MinioAPI()

        return MinioAPI.__instance

    def __init__(self):
        MinioAPI.__instance = self

        self.client = Minio(settings.MINIO_ADDRESS,
                            access_key=settings.MINIO_ACCESS_KEY,
                            secret_key=settings.MINIO_SECRET_KEY,
                            secure=False)

    def upload(self, file):
        self.client.put_object('test',
                               file.name,
                               io.BytesIO(file.read()),
                               file.size,
                               content_type='application/zip')

    def download(self, filename, path):
        with open(path, 'wb') as file:
            data = self.client.get_object('test', filename)
            for chunck in data.stream(32*1024):
                file.write(chunck)
