from datetime import datetime, timezone

import pytest
from django.contrib.auth.models import User

from interface.models import Course, Submission, ActionLog


@pytest.mark.django_db
def test_submission(client, live_server):
    user = User.objects.create_user('user', password='pw', is_staff=True)
    client.login(username='user', password='pw')

    pc = Course.objects.create(name='PC', code='pc')
    pc.teaching_assistants.add(user)

    assignment = pc.assignment_set.create(
        code='a0',
        name='a0',
        max_score=100,
        deadline_soft=datetime(2000, 1, 2, tzinfo=timezone.utc),
        deadline_hard=datetime(2000, 1, 5, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission.timestamp = datetime(2000, 1, 2, tzinfo=timezone.utc)
    submission.save()

    review_message = '+10.0: Good Job\n-5.0: Bad style\n+0.5:Good Readme'
    client.post(
        '/submission/1/review',
        data={'review-code': review_message},
        HTTP_REFERER='/',
    )

    submission.refresh_from_db()

    assert len(submission.review_message) > 0
    assert submission.review_score == 5.5
    assert submission.total_score == 105.5

    assignment.deadline_soft = datetime(2000, 1, 1, tzinfo=timezone.utc)
    assignment.save()

    client.post('/submission/1/recompute', HTTP_REFERER='/')

    submission.refresh_from_db()

    assert submission.total_score == 104.5
    assert submission.penalty == 1

    assert len(ActionLog.objects.all()) == 2
    assert ActionLog.objects.all()[0].content_object == submission
    assert ActionLog.objects.all()[0].action == 'Review submission'
