from datetime import datetime, timezone

import pytest
from django.contrib.auth.models import User

from interface.models import Course


@pytest.fixture
def base_db_setup():
    user = User.objects.create_user('user', password='pw', is_staff=True)

    course = Course.objects.create(name='PC')

    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    return (user, course, assignment)
