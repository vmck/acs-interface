import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class NomadProvider:

    def __init__(self, nomad_addr):
        self.nomad_addr = nomad_addr


class Configuration:

    def __init__(self):
        self.things = []

    def add(self, thing):
        log.debug(f"{self!r} adding {thing!r}")
        self.things.append(thing)

    def render(self):
        log.debug(f"{self!r} rendering")

    def apply(self):
        log.debug(f"{self!r} applying")
