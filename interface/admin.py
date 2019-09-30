from django.contrib import admin
from interface.models import Course, Assignment, Submission

admin.site.register(Course)
admin.site.register(Submission)
admin.site.register(Assignment)
