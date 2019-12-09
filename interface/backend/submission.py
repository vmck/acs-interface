import logging

from django.db import transaction
from django.utils import timezone

import interface.backend.minio_api as storage
from interface.models import Submission
from interface.models import Assignment


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def handle_submission(file, assignment, user):
    log.debug(f'Submission {file.name} received')

    with transaction.atomic():
        Assignment.objects.select_for_update().get(pk=assignment.pk)
        entries = Submission.objects.filter(user=user).order_by('-timestamp')

        entry = entries.first()

        if entry:
            delta_t = timezone.now() - entry.timestamp
            if delta_t.seconds < assignment.min_time_between_uploads:
                log.debug(f'Submission can be made after #{delta_t} seconds')
                wait_t = assignment.min_time_between_uploads - delta_t.seconds
                raise TooManySubmissionsError(wait_t)

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
    def __init__(self, delta_t):
        self.delta_t = delta_t

    def get_delta_t(self):
        return self.delta_t
