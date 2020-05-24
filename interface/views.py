import re
import json
import pprint
import logging
import decimal
import subprocess
from pathlib import Path
from zipfile import BadZipFile
from tempfile import TemporaryDirectory

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from interface import models
from interface import utils
from interface.forms import UploadFileForm, LoginForm
from interface.models import Submission, Course, User
from interface.backend.submission.submission import handle_submission, \
    TooManySubmissionsError, \
    CorruptZipFile
from .scoring import calculate_total_score
from interface.actions_logger import log_action


log = logging.getLogger(__name__)


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
def upload(request, course_pk, assignment_pk):
    course = get_object_or_404(Course, pk=course_pk)
    assignment = get_object_or_404(course.assignment_set, pk=assignment_pk)

    if not assignment.is_active:
        raise Http404("You cannot upload! You are past the deadline!")

    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                handle_submission(file, assignment, request.user)

            except TooManySubmissionsError as e:
                messages.error(
                    request,
                    f'Please wait {e.wait_t}s between submissions',
                )

            except (CorruptZipFile, ValueError):
                messages.error(request, 'The archive is corrupt')

            except BadZipFile:
                messages.error(request, 'File is not a valid zip archive')

            else:
                return redirect(users_list, course_pk, assignment_pk)

            return render(request, 'interface/upload.html', {
                'form': form,
            })
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {
        'form': form,
    })


@login_required
def download(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    if (submission.user != request.user
            and request.user
            not in submission.assignment.course.teaching_assistants.all()):
        return Http404('You are not allowed!')

    with TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)

        submission.download(tmp / f'{submission.pk}.zip')
        review_zip = (tmp / f'{submission.pk}.zip').open('rb')

        log_action("Download submission", request.user, submission)

        return FileResponse(review_zip, as_attachment=True)


@login_required
def homepage(request):
    return render(request, 'interface/homepage.html', {
        'courses': Course.objects.all(),
    })


@login_required
@staff_member_required
@require_POST
def review(request, pk):
    submission = get_object_or_404(models.Submission, pk=pk)

    if (request.user
            not in submission.assignment.course.teaching_assistants.all()):
        return Http404('You are not allowed!')

    submission.review_message = request.POST['review-code']
    submission.changeReason = 'Review'
    submission.save()

    log_action("Review submission", request.user, submission)

    return redirect(request.META['HTTP_REFERER'])


@login_required
@staff_member_required
def rerun_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    if (request.user
            not in submission.assignment.course.teaching_assistants.all()):
        return Http404('You are not allowed!')

    submission.state = Submission.STATE_NEW
    submission.evaluate()

    log_action("Rerun submission", request.user, submission)

    return redirect(request.META['HTTP_REFERER'])


@login_required
@staff_member_required
def recompute_score(request, pk):
    submission = get_object_or_404(models.Submission, pk=pk)

    if (request.user
            not in submission.assignment.course.teaching_assistants.all()):
        return Http404('You are not allowed!')

    # Clear the penalty so it's calculated again
    submission.penalty = None
    submission.save()

    log_action("Recompute submission's score", request.user, submission)

    return redirect(request.META['HTTP_REFERER'])


@login_required
def submission_list(request):
    submissions = Submission.objects.all().order_by('-id')

    paginator = Paginator(submissions, settings.SUBMISSIONS_PER_PAGE)

    page = request.GET.get('page', '1')
    subs = paginator.get_page(page)

    return render(request, 'interface/submission_list.html', {
        'subs': subs,
        'homepage_url': redirect(homepage).url,
        'sub_base_url': redirect(submission_list).url,
        'logout_url': redirect(logout_view).url,
    })


@login_required
def submission_result(request, pk):
    sub = get_object_or_404(Submission, pk=pk)
    fortune_msg = subprocess.check_output("fortune").decode('utf-8')

    return render(request, 'interface/submission_result.html', {
        'sub': sub,
        'homepage_url': redirect(homepage).url,
        'submission_review_message': sub.review_message,
        'submission_list_url': redirect(submission_list).url,
        'fortune': fortune_msg,
    })


@csrf_exempt
def done(request, pk):
    log.debug(f'URL: {request.get_full_path()}')
    log.debug(pprint.pformat(request.body))

    options = json.loads(request.body, strict=False) if request.body else {}

    submission = get_object_or_404(models.Submission,
                                   pk=pk)

    assert submission.verify_jwt(request.GET.get('token'))

    stdout = utils.decode(options['stdout'])
    exit_code = int(options['exit_code'])

    score = re.search(r'.*TOTAL: (\d+\.?\d*)/(\d+)', stdout, re.MULTILINE)
    points = score.group(1) if score else 0
    if not score:
        log.warning('Score is None')

    if len(stdout) > 32768:
        stdout = stdout[:32730] + '... TRUNCATED BECAUSE TOO BIG ...'

    submission.score = decimal.Decimal(points)
    submission.total_score = calculate_total_score(submission)
    submission.stdout = stdout
    submission.update_state()

    log.debug(f'Submission #{submission.pk}:')
    log.debug(f'Stdout:\n{submission.stdout}')
    log.debug(f'Exit code:\n{exit_code}')

    submission.changeReason = 'Evaluation'
    submission.save()

    return JsonResponse({})


def alive(request):
    '''Consul http check'''

    return JsonResponse({'alive': True})


@login_required
def users_list(request, course_pk, assignment_pk):
    course = get_object_or_404(Course, pk=course_pk)
    assignment = get_object_or_404(course.assignment_set, pk=assignment_pk)
    submissions = assignment.submission_set.all()
    list_of_users = []
    for subm in submissions:
        list_of_users.append(subm.user)
    list_of_users = set(list_of_users)
    final_sub_list = []
    for user in list_of_users:
        submissions_list_aux = submissions.filter(user=user)
        submissions_list_aux = submissions_list_aux.order_by('-timestamp')
        subm = submissions_list_aux.first()
        final_sub_list.append(subm)

    return render(request, 'interface/users_list.html', {
        'assignment': assignment,
        'submissions': final_sub_list,
    })


@login_required
def subs_for_user(request, course_pk, assignment_pk, username):
    user = User.objects.get(username=username)
    course = get_object_or_404(Course, pk=course_pk)
    assignment = get_object_or_404(course.assignment_set, pk=assignment_pk)
    submissions = (
        assignment.submission_set
        .filter(user=user)
        .order_by("-timestamp")
    )

    return render(request, 'interface/subs_for_user.html', {
        'assignment': assignment,
        'submissions': submissions,
    })
