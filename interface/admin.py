from tarfile import TarFile
from tempfile import TemporaryDirectory
from pathlib import Path

from django.contrib import admin
from django.http import HttpResponse

from interface.models import Course, Assignment, Submission

admin.site.register(Course)
admin.site.register(Submission)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    actions = ['download_submissions']

    def download_submissions(self, request, queryset):
        submissions = Submission.objects.all()

        with TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)

            with TarFile(tmp / 'review.tar', 'x') as tar:
                for submission in submissions:
                    submission.download(tmp / f'{submission.id}.zip')
                    tar.add(tmp / f'{submission.id}.zip', f'{submission.id}.zip')

            with open(tmp / 'review.tar', 'rb') as tar:
                response = HttpResponse(tar.read(),
                                        content_type='application/x-tar')
            response['Content-Disposition'] = ('attachment;'
                                               'filename="review.tar"')

        return response

    download_submissions.short_description = 'Donwload submissions for review'
