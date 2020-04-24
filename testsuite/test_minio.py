import time
import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from django.conf import settings

import interface.backend.minio_api as storage


def test_minio(client, live_server):
    filepath = settings.BASE_DIR / 'testsuite' / 'test.zip'

    with open(filepath, 'rb') as f:
        storage.upload('myFile.zip', bytes(f.read()))

    assert storage.exists('myFile.zip')

    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)

        storage.download('myFile.zip', tmp / 'downloaded.zip')
        assert filecmp.cmp(filepath, tmp / 'downloaded.zip')
