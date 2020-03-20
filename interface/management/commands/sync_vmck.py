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
            log.info("Check submissions status")

            submissions = (
                Submission.objects
                .exclude(state=Submission.STATE_DONE)
                .order_by('-id')
            )

            for submission in submissions:
                submission.update_state()

            time.sleep(settings.CHECK_INTERVAL_SUBS)
