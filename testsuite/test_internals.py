import pytest

from interface.models import Submission


@pytest.mark.django_db()
def test_submission_update_state_new_get_state_error(
    client,
    stc,
    base_db_setup,
):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user=user,
        evaluator_job_id=9999,
        assignment=assignment,
        state=Submission.STATE_NEW,
    )

    Submission.update_state(submission)
    stc.assertEqual(submission.state, Submission.STATE_ERROR)


@pytest.mark.django_db()
def test_submission_update_state_error_keep_error(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user=user,
        evaluator_job_id=9999,
        assignment=assignment,
        state=Submission.STATE_ERROR,
    )

    Submission.update_state(submission)
    stc.assertEqual(submission.state, Submission.STATE_ERROR)


@pytest.mark.django_db()
def test_submission_update_state_done_keep_done(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = Submission.objects.create(
        user=user,
        assignment=assignment,
        state=Submission.STATE_DONE,
    )

    Submission.update_state(submission)
    stc.assertEqual(submission.state, Submission.STATE_DONE)
