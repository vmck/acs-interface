from django.core.management.base import BaseCommand
from interface.settings import MINIO_BUCKET

import interface.backend.minio_api as storage


class Command(BaseCommand):
    help = (  # noqa: A003
        "If the bucket with the name settings.MINIO_BUCKET"
        "does not exist, create it"
    )

    def handle(self, *args, **options):
        storage.create_bucket(MINIO_BUCKET)
