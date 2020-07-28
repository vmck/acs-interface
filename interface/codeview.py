import io
import logging
from zipfile import ZipFile

from interface.backend.minio_api import MissingFile, download_buffer

log = logging.getLogger(__name__)


def extract_file(request, submission, filename):
    buff = io.BytesIO()
    try:
        download_buffer(f'{submission.pk}.zip', buff)
    except MissingFile:
        return io.StringIO("The archive is missing!")

    submission_archive = ZipFile(buff)
    try:
        file = submission_archive.read(filename)
    except Exception:
        return io.StringIO("The file is missing!")

    return io.StringIO(str(file, encoding="ascii"))
