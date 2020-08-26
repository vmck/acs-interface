import io
import logging
from zipfile import ZipFile

from interface.backend.minio_api import MissingFile, download_buffer
from django.template.defaulttags import register

log = logging.getLogger(__name__)


def extract_file(request, submission, filename):
    buff = io.BytesIO()
    try:
        download_buffer(f"{submission.pk}.zip", buff)
    except MissingFile:
        return io.StringIO("The archive is missing!")

    submission_archive = ZipFile(buff)
    try:
        file = submission_archive.read(filename)
    except KeyError:
        return io.StringIO("The file is missing!")

    return io.StringIO(str(file, encoding="ascii"))


def tree_view(request, submission):
    buff = io.BytesIO()
    try:
        submission.download(buff)
    except MissingFile:
        return {}

    submission_archive = ZipFile(buff)
    return make_dict(submission_archive)


def make_dict(submission_archive):
    tree = {}
    for path in submission_archive.infolist():
        node = tree
        split_path = path.filename.split('/')
        for index, level in enumerate(split_path):
            if path.is_dir():
                obj = {}
            else:
                if index != len(split_path)-1:
                    obj = {}
                else:
                    obj = {'$path': path.filename}

            node = node.setdefault(level, obj)

    return tree


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
