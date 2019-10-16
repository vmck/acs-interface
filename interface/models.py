import logging
import requests
from collections import OrderedDict
from urllib.parse import urljoin

import jwt
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

import interface.backend.minio_api as storage
from interface.utils import vmck_config, get_script_url, get_artifact_url


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


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
    deadline = models.DateTimeField(null=True)

    repo_url = models.CharField(max_length=256, blank=True)
    repo_branch = models.CharField(max_length=256, blank=True)

    @property
    def full_code(self):
        return f'{self.course.code}-{self.code}'

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
    output = models.CharField(max_length=32768, default='none')
    review_message = models.CharField(max_length=4096, default='none')
    state = models.CharField(max_length=32,
                             choices=list(STATE_CHOICES.items()),
                             default=STATE_NEW)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    review_score = models.DecimalField(max_digits=5,
                                       decimal_places=2,
                                       null=True)
    total_score = models.DecimalField(max_digits=5,
                                      decimal_places=2,
                                      null=True)
    score = models.IntegerField(null=True)
    archive_size = models.IntegerField(null=True)
    vmck_job_id = models.IntegerField(null=True)

    def calculate_total_score(self):
        score = self.score if self.score else 0
        review_score = self.review_score if self.review_score else 0

        return score + review_score

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

    def get_url(self):
        return storage.get_link(f'{self.id}.zip')

    def evaluate(self):
        callback = (f"submission/{self.id}/done?"
                    f"token={str(self.generate_jwt(), encoding='latin1')}")

        options = vmck_config(self)
        options['name'] = f'{self.assignment.full_code} submission #{self.id}'
        options['manager'] = True
        options['env'] = {}
        options['env']['archive'] = self.get_url()
        options['env']['vagrant_tag'] = settings.MANAGER_TAG
        options['env']['script'] = get_script_url(self)
        options['env']['artifact'] = get_artifact_url(self)
        options['env']['memory'] = settings.MANAGER_MEMORY
        options['env']['cpu_mhz'] = settings.MANAGER_MHZ
        options['env']['callback'] = urljoin(
            settings.ACS_INTERFACE_ADDRESS,
            callback,
        )
        options['restrict_network'] = True
        log.debug(f'Submission #{self.id} config is done')
        log.debug(f"Callback: {options['env']['callback']}")

        response = requests.post(urljoin(settings.VMCK_API_URL, 'jobs'),
                                 json=options)

        log.debug(f"Submission's #{self.id} VMCK response:\n{response}")

        self.vmck_job_id = response.json()['id']
        self.save()

    def generate_jwt(self):
        """Generates a JWT token that the checker will use
        when it calls back with the result
        """
        return jwt.encode({'data': str(self.id)},
                          settings.SECRET_KEY,
                          algorithm='HS256')

    def verify_jwt(self, message):
        """Verify that the token was generated by us
        so we can trust the checker result
        """
        if not message:
            return False

        decoded_message = jwt.decode(message,
                                     settings.SECRET_KEY,
                                     algorithms=['HS256'])

        return decoded_message['data'] == str(self.id)
