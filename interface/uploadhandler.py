from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.core.files.uploadhandler import MemoryFileUploadHandler, StopUpload


class RestrictedFileUploadHandler(MemoryFileUploadHandler):
    def handle_raw_input(self, input_data, META, content_length,
                         boundary, encoding=None):
        super().handle_raw_input(
            input_data,
            META,
            content_length,
            boundary,
            encoding=None,
        )

        self.too_big = False
        if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            self.too_big = True

    def receive_data_chunk(self, raw_data, start):
        if self.too_big:
            raise StopUpload((
                'File must be below '
                f'{filesizeformat(settings.FILE_UPLOAD_MAX_MEMORY_SIZE)}'
            ))

        super().receive_data_chunk(raw_data, start)
