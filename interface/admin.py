import io
import logging
from zipfile import ZipFile

import simple_history
from django.db import transaction
from django.http import FileResponse
from django.contrib import admin, messages
from django.contrib.auth.models import Permission

from interface.moss import moss_check
from interface.actions_logger import log_action_admin
from interface.backend.minio_api import MissingFile
from interface.utils import get_last_submissions_of_every_user
from interface.models import Course, Assignment, Submission, ActionLog


log = logging.getLogger(__name__)


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "action", "content_object"]
    list_filter = ["timestamp", "user"]
    readonly_fields = ["timestamp", "user", "action"]

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
        "delete_assignment",
    ]

    def _add_new_ta(self, user):
        ta_permissions = Permission.objects.filter(
            codename__in=CourseAdmin._ta_permissions
        )

        if not user.is_staff:
            user.is_staff = True
            user.user_permissions.set(ta_permissions)
            user.save()

    def _remove_ta(self, user, course):
        tas_courses = (
            Course.objects.all()
            .exclude(pk=course.pk)
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
        "download_review_submissions",
        "download_all_submissions",
        "run_moss",
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(AssignmentAdmin, self).get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            qs = form.base_fields["course"].queryset
            form.base_fields["course"].queryset = qs.filter(
                teaching_assistants=request.user
            )

        return form

    def get_queryset(self, request):
        qs = super(AssignmentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(course__teaching_assistants=request.user)

    def zip_submissions(self, request, submissions):
        big_buff = io.BytesIO()
        with ZipFile(big_buff, "a") as zip_archive:
            for submission in submissions:
                buff = io.BytesIO()
                try:
                    submission.download(buff)
                except MissingFile:
                    msg = f"File missing for {submission!r}"
                    messages.error(request, msg)
                    log.warning(msg)
                else:
                    buff.name = (
                        f"{submission.user.username}" f"-{submission.pk}.zip"
                    )
                    zip_archive.writestr(buff.name, buff.getvalue())

        big_buff.seek(0)
        return FileResponse(
            big_buff,
            as_attachment=True,
            filename="Submissions.zip",
        )

    @log_action_admin("Run moss check")
    def run_moss(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, "Only one assignment can be selected")
            return

        assignment = queryset[0]
        submissions = get_last_submissions_of_every_user(assignment)

        url = moss_check(submissions, assignment, request)

        messages.success(request, f"Report url: {url}")

    run_moss.short_description = "Run moss check on the selected assignment"

    @log_action_admin("Download last submissions")
    def download_review_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, "Only one assignment can be selected")
            return

        assignment = queryset[0]

        return self.zip_submissions(
            request,
            get_last_submissions_of_every_user(assignment),
        )

    download_review_submissions.short_description = (
        "Download last submissions for review"
    )

    @log_action_admin("Download all submissions")
    def download_all_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, "Only one assignment can be selected")
            return

        assignment = queryset[0]
        submission_set = assignment.submission_set.order_by("timestamp")

        return self.zip_submissions(request, submission_set)

    download_all_submissions.short_description = (
        "Download all submissions for review"
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if "deadline_soft" not in form.changed_data:
            return
        obj.refresh_submission_penalty()


@admin.register(Submission)
class SubmissionAdmin(simple_history.admin.SimpleHistoryAdmin):
    list_display = [
        "__str__",
        "assignment",
        "timestamp",
        "archive_size",
        "total_score",
        "state",
    ]
    list_display_links = ["__str__", "assignment"]
    list_filter = ["state", "assignment__course", "assignment", "user"]
    readonly_fields = [
        "user",
        "assignment",
        "archive_size",
        "evaluator_job_id",
        "state",
        "review_score",
        "penalty",
        "total_score",
        "stdout",
        "stderr",
    ]
    search_fields = ["user__username"]

    def get_queryset(self, request):
        qs = super(SubmissionAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(assignment__course__teaching_assistants=request.user)
