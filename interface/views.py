from django.shortcuts import render, redirect, get_object_or_404
from interface.forms import UploadFileForm, LoginForm
from interface.backend.submission import handle_submission
from django.http import JsonResponse
from interface import models

import json


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


def done(request):
    # NOTE: make it safe, some form of authentication
    #       we don't want stundets updating their score.
    options = json.loads(request.body) if request.body else {}  # TODO validate

    submission = get_object_or_404(models.Submission, id=options['id'])
    submission.score = options['score']
    submission.save()


def alive(request):
    return JsonResponse({'alive': True})
