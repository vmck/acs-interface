import logging
from copy import deepcopy
from zipfile import ZipFile

from django.db import transaction
from django.utils import timezone

import interface.backend.minio_api as storage

log = logging.getLogger(__name__)


class CorruptZipFile(Exception):
    pass


def handle_submission(file, assignment, user):
    log.debug("Submission %s received", file.name)

    test_file = deepcopy(file)

    with ZipFile(test_file) as archive:
        if archive.testzip():
            raise CorruptZipFile()

    with transaction.atomic():
        """
        Computing time from the last upload by this user. We lock the
        assignment row to prevent simultaneous uploads (race condition).
        """
        entries = assignment.submission_set.filter(user=user).order_by(
            "-timestamp",
        )

        entry = entries.first()

        if entry:
            delta_t = timezone.now() - entry.timestamp
            if delta_t.seconds < assignment.min_time_between_uploads:
                log.debug("Submission can be made after #%s seconds", delta_t)
                raise TooManySubmissionsError(
                    assignment.min_time_between_uploads,
                )

        submission = assignment.submission_set.create(
            user=user,
            archive_size=file.size,
        )

    log.debug("Submission #%s created", submission.pk)
    storage.upload(f"{submission.pk}.zip", file.read())
    log.debug("Submission's #%s zipfile was uploaded", submission.pk)

    submission.evaluate()
    log.debug(
        "Submission #%s was sent to VMCK as #%s",
        submission.pk,
        submission.evaluator_job_id,
    )


class TooManySubmissionsError(Exception):
    def __init__(self, wait_t):
        self.wait_t = wait_t
