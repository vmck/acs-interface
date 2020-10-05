import pytest

from django.conf import settings

from interface.models import User, Submission
from interface.backend.submission.submission_scheduler import (
    SubmissionScheduler,
)

@pytest.mark.django_db
def test_submission_update_state_new_get_state_error(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user = user,
        evaluator_job_id=9999,
        assignment = assignment,
        state = Submission.STATE_NEW
    )

    Submission.update_state(submission)
    STC.assertEqual(submission.state, Submission.STATE_ERROR)

@pytest.mark.django_db
def test_submission_update_state_new_get_state_running(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user = user,
        score=100.00,
        assignment = assignment,
        state = Submission.STATE_NEW
    )

    submission.evaluator_job_id=SubmissionScheduler.evaluator.evaluate(submission)

    Submission.update_state(submission)
    STC.assertEqual(submission.state, Submission.STATE_RUNNING)

@pytest.mark.django_db
def test_submission_update_state_error_keep_error(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user = user,
        evaluator_job_id=9999,
        assignment = assignment,
        state = Submission.STATE_ERROR
    )

    Submission.update_state(submission)
    STC.assertEqual(submission.state, Submission.STATE_ERROR)

@pytest.mark.django_db
def test_submission_update_state_done_keep_done(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user = user,
        assignment = assignment,
        state = Submission.STATE_DONE
    )

    Submission.update_state(submission)
    STC.assertEqual(submission.state, Submission.STATE_DONE)