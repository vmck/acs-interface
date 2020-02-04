import glob
import logging
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory

import mosspy
import simple_history
from django.conf import settings
from django.http import FileResponse
from django.contrib import admin, messages

from interface.actions_logger import log_action
from interface.backend.minio_api import MissingFile
from interface.utils import get_last_submissions_of_every_user
from interface.models import Course, Assignment, Submission, ActionLog

log_level = logging.DEBUG
log = logging.getLogger(__name__)
log.setLevel(log_level)


admin.site.register(Course, simple_history.admin.SimpleHistoryAdmin)


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'content_object']
    list_filter = ['timestamp', 'user']
    readonly_fields = ['timestamp', 'user', 'action']

    actions_selection_counter = False
    list_display_links = None
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Assignment)
class AssignmentAdmin(simple_history.admin.SimpleHistoryAdmin):
    actions = [
        'download_review_submissions',
        'download_all_submissions',
        'run_moss',
    ]

    def zip_submissions(self, request, submissions):
        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            with ZipFile(tmp / 'review.zip', 'x') as zipfile:
                for submission in submissions:
                    try:
                        submission.download(tmp / f'{submission.id}.zip')
                    except MissingFile:
                        msg = f"File missing for {submission!r}"
                        messages.error(request, msg)
                        log.warning(msg)
                    else:
                        zipfile.write(
                            tmp / f'{submission.id}.zip',
                            f'{submission.user.username}-{submission.id}.zip',
                        )

            review_zip = (tmp / 'review.zip').open('rb')
            return FileResponse(review_zip)

    @log_action('Run moss check')
    def run_moss(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]
        submissions = get_last_submissions_of_every_user(assignment)

        moss = mosspy.Moss(
            settings.MOSS_USER_ID,
            assignment.get_language_display(),
        )
        moss.setDirectoryMode(1)

        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            for submission in submissions:
                try:
                    submission.download(tmp / f'{submission.id}.zip')
                except MissingFile:
                    msg = f"File missing for {submission!r}"
                    messages.error(request, msg)
                    log.warning(msg)

                submission_archive = ZipFile(tmp / f'{submission.id}.zip')
                submission_archive.extractall(
                    tmp / f'{submission.user.username}',
                )

                read_files = glob.glob(
                    str(tmp / (f'{submission.user.username}'
                        '/*.{submission.assignment.language}')
                        ),
                )

                for f in read_files:
                    new_filename = f.split('/')[-2]
                    + f'/{submission.user.username}_'
                    + f.split('/')[-1]

                    moss.addFile(f, new_filename)

            url = moss.send()

        messages.success(request, f'Report url: {url}')

    run_moss.short_description = 'Run moss check on the selected assignment'

    @log_action('Download last submissions')
    def download_review_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]

        return self.zip_submissions(
            request,
            get_last_submissions_of_every_user(assignment),
        )

    download_review_submissions.short_description = ('Download last '
                                                     'submissions for review')

    @log_action('Download all submissions')
    def download_all_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]
        submission_set = assignment.submission_set.order_by('timestamp')

        return self.zip_submissions(request, submission_set)

    download_all_submissions.short_description = ('Download all submissions '
                                                  'for review')


@admin.register(Submission)
class SubmissionAdmin(simple_history.admin.SimpleHistoryAdmin):
    actions = ['rerun_submissions', 'download_archive', 'recompute_score']
    list_display = [
        '__str__', 'assignment', 'timestamp',
        'archive_size', 'total_score', 'state',
    ]
    list_display_links = ['__str__', 'assignment']
    list_filter = ['state', 'assignment__course', 'assignment', 'user']
    readonly_fields = [
        'user', 'assignment', 'archive_size', 'vmck_job_id', 'state',
        'review_score', 'penalty', 'total_score', 'stdout', 'stderr',
    ]

    @log_action('Rerun submission')
    def rerun_submissions(self, request, submissions):
        for submission in submissions:
            submission.state = Submission.STATE_NEW
            submission.evaluate()

    rerun_submissions.short_description = 'Re-run submissions'

    @log_action('Donwload submission archive')
    def download_archive(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one submission can be selected')
            return

        submission = queryset[0]

        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            try:
                submission.download(tmp / f'{submission.id}.zip')
            except MissingFile:
                msg = f"File missing for {submission!r}"
                messages.error(request, msg)
                log.warning(msg)
                return

            else:
                submission_zip = (tmp / f'{submission.id}.zip').open('rb')
                return FileResponse(submission_zip)

    download_archive.short_description = 'Download submission archive'

    @log_action('Recompute score')
    def recompute_score(self, request, submissions):
        for submission in submissions:
            # Clear the penalty so it's calculated again
            submission.penalty = None
            submission.save()

    recompute_score.short_description = 'Recompute score'
