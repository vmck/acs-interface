from django.db import models


class Submission(models.Model):
    ''' Model for a homework submission

    Attributes:
    username -- the user id provided by the LDAP
    assignment_id -- class specific, will have the form
                     `{course_name}_{homework_id}` for example pc_00
    url -- signed url to download the homework archive along with the
           correctly rendered `Vagrantfile` from the blob storage
    message -- the output message of the checker
    score -- the score of the submission given by the checker
    max_score -- the maximum score for the submission
    '''

    username = models.CharField(max_length=64, default='none')
    assignment_id = models.CharField(max_length=64, default='none')
    url = models.CharField(max_length=256, default='none')
    message = models.CharField(max_length=4096, default='none')

    score = models.IntegerField(default=-1)
    max_score = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.id}"
