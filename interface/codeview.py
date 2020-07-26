import logging
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory

from django.contrib import messages

from interface.backend.minio_api import MissingFile


log = logging.getLogger(__name__)


def submission_cut(request, submission, filename):
    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)
        try:
            submission.download(tmp / f'{submission.pk}.zip')
        except MissingFile:
            msg = f"File missing for {submission!r}"
            messages.error(request, msg)
            log.warning(msg)

        submission_archive = ZipFile(tmp / f'{submission.pk}.zip')
        submission_archive.extract(
            filename,
            path=tmp,
            pwd=None,
        )
        path = Path(tmp / f'{filename}')
        file = open(path, "r")

    return file
