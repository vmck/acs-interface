import logging
from zipfile import ZipFile

from django.db import transaction
from django.utils import timezone
from django.contrib import messages

from interface.models import Assignment
import interface.backend.minio_api as storage


log = logging.getLogger(__name__)


class CorruptZipFile(Exception):
    pass


def handle_submission(file, assignment, user):
    log.debug(f'Submission {file.name} received')

    with ZipFile(file) as archive:
        if archive.testzip():
            raise CorruptZipFile()

    with transaction.atomic():
        """
            Computing time from the last upload by this user. We lock the
            assignment row to prevent simultaneous uploads (race condition).
        """
        assignment = (
            Assignment.objects.select_for_update()
            .get(pk=assignment.pk)
        )
        entries = (
            assignment.submission_set
            .filter(user=user)
            .order_by('-timestamp')
        )

        entry = entries.first()

        if entry:
            delta_t = timezone.now() - entry.timestamp
            if delta_t.seconds < assignment.min_time_between_uploads:
                log.debug(f'Submission can be made after #{delta_t} seconds')
                raise TooManySubmissionsError(
                            assignment.min_time_between_uploads
                        )

        submission = assignment.submission_set.create(
            user=user,
            archive_size=file.size,
        )

    log.debug(f'Submission #{submission.id} created')

    storage.upload(f'{submission.id}.zip', file.read())
    log.debug(f"Submission's #{submission.id} zipfile was uploaded")

    submission.evaluate()
    log.debug(f'Submission #{submission.id} was sent to VMCK '
              f'as #{submission.vmck_job_id}')


class TooManySubmissionsError(Exception):
    def __init__(self, wait_t):
        self.wait_t = wait_t
