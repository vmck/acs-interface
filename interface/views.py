from django.shortcuts import render, redirect, get_object_or_404
from interface.backend.submission import handle_submission
from interface.forms import UploadFileForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
from interface.models import Submission
from django.http import JsonResponse
from django.conf import settings
from interface import models
from tempfile import TemporaryDirectory
from pathlib import Path
from zipfile import ZipFile

import json
import logging
import base64
import os


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
    page = int(request.GET.get('page', 1))

    lower_id = (page-1) * settings.SUBMISSIONS_PER_PAGE
    upper_id = page * settings.SUBMISSIONS_PER_PAGE

    submissions = Submission.objects.all()[::-1][lower_id:upper_id]

    for sub in submissions:
        sub.update_state()

    first_id = submissions[0].id

    if first_id > settings.SUBMISSIONS_PER_PAGE:
        next_url = redirect(submission_list).url + f'?page={page + 1}'
    else:
        next_url = redirect(submission_list).url + f'?page={page}'

    if page == 1:
        prev_url = redirect(submission_list).url + f'?page={page}'
    else:
        prev_url = redirect(submission_list).url + f'?page={page - 1}'

    return render(request, 'interface/submission_list.html',
                  {'subs': submissions,
                   'upload_url': redirect(upload).url,
                   'sub_base_url': redirect(submission_list).url,
                   'next_url': next_url,
                   'prev_url': prev_url})


def submission_result(request, pk):
    sub = get_object_or_404(Submission, pk=pk)

    return render(request, 'interface/submission_result.html',
                  {'sub': sub,
                   'upload_url': redirect(upload).url,
                   'submission_list_url': redirect(submission_list).url})


def review(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    with TemporaryDirectory() as _tmpdir:
        tmpdir = Path(_tmpdir)
        submission.download(tmpdir / 'archive.zip')

        with ZipFile(tmpdir / 'archive.zip') as zipfile:
            zipfile.extractall(tmpdir)

        for _, d, f in os.walk(tmpdir):
                    print(d, *f)

    return render(request, 'interface/review.html')


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
