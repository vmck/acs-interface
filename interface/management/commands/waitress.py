from django.core.management.base import BaseCommand
from waitress import serve
from whitenoise import WhiteNoise

from interface.settings import APP_THREAD_COUNT, STATIC_ROOT
from interface.wsgi import application


class Command(BaseCommand):
    help = "Start the app on port 8100"  # noqa: A003

    def handle(self, *args, **options):
        app = WhiteNoise(application, root=STATIC_ROOT)
        serve(
            app,
            port="8100",
            threads=APP_THREAD_COUNT,
        )
