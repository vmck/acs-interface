import filecmp
import io
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings

import interface.backend.minio_api as storage

filepath = settings.BASE_DIR / "testsuite" / "test.zip"


def test_minio(client):
    with open(filepath, "rb") as f:
        storage.upload("myFile.zip", bytes(f.read()))

    assert storage.exists("myFile.zip")

    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)

        storage.download("myFile.zip", tmp / "downloaded.zip")
        assert filecmp.cmp(filepath, tmp / "downloaded.zip")


def test_minio_buff(client):
    with open(filepath, "rb") as f:
        storage.upload("myFile.zip", bytes(f.read()))

    assert storage.exists("myFile.zip")

    buff = io.BytesIO()
    storage.download_buffer("myFile.zip", buff)
    buff.seek(0)

    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)
        with open(tmp / "test1.zip", "wb") as f:
            f.write(buff.getbuffer())

        assert filecmp.cmp(filepath, tmp / "test1.zip")
