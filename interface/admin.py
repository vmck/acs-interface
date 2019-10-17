from zipfile import ZipFile
from tempfile import TemporaryDirectory
from pathlib import Path

from django.contrib import admin, messages
from django.http import FileResponse

from interface.models import Course, Assignment, Submission


admin.site.register(Course)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    actions = ['download_submissions']

    def download_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]
        submission_set = assignment.submission_set.order_by('timestamp')

        submissions = {}

        # we only want the last submission of every user
        for submission in submission_set:
            submissions[submission.user.username] = submission

        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            with ZipFile(tmp / 'review.zip', 'x') as zipfile:
                for submission in submissions.values():
                    submission.download(tmp / f'{submission.id}.zip')
                    zipfile.write(
                        tmp / f'{submission.id}.zip',
                        f'{submission.user.username}-{submission.id}.zip',
                    )

            review_zip = (tmp / 'review.zip').open('rb')
            return FileResponse(review_zip)

    download_submissions.short_description = 'Download submissions for review'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    actions = ['rerun_submissions']
    list_display = ['__str__', 'assignment', 'timestamp', 'archive_size']
    list_display_links = ['__str__', 'assignment']
    list_filter = ['user', 'assignment', 'assignment__course']

    def rerun_submissions(self, request, submissions):
        for submission in submissions:
            submission.state = Submission.STATE_NEW
            submission.evaluate()

    rerun_submissions.short_description = 'Re-run submissions'
