import io
import logging
from zipfile import ZipFile, BadZipFile

from interface.backend.minio_api import MissingFile, download_buffer
from django.template.defaulttags import register

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
    except KeyError:
        return io.StringIO("The file is missing!")

    return io.StringIO(str(file, encoding="ascii"))


def tree_view(request, submission):
    buff = io.BytesIO()
    try:
        download_buffer(f'{submission.pk}.zip', buff)
    except MissingFile:
        return BadZipFile

    submission_archive = ZipFile(buff)
    return submission_archive


def make_dict(submission_archive):
    tree = {}
    for path in submission_archive.infolist():
        node = tree
        print(path.filename)
        for index, level in enumerate(path.filename.split('/')):
            if level:
                if path.is_dir():
                    obj = {}
                else:
                    if index != len(path.filename.split('/'))-1:
                        obj = {}
                    else:
                        obj = {'$path': path.filename}

                node = node.setdefault(level, obj)

    return tree


def pretty(d, indent=0):
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) and value.get('$path'):
                print('  ' * indent + str(key) + ' ' + value.get('$path'))
                continue
            else:
                print('  ' * indent + str(key))

            pretty(value, indent+1)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
