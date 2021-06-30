#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
    SUDO="sudo -Hu vagrant"
fi

# set the necessary envs if they are not present
if [ ! -f .env ]; then
    sudo -Hu vagrant cp ./examples/.env .
fi

sudo -Hu vagrant sed -i "/PROFILE=True/c\PROFILE=False" .env

$SUDO pipenv run pytest
