from django.core.management.base import BaseCommand
from interface.wsgi import application

from waitress import serve


class Command(BaseCommand):
    help = 'Start the app on port 8100'

    def handle(self, *args, **options):
        serve(application, port='8100')
