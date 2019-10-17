from zipfile import ZipFile
from tempfile import TemporaryDirectory
from pathlib import Path

from django.contrib import admin, messages
from django.http import FileResponse

from interface.models import Course, Assignment, Submission


admin.site.register(Course)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    actions = ['download_review_submissions', 'download_all_submissions']

    def zip_response_with_submissions(self, submissions):
        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            with ZipFile(tmp / 'review.zip', 'x') as zipfile:
                for submission in submissions:
                    submission.download(tmp / f'{submission.id}.zip')
                    zipfile.write(
                        tmp / f'{submission.id}.zip',
                        f'{submission.user.username}-{submission.id}.zip',
                    )

            review_zip = (tmp / 'review.zip').open('rb')
            return FileResponse(review_zip)

    def download_review_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]
        submission_set = assignment.submission_set.order_by('timestamp')

        submissions = {}

        # we only want the last submission of every user
        for submission in submission_set:
            submissions[submission.user.username] = submission

        return self.zip_response_with_submissions(submissions.values())

    download_review_submissions.short_description = ('Download last '
                                                     'submissions for review')

    def download_all_submissions(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]
        submission_set = assignment.submission_set.order_by('timestamp')

        return self.zip_response_with_submissions(submission_set)

    download_all_submissions.short_description = ('Download all submissions '
                                                  'for review')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    actions = ['rerun_submissions', 'download_archive']
    list_display = ['__str__', 'assignment', 'timestamp', 'archive_size']
    list_display_links = ['__str__', 'assignment']
    list_filter = ['assignment__course', 'assignment', 'user']

    def rerun_submissions(self, request, submissions):
        for submission in submissions:
            submission.state = Submission.STATE_NEW
            submission.evaluate()

    rerun_submissions.short_description = 'Re-run submissions'

    def download_archive(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one submission can be selected')
            return

        submission = queryset[0]

        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            submission.download(tmp / f'{submission.id}.zip')

            submission_zip = (tmp / f'{submission.id}.zip').open('rb')
            return FileResponse(submission_zip)

    download_archive.short_description = 'Download submission archive'
