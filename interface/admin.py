from zipfile import ZipFile
from tempfile import TemporaryDirectory
from pathlib import Path

from django.contrib import admin
from django.db.models import F
from django.http import HttpResponse

from interface.models import Course, Assignment, Submission

admin.site.register(Course)
admin.site.register(Submission)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    actions = ['download_submissions']

    def download_submissions(self, request, _assignment):
        assignment = _assignment[0]

        subs = Submission.objects.filter(
                assignment=assignment).order_by(F('timestamp').asc())

        submissions = {}

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

            with open(tmp / 'review.zip', 'rb') as zipfile:
                response = HttpResponse(zipfile.read(),
                                        content_type='application/zip')
            response['Content-Disposition'] = ('attachment;'
                                               'filename="review.zip"')

        return response

    download_submissions.short_description = 'Download submissions for review'
