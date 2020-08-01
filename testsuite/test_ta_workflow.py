import pytest
from datetime import datetime, timezone
from django.contrib.admin.sites import AdminSite

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from interface.models import Course, Submission
from interface.admin import CourseAdmin


FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'


class MockObject(object):
    pass


@pytest.mark.django_db
def test_ta_add_new_ta(client, STC, base_db_setup):
    '''
        Create one teaching assistant, 5 courses and 3 assignments for
        each course.

        The TA is added to courses 1, 3, 5 and should see only those
        assignments
    '''
    (super_user, ta, user, course, _) = base_db_setup

    client.login(username=user.username, password='pw')
    response = client.get('/admin/')
    STC.assertRedirects(response, '/admin/login/?next=/admin/')

    request = MockObject()
    request.user = super_user

    form = MockObject()
    form.changed_data = ["teaching_assistants"]
    form.cleaned_data = {"teaching_assistants": [user, ta]}

    test_course_admin = CourseAdmin(model=Course, admin_site=AdminSite())
    test_course_admin.save_model(
        obj=course,
        request=request,
        form=form,
        change=True,
    )

    course.teaching_assistants.add(user)
    course.save()

    # Now you should be able to access it
    response = client.get('/admin/')
    assert response.status_code == 200

    response = client.get('/admin/interface/assignment/')
    # There is only one assignment added in the conftest for a course
    assert len(response.context['results']) == 1


@pytest.mark.django_db
def test_ta_view_assignment(client, base_db_setup):
    '''
        Test if the teaching assistant can view the already existing assignment
    '''
    (_, ta, _, _, _) = base_db_setup
    client.login(username=ta.username, password='pw')
    response = client.get('/admin/')
    assert response.status_code == 200

    response = client.get('/admin/interface/assignment/')
    # There is only one assignment added in the conftest for a course
    assert len(response.context['results']) == 1


@pytest.mark.django_db
def test_ta_cannot_view_assignment(STC, client, base_db_setup):
    '''
        Test if users can not view an assignment where they are not
        a teaching assistant
    '''

    (_, ta, _, _, _) = base_db_setup
    course = Course.objects.create(name='PC')
    course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    client.login(username=ta.username, password='pw')

    response = client.get('/admin/')
    assert response.status_code == 200

    response = client.get('/admin/interface/assignment/')
    # There is only one assignment added in the conftest for a course
    assert len(response.context['results']) == 1


@pytest.mark.django_db
def test_ta_view_submissions(client, base_db_setup):
    '''
        Test if the teaching assistant can view already existing submissions
    '''
    expected_submissions = 5
    (_, ta, user, _, assignment) = base_db_setup

    for _ in range(expected_submissions):
        assignment.submission_set.create(
            score=100.00,
            state=Submission.STATE_DONE,
            user=user,
        )

    client.login(username=ta.username, password='pw')

    response = client.get('/admin/interface/submission/')
    assert response.status_code == 200
    assert len(response.context['results']) == expected_submissions


@pytest.mark.django_db
def test_ta_cannot_view_submissions(client, base_db_setup):
    '''
        Test if the users can not views submissions from the courses
        where they are not teaching assistants
    '''
    (_, ta, user, _, _) = base_db_setup

    course = Course.objects.create(name='PP')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')

    response = client.get('/admin/interface/submission/')

    assert response.status_code == 200
    assert len(response.context['results']) == 0


@pytest.mark.django_db
def test_ta_add_new_assignment(STC, client, base_db_setup):
    '''
        Test if the teaching assistant can view new added assignments
    '''

    (_, ta, _, course, _) = base_db_setup
    client.login(username=ta.username, password='pw')

    date = datetime(2050, 1, 1, tzinfo=timezone.utc)
    assignment_params = {
        'course': course.pk,
        'name': 'a_new',
        'max_score': 100,
        'deadline_soft_0': date.date(),
        'deadline_soft_1': date.time(),
        'deadline_hard_0': date.date(),
        'deadline_hard_1': date.time(),
        'min_time_between_uploads': 30,
        'language': 'c',
        'value': 'Save',
    }
    response = client.post(
        f'/admin/interface/assignment/add/',
        data=assignment_params,
    )

    STC.assertRedirects(
        response,
        '/admin/interface/assignment/',
    )

    response = client.get('/admin/interface/assignment/')
    assert len(response.context['results']) == 2


@pytest.mark.django_db
def test_ta_cannot_add_new_assignment(STC, client, base_db_setup):
    '''
        Test if the users can not add new assignment at the courses they are
        not teaching assistants
    '''

    (_, ta, _, _, _) = base_db_setup
    course = Course.objects.create(name='PP')
    course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    client.login(username=ta.username, password='pw')

    date = datetime(2050, 1, 1, tzinfo=timezone.utc)
    assignment_params = {
        'course': course.pk,
        'name': 'a_new',
        'max_score': 100,
        'deadline_soft_0': date.date(),
        'deadline_soft_1': date.time(),
        'deadline_hard_0': date.date(),
        'deadline_hard_1': date.time(),
        'min_time_between_uploads': 30,
        'language': 'c',
        'value': 'Save',
    }
    response = client.post(
        f'/admin/interface/assignment/add/',
        data=assignment_params,
    )

    errors = response.context['errors']
    assert len(errors) == 1

    msg_error = errors[0][0]
    expected_error = (
        'Select a valid choice. That choice is not '
        'one of the available choices.'
    )
    assert msg_error == expected_error


@pytest.mark.django_db
def test_ta_edit_assignment(STC, client, base_db_setup):
    '''
        Test if the teaching assistant can edit an assignment
    '''

    (_, ta, _, course, assignment) = base_db_setup
    client.login(username=ta.username, password='pw')

    # Change name and max_score deadline
    assignment_change_params = {
        'course': assignment.course.pk,
        "name": "a_change",
        'max_score': 50,
        "deadline_soft_0": assignment.deadline_soft.date(),
        'deadline_soft_1': assignment.deadline_hard.time(),
        'deadline_hard_0': assignment.deadline_hard.date(),
        'deadline_hard_1': assignment.deadline_hard.time(),
        'min_time_between_uploads': assignment.min_time_between_uploads,
        'language': assignment.language,
        'value': 'Save',

    }

    response = client.post(
        f'/admin/interface/assignment/{assignment.pk}/change/',
        data=assignment_change_params,
    )

    STC.assertRedirects(
        response,
        '/admin/interface/assignment/',
    )

    response = client.get('/admin/interface/assignment/')
    assert len(response.context['results']) == 1
    new_assignment = course.assignment_set.all()[0]

    assert new_assignment.name == "a_change"
    assert new_assignment.max_score == 50

    new_assignment.name = assignment.name
    new_assignment.max_score = assignment.max_score
    assert new_assignment == assignment


@pytest.mark.django_db
def test_ta_cannot_edit_assignment(STC, client, base_db_setup):
    '''
        Test if users can not edit an assignment where they are not
        a teaching assistant
    '''

    (_, ta, _, _, _) = base_db_setup
    course = Course.objects.create(name='PP')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    client.login(username=ta.username, password='pw')

    # Change name and max_score deadline
    assignment_change_params = {
        'course': assignment.course.pk,
        "name": "a_change",
        'max_score': 50,
        "deadline_soft_0": assignment.deadline_soft.date(),
        'deadline_soft_1': assignment.deadline_hard.time(),
        'deadline_hard_0': assignment.deadline_hard.date(),
        'deadline_hard_1': assignment.deadline_hard.time(),
        'min_time_between_uploads': assignment.min_time_between_uploads,
        'language': assignment.language,
        'value': 'Save'

    }

    response = client.post(
        f'/admin/interface/assignment/{assignment.pk}/change/',
        data=assignment_change_params,
        follow=True,
    )

    message_list = list(response.context['messages'])
    assert len(message_list) == 1

    message = message_list[0].message

    # Carefull at the quoation marks
    expected_prefix = (
        f'''assignment with ID “{assignment.pk}” doesn’t exist.'''
    )
    assert message.startswith(expected_prefix)


@pytest.mark.django_db
def test_ta_remove_assignment(client, STC, base_db_setup):
    '''
        Test if the teaching assistant can remove an assignment
    '''

    (_, ta, _, _, assignment) = base_db_setup
    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/admin/interface/assignment/{assignment.pk}/delete/',
        data={"post": "yes"}
    )

    STC.assertRedirects(
        response,
        '/admin/interface/assignment/',
    )
    response = client.get('/admin/interface/assignment/')
    assert len(response.context['results']) == 0


@pytest.mark.django_db
def test_ta_cannot_remove_assignment(client, STC, base_db_setup):
    '''
        Test if users can not edit an assignment where they are not
        a teaching assistant
    '''

    (_, ta, _, _, _) = base_db_setup
    client.login(username=ta.username, password='pw')

    course = Course.objects.create(name='PP')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    response = client.post(
        f'/admin/interface/assignment/{assignment.pk}/delete/',
        data={"post": "yes"},
        follow=True,
    )

    message_list = list(response.context['messages'])
    assert len(message_list) == 1

    message = message_list[0].message

    # Carefull at the quoation marks
    expected_prefix = (
        f'''assignment with ID “{assignment.pk}” doesn’t exist.'''
    )
    assert message.startswith(expected_prefix)


@pytest.mark.django_db
def test_ta_check_possible_courses(client, base_db_setup):
    '''
        Check if users can make assignments only for the courses
        where they are teaching assistants
    '''

    course_names = {"PCOM", "PP", "PA", "SO", "LFA"}
    course_names_ta = {"PC", "PCOM", "PA", "SO"}
    courses = []

    (_, ta, _, _, _) = base_db_setup

    for course_name in course_names:
        course = Course.objects.create(name=f'{course_name}')
        courses.append(course)

        if course_name in course_names_ta:
            course_admin = CourseAdmin(model=Course, admin_site=AdminSite())
            course_admin._add_new_ta(ta)
            course.teaching_assistants.set([ta])

    client.login(username=ta.username, password='pw')
    response = client.get('/admin/interface/assignment/add/')
    assert response.status_code == 200

    found_courses = set(map(
        lambda x: x[1][0]['label'],
        response.context['widget']['optgroups'],
    ))

    # Default value
    course_names_ta.add('---------')
    assert found_courses == course_names_ta


@pytest.mark.django_db
def test_ta_download_submission(client, STC, base_db_setup):
    '''
        Test if the teaching assistant can download submission
    '''

    (_, ta, user, _, assignment) = base_db_setup
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')
    response = client.get(f'/submission/{submission.pk}/download')

    assert response.status_code == 200


@pytest.mark.django_db
def test_ta_cannot_download_submission(client, base_db_setup):
    '''
        Test if a teaching assistant can not download submission
        from another course
    '''

    (_, ta, user, _, _) = base_db_setup

    course = Course.objects.create(name='PP')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')
    response = client.get(f'/submission/{submission.pk}/download')

    assert response.status_code == 403


@pytest.mark.django_db
def test_ta_review_submission(client, STC, base_db_setup):
    '''
        Test if the teaching assistant can add review to submission
    '''

    (user, ta, _, _, assignment) = base_db_setup
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')

    # Add review and add some points
    review_message = '+10.0: Babas'
    response = client.post(
        f'/submission/{submission.pk}/review',
        data={'review-code': review_message},
        follow=True,
    )

    STC.assertRedirects(response, '/homepage/')

    all_subs = assignment.submission_set.all()
    assert len(all_subs) == 1

    changed_sub = all_subs[0]
    assert changed_sub.review_score == 10
    assert changed_sub.total_score == 110

    # Add review and substract some points
    review_message = '-20.0: Not nice'
    response = client.post(
        f'/submission/{submission.pk}/review',
        data={'review-code': review_message},
        follow=True,
    )

    STC.assertRedirects(response, '/homepage/')

    all_subs = assignment.submission_set.all()
    assert len(all_subs) == 1

    changed_sub = all_subs[0]
    assert changed_sub.review_score == -20
    assert changed_sub.total_score == 80


@pytest.mark.django_db
def test_ta_cannot_review_submission(client, STC, base_db_setup):
    '''
        Check if users can not review submission from a different
        course where they are not teaching assistants
    '''
    (_, ta, user, _, _) = base_db_setup

    course = Course.objects.create(name='PC')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')

    # Add review and add some points
    review_message = '+10.0: Babas'
    response = client.post(
        f'/submission/{submission.pk}/review',
        data={'review-code': review_message},
        follow=True,
    )

    response.status_code == 403


@pytest.mark.django_db
def test_ta_rerun_submission(STC, client, base_db_setup):
    '''
        Test if a teaching assistant can rerun a submission
    '''
    (_, ta, user, _, assignment) = base_db_setup
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/submission/{submission.pk}/rerun',
        follow=True,
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_ta_cannot_rerun_submission(STC, client, base_db_setup):
    '''
        Check if users can not rerun a submission that is from a
        different course and they are not teaching assistants there
    '''
    (_, ta, user, _, _) = base_db_setup

    course = Course.objects.create(name='PC')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/submission/{submission.pk}/rerun',
        follow=True,
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_ta_recompute_score(STC, client, base_db_setup):
    '''
        Test if a teaching assistant can recompute the score of a
        submission if the checker changed
    '''
    (_, ta, user, _, assignment) = base_db_setup

    client.login(username=ta.username, password='pw')
    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    response = client.post(
        f'/submission/{submission.pk}/recompute',
        follow=True,
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_ta_cannot_recompute_score(STC, client, base_db_setup):
    '''
        Check if users can not recompute score for the submissions
        that are from a course where they are not teaching assistants
    '''

    (_, ta, user, _, _) = base_db_setup

    course = Course.objects.create(name='PC')
    assignment = course.assignment_set.create(
        name='a0',
        max_score=100,
        deadline_soft=datetime(2050, 1, 1, tzinfo=timezone.utc),
        deadline_hard=datetime(2050, 1, 1, tzinfo=timezone.utc),
        repo_url='https://github.com/vmck/assignment',
        repo_path='pc-00',
    )

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
    )

    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/submission/{submission.pk}/recompute',
        follow=True,
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_ta_download_last_sub(client, base_db_setup, mock_admin_assignment):
    '''
        Check if users can download the last submission for review
        if they are teaching assistants
    '''

    (_, ta, _, _, _) = base_db_setup

    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/admin/interface/assignment/',
        data={
            'action': 'download_review_submissions',
            '_selected_action': '1'
        },
        follow=True,
    )

    assert response.status_code == 200
    assert response.json()['type'] == "download_review_submissions"


@pytest.mark.django_db
def test_ta_download_all_subs(client, base_db_setup, mock_admin_assignment):
    '''
        Check if users can download all the submissions for review
        if they are teaching assistants
    '''

    (_, ta, _, _, _) = base_db_setup

    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/admin/interface/assignment/',
        data={
            'action': 'download_all_submissions',
            '_selected_action': '1'
        },
        follow=True,
    )

    assert response.status_code == 200
    assert response.json()['type'] == "download_all_submissions"


@pytest.mark.django_db
def test_ta_run_moss(client, base_db_setup, mock_admin_assignment):
    '''
        Check if users can run moss if they are teaching assistants
    '''

    (_, ta, user, _, _) = base_db_setup

    client.login(username=ta.username, password='pw')

    response = client.post(
        f'/admin/interface/assignment/',
        data={
            'action': 'run_moss',
            '_selected_action': '1'
        },
        follow=True,
    )

    assert response.status_code == 200
    assert response.json()['type'] == "run_moss"


@pytest.mark.django_db
def test_ta_login(client, STC, base_db_setup):
    (_, ta, _, _, _) = base_db_setup
    client.post('/', {'username': ta.username, 'password': 'pw'})

    response = client.post('/admin/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_ta_logout(client, STC, base_db_setup):
    (_, ta, _, _, _) = base_db_setup
    client.post('/', {'username': ta.username, 'password': 'pw'})

    response = client.post('/logout/')
    STC.assertRedirects(response, '/')


@pytest.mark.django_db
def test_ta_reveal(client, STC, base_db_setup):
    (_, ta, user, course, assignment) = base_db_setup

    client.login(username=ta.username, password='pw')

    response = client.get(f'/assignment/{course.pk}/{assignment.pk}/reveal')

    STC.assertRedirects(response, f'/assignment/{course.pk}/{assignment.pk}')

    if not assignment.hidden_score:
        assert False


@pytest.mark.django_db
def test_ta_see_revealed_score(client, STC, base_db_setup):
    (_, ta, user, course, assignment) = base_db_setup

    client.login(username=ta.username, password='pw')

    assignment.hidden_score = False
    assignment.save()

    response = client.get(f'/assignment/{course.pk}/{assignment.pk}')
    STC.assertNotContains(response, "N/A")


@pytest.mark.django_db
def test_ta_code_view(client, STC, base_db_setup):
    FILEPATH = settings.BASE_DIR / 'testsuite' / 'test.zip'

    (_, ta, _, course, assignment) = base_db_setup

    client.login(username=ta.username, password='pw')

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(
            FILEPATH.name,
            file.read(),
            content_type='application/zip',
        )
        client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
            format='multipart',
        )

    submission = Submission.objects.all()[0]

    response = client.get(
        f'/submission/{submission.pk}/test',
        follow=True,
    )

    assert response.status_code == 200
    STC.assertNotContains(response, "N/A")


@pytest.mark.django_db
def test_ta_code_view_file_missing(client, STC, base_db_setup):
    (_, ta, _, course, assignment) = base_db_setup

    client.login(username=ta.username, password='pw')

    with open(FILEPATH, 'rb') as file:
        upload = SimpleUploadedFile(
            FILEPATH.name,
            file.read(),
            content_type='application/zip',
        )
        client.post(
            f'/assignment/{course.pk}/{assignment.pk}/upload/',
            data={'name': FILEPATH.name, 'file': upload},
            format='multipart',
        )

    submission = Submission.objects.all()[0]

    response = client.get(
        f'/submission/{submission.pk}/test1',
        follow=True,
    )

    assert response.status_code == 200
    STC.assertContains(response, "The file is missing!")


@pytest.mark.django_db
def test_ta_code_view_archive_missing(client, STC, base_db_setup):
    (_, ta, user, course, assignment) = base_db_setup

    client.login(username=ta.username, password='pw')

    submission = assignment.submission_set.create(
        score=100.00,
        state=Submission.STATE_DONE,
        user=user,
        id=1000,
    )

    response = client.get(
        f'/submission/{submission.pk}/test',
        follow=True,
    )

    assert response.status_code == 200
    STC.assertContains(response, "The archive is missing!")
