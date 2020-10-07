import re
import logging
import datetime
from collections import OrderedDict
from urllib.parse import urljoin

import jwt
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from simple_history.models import HistoricalRecords

import interface.backend.minio_api as storage
from interface import signals
from interface.backend.submission.submission_scheduler import (
    SubmissionScheduler,
)

log = logging.getLogger(__name__)


class ActionLog(models.Model):
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    action = models.CharField(max_length=256)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class Course(models.Model):
    name = models.CharField(max_length=256, blank=False)
    teaching_assistants = models.ManyToManyField(User, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name}"


class Assignment(models.Model):
    LANG_C = "c"
    LANG_PYTHON = "py"
    LANG_JAVA = "java"

    # This is a maping from file format to what moss expects
    # as input when choosing a language
    LANG_CHOICES = OrderedDict(
        [(LANG_C, "c"), (LANG_PYTHON, "python"), (LANG_JAVA, "java")]
    )

    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=256, blank=False)
    max_score = models.IntegerField(default=100)
    deadline_soft = models.DateTimeField()
    deadline_hard = models.DateTimeField()
    min_time_between_uploads = models.IntegerField(default=60)
    repo_url = models.CharField(max_length=256, blank=True)
    repo_branch = models.CharField(max_length=256, blank=True)
    repo_path = models.CharField(max_length=256, blank=True)
    language = models.CharField(
        max_length=32, choices=list(LANG_CHOICES.items()), default=LANG_C,
    )
    image_path = models.CharField(max_length=256, blank=False)

    def get_default_penalty_info():
        return {
            "penalty_weights": [],
            "holiday_start": "0001-01-01 00:00:00",
            "holday_finish": "0001-01-01 00:00:00",
        }

    def get_default_vm_info():
        return {"nr_cpus": 1, "memory": 512}

    penalty_info = models.JSONField(default=get_default_penalty_info)
    vm_options = models.JSONField(default=get_default_vm_info)

    history = HistoricalRecords()
    hidden_score = models.BooleanField(default=True)

    def clean(self):
        penalty_weights = self.penalty_info["penalty_weights"]
        if not isinstance(penalty_weights, list) or not all(
            isinstance(x, (float, int)) for x in penalty_weights
        ):
            raise ValidationError(
                "Penalty weights should be a list of integer/floats"
            )

        if (
            len(penalty_weights)
            != (self.deadline_hard - self.deadline_soft).days
        ):
            raise ValidationError(
                "Number of penalty weights should be == days from soft "
                "to hard deadline"
            )

    @property
    def full_code(self):
        return f"{self.course.pk}-{self.pk}"

    @property
    def is_active(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = self.deadline_hard - now

        return diff.total_seconds() > 0

    def __str__(self):
        return f"{self.full_code} {self.name}"

    def url_for(self, filename):
        m = re.match(
            r"https://github.com/(?P<org>[^/]+)/(?P<repo>[^/]+)/?$",
            self.repo_url,
        )
        url_base = "https://raw.githubusercontent.com/" "{0}/{1}/".format(
            *list(m.groups())
        )
        branch = self.repo_branch or "master"
        path = f"{self.repo_path}/" if self.repo_path else ""
        return urljoin(url_base, f"{branch}/{path}{filename}")


class Submission(models.Model):
    """ Model for a homework submission

    Attributes:
    username -- the user id provided by the LDAP
    assignment_id -- class specific, will have the form
                     `{course_name}_{homework_id}` for example pc_00
    stdout -- the output message of the checker
    stderr -- the error message of the checker
    score -- the score of the submission given by the checker
    review_score -- score set by the assignment reviewer
    total_score -- score + review_score
    max_score -- the maximum score for the submission
    archive_size -- archive, sent to server, size in KB
    """

    STATE_NEW = "new"
    STATE_RUNNING = "running"
    STATE_DONE = "done"
    STATE_QUEUED = "queued"

    STATE_CHOICES = OrderedDict(
        [
            (STATE_NEW, "New"),
            (STATE_RUNNING, "Running"),
            (STATE_DONE, "Done"),
            (STATE_QUEUED, "Queue"),
        ]
    )

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, null=True
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    stdout = models.TextField(max_length=32768, default="", blank=True)
    stderr = models.TextField(max_length=32768, default="", blank=True)
    review_message = models.TextField(max_length=4096, default="", blank=True)
    state = models.CharField(
        max_length=32, choices=list(STATE_CHOICES.items()), default=STATE_NEW
    )
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    review_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True
    )
    total_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    penalty = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    archive_size = models.IntegerField(null=True)
    evaluator_job_id = models.IntegerField(null=True)

    history = HistoricalRecords()

    def update_state(self):
        if self.state == self.STATE_DONE or self.evaluator_job_id is None:
            return

        state = SubmissionScheduler.evaluator.update(self)
        if state != self.state:
            self.state = state

            if state == Submission.STATE_DONE:
                SubmissionScheduler.get_instance().done_evaluation()

            self.changeReason = f"Update state to {state}"
            self.save()

    def download(self, buff):
        storage.download_buffer(f"{self.pk}.zip", buff)

    def get_script_url(self):
        return self.assignment.url_for("checker.sh")

    def get_artifact_url(self):
        return self.assignment.url_for("artifact.zip")

    def __str__(self):
        return f"#{self.pk} by {self.user}"

    @property
    def state_label(self):
        return self.STATE_CHOICES[self.state]

    def get_url(self):
        return storage.get_link(f"{self.pk}.zip")

    def evaluate(self):
        SubmissionScheduler.get_instance().add_submission(self)

    def generate_jwt(self):
        """Generates a JWT token that the checker will use
        when it calls back with the result
        """
        return jwt.encode(
            {"data": str(self.pk)}, settings.SECRET_KEY, algorithm="HS256"
        )

    def verify_jwt(self, message):
        """Verify that the token was generated by us
        so we can trust the checker result
        """
        if not message:
            return False

        decoded_message = jwt.decode(
            message, settings.SECRET_KEY, algorithms=["HS256"]
        )

        return decoded_message["data"] == str(self.id)


pre_save.connect(signals.update_total_score, sender=Submission)
