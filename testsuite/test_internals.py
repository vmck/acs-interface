import pytest

from django.conf import settings

from interface.models import User, Submission

@pytest.mark.django_db
def test_submission_update_state_error(client, STC, base_db_setup):
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