import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from interface.models import Submission


@pytest.mark.django_db
def test_zip_bad_zipfile(client, base_db_setup, mock_evaluate):
    FILEPATH = FILEPATH = settings.BASE_DIR / 'testsuite' / 'not_a_zip.zip'
    (_, course, assignment) = base_db_setup

    client.login(username='user', password='pw')

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(FILEPATH.name,
                                    file.read(),
                                    content_type='application/zip')

        response = client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
            format='multipart',
        )

        assert Submission.objects.all().count() == 0

        message_list = list(response.context['messages'])
        assert len(message_list) == 1

        message = str(message_list[0])
        assert message == 'File is not a valid zip archive'


@pytest.mark.django_db
def test_zip_corrupt_zipfile(client, base_db_setup, mock_evaluate):
    FILEPATH = FILEPATH = settings.BASE_DIR / 'testsuite' / 'corrupt.zip'
    (_, course, assignment) = base_db_setup

    client.login(username='user', password='pw')

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(FILEPATH.name,
                                    file.read(),
                                    content_type='application/zip')

        response = client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
            format='multipart',
        )

        assert Submission.objects.all().count() == 0

        message_list = list(response.context['messages'])
        assert len(message_list) == 1

        message = str(message_list[0])
        assert message == 'The archive is corrupt'
