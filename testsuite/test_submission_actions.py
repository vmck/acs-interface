from datetime import datetime, timezone

import pytest

from interface.models import ActionLog, Submission

pytestmark = [pytest.mark.django_db()]


def create_submission(assignment):
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission.timestamp = datetime(2000, 1, 2, tzinfo=timezone.utc)
    submission.save()

    return submission


def test_review(client, base_db_setup):
    (_, ta, _, course, assignment) = base_db_setup

    client.login(username=ta.username, password="pw")

    submission = create_submission(assignment)

    review_message = "+10.0: Good Job\n-5.0: Bad style\n+0.5:Good Readme"
    client.post(
        f"/submission/{submission.pk}/review",
        data={"review-code": review_message},
    )

    submission.refresh_from_db()

    assert len(submission.review_message) > 0
    assert submission.review_score == 5.5
    assert submission.total_score == 105.5

    assert ActionLog.objects.all().count() == 1
    assert ActionLog.objects.all()[0].content_object == submission
    assert ActionLog.objects.all()[0].action == "Review submission"


def test_recompute(client, base_db_setup):
    (_, ta, _, course, assignment) = base_db_setup

    client.login(username=ta.username, password="pw")

    submission = create_submission(assignment)

    assignment.deadline_soft = datetime(2000, 1, 1, tzinfo=timezone.utc)
    assignment.deadline_hard = datetime(2000, 1, 5, tzinfo=timezone.utc)
    assignment.save()

    client.post(f"/submission/{submission.pk}/recompute")

    submission.refresh_from_db()

    assert submission.total_score == 99
    assert submission.penalty == 1

    assert ActionLog.objects.all().count() == 1
    assert ActionLog.objects.all()[0].content_object == submission
    assert ActionLog.objects.all()[0].action == "Recompute submission's score"
