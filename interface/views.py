import re
import json
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings


from interface.backend.submission import handle_submission
from interface.forms import UploadFileForm, LoginForm
from interface.models import Submission, Assignment, Course
from interface import models
from interface import utils


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.data['username'],
                                password=form.data['password'])
            if user and user.username in settings.ACS_USER_WHITELIST:
                login(request, user)
                return redirect(homepage)
    else:
        form = LoginForm()

    return render(request, 'interface/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(login_view)


@login_required
def upload(request):
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request)
            return redirect(submission_list)
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {'form': form})


@login_required
def homepage(request):
    data = []

    for course in Course.objects.all():
        assignment_data = []
        for assignment in Assignment.objects.filter(course=course):
            assignment_data.append((redirect(upload).url
                                    + f'?assignment_id={assignment.code}',
                                    assignment.name))
        data.append((course.name, assignment_data))

    return render(request, 'interface/homepage.html',
                  {'data': data,
                   'submission_list_url': redirect(submission_list).url,
                   'logout_url': redirect(logout_view).url})


@login_required
def submission_list(request):
    submissions = Submission.objects.all()[::-1]
    paginator = Paginator(submissions, settings.SUBMISSIONS_PER_PAGE)

    page = request.GET.get('page', '1')
    subs = paginator.get_page(page)

    for submission in subs:
        submission.update_state()

    return render(request, 'interface/submission_list.html',
                  {'subs': subs,
                   'homepage_url': redirect(homepage).url,
                   'sub_base_url': redirect(submission_list).url,
                   'current_user': request.user,
                   'logout_url': redirect(logout_view).url})


@login_required
def submission_result(request, pk):
    sub = get_object_or_404(Submission, pk=pk)

    return render(request, 'interface/submission_result.html',
                  {'sub': sub,
                   'homepage_url': redirect(homepage).url,
                   'submission_list_url': redirect(submission_list).url})


@csrf_exempt
def done(request, pk):
    # NOTE: make it safe, some form of authentication
    #       we don't want stundets updating their score.
    log.debug(request.body)

    options = json.loads(request.body, strict=False) if request.body else {}

    submission = get_object_or_404(models.Submission,
                                   pk=pk,
                                   score__isnull=True)

    stdout = utils.decode(options['stdout'])
    stderr = utils.decode(options['stderr'])
    exit_code = int(options['exit_code'])

    score = re.search(r'.*TOTAL: (\d+)/(\d+)', stdout, re.MULTILINE)
    points = score.group(1) if score else 0
    if not score:
        log.warning('Score is None')

    submission.score = points
    submission.output = stdout + '\n' + stderr

    log.debug(f'Submission #{submission.id} has the output:\n{submission.output}')  # noqa: E501
    log.debug(f'Stderr:\n{stderr}')
    log.debug(f'Exit code:\n{exit_code}')

    submission.save()

    return JsonResponse({})


def alive(request):
    '''Consul http check'''

    return JsonResponse({'alive': True})
