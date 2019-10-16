from django.core.management.base import BaseCommand
from interface.wsgi import application
from interface.settings import STATIC_ROOT

from waitress import serve
from whitenoise import WhiteNoise


class Command(BaseCommand):
    help = 'Start the app on port 8100'

    def handle(self, *args, **options):

        app = WhiteNoise(application, root=STATIC_ROOT)
        serve(app, port='8100', threads=20)
