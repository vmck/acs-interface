import time
import filecmp
import zipfile
import threading
from io import BytesIO

from tempfile import NamedTemporaryFile
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

import interface.backend.minio_api as storage
from interface.models import Submission, Assignment


FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'


@pytest.fixture
def mock_config(monkeypatch):
    ADDR = '10.66.60.1'
    PORT = 5000

    class Server:
        def __init__(self):
            self.server = HTTPServer(
                (ADDR, PORT),
                SimpleHTTPRequestHandler,
            )

        def start_server(self):
            thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
            )
            thread.start()

        def stop_server(self):
            self.server.shutdown()
            self.server.server_close()

    def url_for(self, filename):
        return f'http://{ADDR}:{PORT}/testsuite/{filename}'

    monkeypatch.setattr(Assignment, 'url_for', url_for)

    return Server()


FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'


@pytest.mark.django_db
def test_submission(client, live_server, base_db_setup, mock_config):
    FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'

    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    mock_config.start_server()

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(FILEPATH.name,
                                    file.read(),
                                    content_type='application/zip')
        client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
            format='multipart',
        )

    assert Submission.objects.all().count() == 1
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
    while submission.evaluator_job_id is None:
        time.sleep(0.5)
        submission.refresh_from_db()

        assert time.time() - start < 2

    assert submission.evaluator_job_id > 0

    start = time.time()
    while submission.state != submission.STATE_DONE:
        submission.refresh_from_db()

        time.sleep(1)

        if time.time() - start >= 180:
            assert False

    mock_config.stop_server()

    assert submission.score == 100
    assert submission.total_score == 100

    response = client.get(f'/submission/{submission.pk}/download')

    with NamedTemporaryFile(delete=False) as f:
        for data in response.streaming_content:
            f.write(data)

    assert filecmp.cmp(f.name, FILEPATH, shallow=False)


@pytest.mark.django_db
def test_upload_too_many_times(client, base_db_setup, mock_evaluate):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

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

    message = message_list[0].message
    assert message == 'Please wait 60s between submissions'


@pytest.mark.django_db
def test_download_from_someone_else(client, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    other = User.objects.create_user('other', password='pw')
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=other,
    )

    response = client.get(f'/submission/{submission.pk}/download')
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_review(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')
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
    STC.assertRedirects(
        response,
        f'/admin/login/?next=/submission/{submission.pk}/review',
    )


@pytest.mark.django_db
def test_user_cannot_recompute_score(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    response = client.post(f'/submission/{submission.pk}/recompute')
    STC.assertRedirects(
        response,
        f'/admin/login/?next=/submission/{submission.pk}/recompute',
    )


@pytest.mark.django_db
def test_user_cannot_rerun(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    response = client.post(f'/submission/{submission.pk}/rerun')
    STC.assertRedirects(
        response,
        f'/admin/login/?next=/submission/{submission.pk}/rerun',
    )


@pytest.mark.django_db
def test_user_login(client, STC, base_db_setup):
    (_, _, user, _, _) = base_db_setup

    response = client.post('/', {'username': 'user', 'password': 'pw'})
    STC.assertRedirects(response, '/homepage/')


@pytest.mark.django_db
def test_user_logout(client, STC, base_db_setup):
    (_, _, user, _, _) = base_db_setup
    client.post('/', {'username': user.username, 'password': 'pw'})

    response = client.post('/logout/')
    STC.assertRedirects(response, '/')


def test_anonymous(client, STC):
    response = client.get('/homepage/')
    STC.assertRedirects(response, '/?next=/homepage/')

    response = client.get('/submission/')
    STC.assertRedirects(response, '/?next=/submission/')


@pytest.mark.django_db
def test_user_cannot_see_another_userpage(client, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    other = User.objects.create_user('other', password='pw')

    response = client.get(
        f'/mysubmissions/{other.username}',
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_filesize_limit(client, base_db_setup, mock_evaluate, STC):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    buff = BytesIO()
    zip_archive = zipfile.ZipFile(buff, mode='w')
    zip_archive.writestr('test.c', 'aaaa'*2**20)

    upload = SimpleUploadedFile(
        FILEPATH.name,
        buff.getvalue(),
        content_type='application/zip',
    )

    response = client.post(
        f'/assignment/{course.pk}/{assignment.pk}/upload/',
        data={'name': FILEPATH.name, 'file': upload},
        format='multipart',
    )

    assert Submission.objects.all().count() == 0

    STC.assertContains(response, 'Keep files below')


@pytest.mark.django_db
def test_user_cannot_reveal(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    response = client.post(
        f'/assignment/{course.pk}/{assignment.pk}/reveal',
    )
    STC.assertRedirects(
        response,
        f'/admin/login/?next=/assignment/{course.pk}/{assignment.pk}/reveal',
    )


@pytest.mark.django_db
def test_user_cannot_see_another_submission_score(client, STC, base_db_setup):
    (_, _, user, _, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    other = User.objects.create_user('other', password='pw')

    submission = assignment.submission_set.create(
        user=other,
        score=100.00,
        state=Submission.STATE_DONE,
    )

    response = client.get(
        f'/submission/{submission.pk}/',
    )

    assert response.status_code == 200
    STC.assertTemplateUsed(response, 'interface/submission_result.html')
    STC.assertContains(response, other.username)
    STC.assertContains(response, "N/A")
    STC.assertNotContains(response, "TOTAL")


@pytest.mark.django_db
def test_user_see_revealed_score(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    assignment.hidden_score = False
    assignment.save()

    response = client.get(
        f'/submission/{submission.pk}',
        follow=True,
    )
    STC.assertNotContains(response, "N/A")
    STC.assertContains(response, "Final score")


@pytest.mark.django_db
def test_user_code_view(client, STC, base_db_setup):
    FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'

    (_, _, user, course, assignment) = base_db_setup

    client.login(username=user.username, password='pw')

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(
            FILEPATH.name,
            file.read(),
            content_type='application/zip',
        )
        client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
            format='multipart',
        )

    submission = Submission.objects.all()[0]

    response = client.get(
        f'/submission/{submission.pk}/test/',
        follow=True,
    )

    STC.assertTemplateNotUsed(response, 'interface/code_view.html')
    assert response.status_code == 200
    STC.assertRedirects(
        response,
        f'/admin/login/?next=/submission/{submission.pk}/test/',
    )
