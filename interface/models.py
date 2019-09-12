from django.db import models
from urllib.parse import urljoin
from django.conf import settings

import interface.backend.minio_api as storage
import requests


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

    STATE_CHOICES = [
        (STATE_NEW, 'New'),
        (STATE_RUNNING, 'Running'),
        (STATE_DONE, 'Done'),
    ]

    username = models.CharField(max_length=64, default='none')
    assignment_id = models.CharField(max_length=64, default='none')
    message = models.CharField(max_length=4096, default='none')
    state = models.CharField(max_length=32,
                             choices=STATE_CHOICES,
                             default=STATE_NEW)

    score = models.IntegerField(null=True)
    review_score = models.IntegerField(null=True)
    max_score = models.IntegerField(null=True)
    archive_size = models.IntegerField(null=True)
    vmck_id = models.IntegerField(null=True)

    def get_url(self):
        return storage.get_link(f'{self.id}.zip')

    def update_state(self):
        if self.state is not self.STATE_DONE and self.vmck_id is not None:
            response = requests.get(urljoin(settings.VMCK_API_URL,
                                            f'jobs/{self.vmck_id}'))

            self.state = response.json()['state']
            self.save()

    def download(self, path):
        storage.download(f'{self.id}.zip', path)

    def __str__(self):
        return f"{self.id}"


class Assignment(models.Model):
    url = models.CharField(max_length=256, default='none')
    branch = models.CharField(max_length=64, default='none')
    name = models.CharField(max_length=256, default='none')
    assignment_id = models.CharField(max_length=64, default='none')


class Class(models.Model):
    name = models.CharField(max_length=256, default='none')
