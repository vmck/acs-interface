import logging
from pathlib import Path
from zipfile import ZipFile
from tempfile import TemporaryDirectory

import simple_history
from django.db import transaction
from django.http import FileResponse
from django.contrib import admin, messages
from django.contrib.auth.models import Permission

from interface.moss import moss_check
from interface.actions_logger import log_action
from interface.backend.minio_api import MissingFile
from interface.utils import get_last_submissions_of_every_user
from interface.models import Course, Assignment, Submission, ActionLog


log = logging.getLogger(__name__)


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


@admin.register(Course)
class CourseAdmin(simple_history.admin.SimpleHistoryAdmin):
    filter_horizontal = ["teaching_assistants"]
    _ta_permissions = [
        "view_submission",
        "add_assignment",
        "change_assignment",
        "delete_assignment"
    ]

    def _add_new_ta(self, user):
        ta_permissions = (
                Permission.objects
                .filter(codename__in=CourseAdmin._ta_permissions)
            )
        print(user)

        if not user.is_staff:
            user.is_staff = True
            user.user_permissions.set(ta_permissions)
            user.save()

    def _remove_ta(self, user, course):
        tas_courses = (
                    Course.objects.all()
                    .exclude(code=course.code)
                    .filter(teaching_assistants=user)
                )
        if not tas_courses:
            user.is_staff = False
            user.user_permissions.set([])
            user.save()

    def get_queryset(self, request):
        qs = super(CourseAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(teaching_assistants=request.user)

    def save_model(self, request, obj, form, change):
        if obj.id is None:
            # New course was added
            # need to save it to have access to member vars
            super().save_model(request, obj, form, change)

        if "teaching_assistants" not in form.changed_data:
            return

        tas = set(obj.teaching_assistants.all())
        new_tas = set(form.cleaned_data["teaching_assistants"])

        to_add_tas = new_tas - tas
        to_remove_tas = tas - new_tas

        for user in to_add_tas:
            self._add_new_ta(user)

        with transaction.atomic():
            for user in to_remove_tas:
                self._remove_ta(user, obj)


@admin.register(Assignment)
class AssignmentAdmin(simple_history.admin.SimpleHistoryAdmin):
    actions = [
        'download_review_submissions',
        'download_all_submissions',
        'run_moss',
    ]

    def get_queryset(self, request):
        qs = super(AssignmentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(course__teaching_assistants=request.user)

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

        url = moss_check(submissions, assignment, request)

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
    actions = ['recompute_score']
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
    search_fields = ['user__username']

    def get_queryset(self, request):
        qs = super(SubmissionAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(assignment__course__teaching_assistants=request.user)

    @log_action('Recompute score')
    def recompute_score(self, request, submissions):
        for submission in submissions:
            # Clear the penalty so it's calculated again
            submission.penalty = None
            submission.save()

    recompute_score.short_description = 'Recompute score'
