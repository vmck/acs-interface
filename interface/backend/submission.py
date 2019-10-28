import logging

import interface.backend.minio_api as storage


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def handle_submission(file, assignment, user):
    log.debug(f'Submission {file.name} received')

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
