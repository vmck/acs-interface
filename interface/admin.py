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

    def get_submission_set(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, 'Only one assignment can be selected')
            return

        assignment = queryset[0]
        submission_set = assignment.submission_set.order_by('timestamp')

        return submission_set

    def archive_submissions(self, submissions):
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
        submission_set = self.get_submission_set(request, queryset)

        submissions = {}

        # we only want the last submission of every user
        for submission in submission_set:
            submissions[submission.user.username] = submission

        return self.archive_submissions(submissions.values())

    download_review_submissions.short_description = ('Download last '
                                                     'submissions for review')

    def download_all_submissions(self, request, queryset):
        submission_set = self.get_submission_set(request, queryset)

        return self.archive_submissions(submission_set)

    download_all_submissions.short_description = ('Download all submissions'
                                                  ' for review')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    actions = ['rerun_submissions']

    def rerun_submissions(self, request, submissions):
        for submission in submissions:
            submission.evaluate()

    rerun_submissions.short_description = 'Re-run submissions'
