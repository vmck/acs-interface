import pytest
import json

from django.conf import settings

from interface.models import User, Submission
from interface import utils


def test_login(client, stc):
    response = client.get("/")

    stc.assertTemplateUsed(response, "interface/login.html")
    assert response.context["form"]


@pytest.mark.django_db()
def test_upload(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    response = client.get(f"/assignment/{course.pk}/{assignment.pk}/upload/")

    stc.assertTemplateUsed(response, "interface/upload.html")
    assert response.context["form"]


@pytest.mark.django_db()
def test_homepage(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    response = client.get(f"/homepage/?course={course.id}")

    stc.assertTemplateUsed(response, "interface/homepage.html")
    assert response.context["courses"]
    assert len(response.context["courses"]) == 1
    assert response.context["courses"][0] == course
    stc.assertContains(response, course.name)
    stc.assertContains(response, assignment.name)


@pytest.mark.django_db()
def test_submission_list(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    for _ in range(30):
        assignment.submission_set.create(
            user=user,
            score=100.00,
            state=Submission.STATE_DONE,
        )

    response = client.get("/submission/")

    stc.assertTemplateUsed(response, "interface/submission_list.html")
    assert response.context["submissions"]
    assert (
        len(response.context["submissions"]) == settings.SUBMISSIONS_PER_PAGE
    )


@pytest.mark.django_db()
def test_submission_result_done(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
        stdout="We are done!",
    )

    response = client.get(f"/submission/{submission.pk}/")
    stc.assertTemplateUsed(response, "interface/submission_result.html")
    stc.assertContains(response, "We are done!")
    assert response.context["sub"] == submission


@pytest.mark.django_db()
def test_submission_done_submit(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = assignment.submission_set.create(
        user=user,
        state=Submission.STATE_RUNNING,
        stdout="Runnning",
    )
    token = str(submission.generate_jwt(), encoding="latin1")

    response = client.post(
        f"/submission/{submission.pk}/done?token={token}",
        json.dumps({"stdout": utils.encode("TOTAL: 100/100"), "exit_code": 1}),
        content_type="application/json",
    )
    assert response.status_code == 200

    submission.refresh_from_db()
    assert submission.score == 100


@pytest.mark.django_db()
def test_submission_done_submit_wrong_token(client, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = assignment.submission_set.create(
        user=user,
        score=0,
        state=Submission.STATE_RUNNING,
        stdout="Runnning",
    )
    token = "yabayaba"

    response = client.post(
        f"/submission/{submission.pk}/done?token={token}",
        json.dumps({"stdout": utils.encode("TOTAL: 100/100"), "exit_code": 1}),
        content_type="application/json",
    )
    assert response.status_code == 400

    submission.refresh_from_db()
    assert submission.score == 0


@pytest.mark.django_db()
def test_submission_result_new(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_NEW,
        stdout="We are done!",
    )

    response = client.get(f"/submission/{submission.pk}/")
    stc.assertTemplateUsed(response, "interface/submission_result.html")
    stc.assertNotContains(response, submission.stdout)


@pytest.mark.django_db()
def test_user_list(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    other = User.objects.create_user("other", password="pw")

    submission1 = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission2 = assignment.submission_set.create(
        user=other,
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission3 = assignment.submission_set.create(
        user=other,
        score=100.00,
        state=Submission.STATE_DONE,
    )

    response = client.get(f"/assignment/{course.pk}/{assignment.pk}")
    stc.assertTemplateUsed(response, "interface/users_list.html")
    stc.assertContains(response, user.username)
    stc.assertContains(response, other.username)
    assert submission1 in response.context["submissions"]
    assert submission2 not in response.context["submissions"]
    assert submission3 in response.context["submissions"]
    assert response.context["assignment"] == assignment


@pytest.mark.django_db()
def test_subs_for_user(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    submission1 = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission2 = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
    )

    response = client.get(
        f"/assignment/{course.pk}/{assignment.pk}/user/{user.username}",
    )
    stc.assertTemplateUsed(response, "interface/subs_for_user.html")
    stc.assertContains(response, user.username)
    assert submission1 in response.context["submissions"]
    assert submission2 in response.context["submissions"]
    assert response.context["assignment"] == assignment


@pytest.mark.django_db()
def test_user_page(client, stc, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password="pw")

    other = User.objects.create_user("other", password="pw")

    submission1 = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission2 = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
    )
    submission3 = assignment.submission_set.create(
        user=other,
        score=100.00,
        state=Submission.STATE_DONE,
    )

    response = client.get(
        f"/mysubmissions/{user.username}",
    )

    stc.assertTemplateUsed(response, "interface/user_page.html")
    stc.assertContains(response, assignment.name)
    stc.assertContains(response, course.name)
    assert submission1 in response.context["submissions"]
    assert submission2 in response.context["submissions"]
    assert submission3 not in response.context["submissions"]
