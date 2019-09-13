import json
import logging
import base64

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings

from interface.backend.submission import handle_submission
from interface.forms import UploadFileForm, LoginForm
from interface.models import Submission, Assignment, Course
from interface import models


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect(homepage)
    else:
        form = LoginForm()

    return render(request, 'interface/login.html', {'form': form})


def upload(request):
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request)
            return redirect(submission_list)
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {'form': form})


def homepage(request):
    data = []

    for course in Course.objects.all():
        assignment_data = []
        for assignment in Assignment.objects.filter(course=course):
            assignment_data.append((redirect(upload).url
                                    + f'?assignment_id={assignment.code}',
                                    assignment.name))
        data.append((course.name, assignment_data))

    return render(request, 'interface/homepage.html', {'data': data})


def submission_list(request):
    submissions = Submission.objects.all()[::-1]
    paginator = Paginator(submissions, settings.SUBMISSIONS_PER_PAGE)

    page = request.GET.get('page', '1')
    subs = paginator.get_page(page)

    for submission in subs:
        submission.update_state()

    return render(request, 'interface/submission_list.html',
                  {'subs': subs,
                   'upload_url': redirect(homepage).url,
                   'sub_base_url': redirect(submission_list).url})


def submission_result(request, pk):
    sub = get_object_or_404(Submission, pk=pk)

    return render(request, 'interface/submission_result.html',
                  {'sub': sub,
                   'upload_url': redirect(homepage).url,
                   'submission_list_url': redirect(submission_list).url})


@csrf_exempt
def done(request):
    # NOTE: make it safe, some form of authentication
    #       we don't want stundets updating their score.
    options = json.loads(request.body, strict=False) if request.body else {}

    submission = get_object_or_404(models.Submission,
                                   pk=int(options['token']),
                                   score__isnull=True)

    decoded_message = base64.decodestring(bytes(options['output'],
                                                encoding='latin-1'))
    message_lines = str(decoded_message, encoding='latin-1').split('\n')

    submission.score = int(message_lines[-2].split('/')[0])
    submission.max_score = int(message_lines[-2].split('/')[1])
    submission.output = '\n'.join(message_lines[:-2])

    log.debug(f'Submission #{submission.id} has the output:\n{submission.output}')  # noqa: E501

    submission.save()

    return JsonResponse({})


def alive(request):
    '''Consul http check'''

    return JsonResponse({'alive': True})
