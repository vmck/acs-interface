import datetime
from queue import PriorityQueue, Empty
import logging
from threading import Lock


from django.utils import timezone
from background_task import background

from interface import vmck
from interface.settings import NR_TOTAL_MACHINES, NR_RESERVED_MACHINES


log = logging.getLogger(__name__)


class SubQueue(object):

    def __init__(self, free_machines=1):
        self.lock = Lock()
        self.queue = PriorityQueue()
        self.max_machines = free_machines
        self.free_machines = free_machines

    def add_sub(self, sub):
        self.queue.put((sub.timestamp, sub))

        with self.lock:
            if self.free_machines != 0:
                # There is a free machine
                try:
                    _, sub = self.queue.get_nowait()
                    self.free_machines -= 1
                    SubQueue.evaluate_submission(sub)
                except Empty:
                    pass

    def change_nr_machines(self, new_nr):
        with self.lock:
            already_taken_machines = self.max_machines - self.free_machines
            self.free_machines = new_nr - already_taken_machines

    def _done_eval(self, sub):
        with self.lock:
            self.free_machines += 1
            try:
                _, sub = self.queue.get_nowait()
                self.free_machines -= 1
                SubQueue.evaluate_submission(sub)
            except Empty:
                pass

    def _evaluate_submission(self, sub):
        sub.vmck_job.id = vmck.evaluate(sub, self._done_eval)
        sub.changeReason = "VMCK id"
        sub.save()

    def __str__(self):
        return f"Queue [{self.queue}] and elements: {self.queue.queue}"


class SubmissionManager(object):
    # Key   -> Assignment
    # Value -> SubQueue
    prio_dict = {}
    prio_dict_lock = Lock()

    # Queue for all the assignments that are not prioritiezed
    general_queue = SubQueue(4)

    def __init__(self):
        raise AttributeError("No init method for SubmissionManager")

    @staticmethod
    def _compute_resources():
        '''
            ATTENTION!
            The prio_dict_lock should be hold before calling this method
        '''
        prio_resources = (NR_TOTAL_MACHINES - NR_RESERVED_MACHINES)
        nr_prio_assignments = len(SubmissionManager.prio_dict)

        if nr_prio_assignments == 0:
            # General queue can take more resources
            SubmissionManager.general_queue.change_nr_machines(4)
        else:
            SubmissionManager.general_queue.change_nr_machines(1)
            prio_resources //= nr_prio_assignments

        for _, sub_queue in SubmissionManager.prio_dict.items():
            sub_queue.change_nr_machines(prio_resources)

        log.info(f"Deadline resources {prio_resources} updated")

    @background(schedule=30)
    def _add_prio_assignment(assignment_code):
        log.info(f"Add {assignment_code} to priority deadlines")
        print(f"Add {assignment_code} to priority deadlines")
        SubmissionManager.prio_dict["B"] = 5

        with SubmissionManager.prio_dict_lock:
            # TODO Can this ever happen?
            if assignment_code in SubmissionManager.prio_dict:
                return

            SubmissionManager.prio_dict[assignment_code] = SubQueue()
            SubmissionManager._compute_resources()

    @background
    def _remove_prio_assignment(assignment_code):
        log.info(f"Remove {assignment_code} from priority deadlines")

        '''
            1. Save all the submissions from the priority queue
            2. Delete the assignment from the queue
            3. Add the saved submissions to the general submission queue
        '''

        subs = [e for e in SubmissionManager.prio_dict[assignment_code].queue]

        with SubmissionManager.priority_queue_lock:
            del SubmissionManager.prio_dict[assignment_code]
            SubmissionManager._compute_resources()

        for sub in subs:
            SubmissionManager.general_queue.put((sub.timestamp, sub))

    @staticmethod
    def _trigger_prio_assignment(assignment):
        print("Hellllo")
        # Check if we have any assignment
        dead_soft = assignment.deadline_soft

        # active 1 day before
        dead_soft -= datetime.timedelta(days=1)

        now = timezone.now()
        print(f"Now is {now}")
        now += datetime.timedelta(seconds=5)
        print(f"Now is {now} changed")
        SubmissionManager._add_prio_assignment(
            assignment.full_code,
            schedule=5)

        from time import sleep
        sleep(10)

    @staticmethod
    def _is_deadline_day():
        return len(SubmissionManager.prio_dict) != 0

    @staticmethod
    def populate_assignments():
        from interface.models import Assignment
        now = datetime.datetime.now(datetime.timezone.utc)

        for assignment in Assignment.objects.all():
            if (assignment.deadline_soft - now).total_seconds() > 0:
                print(assignment.deadline_soft)
                SubmissionManager._trigger_prio_assignment(assignment)

    @staticmethod
    def add_submission(sub):
        queue = None

        with SubmissionManager.prio_dict_lock():

            if sub.assignment in SubmissionManager.prio_dict:
                # If it is a submission that should be prioritized
                queue = SubmissionManager.prio_dict[sub.assignment]

        if queue is None:
            # It is a submission that does not have the deadline today
            queue = SubmissionManager.general_queue

        if queue is None:
            log.error("Queue to place a submission is None!")
            return

        queue.add_sub(sub)

    @staticmethod
    def show():
        print("Deadlines assignments")
        print(SubmissionManager.prio_dict)

        print("General assignments")
        print(SubmissionManager.general_queue)

        for assignment, q in SubmissionManager.prio_dict.items():
            print(assignment)
            print(f"\tSubmissions to send: {q}")
