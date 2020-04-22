import time
from datetime import datetime, timezone

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

import interface.backend.minio_api as storage
from interface.models import Course, Submission


@pytest.mark.django_db
def test_submission(client, live_server):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    User.objects.create_user('user', password='pw', is_staff=True)
    client.login(username='user', password='pw')
    pc = Course.objects.create(name='PC', code='pc')
    pc.assignment_set.create(
        code='a0',
        name='a0',
        max_score=100,
        deadline_soft=datetime(2100, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2100, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
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
    assert storage.exists('1.zip')

    submission = Submission.objects.all()[0]

    # There is a delay before the general queue's threads starts so, depending
    # on the system, the submission might be in the queue or already sent
    assert submission.state == submission.STATE_NEW \
        or submission.state == submission.STATE_QUEUED
    assert submission.assignment.code == 'a0'
    assert submission.archive_size > 0

    # As the reason mentioned above, the submission might have been already
    # submitted
    start = time.time()
    while submission.vmck_job_id is None:
        time.sleep(0.5)
        submission.refresh_from_db()

        if time.time() - start >= 2:
            assert False

    assert submission.vmck_job_id > 0

    start = time.time()
    while submission.state != submission.STATE_DONE:
        submission.refresh_from_db()

        time.sleep(1)

        if time.time() - start >= 180:
            assert False

    assert submission.score == 100
    assert submission.total_score == 100

    client.post(
        '/submission/1/review',
        data={'review-code': '+10.0: Good Job'},
        HTTP_REFERER='/',
    )

    submission.refresh_from_db()

    assert len(submission.review_message) > 0
    assert submission.review_score == 10
    assert submission.total_score == 110
