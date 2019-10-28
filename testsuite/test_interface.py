import time

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

import interface.backend.minio_api as storage
from interface.models import Course, Submission


@pytest.mark.skip(reason="Minio is not set up correctly")
@pytest.mark.django_db
def test_submission(client):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    User.objects.create_user('user', password='pw')
    client.login(username='user', password='pw')
    pc = Course.objects.create(name='PC', code='pc')
    pc.assignment_set.create(code='a0')

    with open(filepath, 'rb') as file:
        upload = SimpleUploadedFile(filepath.name,
                                    file.read(),
                                    content_type='application/zip')
        client.post(
            '/assignment/pc/a0/upload/',
            data={'name': filepath.name, 'file': upload},
            format='multipart',
        )

    assert len(Submission.objects.all()) == 1
    assert storage.exists('1.zip')

    submission = Submission.objects.all()[0]

    assert submission.state == submission.STATE_NEW
    assert submission.assignment.code == 'pc-a0'
    assert submission.archive_size > 0
    assert submission.vmck_job_id > 0

    while submission.state != submission.STATE_DONE:
        time.sleep(2)

    assert submission.score > 0
