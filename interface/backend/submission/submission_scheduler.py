import time
import logging
from queue import PriorityQueue
from threading import Semaphore, Thread

from django.conf import settings

from interface import models
from interface.backend.submission.evaluator.vmck import VMCK

log = logging.getLogger(__name__)


class SubQueue(object):
    def __init__(self, free_machines=1):
        self.queue = PriorityQueue()
        self.max_machines = free_machines
        self.sem = Semaphore(free_machines)
        self.consumer = Thread(target=self._run_submission, daemon=True)
        self.sync = Thread(target=self._sync_evaluator, daemon=True)

        self.consumer.start()
        self.sync.start()

    def _run_submission(self):
        while True:
            _, sub = self.queue.get()
            self.sem.acquire()
            self._evaluate_submission(sub)

    def _sync_evaluator(self):
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
        log.info(f"Add submission #{sub.id} to queue")
        sub.state = sub.STATE_QUEUED
        sub.save()
        self.queue.put((sub.timestamp, sub))

    def done_eval(self):
        self.sem.release()

    def _evaluate_submission(self, sub):
        log.info(f"Evaluate submission #{sub.id}")
        sub.evaluator_job_id = SubmissionScheduler.evaluator.evaluate(sub)
        sub.state = sub.STATE_NEW
        sub.changeReason = "Evaluator id"
        sub.save()

    def __str__(self):
        return f"Queue [{self.queue}] and elements: {self.queue.queue}"


class SubmissionScheduler(object):
    _instance = None
    evaluator = VMCK

    @staticmethod
    def get_instance():
        if SubmissionScheduler._instance is None:
            SubmissionScheduler()

        return SubmissionScheduler._instance

    def __init__(self):
        if SubmissionScheduler._instance is not None:
            raise Exception("SubmissionScheduler already initialized")
        else:
            # Queue for all the assignments that are not prioritiezed
            self.general_queue = SubQueue(settings.TOTAL_MACHINES)
            SubmissionScheduler._instance = self

    def add_submission(self, sub):
        self.general_queue.add_sub(sub)

    def done_evaluation(self):
        self.general_queue.done_eval()

    def show(self):
        print("General assignments")
        print(str(self.general_queue))
