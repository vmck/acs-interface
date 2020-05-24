import time
import filecmp
from datetime import datetime, timezone
from tempfile import NamedTemporaryFile

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import interface.backend.minio_api as storage
from interface.models import Submission


@pytest.mark.django_db
def test_submission(client, live_server, base_db_setup):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    (_, course, assignment) = base_db_setup
    assignment.deadline_soft = datetime(2050, 1, 2, tzinfo=timezone.utc)
    assignment.deadline_hard = datetime(2050, 1, 2, tzinfo=timezone.utc)
    assignment.save()

    client.login(username='user', password='pw')

    with open(filepath, 'rb') as file:
        upload = SimpleUploadedFile(filepath.name,
                                    file.read(),
                                    content_type='application/zip')
        client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
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
    assert submission.archive_size > 0

    # As the reason mentioned above, the submission might have been already
    # submitted
    start = time.time()
    while submission.vmck_job_id is None:
        time.sleep(0.5)
        submission.refresh_from_db()

        assert time.time() - start < 2

    assert submission.vmck_job_id > 0

    start = time.time()
    while submission.state != submission.STATE_DONE:
        submission.refresh_from_db()

        time.sleep(1)

        if time.time() - start >= 180:
            assert False

    assert submission.score == 100
    assert submission.total_score == 100

    response = client.get('/submission/1/download')

    with NamedTemporaryFile(delete=False) as f:
        for data in response.streaming_content:
            f.write(data)

    assert filecmp.cmp(f.name, filepath, shallow=False)
