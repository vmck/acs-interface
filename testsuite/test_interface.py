from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import interface.backend.minio_api as storage
import pytest

pytestmark = [pytest.mark.django_db]


def test_uploading_archive(client):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    with open(filepath, 'rb') as file:
        upload = SimpleUploadedFile(filepath.name,
                                    file.read(),
                                    content_type='application/zip')
        client.post('/upload/',
                    data={'name': filepath.name, 'file': upload},
                    format='multipart')

    assert storage.exists(filepath.name)
