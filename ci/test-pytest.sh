#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

# set the necessary envs if they are not present
if [ ! -f .env ]; then
    cp ./examples/.env .
fi

sed -i "/PROFILE=True/c\PROFILE=False" .env

pipenv run pytest
