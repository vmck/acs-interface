from django.db import models


class Submission(models.Model):
    username = models.CharField(max_length=64, default='none')
    assignment_id = models.CharField(max_length=64, default='none')
    url = models.CharField(max_length=256, default='none')
    token = models.CharField(max_length=128, default='none')
    score = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.id}"
