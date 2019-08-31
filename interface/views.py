from django.shortcuts import render, redirect, get_object_or_404
from interface.backend.submission import handle_submission
from interface.forms import UploadFileForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
from interface.models import Submission
from django.http import JsonResponse
from interface import models

import json
import logging


log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


def homepage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect(submission)
    else:
        form = LoginForm()

    return render(request, 'interface/homepage.html', {'form': form})


def upload(request):
    if request.method == 'POST'and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request)
            return redirect(submission)
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {'form': form})


def submission(request):
    sub = Submission.objects.latest('pk')

    return render(request, 'interface/submission.html',
                  {'sub': sub, 'upload_url': redirect(upload).url})


@csrf_exempt
def done(request):
    # NOTE: make it safe, some form of authentication
    #       we don't want stundets updating their score.
    options = json.loads(request.body, strict=False) if request.body else {}  # noqa: E501

    submission = get_object_or_404(models.Submission,
                                   url=options['token'],
                                   score=-1)
    submission.score = int(options['output'].split('\n')[-1].split('/')[0])
    submission.max_score = int(options['output'].split('\n')[-1].split('/')[1])
    submission.message = str(''.join(options['output'].split('\n')[:-1]))

    log.debug(f'Submission #{submission.id} has the output:\n{options["output"]}')  # noqa: E501

    submission.save()

    return JsonResponse({})


def alive(request):
    '''Consul http check'''

    return JsonResponse({'alive': True})
