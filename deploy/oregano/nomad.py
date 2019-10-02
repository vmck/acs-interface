from os.path import relpath

from .templates import render


class Provider:

    def __init__(self, nomad_addr):
        self.nomad_addr = nomad_addr

    def __repr__(self):
        return f"<nomad.Provider {self.nomad_addr!r}>"

    def render(self):
        return render('nomad_provider.tf', {
            'address': self.nomad_addr,
        })


class Job:

    def __init__(self, name, template):
        self.name = name
        self.template = template

    def __repr__(self):
        return f"<nomad.Job {self.name!r}>"

    def render(self):
        return render('nomad_job.tf', {
            'name': self.name,
            'template_path': relpath(self.template, self.tf.path),
        })
