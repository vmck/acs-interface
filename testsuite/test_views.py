import pytest

from django.conf import settings

from interface.models import User, Submission


def test_login(client, STC):
    response = client.get('/')

    STC.assertTemplateUsed(response, 'interface/login.html')
    assert response.context['form']


@pytest.mark.django_db
def test_upload(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    response = client.get(f'/assignment/{course.pk}/{assignment.pk}/upload/')

    STC.assertTemplateUsed(response, 'interface/upload.html')
    assert response.context['form']


@pytest.mark.django_db
def test_homepage(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    response = client.get(f'/homepage/')

    STC.assertTemplateUsed(response, 'interface/homepage.html')
    assert response.context['courses']
    assert len(response.context['courses']) == 1
    assert response.context['courses'][0] == course
    STC.assertContains(response, course.name)
    STC.assertContains(response, assignment.name)


@pytest.mark.django_db
def test_submission_list(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    for _ in range(30):
        assignment.submission_set.create(
            user=user,
            score=100.00,
            state=Submission.STATE_DONE,
        )

    response = client.get('/submission/')

    STC.assertTemplateUsed(response, 'interface/submission_list.html')
    assert response.context['subs']
    assert len(response.context['subs']) == settings.SUBMISSIONS_PER_PAGE


@pytest.mark.django_db
def test_submission_result_done(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    submission = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_DONE,
        stdout='We are done!',
    )

    response = client.get(f'/submission/{submission.pk}/')
    STC.assertTemplateUsed(response, 'interface/submission_result.html')
    STC.assertContains(response, 'We are done!')
    assert response.context['sub'] == submission


@pytest.mark.django_db
def test_submission_result_new(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    submission = assignment.submission_set.create(
        user=user,
        score=100.00,
        state=Submission.STATE_NEW,
        stdout='We are done!',
    )

    response = client.get(f'/submission/{submission.pk}/')
    STC.assertTemplateUsed(response, 'interface/submission_result.html')
    STC.assertNotContains(response, submission.stdout)


@pytest.mark.django_db
def test_user_list(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

    other = User.objects.create_user('other', password='pw')

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

    response = client.get(f'/assignment/{course.pk}/{assignment.pk}')
    STC.assertTemplateUsed(response, 'interface/users_list.html')
    STC.assertContains(response, user.username)
    STC.assertContains(response, other.username)
    assert submission1 in response.context['submissions']
    assert submission2 not in response.context['submissions']
    assert submission3 in response.context['submissions']
    assert response.context['assignment'] == assignment


@pytest.mark.django_db
def test_subs_for_user(client, STC, base_db_setup):
    (_, _, user, course, assignment) = base_db_setup
    client.login(username=user.username, password='pw')

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
        f'/assignment/{course.pk}/{assignment.pk}/user/{user.username}',
    )
    STC.assertTemplateUsed(response, 'interface/subs_for_user.html')
    STC.assertContains(response, user.username)
    assert submission1 in response.context['submissions']
    assert submission2 in response.context['submissions']
    assert response.context['assignment'] == assignment
