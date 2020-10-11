#!/bin/bash -ex

cd /vagrant

# set the necessary envs if they are not present
if [ ! -f .env ]; then
    cp ./examples/.env .
fi

exec pipenv run pytest
