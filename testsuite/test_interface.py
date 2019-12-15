import time
from datetime import datetime

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

import interface.backend.minio_api as storage
from interface.models import Course, Submission


@pytest.mark.django_db
def test_submission(client, live_server):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    User.objects.create_user('user', password='pw')
    client.login(username='user', password='pw')
    pc = Course.objects.create(name='PC', code='pc')
    pc.assignment_set.create(
        code='a0',
        name='a0',
        max_score=100,
        deadline_soft=datetime(2100, 1, 1),
        deadline_hard=datetime(2100, 1, 1),
        repo_url='https://github.com/vmck/assignment',
        repo_branch='pc-00',
    )

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
    assert storage.exists('1.zip') == True

    submission = Submission.objects.all()[0]

    assert submission.state == submission.STATE_NEW
    assert submission.assignment.code == 'a0'
    assert submission.archive_size > 0
    assert submission.vmck_job_id > 0

    count = 0
    while submission.state != submission.STATE_DONE:
        submission = Submission.objects.all()[0]

        time.sleep(10)

        count += 1
        if count == 50:
            assert False == True

    assert submission.score == 100
    assert submission.total_score == 100
