import time

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import interface.backend.minio_api as storage
from interface.models import Submission


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

    assert len(Submission.objects.all()) == 1
    assert storage.exists('1.zip')

    submission = Submission.objects.all()[0]

    assert submission.state == submission.STATE_NEW
    assert submission.assignment.code == 'pc-00'
    assert submission.archive_size > 0
    assert submission.vmck_job_id > 0

    while submission.state != submission.STATE_DONE:
        time.sleep(2)

    assert submission.score > 0
