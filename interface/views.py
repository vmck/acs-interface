import re
import json
import logging
import decimal
import pprint
from pathlib import Path
from tempfile import TemporaryDirectory

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse, Http404
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
    if request.user.is_authenticated:
        return redirect(homepage)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.data['username']
            password = form.data['password']

            user = authenticate(username=username, password=password)

            if not user:
                log.info(f"Login failure for {username}")
            else:
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
def download(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    if submission.user != request.user:
        return Http404('You are not allowed!')

    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)

        submission.download(tmp / f'{submission.id}.zip')

        review_zip = (tmp / f'{submission.id}.zip').open('rb')
        return FileResponse(review_zip)


@login_required
def homepage(request):
    data = []

    for course in Course.objects.all():
        assignment_data = []
        for assignment in Assignment.objects.filter(course=course):
            url = redirect(upload).url + f'?assignment_id={assignment.code}'
            assignment_data.append((url, assignment.name))
        data.append((course.name, assignment_data))

    return render(request, 'interface/homepage.html',
                  {'data': data,
                   'submission_list_url': redirect(submission_list).url,
                   'logout_url': redirect(logout_view).url})


@login_required
@staff_member_required
@require_POST
def review(request, pk):
    submission = get_object_or_404(models.Submission, pk=pk)

    marks = re.findall(
        r'^([+-]\d+\.*\d*):',
        request.POST['review-code'],
        re.MULTILINE,
    )
    log.debug('Marks found: ' + str(marks))

    review_score = sum([decimal.Decimal(mark) for mark in marks])

    submission.review_score = review_score
    submission.total_score = submission.calculate_total_score()
    submission.review_message = request.POST['review-code']
    submission.save()

    return redirect(request.META['HTTP_REFERER'])


@login_required
def submission_list(request):
    submissions = Submission.objects.all().order_by('-id')

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
                   'current_user': request.user,
                   'homepage_url': redirect(homepage).url,
                   'submission_list_url': redirect(submission_list).url})


@csrf_exempt
def done(request, pk):
    log.debug(f'URL: {request.get_full_path()}')
    log.debug(pprint.pformat(request.body))

    options = json.loads(request.body, strict=False) if request.body else {}

    submission = get_object_or_404(models.Submission,
                                   pk=pk)

    assert submission.verify_jwt(request.GET.get('token'))

    stdout = utils.decode(options['stdout'])
    stderr = utils.decode(options['stderr'])
    exit_code = int(options['exit_code'])

    score = re.search(r'.*TOTAL: (\d+\.?\d*)/(\d+)', stdout, re.MULTILINE)
    points = score.group(1) if score else 0
    if not score:
        log.warning('Score is None')

    if len(stdout) > 32768:
        stdout = stdout[:32730] + '... TRUNCATED BECAUSE TOO BIG ...'

    if len(stderr) > 32768:
        stderr = stderr[:32730] + '... TRUNCATED BECAUSE TOO BIG ...'

    submission.score = decimal.Decimal(points)
    submission.total_score = submission.calculate_total_score()
    submission.stdout = stdout
    submission.stderr = stderr
    submission.state = Submission.STATE_DONE

    log.debug(f'Submission #{submission.id}:')
    log.debug(f'Stdout:\n{submission.stdout}')
    log.debug(f'Stderr:\n{submission.stderr}')
    log.debug(f'Exit code:\n{exit_code}')

    submission.save()

    return JsonResponse({})


def alive(request):
    '''Consul http check'''

    return JsonResponse({'alive': True})
