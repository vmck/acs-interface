import time
import filecmp
from tempfile import NamedTemporaryFile

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

import interface.backend.minio_api as storage
from interface.models import Submission


FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'

@pytest.mark.skip
@pytest.mark.django_db
def test_submission(client, live_server, base_db_setup):
    FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'

    (_, course, assignment) = base_db_setup

    client.login(username='user', password='pw')

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(FILEPATH.name,
                                    file.read(),
                                    content_type='application/zip')
        client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
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

    response = client.get(f'/submission/{submission.pk}/download')

    with NamedTemporaryFile(delete=False) as f:
        for data in response.streaming_content:
            f.write(data)

    assert filecmp.cmp(f.name, FILEPATH, shallow=False)


@pytest.mark.django_db
def test_upload_too_many_times(client, base_db_setup, mock_evaluate):
    (_, course, assignment) = base_db_setup

    client.login(username='user', password='pw')

    for _ in range(2):
        with open(FILEPATH, 'rb') as file:
            upload = SimpleUploadedFile(FILEPATH.name,
                                        file.read(),
                                        content_type='application/zip')

            response = client.post(
                f'/assignment/{course.pk}/{assignment.pk}/upload/',
                data={'name': FILEPATH.name, 'file': upload},
                format='multipart',
            )

    message_list = list(response.context['messages'])
    assert len(message_list) == 1

    message = str(message_list[0])
    assert message == 'Please wait 60s between submissions'


@pytest.mark.django_db
def test_download_from_someone_else(client, base_db_setup):
    (user, course, assignment) = base_db_setup

    client.login(username='user', password='pw')

    other = User.objects.create_user('other', password='pw')
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=other,
    )

    response = client.get(f'/submission/{submission.pk}/download')
    assert response.status_code == 404


@pytest.mark.django_db
def test_no_review(client, base_db_setup):
    (user, course, assignment) = base_db_setup
    user.is_staff = False
    user.save()

    client.login(username='user', password='pw')
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    review_message = '+10.0: Hacker'
    response = client.post(
        f'/submission/{submission.pk}/review',
        data={'review-code': review_message},
    )

    # because we use @staff_member_required we are redirected to the admin
    # page to login with an actual admin account
    assert user.is_staff is False
    assert response.status_code == 302
    assert response.url \
        == f'/admin/login/?next=/submission/{submission.pk}/review'
