from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

import interface.backend.minio_api as storage


@pytest.mark.django_db
def test_submission(client):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    with open(filepath, 'rb') as file:
        upload = SimpleUploadedFile(filepath.name,
                                    file.read(),
                                    content_type='application/zip')
        client.post('/upload/?assignment_id=pc-00',
                    data={'name': filepath.name, 'file': upload},
                    format='multipart')

    assert storage.exists('1.zip')
