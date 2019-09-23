import requests
from collections import OrderedDict
from urllib.parse import urljoin

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

import interface.backend.minio_api as storage


class Course(models.Model):
    name = models.CharField(max_length=256, blank=True)
    code = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"{self.name}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    code = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=256, blank=True)
    max_score = models.IntegerField(default=100)

    repo_url = models.CharField(max_length=256, blank=True)
    repo_branch = models.CharField(max_length=256, blank=True)

    @property
    def full_code(self):
        return f'{self.course.code}-{self.code}'

    @property
    def submission_set(self):
        return Submission.objects.filter(assignment=self)

    def __str__(self):
        return f"{self.full_code} {self.name}"


class Submission(models.Model):
    ''' Model for a homework submission

    Attributes:
    username -- the user id provided by the LDAP
    assignment_id -- class specific, will have the form
                     `{course_name}_{homework_id}` for example pc_00
    message -- the output message of the checker
    score -- the score of the submission given by the checker
    review_score - score set by the assignment reviwer
    max_score -- the maximum score for the submission
    archive_size -- archive, sent to server, size in KB
    '''

    STATE_NEW = 'new'
    STATE_RUNNING = 'running'
    STATE_DONE = 'done'

    STATE_CHOICES = OrderedDict([
        (STATE_NEW, 'New'),
        (STATE_RUNNING, 'Running'),
        (STATE_DONE, 'Done'),
    ])

    assignment = models.ForeignKey(Assignment,
                                   on_delete=models.PROTECT,
                                   null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    output = models.CharField(max_length=4096, default='none')
    state = models.CharField(max_length=32,
                             choices=list(STATE_CHOICES.items()),
                             default=STATE_NEW)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    score = models.IntegerField(null=True)
    review_score = models.IntegerField(null=True)
    archive_size = models.IntegerField(null=True)
    vmck_job_id = models.IntegerField(null=True)

    def get_url(self):
        return storage.get_link(f'{self.id}.zip')

    def update_state(self):
        if self.state != self.STATE_DONE and self.vmck_job_id is not None:
            response = requests.get(urljoin(settings.VMCK_API_URL,
                                            f'jobs/{self.vmck_job_id}'))

            self.state = response.json()['state']
            self.save()

    def download(self, path):
        storage.download(f'{self.id}.zip', path)

    def __str__(self):
        return f"{self.assignment} {self.id}"

    @property
    def state_label(self):
        return self.STATE_CHOICES[self.state]
