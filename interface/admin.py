from zipfile import ZipFile
from tempfile import TemporaryDirectory
from pathlib import Path

from django.contrib import admin
from django.http import FileResponse

from interface.models import Course, Assignment, Submission

admin.site.register(Course)
admin.site.register(Submission)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    actions = ['download_submissions']

    def download_submissions(self, request, queryset):
        if queryset.count() != 1:
            raise RuntimeError('Only one assignment can be selected')

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
                        f'{submission.user.username}-{submission.id}.zip'
                        )

            review_zip = (tmp / 'review.zip').open('rb')
            return FileResponse(review_zip)

    download_submissions.short_description = 'Download submissions for review'
