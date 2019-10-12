import logging

from django.shortcuts import get_object_or_404
from django.http import Http404

import interface.backend.minio_api as storage
from interface.models import Submission, Assignment


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def handle_submission(request):
    file = request.FILES['file']
    log.debug(f'Submission {file.name} received')

    assignment = get_object_or_404(Assignment.objects,
                                   code=request.GET['assignment_id'])
    # if not assignment.is_open_for(request.uesr):
    #     return render('ești bou.html')

    if not assignment:
        return Http404()

    submission = Submission.objects.create(
        archive_size=file.size,
        user=request.user,
        assignment=assignment,
    )
    log.debug("Salut")
    log.debug("Salut2")
    storage.upload(f'{submission.id}.zip', file.read())

    submission.evaluate()

    log.debug(f'Submission #{submission.id} sent to VMCK '
              f'as #{submission.vmck_job_id}')
