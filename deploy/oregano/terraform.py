import logging

from .templates import render


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Configuration:

    def __init__(self, path):
        self.path = path
        self.components = []

    def __repr__(self):
        return f"<terraform.Configuration at {self.path}>"

    def add(self, thing):
        log.debug(f"{self!r} adding {thing!r}")
        self.components.append(thing)
        thing.tf = self

    def render(self):
        log.debug(f"{self!r} rendering")
        self.path.mkdir(exist_ok=True)
        with (self.path / 'main.tf').open('w', encoding='utf8') as f:
            f.write(render('main.tf', {
                'components': self.components,
            }))

    def apply(self):
        log.debug(f"{self!r} applying")
