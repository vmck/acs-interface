from django.shortcuts import render, redirect, get_object_or_404
from interface.backend.submission import handle_submission
from interface.forms import UploadFileForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
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
            return redirect(upload)
    else:
        form = LoginForm()

    return render(request, 'interface/homepage.html', {'form': form})


def upload(request):
    if request.method == 'POST'and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request)
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {'form': form})


@csrf_exempt
def done(request):
    # NOTE: make it safe, some form of authentication
    #       we don't want stundets updating their score.
    options = json.loads(request.body, strict=False) if request.body else {}  # noqa: E501

    submission = get_object_or_404(models.Submission, url=options['token'])
    submission.score = 0

    log.debug(f'Submission #{submission.id} has the output:\n{options["output"]}')  # noqa: E501

    submission.save()

    return JsonResponse({})


def alive(request):
    return JsonResponse({'alive': True})
