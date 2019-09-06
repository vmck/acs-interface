from django.db import models

import interface.backend.minio_api as storage


class Submission(models.Model):
    ''' Model for a homework submission

    Attributes:
    username -- the user id provided by the LDAP
    assignment_id -- class specific, will have the form
                     `{course_name}_{homework_id}` for example pc_00
    _url -- signed url to download the homework archive along with the
            correctly rendered `Vagrantfile` from the blob storage
    message -- the output message of the checker
    score -- the score of the submission given by the checker
    review_score - score set by the assignment reviwer
    max_score -- the maximum score for the submission
    archive_size -- archive, sent to server, size in KB
    '''

    username = models.CharField(max_length=64, default='none')
    assignment_id = models.CharField(max_length=64, default='none')
    _url = models.CharField(max_length=256, default='none')
    message = models.CharField(max_length=4096, default='none')

    score = models.IntegerField(null=True)
    review_score = models.IntegerField(null=True)
    max_score = models.IntegerField(null=True)
    archive_size = models.IntegerField(null=True)

    @property
    def url(self):
        if self._url == 'none':
            self._url = storage.get_link(f'{self.id}.zip')
            self.save()

        return self._url

    def __str__(self):
        return f"{self.id}"
