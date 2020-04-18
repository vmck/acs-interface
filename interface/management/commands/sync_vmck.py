from django.core.management.base import BaseCommand
from django.conf import settings

from interface.models import Submission

import time
import logging

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check submission status'

    def handle(self, *args, **options):
        while True:
            submissions = (
                Submission.objects
                .exclude(state=Submission.STATE_DONE)
                .exclude(state=Submission.STATE_QUEUED)
                .order_by('-id')
            )

            for submission in submissions:
                submission.update_state()
                log.info(f"Check submission #{submission.id} status")

            time.sleep(settings.CHECK_INTERVAL_SUBS)
