#!/usr/bin/env python3

from pathlib import Path
from oregano import terraform, nomad, cli

templates = Path(__file__).resolve().parent

config = terraform.Configuration()
config.add(terraform.NomadProvider('http://10.42.2.1:4646'))

job = nomad.Job(template=templates / 'interface.nomad')
config.add(job)

@cli.command()
def deploy():
    config.render()
    config.apply()

cli.main()
