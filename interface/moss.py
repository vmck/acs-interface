import glob
import logging
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory

import mosspy
from django.conf import settings
from django.contrib import messages

from interface.backend.minio_api import MissingFile


log = logging.getLogger(__name__)


def moss_check(submissions, assignment, request):
    moss = mosspy.Moss(
        settings.MOSS_USER_ID,
        assignment.get_language_display(),
    )
    moss.setDirectoryMode(1)

    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)

        for submission in submissions:
            try:
                submission.download(tmp / f'{submission.id}.zip')
            except MissingFile:
                msg = f"File missing for {submission!r}"
                messages.error(request, msg)
                log.warning(msg)

            submission_archive = ZipFile(tmp / f'{submission.id}.zip')
            submission_archive.extractall(
                tmp / f'{submission.user.username}',
            )

            read_files = glob.glob(
                str(tmp / (f'{submission.user.username}'
                    f'/**/*.{submission.assignment.language}')
                    ),
                recursive=True,
            )

            for f in read_files:
                user_dir = f[len(str(tmp)):]
                new_filename = (user_dir.split('/')[1]
                                + f'/{submission.user.username}_'
                                + user_dir.split('/')[-1]
                                )

                moss.addFile(f, new_filename)

        url = moss.send()
    return url
