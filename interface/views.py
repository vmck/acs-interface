from django.shortcuts import render, redirect, get_object_or_404
from interface.backend.submission import handle_submission
from interface.forms import UploadFileForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
from interface.models import Submission
from django.http import JsonResponse
from interface import models

import json
import logging
import base64


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def homepage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect(submission_list)
    else:
        form = LoginForm()

    return render(request, 'interface/homepage.html', {'form': form})


def upload(request):
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request)
            return redirect(submission_list)
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {'form': form})


def submission_list(request):
    submissions = Submission.objects.all()[::-1]

    return render(request, 'interface/submission_list.html',
                  {'subs': submissions,
                   'upload_url': redirect(upload).url,
                   'sub_base_url': redirect(submission_list).url})


def submission(request, pk):
    sub = get_object_or_404(models.Submission, pk=pk)

    return render(request, 'interface/submission.html',
                  {'sub': sub,
                   'upload_url': redirect(upload).url,
                   'submission_list_url': redirect(submission_list).url})


@csrf_exempt
def done(request):
    # NOTE: make it safe, some form of authentication
    #       we don't want stundets updating their score.

    options = json.loads(request.body, strict=False) if request.body else {}

    submission = get_object_or_404(models.Submission,
                                   _url=options['token'],
                                   score__isnull=True)

    decoded_message = base64.decodestring(bytes(options['output'],
                                                encoding='latin-1'))
    message_lines = str(decoded_message, encoding='latin-1').split('\n')

    submission.score = int(message_lines[-2].split('/')[0])
    submission.max_score = int(message_lines[-2].split('/')[1])
    submission.message = '\n'.join(message_lines[:-2])

    log.debug(f'Submission #{submission.id} has the output:\n{submission.message}')  # noqa: E501

    submission.save()

    return JsonResponse({})


def alive(request):
    '''Consul http check'''

    return JsonResponse({'alive': True})
