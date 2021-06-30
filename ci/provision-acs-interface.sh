#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
else
    cp ./examples/.env .
fi

pipenv install --dev --ignore-pipfile
sudo -Hu vagrant mkdir -p data

container=$(docker ps -f name=minio -aq)
if [ -z "$container" ]; then (
    pipenv run examples/minio.sh
) fi

container=$(docker ps -f name=database -aq)
if [ -z "$container" ]; then (
    pipenv run examples/postgres.sh
) fi

sleep 2

pipenv run ./manage.py migrate
pipenv run ./manage.py storage_setup
pipenv run ./manage.py collectstatic --noinput
pipenv run ./manage.py loaddata ci/fixtures.json

echo "✔ acs-interface installed successfully"
