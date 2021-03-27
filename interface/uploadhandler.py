from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadhandler import MemoryFileUploadHandler


class RestrictedFileUploadHandler(MemoryFileUploadHandler):
    def handle_raw_input(
        self,
        input_data,
        META,
        content_length,
        boundary,
        encoding=None,
    ):
        super().handle_raw_input(
            input_data,
            META,
            content_length,
            boundary,
            encoding=None,
        )

        if content_length >= settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            return (
                {"csrfmiddlewaretoken": META.get("CSRF_COOKIE", "")},
                {
                    "file": InMemoryUploadedFile(
                        file=None,
                        field_name=None,
                        name="FileTooBig",
                        content_type=None,
                        size=content_length,
                        charset=None,
                        content_type_extra=None,
                    ),
                },
            )

        return None
