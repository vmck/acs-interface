import time
import logging
from queue import PriorityQueue
from threading import BoundedSemaphore, Thread, Lock

from django.conf import settings

from interface.backend.submission.evaluator.vmck import VMCK

log = logging.getLogger(__name__)


class SubQueue(object):
    def __init__(self, free_machines=1):
        self.queue = PriorityQueue()
        self.max_machines = free_machines
        self.sem = BoundedSemaphore(free_machines)

        self.subs_lock = Lock()
        self.subs = set()

        self.sync = Thread(target=self._sync_evaluator, daemon=True)
        self.consumer = Thread(target=self._run_submission, daemon=True)

        self.sync.start()
        self.consumer.start()

    def _run_submission(self):
        while True:
            self.sem.acquire()
            _, sub = self.queue.get()
            log.info("Take submission #%s for evaluation", sub.id)
            with self.subs_lock:
                self.subs.add(sub)
            self._evaluate_submission(sub)

    def _sync_evaluator(self):
        while True:
            with self.subs_lock:
                copy_submissions = set(self.subs)

            log.info("Check submissions %s", len(copy_submissions))

            for submission in copy_submissions:
                try:
                    submission.update_state()
                    log.info("Check submission #%s status", submission.id)
                except Exception as e:
                    log.error("Exception %s for #%s", e, submission.id)

            time.sleep(settings.CHECK_INTERVAL_SUBS)

    def add_sub(self, sub):
        log.info("Add submission #%s to queue", sub.id)
        sub.state = sub.STATE_QUEUED
        sub.save()
        self.queue.put((sub.timestamp, sub))

    def done_eval(self, sub):
        log.info("Submission #%s done evaluation", sub.id)
        with self.subs_lock:
            try:
                self.subs.remove(sub)
            except Exception as e:
                log.info("Exception %s for sub #%s", e, sub.id)
        self.sem.release()

    def _evaluate_submission(self, sub):
        log.info("Evaluate submission #%s", sub.id)
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

    def done_evaluation(self, sub):
        self.general_queue.done_eval(sub)

    def show(self):
        print("General assignments")
        print(str(self.general_queue))
