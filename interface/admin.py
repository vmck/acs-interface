from zipfile import ZipFile
from tempfile import TemporaryDirectory
from pathlib import Path

from django.contrib import admin
from django.db.models import F
from django.http import FileResponse

from interface.models import Course, Assignment, Submission

admin.site.register(Course)
admin.site.register(Submission)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    actions = ['download_submissions']

    def download_submissions(self, request, _assignment):
        if _assignment.count() != 1:
            raise RuntimeError('Only one assignment can be selected')

        assignment = _assignment[0]

        subs = Submission.objects.filter(
                assignment=assignment).order_by(F('timestamp').asc())

        submissions = {}

        # we only want the last submission of every user
        for submission in subs:
            submissions[submission.user.username] = submission

        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            with ZipFile(tmp / 'review.zip', 'x') as zipfile:
                for _, submission in submissions.items():
                    submission.download(tmp / f'{submission.id}.zip')
                    zipfile.write(
                        tmp / f'{submission.id}.zip',
                        f'{submission.user.username}-{submission.id}.zip')

            review_zip = (tmp / 'review.zip').open('rb')
            response = FileResponse(review_zip)

            return response

    download_submissions.short_description = 'Download submissions for review'
