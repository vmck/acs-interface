import time
import logging
from queue import PriorityQueue
from threading import Semaphore, Thread

from django.conf import settings

from interface import vmck
from interface import models


log = logging.getLogger(__name__)


class SubQueue(object):

    def __init__(self, free_machines=1):
        self.queue = PriorityQueue()
        self.max_machines = free_machines
        self.sem = Semaphore(free_machines)
        self.consumer = Thread(target=self._run_submission)
        self.sync = Thread(target=self._sync_vmck)

    def _run_submission(self):
        while True:
            _, sub = self.queue.get()
            self.sem.acquire()
            self._evaluate_submission(sub)

    def _sync_vmck(self):
        while True:
            submissions = (
                models.Submission.objects
                .exclude(state=models.Submission.STATE_DONE)
                .exclude(state=models.Submission.STATE_QUEUED)
                .order_by('-id')
            )

            for submission in submissions:
                submission.update_state()
                log.info(f"Check submission #{submission.id} status")

            time.sleep(settings.CHECK_INTERVAL_SUBS)

    def add_sub(self, sub):
        if not self.consumer.is_alive():
            self.consumer.start()

        if not self.sync.is_alive():
            self.sync.start()

        log.info(f"Add submission #{sub.id} to queue")
        self.queue.put((sub.timestamp, sub))
        sub.state = sub.STATE_QUEUED
        sub.save()

    def done_eval(self):
        self.sem.release()

    def _evaluate_submission(self, sub):
        log.info(f"Evaluate submission #{sub.id}")
        sub.vmck_job_id = vmck.evaluate(sub)
        sub.state = sub.STATE_NEW
        sub.changeReason = "VMCK id"
        sub.save()

    def __str__(self):
        return f"Queue [{self.queue}] and elements: {self.queue.queue}"


class SubmissionScheduler(object):
    # Queue for all the assignments that are not prioritiezed
    general_queue = SubQueue(4)

    def __init__(self):
        raise AttributeError("No init method for SubmissionScheduler")

    @staticmethod
    def add_submission(sub):
        queue = SubmissionScheduler.general_queue

        if queue is None:
            log.error("Queue to place a submission is None!")
            return

        queue.add_sub(sub)

    @staticmethod
    def done_evaluation():
        SubmissionScheduler.general_queue.done_eval()

    @staticmethod
    def show():
        print("General assignments")
        print(str(SubmissionScheduler.general_queue))
