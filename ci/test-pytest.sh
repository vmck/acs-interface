#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

# set the necessary envs if they are not present
if [ ! -f .env ]; then
    cp ./examples/.env .
fi

exec sudo -Hu vagrant pipenv run pytest
