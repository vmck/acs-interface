#!/usr/bin/env python3

from pathlib import Path
from oregano import terraform, nomad, cli

path = Path(__file__).resolve().parent

config = terraform.Configuration(path / 'tf')
config.add(nomad.Provider('http://10.42.2.1:4646'))

job = nomad.Job('acs-interface', template=path / 'interface.nomad')
config.add(job)

@cli.command()
def deploy():
    config.init()
    config.render()
    config.apply()

cli.main()
