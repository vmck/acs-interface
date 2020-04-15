from queue import PriorityQueue, Empty
import logging
from threading import Semaphore, Thread

from django.utils import timezone

from interface import vmck


log = logging.getLogger(__name__)


class SubQueue(object):

    def __init__(self, free_machines=1):
        self.queue = PriorityQueue()
        self.max_machines = free_machines
        self.sem = Semaphore(free_machines)
        self.consumer = Thread(target=self._run_submission)

        self.consumer.start()

    def _run_submission(self):
        while True:
            print("Done")
            _, sub = self.queue.get()
            self.sem.acquire()
            print("Send submission")
            self._evaluate_submission(sub)

    def add_sub(self, sub):
        log.info(f"Add submission #{sub.id} to queue")
        self.queue.put((sub.timestamp, sub))
        sub.state = sub.STATE_QUEUED

    def done_eval(self):
        print("Done eval")
        self.sem.release()

    def _evaluate_submission(self, sub):
        print("Eval")
        log.info(f"Evaluate submission #{sub.id}")
        sub.vmck_job_id = vmck.evaluate(sub)
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
        print(SubmissionScheduler.general_queue)
