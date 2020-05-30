from datetime import datetime, timezone

import pytest
from django.test import SimpleTestCase
from django.contrib.auth.models import User

from interface.models import Course, Submission


@pytest.fixture
def base_db_setup():
    user = User.objects.create_user('user', password='pw')

    ta = User.objects.create_user('ta', password='pw', is_staff=True)

    super_user = User.objects.create_user(
        'root',
        password='pw',
        is_superuser=True,
        is_staff=True,
    )

    course = Course.objects.create(name='PC')
    course.teaching_assistants.set([ta])
    course.save()

    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    return (super_user, ta, user, course, assignment)


@pytest.fixture
def STC():
    return SimpleTestCase()
