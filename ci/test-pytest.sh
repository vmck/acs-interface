#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

# set the necessary envs if they are not present
if [ ! -f .env ]; then
    sudo -Hu vagrant cp ./examples/.env .
fi

sudo -Hu vagrant sed -i "/PROFILE=True/c\PROFILE=False" .env

sudo -Hu vagrant pipenv run pytest
